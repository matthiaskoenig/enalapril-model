"""Simulation experiment of the study Lee2003."""

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


class Lee2003(EnalaprilSimulationExperiment):
    """Simulation experiment of Lee2003.

    A method paper (LC/MS/MS) with a pharmacokinetic application: 12 healthy
    Korean volunteers (sex, age and BW not reported), a single oral dose of
    20 mg enalapril maleate in tablets, fasting not reported. Plasma enalapril
    and enalaprilat to 12 hr (Fig4, mean ± SD; LLOQ 0.2 ng/ml enalapril, 1
    ng/ml enalaprilat).
    """

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig4"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                if label.startswith("enalapril_"):
                    dset.unit_conversion("mean", 1 / self.Mr.ena)
                elif label.startswith("enalaprilat_"):
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(label)] = dset
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        simulations["po_ENA20"] = Simulation(
            time_unit="hr",
            end=13,
            preinit_changes={
                **self.default_changes(),
                "PODOSE_ena": Q(20, "mg")
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
            mappings[self.to_sid(f"fm_lee2003_po_ENA20_{name}")] = FitMapping(
                self,
                reference=FitData(
                    self,
                    dataset=self.to_sid(f"{name}_plasma"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                ),
                observable=FitData(
                    self,
                    task="task_po_ENA20",
                    xid="time",
                    yid=sid,
                ),
                metadata=PKPDMappingMetaData(
                    tissue=Tissue.PLASMA,
                    route=Route.PO,
                    application_form=ApplicationForm.TABLET,
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
            sid="Fig4",
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
            plots[kp].add_data(
                task="task_po_ENA20",
                xid="time",
                yid=f"[Cve_{sid}]",
                label=sid,
                color="black",
            )
        # data
        for kp, name in enumerate(["enalapril", "enalaprilat"]):
            plots[kp].add_data(
                dataset=self.to_sid(f"{name}_plasma"),
                xid="time",
                yid="mean",
                yid_sd="mean_sd",
                count="count",
                label=name,
                color="black",
            )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Lee2003, output_dir=Lee2003.__name__)
