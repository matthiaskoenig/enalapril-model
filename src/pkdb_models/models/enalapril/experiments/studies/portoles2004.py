"""Simulation experiment of the study Portoles2004."""

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

from pkdb_models.models.enalapril import MODEL
from pkdb_models.models.enalapril.experiments.base_experiment import (
    EnalaprilSimulationExperiment,
)


class Portoles2004(EnalaprilSimulationExperiment):
    """Simulation experiment of Portoles2004.

    Bioequivalence of two enalapril maleate 20 mg tablets (test Enalapril
    Farmoz, reference Renitec) in 24 healthy white volunteers (23 analysed, BW
    65.1 kg, height 173.0 cm), fasted 10 hr before and 4 hr after the dose,
    crossover. Plasma enalapril and enalaprilat by HPLC (Fig1, means without
    SD) and the blood pressure (Fig2, mean and SD). Every formulation is
    simulated with the blood pressure before its dose.
    """

    interventions: ClassVar[list[str]] = ["ENA20", "REN20"]
    # formulation: magenta (light = test, dark = reference)
    colors: ClassVar[dict[str, str]] = {
        "ENA20": EnalaprilSimulationExperiment.formulation_ramp[0],
        "REN20": EnalaprilSimulationExperiment.formulation_ramp[2],
    }
    SBP_refs: ClassVar[dict[str, float]] = {
        "ENA20": 114.04,
        "REN20": 112.90,
    }
    DBP_refs: ClassVar[dict[str, float]] = {
        "ENA20": 71.79,
        "REN20": 67.80,
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1", "Fig2"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                if label.endswith("_enalapril"):
                    dset.unit_conversion("mean", 1 / self.Mr.ena)
                elif label.endswith("_enalaprilat"):
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(label)] = dset
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        for intervention in self.interventions:
            simulations[self.to_sid(f"po_{intervention}")] = Simulation(
                time_unit="hr",
                end=38,
                preinit_changes={
                    **self.default_changes(),
                    "BW": Q(65.10, "kg"),  # body weight
                    "HEIGHT": Q(173.00, "cm"),  # height
                    "PODOSE_ena": Q(20, "mg")
                    * self.Mr.ena
                    / self.Mr.enamal,  # enalapril maleate
                    "SBP_ref": Q(self.SBP_refs[intervention], "mmHg"),
                    "DBP_ref": Q(self.DBP_refs[intervention], "mmHg"),
                },
            )
        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        info = {
            "[Cve_ena]": "enalapril",
            "[Cve_eat]": "enalaprilat",
            "SBP": "blood pressure systolic",
            "DBP": "blood pressure diastolic",
        }

        mappings = {}
        for sid, name in info.items():
            pk = sid in ["[Cve_ena]", "[Cve_eat]"]
            for intervention in self.interventions:
                mappings[self.to_sid(f"fm_ena20_{intervention}_{name}")] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(f"{intervention}_{name}"),
                        xid="time",
                        yid="mean",
                        # the concentrations are means without SD
                        yid_sd=None if pk else "mean_sd",
                        count="count",
                    ),
                    observable=FitData(
                        self,
                        task=self.to_sid(f"task_po_{intervention}"),
                        xid="time",
                        yid=sid,
                    ),
                    metadata=PKPDMappingMetaData(
                        tissue=Tissue.PLASMA if pk else Tissue.NONE,
                        route=Route.PO,
                        application_form=ApplicationForm.TABLET,
                        dosing=Dosing.SINGLE,
                        health=Health.HEALTHY,
                        genotype=Genotype.NR,
                        fasting=Fasting.FASTED,
                        data=PKPDData.PK if pk else PKPDData.PD,
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
            num_cols=1,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(self.labels["[Cve_ena]"], unit=self.units["[Cve_ena]"])
        plots[1].set_yaxis(self.labels["[Cve_eat]"], unit=self.units["[Cve_eat]"])

        # simulation
        for kp, sid in enumerate(["ena", "eat"]):
            for intervention in self.interventions:
                plots[kp].add_data(
                    task=self.to_sid(f"task_po_{intervention}"),
                    xid="time",
                    yid=f"[Cve_{sid}]",
                    label=intervention,
                    color=self.colors[intervention],
                )
        # data
        for kp, name in enumerate(["enalapril", "enalaprilat"]):
            for intervention in self.interventions:
                plots[kp].add_data(
                    dataset=self.to_sid(f"{intervention}_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd=None,
                    count="count",
                    label=f"{name} ({intervention})",
                    color=self.colors[intervention],
                )

        return self.figures_by_sid(fig)

    def _figure_pd(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig2",
            num_rows=2,
            num_cols=1,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(self.labels["SBP"], unit=self.units["SBP"])
        plots[1].set_yaxis(self.labels["DBP"], unit=self.units["DBP"])

        # simulation
        for kp, sid in enumerate(["SBP", "DBP"]):
            for intervention in self.interventions:
                plots[kp].add_data(
                    task=self.to_sid(f"task_po_{intervention}"),
                    xid="time",
                    yid=sid,
                    label=intervention,
                    color=self.colors[intervention],
                )
        # data
        for kp, name in enumerate(
            ["blood pressure systolic", "blood pressure diastolic"]
        ):
            for intervention in self.interventions:
                plots[kp].add_data(
                    dataset=self.to_sid(f"{intervention}_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=f"{name} ({intervention})",
                    color=self.colors[intervention],
                )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Portoles2004, output_dir=Portoles2004.__name__)
