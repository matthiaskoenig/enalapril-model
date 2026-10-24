"""Simulation experiment of the study Oguchi1993."""

from typing import ClassVar, override

from pkpdsim.metadata import (
    ApplicationForm,
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
from sbmlsim.units import Quantity

from pkdb_models.models.enalapril import MODEL
from pkdb_models.models.enalapril.experiments.base_experiment import (
    EnalaprilSimulationExperiment,
)


class Oguchi1993(EnalaprilSimulationExperiment):
    """Simulation experiment of Oguchi1993.

    Enalapril maleate 5 mg (one tablet, 30 min after breakfast) in hypertensive
    inpatients with normal (group 1, CLcr 109.1 ml/min/1.73 m2, BW 62.0 kg),
    moderately (group 2, 50.2, 60.4 kg) and severely impaired renal function
    (group 3, 10.3, 56.0 kg), n = 6 each (the temocapril arms are not
    simulated). Plasma enalapril and enalaprilat by GC-MS (Fig2, mean and SE),
    the urinary recovery 0-48 hr in percent of the dose (Tab3) and the ACE
    inhibition (Fig4). The breakfast of the standard hospital diet (2000-2200
    kcal per day) is a light breakfast (`fasting_map`).
    """

    groups: ClassVar[list[str]] = ["1", "2", "3"]
    colors: ClassVar[dict[str, str]] = {
        "1": EnalaprilSimulationExperiment.renal_colors["Normal renal function"],
        "2": EnalaprilSimulationExperiment.renal_colors["Moderate renal impairment"],
        "3": EnalaprilSimulationExperiment.renal_colors["Severe renal impairment"],
    }
    #: the measured creatinine clearance (ml/min/1.73 m2) over the GFR of the
    #: model (101 ml/min)
    renal_functions: ClassVar[dict[str, float]] = {
        "1": 109.1 / 101,
        "2": 50.2 / 101,
        "3": 10.3 / 101,
    }
    # only enalapril groups considered; temocapril excluded
    bodyweights: ClassVar[dict[str, float]] = {"1": 62, "2": 60.4, "3": 56}

    #: the dose of enalapril maleate as an amount, the recovery is a fraction of it
    dose_amount: ClassVar[Quantity] = (
        Q(5, "mg") / EnalaprilSimulationExperiment.Mr.enamal
    )

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig2", "Fig4", "Tab3"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                if label.startswith("Tem") or "cumulative amount" in label:
                    # temocapril; the amounts are the recovery times the dose
                    # in mg of the maleate, not the amounts of the analytes
                    continue
                dset = DataSet.from_df(df_label, self.ureg)
                if "_recovery_" in label:
                    # the fraction of the dose excreted in the urine (molar)
                    dset.unit_conversion("mean", self.dose_amount)
                elif label.endswith("_enalapril"):
                    dset.unit_conversion("mean", 1 / self.Mr.ena)
                elif label.endswith("_enalaprilat"):
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(label)] = dset
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}

        for group in self.groups:
            simulations[self.to_sid(f"po_ENA5_{group}")] = Simulation(
                time_unit="hr",
                end=50,
                preinit_changes={
                    **self.default_changes(),
                    "BW": Q(self.bodyweights[group], "kg"),
                    "KI__f_renal_function": Q(
                        self.renal_functions[group], "dimensionless"
                    ),
                    "GU__fed": Q(self.fasting_map["light breakfast"], "dimensionless"),
                    "PODOSE_ena": Q(5, "mg")
                    * self.Mr.ena
                    / self.Mr.enamal,  # enalapril maleate
                },
            )

        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        info = {
            "[Cve_ena]": "enalapril",
            "[Cve_eat]": "enalaprilat",
            "Aurine_ena": "recovery_enalapril",
            "Aurine_eat": "recovery_enalaprilat",
            "ace_inhibition": "ACE inhibition",
        }

        mappings = {}
        for group in self.groups:
            for sid, name in info.items():
                mappings[self.to_sid(f"fm_po_ENA5_{group}_{name}")] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(f"Ena{group}_{name}"),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                    ),
                    observable=FitData(
                        self,
                        task=self.to_sid(f"task_po_ENA5_{group}"),
                        xid="time",
                        yid=sid,
                    ),
                    metadata=PKPDMappingMetaData(
                        tissue=Tissue.URINE
                        if sid.startswith("Aurine")
                        else Tissue.PLASMA,
                        route=Route.PO,
                        application_form=ApplicationForm.TABLET,
                        dosing=Dosing.SINGLE,
                        health=Health.HYPERTENSION
                        if group == "1"
                        else Health.RENAL_IMPAIRMENT,
                        genotype=Genotype.NR,
                        fasting=Fasting.LIGHT_BREAKFAST,
                        data=PKPDData.PD if sid == "ace_inhibition" else PKPDData.PK,
                    ),
                )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        return {**self._figure_pk(), **self._figure_pd()}

    def _figure_pk(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig1",
            num_rows=2,
            num_cols=2,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(self.labels["[Cve_ena]"], unit=self.units["[Cve_ena]"])
        plots[1].set_yaxis(self.labels["[Cve_eat]"], unit=self.units["[Cve_eat]"])
        plots[2].set_yaxis(self.labels["Aurine_ena"], unit=self.units["Aurine_ena"])
        plots[3].set_yaxis(self.labels["Aurine_eat"], unit=self.units["Aurine_eat"])

        # simulation
        for group in self.groups:
            for krow, sid in enumerate(["ena", "eat"]):
                for kcol, yid in enumerate([f"[Cve_{sid}]", f"Aurine_{sid}"]):
                    plots[kcol * 2 + krow].add_data(
                        task=self.to_sid(f"task_po_ENA5_{group}"),
                        xid="time",
                        yid=yid,
                        label=f"group {group}",
                        color=self.colors[group],
                    )

            # data
            for krow, name in enumerate(["enalapril", "enalaprilat"]):
                plots[krow].add_data(
                    dataset=self.to_sid(f"Ena{group}_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=f"{name} (group {group})",
                    color=self.colors[group],
                )
                plots[krow + 2].add_data(
                    dataset=self.to_sid(f"Ena{group}_recovery_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=f"{name} urine (group {group})",
                    color=self.colors[group],
                )

        return self.figures_by_sid(fig)

    def _figure_pd(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig2",
            num_rows=1,
            num_cols=1,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(
            self.labels["ace_inhibition"], unit=self.units["ace_inhibition"]
        )

        for group in self.groups:
            # simulation
            plots[0].add_data(
                task=self.to_sid(f"task_po_ENA5_{group}"),
                xid="time",
                yid="ace_inhibition",
                label=f"group {group}",
                color=self.colors[group],
            )
            # data
            plots[0].add_data(
                dataset=self.to_sid(f"Ena{group}_ACE inhibition"),
                xid="time",
                yid="mean",
                yid_sd="mean_sd",
                count="count",
                label=f"ACE inhibition (group {group})",
                color=self.colors[group],
            )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Oguchi1993, output_dir=Oguchi1993.__name__)
