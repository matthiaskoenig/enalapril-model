"""Simulation experiment of the study Gu2004."""

from typing import override

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


class Gu2004(EnalaprilSimulationExperiment):
    """Simulation experiment of Gu2004.

    20 healthy volunteers, single oral dose of 10 mg enalapril maleate; plasma
    for 72 hr (LC-MS/MS, LLOQ 0.1 ng/ml). The paper reports neither the form
    (the curation says capsule) nor the food; the error bars are assumed SD.
    """

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig3"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                if label.endswith("_enalapril"):
                    dset.unit_conversion("mean", 1 / self.Mr.ena)
                elif label.endswith("_enalaprilat"):
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[label] = dset

        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        simulations["po_enamal10"] = Simulation(
            time_unit="hr",
            end=80,
            preinit_changes={
                **self.default_changes(),
                "PODOSE_ena": Q(10, "mg")
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
        }

        mappings = {}
        for sid, name in info.items():
            mappings[f"fm_ena10_{name}"] = FitMapping(
                self,
                reference=FitData(
                    self,
                    dataset=f"ENA10_{name}",
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
                    tissue=Tissue.PLASMA,
                    route=Route.PO,
                    # not reported in the paper
                    application_form=ApplicationForm.NR,
                    dosing=Dosing.SINGLE,
                    health=Health.HEALTHY,
                    genotype=Genotype.NR,
                    fasting=Fasting.NR,
                    data=PKPDData.PK,
                    data_type=DataType.MEAN,
                ),
            )

        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig3",
            num_rows=1,
            num_cols=2,
            name=f"{self.__class__.__name__} (healthy, 10 mg PO)",
            height=self.panel_height,
            width=self.panel_width * 2,
            settings={"legend_scope": "row"},
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(self.labels["[Cve_ena]"], unit=self.units["[Cve_ena]"])
        plots[1].set_yaxis(self.labels["[Cve_eat]"], unit=self.units["[Cve_eat]"])

        # simulation
        for kp, sid in enumerate(["ena", "eat"]):
            plots[kp].add_data(
                task="task_po_enamal10",
                xid="time",
                yid=f"[Cve_{sid}]",
                label="sim 10 mg",
                color=self.healthy_color,
            )
        # data
        for kp, name in enumerate(["enalapril", "enalaprilat"]):
            plots[kp].add_data(
                dataset=f"ENA10_{name}",
                xid="time",
                yid="mean",
                yid_sd="mean_sd",
                count="count",
                label="exp 10 mg",
                color=self.healthy_color,
            )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Gu2004, output_dir=Gu2004.__name__)
