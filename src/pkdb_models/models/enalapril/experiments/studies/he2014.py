"""Simulation experiment of the study He2014."""

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


class He2014(EnalaprilSimulationExperiment):
    """Simulation experiment of He2014.

    Healthy men and women (18-45 yr, BMI 18-30), crossover of 40 mg enalapril
    alone and with colesevelam 3750 mg; only the arm of enalapril alone is
    curated (35 subjects, colesevelam has no effect). Plasma for 144 hr
    (LC-MS/MS, Fig1C). The paper says "enalapril 40 mg" (the product and the
    reference standards are enalapril maleate, the dose is taken as the
    maleate); form and food are not reported.
    """

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1"]:
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
        simulations["po_ENA40"] = Simulation(
            time_unit="hr",
            end=145,
            preinit_changes={
                **self.default_changes(),
                "PODOSE_ena": Q(40, "mg")
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
            mappings[f"fm_po_ENA40_{name}"] = FitMapping(
                self,
                reference=FitData(
                    self,
                    dataset=f"ENA40_{name}",
                    xid="time",
                    yid="mean",
                    yid_sd=None,
                    count="count",
                ),
                observable=FitData(
                    self,
                    task="task_po_ENA40",
                    xid="time",
                    yid=sid,
                ),
                metadata=PKPDMappingMetaData(
                    tissue=Tissue.PLASMA,
                    route=Route.PO,
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
            sid="Fig1",
            num_rows=2,
            num_cols=2,
            name=f"{self.__class__.__name__} (healthy, 40 mg PO)",
            height=self.panel_height * 2,
            width=self.panel_width * 2,
            settings={"legend_scope": "row"},
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        for kr, scale in enumerate(["linear", "log"]):
            for kc, (sid, name) in enumerate(
                [("[Cve_ena]", "enalapril"), ("[Cve_eat]", "enalaprilat")]
            ):
                plot = plots[2 * kr + kc]
                plot.set_yaxis(
                    self.labels[sid],
                    unit=self.units[sid],
                    scale=scale,
                    min=1e-4 if scale == "log" else None,
                )
                # simulation
                plot.add_data(
                    task="task_po_ENA40",
                    xid="time",
                    yid=sid,
                    label="sim 40 mg",
                    color=self.healthy_color,
                )
                # data
                plot.add_data(
                    dataset=f"ENA40_{name}",
                    xid="time",
                    yid="mean",
                    yid_sd=None,
                    count="count",
                    label="exp 40 mg",
                    color=self.healthy_color,
                )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(He2014, output_dir=He2014.__name__)
