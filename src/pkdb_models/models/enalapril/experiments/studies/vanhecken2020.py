"""Simulation experiment of the study VanHecken2020."""

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


class VanHecken2020(EnalaprilSimulationExperiment):
    """Simulation experiment of VanHecken2020.

    24 healthy white adults (BW not reported), open randomized 3-way crossover
    after an overnight fast: 10 mg enalapril maleate as 2 x 5 mg Renitec
    tablets (REN10, reference, n = 23), as 10 x 1 mg orodispersible
    minitablets swallowed with water (ENAw10) or dispersed in the mouth
    (ENA10). Enalapril (Fig1) and enalaprilat (Fig2) in serum by LC-MS/MS,
    mean ± SD. The formulations are bioequivalent and simulated alike; the same
    subjects took all three.
    """

    interventions: ClassVar[dict[str, str]] = {
        "REN10": "tablets",
        "ENAw10": "minitablets swallowed",
        "ENA10": "minitablets dispersed",
    }
    # formulation: magenta (light = test, dark = reference)
    colors: ClassVar[dict[str, str]] = {
        "REN10": EnalaprilSimulationExperiment.formulation_ramp[2],
        "ENA10": EnalaprilSimulationExperiment.formulation_ramp[0],
        "ENAw10": EnalaprilSimulationExperiment.formulation_ramp[1],
    }
    markers: ClassVar[dict[str, str]] = {"REN10": "o", "ENAw10": "s", "ENA10": "^"}

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
        return {
            "po_enamal10": Simulation(
                time_unit="hr",
                end=50,
                preinit_changes={
                    **self.default_changes(),
                    "PODOSE_ena": Q(10, "mg")
                    * self.Mr.ena
                    / self.Mr.enamal,  # enalapril maleate
                },
            )
        }

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        info = {
            "[Cve_ena]": "enalapril",
            "[Cve_eat]": "enalaprilat",
        }

        mappings = {}
        for intervention in self.interventions:
            for sid, name in info.items():
                key = self.to_sid(f"fm_vanhecken2020_{intervention}_{name}")
                mappings[key] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(f"{intervention}_{name}"),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                    ),
                    observable=FitData(
                        self,
                        task="task_po_enamal10",
                        xid="time",
                        yid=sid,
                    ),
                    metadata=PKPDMappingMetaData(
                        tissue=Tissue.SERUM,
                        route=Route.PO,
                        # orodispersible minitablets: no member of their own
                        application_form=ApplicationForm.TABLET,
                        dosing=Dosing.SINGLE,
                        health=Health.HEALTHY,
                        genotype=Genotype.NR,
                        fasting=Fasting.FASTED,
                        data=PKPDData.PK,
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
            num_cols=2,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(self.labels["[Cve_ena]"], unit=self.units["[Cve_ena]"])
        plots[1].set_yaxis(self.labels["[Cve_eat]"], unit=self.units["[Cve_eat]"])
        plots[0].set_xaxis(self.labels["time"], unit=self.units["time"], min=0, max=12)

        for kp, sid in enumerate(["[Cve_ena]", "[Cve_eat]"]):
            plots[kp].add_data(
                task="task_po_enamal10",
                xid="time",
                yid=sid,
                label="ENA 10 mg",
                color=self.colors["REN10"],
            )
        for intervention, form in self.interventions.items():
            for kp, name in enumerate(["enalapril", "enalaprilat"]):
                plots[kp].add_data(
                    dataset=self.to_sid(f"{intervention}_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=f"ENA 10 mg ({form})",
                    color=self.colors[intervention],
                    marker=self.markers[intervention],
                )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(VanHecken2020, output_dir=VanHecken2020.__name__)
