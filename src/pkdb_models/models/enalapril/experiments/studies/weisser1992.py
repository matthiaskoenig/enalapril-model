"""Simulation experiment of the study Weisser1992."""

from typing import ClassVar, override

from pkpdsim.metadata import (
    ApplicationForm,
    Coadministration,
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


class Weisser1992(EnalaprilSimulationExperiment):
    """Simulation experiment of Weisser1992.

    19 elderly hypertensive patients (62-84 yr) with a creatinine clearance of
    11-93 ml/min (mean 45.6), after 3 days on a low sodium diet: a single
    tablet of 10 mg enalapril maleate, or 10 mg enalapril maleate with 25 mg
    hydrochlorothiazide (randomized crossover, 4 days washout). Enalaprilat in
    serum by RIA, enalapril indirectly (total drug after hydrolysis minus
    enalaprilat, in enalaprilat equivalents), 0-32 hr (Fig1), the cumulative
    urinary excretion 0-24 hr (Tab1, n = 18) and the serum ACE activity in vitro
    (1:11 dilution) relative to the value before the dose (Fig3). The renal
    function is the mean creatinine clearance. Hydrochlorothiazide is simulated
    without an interaction (`INTERACTION_FACTORS`); the study found a lower
    renal clearance of enalaprilat with it (62 -> 43 ml/min), which is not
    modelled.
    """

    #: the arms by the coadministration
    interventions: ClassVar[dict[str, Coadministration]] = {
        "ENA10": Coadministration.NONE,
        "HCTZ25, ENA10": Coadministration.HCTZ,
    }
    #: the mean creatinine clearance of the patients [ml/min]
    clcr: ClassVar[float] = 45.6

    # renal impairment: green (moderate, CLcr 45.6), the arm by the marker
    colors: ClassVar[dict[str, str]] = {
        "ENA10": EnalaprilSimulationExperiment.renal_colors[
            "Moderate renal impairment"
        ],
        "HCTZ25, ENA10": EnalaprilSimulationExperiment.renal_colors[
            "Moderate renal impairment"
        ],
    }
    markers: ClassVar[dict[str, str]] = {"ENA10": "o", "HCTZ25, ENA10": "s"}
    linestyles: ClassVar[dict[str, str]] = {"ENA10": "-", "HCTZ25, ENA10": "--"}
    arm_ids: ClassVar[dict[str, str]] = {
        "ENA10": "ENA10",
        "HCTZ25, ENA10": "ENA10_HCTZ25",
    }
    arm_labels: ClassVar[dict[str, str]] = {
        "ENA10": "ENA 10 mg",
        "HCTZ25, ENA10": "ENA 10 mg + HCTZ 25 mg",
    }

    #: the observables by the name of the data
    study_observables: ClassVar[dict[str, str]] = {
        "enalapril": "[Cve_ena]",
        "enalaprilat": "[Cve_eat]",
        "cumulative amount_enalapril": "Aurine_ena",
        "cumulative amount_enalaprilat": "Aurine_eat",
        "relative ACE activity": "ace_activity",
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1", "Tab1U", "Fig3"]:
            df = self.load_dataframe(fig_id)
            if fig_id == "Tab1U":
                # the cumulative amounts (mg), not the recovery the curation
                # derived from them (a mass ratio to the dose of the maleate)
                df = df[df["measurement_type"] == "cumulative amount"]
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                if label.endswith(("_enalapril", "_enalaprilat")):
                    # the enalapril of the indirect RIA is in enalaprilat
                    # equivalents, both are converted with the Mr of enalaprilat
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(label)] = dset

        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        return {
            self.to_sid(f"po_{intervention}"): Simulation(
                time_unit="hr",
                end=33,
                preinit_changes={
                    **self.default_changes(),
                    **self.interaction_changes(coadministration),
                    "PODOSE_ena": Q(10, "mg")
                    * self.Mr.ena
                    / self.Mr.enamal,  # enalapril maleate
                    # the mean creatinine clearance, CLcr / 101 ml/min
                    "KI__f_renal_function": Q(self.clcr / 101, "dimensionless"),
                },
            )
            for intervention, coadministration in self.interventions.items()
        }

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for intervention, coadministration in self.interventions.items():
            for name, sid in self.study_observables.items():
                urine = sid.startswith("Aurine")
                key = self.to_sid(f"fm_weisser1992_{self.arm_ids[intervention]}_{name}")
                mappings[key] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(f"{intervention}_{name}"),
                        xid="time",
                        yid="mean",
                        # the ACE activity has no errors
                        yid_sd=None if sid == "ace_activity" else "mean_sd",
                        count="count",
                    ),
                    observable=FitData(
                        self,
                        task=self.to_sid(f"task_po_{intervention}"),
                        xid="time",
                        yid=sid,
                    ),
                    metadata=PKPDMappingMetaData(
                        tissue=Tissue.URINE if urine else Tissue.SERUM,
                        route=Route.PO,
                        application_form=ApplicationForm.TABLET,
                        dosing=Dosing.SINGLE,
                        # hypertensive elderly patients, the renal function
                        # (CLcr 11-93 ml/min) changes the pharmacokinetics
                        health=Health.RENAL_IMPAIRMENT,
                        genotype=Genotype.NR,
                        fasting=Fasting.NR,
                        coadministration=coadministration,
                        data=PKPDData.PD if sid == "ace_activity" else PKPDData.PK,
                        data_type=DataType.MEAN,
                    ),
                )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig1",
            num_rows=1,
            num_cols=5,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_xaxis(self.labels["time"], unit=self.units["time"], min=0, max=12)
        for kp, sid in enumerate(self.study_observables.values()):
            plots[kp].set_yaxis(self.labels[sid], unit=self.units[sid])

        for intervention in self.interventions:
            for kp, (name, sid) in enumerate(self.study_observables.items()):
                plots[kp].add_data(
                    task=self.to_sid(f"task_po_{intervention}"),
                    xid="time",
                    yid=sid,
                    label=self.arm_labels[intervention],
                    color=self.colors[intervention],
                    linestyle=self.linestyles[intervention],
                )
                plots[kp].add_data(
                    dataset=self.to_sid(f"{intervention}_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd=None if sid == "ace_activity" else "mean_sd",
                    count="count",
                    label=self.arm_labels[intervention],
                    color=self.colors[intervention],
                    marker=self.markers[intervention],
                    linestyle="" if sid.startswith("Aurine") else "--",
                )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Weisser1992, output_dir=Weisser1992.__name__)
