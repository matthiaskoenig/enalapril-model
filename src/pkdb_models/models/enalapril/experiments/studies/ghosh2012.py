"""Simulation experiment of the study Ghosh2012."""

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


class Ghosh2012(EnalaprilSimulationExperiment):
    """Simulation experiment of Ghosh2012.

    36 healthy male volunteers, two-way crossover of two tablets (test and
    reference) of 20 mg enalapril maleate after an overnight fast of at least
    10 hr; plasma for 72 hr (LC-MS/MS). Both arms are the same subjects.

    The enalapril has a plateau of 6-8 ng/ml from 9 to 72 hr (Fig5A, mean
    AUCinf 2846 +- 9314 ng*hr/ml, t1/2 44.6 +- 117.7 hr), a few subjects with
    a persistent signal; the half-life of enalapril is 1-2 hr in the other
    LC-MS/MS studies (Gu2004, He2014, Her2021). The enalapril from 9 hr on is
    mapped separately (`*_enalapril_late`) as an outlier.
    """

    tablets: ClassVar[list[str]] = ["Test", "Ref"]
    # formulation: magenta (light = test, dark = reference)
    colors: ClassVar[dict[str, str]] = {
        "Test": EnalaprilSimulationExperiment.formulation_ramp[0],
        "Ref": EnalaprilSimulationExperiment.formulation_ramp[2],
    }
    #: the enalapril from this time on is the plateau of a few subjects [hr]
    t_plateau: ClassVar[float] = 9.0

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig5A", "Fig5B"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                parts = {label: df_label}
                if label.endswith("_enalapril"):
                    late = df_label.time >= self.t_plateau
                    parts = {label: df_label[~late], f"{label}_late": df_label[late]}
                for key, df_part in parts.items():
                    dset = DataSet.from_df(df_part, self.ureg)
                    if label.endswith("_enalapril"):
                        dset.unit_conversion("mean", 1 / self.Mr.ena)
                    elif label.endswith("_enalaprilat"):
                        dset.unit_conversion("mean", 1 / self.Mr.eat)
                    dsets[key] = dset
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        simulations["po_enamal20"] = Simulation(
            time_unit="hr",
            end=74,
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
            "enalapril": "[Cve_ena]",
            "enalapril_late": "[Cve_ena]",
            "enalaprilat": "[Cve_eat]",
        }
        mappings = {}
        for name, sid in info.items():
            for tablet in self.tablets:
                # the outlier keys are unique across the studies
                mappings[f"fm_ghosh2012_enamal20_{name}_{tablet}"] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=f"{tablet}_{name}",
                        xid="time",
                        yid="mean",
                        yid_sd=None,
                        count="count",
                    ),
                    observable=FitData(
                        self,
                        task="task_po_enamal20",
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
            sid="Fig5",
            num_rows=2,
            num_cols=2,
            name=f"{self.__class__.__name__} (healthy, 20 mg PO)",
            height=self.panel_height * 2,
            width=self.panel_width * 2,
            settings={"legend_scope": "row"},
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        for kr, scale in enumerate(["linear", "log"]):
            for kc, (sid, names) in enumerate(
                [
                    ("[Cve_ena]", ["enalapril", "enalapril_late"]),
                    ("[Cve_eat]", ["enalaprilat"]),
                ]
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
                    task="task_po_enamal20",
                    xid="time",
                    yid=sid,
                    label="sim 20 mg",
                    color=self.healthy_color,
                )
                # data
                for tablet in self.tablets:
                    for name in names:
                        late = name.endswith("_late")
                        plot.add_data(
                            dataset=f"{tablet}_{name}",
                            xid="time",
                            yid="mean",
                            yid_sd=None,
                            count="count",
                            label=f"exp {tablet}{' (outlier)' if late else ''}",
                            color=self.colors[tablet],
                            marker="x" if late else "s",
                        )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Ghosh2012, output_dir=Ghosh2012.__name__)
