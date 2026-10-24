"""Simulation experiment of the study Witte1993."""

from typing import ClassVar, override

from pkpdsim.metadata import (
    ApplicationForm,
    DataType,
    Dosing,
    Fasting,
    Genotype,
    Health,
    PKPDData,
    PKPDMappingMetaData,
    Route,
    Tissue,
)
from sbmlsim import Q
from sbmlsim.data import DataSet
from sbmlsim.fit import FitData, FitMapping
from sbmlsim.plot import Axis, Figure
from sbmlsim.simulation import Simulation

from pkdb_models.models.enalapril import MODEL
from pkdb_models.models.enalapril.experiments.base_experiment import (
    EnalaprilSimulationExperiment,
)

#: the time of the last of the 21 daily doses [hr]
LAST_DOSE = 480.0


class Witte1993(EnalaprilSimulationExperiment):
    """Simulation experiment of Witte1993.

    8 patients with mild to moderate essential hypertension (normal renal
    function), after a drug-free run-in 3 weeks of 10 mg enalapril maleate
    (Xanef tablets) once daily at 07:00 ("morning") or at 19:00 ("night"),
    randomized crossover. Ambulatory blood pressure on the drug-free control
    day (NA), after the first dose (ENAs10, Fig2) and after the last dose
    (ENAm10, Fig1); enalapril and enalaprilat in serum by RIA (enalapril
    indirectly, total drug after hydrolysis minus enalaprilat, in enalaprilat
    equivalents) 0-24 hr after the first and 0-48 hr after the last dose; the
    serum ACE activity in vitro (1:11 dilution) every 4 hr (Fig3), mean ± SEM.
    The time of the data is the time after the dose (the first dose at 0 hr,
    the last at 480 hr). The model has no circadian rhythm: both dosing times
    are the same simulation, the blood pressure is relative to the 24 hr mesor
    of the control day.
    """

    doses: ClassVar[dict[str, str]] = {
        "ENAs10": "first dose",
        "ENAm10": "last dose",
    }
    phases: ClassVar[dict[str, str]] = {"morning": "07:00", "night": "19:00"}
    markers: ClassVar[dict[str, str]] = {
        "morning": EnalaprilSimulationExperiment.time_markers["morning"],
        "night": EnalaprilSimulationExperiment.time_markers["night"],
    }
    # colour = dosing (no-drug arms grey, single < multiple dose in gold shades),
    # marker = time of day
    colors: ClassVar[dict[str, str]] = {
        "NA": EnalaprilSimulationExperiment.placebo_color,
        **EnalaprilSimulationExperiment.dose_colors(["ENAs10", "ENAm10"]),
    }
    #: the figure of the data of a dose
    fig_ids: ClassVar[dict[str, str]] = {"ENAs10": "Fig2", "ENAm10": "Fig1"}

    #: the observables by the name of the data
    study_observables: ClassVar[dict[str, str]] = {
        "enalapril": "[Cve_ena]",
        "enalaprilat": "[Cve_eat]",
        "blood pressure systolic": "SBP",
        "blood pressure diastolic": "DBP",
        "relative ACE activity": "ace_activity",
    }

    def data_key(self, dose: str, phase: str, name: str) -> str:
        """Get the key of a dataset of the study."""
        fig_id = "Fig3" if name == "relative ACE activity" else self.fig_ids[dose]
        return self.to_sid(f"{fig_id}_{phase}_{dose}_{name}")

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1", "Fig2", "Fig3"]:
            df = self.load_dataframe(fig_id)
            # the predose sample of Fig2 is digitized at -0.05 hr, it is the
            # value at the dose
            df.loc[df["time"] < 0, "time"] = 0.0
            if fig_id == "Fig3":
                df = df[df["measurement_type"] == "relative ACE activity"]
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                if label.endswith(("_enalapril", "_enalaprilat")):
                    # the enalapril of the indirect RIA is in enalaprilat
                    # equivalents, both are converted with the Mr of enalaprilat
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(f"{fig_id}_{label}")] = dset
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        reference = {
            # the 24 hr mesor of the blood pressure on the drug-free control day
            # (Tab2), the reference of all arms
            "SBP_ref": Q(145.8, "mmHg"),
            "DBP_ref": Q(85.0, "mmHg"),
        }
        dose = Q(10, "mg") * self.Mr.ena / self.Mr.enamal  # enalapril maleate
        return {
            # 21 daily doses, the first at 0 hr, the last at 480 hr
            "po_ENAm10": Simulation(
                time_unit="hr",
                end=LAST_DOSE + 50,
                preinit_changes={
                    **self.default_changes(),
                    **reference,
                    "PODOSE_ena": dose,
                },
                changes=[
                    self.add_doses(
                        [24.0 * k for k in range(1, 21)],
                        {"PODOSE_ena": dose},
                    )
                ],
            ),
            # the drug-free control day
            "po_NA": Simulation(
                time_unit="hr",
                end=50,
                preinit_changes={
                    **self.default_changes(),
                    **reference,
                    "PODOSE_ena": Q(0, "mg"),
                },
            ),
        }

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for dose in self.doses:
            for phase in self.phases:
                for name, sid in self.study_observables.items():
                    key = self.to_sid(f"fm_witte1993_{phase}_{dose}_{name}")
                    mappings[key] = FitMapping(
                        self,
                        reference=FitData(
                            self,
                            dataset=self.data_key(dose, phase, name),
                            xid="time",
                            yid="mean",
                            yid_sd="mean_sd",
                            count="count",
                        ),
                        observable=FitData(
                            self, task="task_po_ENAm10", xid="time", yid=sid
                        ),
                        metadata=PKPDMappingMetaData(
                            tissue=Tissue.NONE
                            if sid in {"SBP", "DBP"}
                            else Tissue.SERUM,
                            route=Route.PO,
                            application_form=ApplicationForm.TABLET,
                            # the data after the first dose are the data of a
                            # single dose
                            dosing=Dosing.SINGLE
                            if dose == "ENAs10"
                            else Dosing.MULTIPLE,
                            health=Health.HYPERTENSION,
                            genotype=Genotype.NR,
                            # 07:00 after the night, breakfast at 08:00; 19:00
                            # 1.5 hr after the evening meal (simulated as the
                            # morning dose)
                            fasting=Fasting.FASTED
                            if phase == "morning"
                            else Fasting.NR,
                            data=PKPDData.PK
                            if sid in {"[Cve_ena]", "[Cve_eat]"}
                            else PKPDData.PD,
                            data_type=DataType.MEAN,
                        ),
                    )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        names = list(self.study_observables)
        fig = Figure(
            experiment=self,
            sid="Fig1",
            num_rows=2,
            num_cols=len(names),
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        # first row: the first dose and the control day, second row: the last
        # dose
        windows = {"ENAs10": (-1, 26), "ENAm10": (LAST_DOSE - 1, LAST_DOSE + 50)}
        for krow, dose in enumerate(self.doses):
            tmin, tmax = windows[dose]
            for kcol, name in enumerate(names):
                sid = self.study_observables[name]
                plot = plots[krow * len(names) + kcol]
                plot.set_xaxis(
                    self.labels["time"], unit=self.units["time"], min=tmin, max=tmax
                )
                plot.set_yaxis(self.labels[sid], unit=self.units[sid])
                plot.add_data(
                    task="task_po_ENAm10",
                    xid="time",
                    yid=sid,
                    label=f"ENA 10 mg ({self.doses[dose]})",
                    color=self.colors[dose],
                )
                if dose == "ENAs10" and sid not in {"[Cve_ena]", "[Cve_eat]"}:
                    plot.add_data(
                        task="task_po_NA",
                        xid="time",
                        yid=sid,
                        label="control day",
                        color=self.colors["NA"],
                    )
                for phase, clock in self.phases.items():
                    if dose == "ENAs10" and sid not in {"[Cve_ena]", "[Cve_eat]"}:
                        # the drug-free control day (blood pressure: Fig2)
                        fig_id = "Fig3" if sid == "ace_activity" else "Fig2"
                        plot.add_data(
                            dataset=self.to_sid(f"{fig_id}_{phase}_NA_{name}"),
                            xid="time",
                            yid="mean",
                            yid_sd="mean_sd",
                            count="count",
                            label=f"control ({clock})",
                            color=self.colors["NA"],
                            marker=self.markers[phase],
                        )
                    plot.add_data(
                        dataset=self.data_key(dose, phase, name),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                        label=f"ENA 10 mg {self.doses[dose]} ({clock})",
                        color=self.colors[dose],
                        marker=self.markers[phase],
                    )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Witte1993, output_dir=Witte1993.__name__)
