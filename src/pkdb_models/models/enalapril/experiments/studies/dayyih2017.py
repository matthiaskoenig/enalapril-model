"""Simulation experiment of the study Dayyih2017."""

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


class Dayyih2017(EnalaprilSimulationExperiment):
    """Simulation experiment of Dayyih2017.

    Bioequivalence study in 30 healthy men: a single "enalapril 20 mg" tablet
    of a reference (`REF20`) and a test formulation (`TEST20`) in a crossover
    with 14 days of washout, after a fast of 12 h. Plasma enalapril (Fig5) and
    enalaprilat (Fig6) by LC-MS/MS (LLOQ 1 ng/ml) to 72 h, means without error
    bars.

    The paper does not name the salt; the marketed 20 mg tablets contain 20 mg
    enalapril maleate, which is simulated. The values below the LLOQ after the
    peak (enalapril from 8 h on, enalaprilat at 72 h) are read from a linear
    axis of 140 ng/ml and are not used. Both arms are the same subjects: the
    reference arm is fitted, the test arm is an aggregate of the same subjects.
    """

    interventions: ClassVar[list[str]] = ["REF20", "TEST20"]
    # formulation: magenta (light = test, dark = reference)
    colors: ClassVar[dict[str, str]] = {
        "TEST20": EnalaprilSimulationExperiment.formulation_ramp[0],
        "REF20": EnalaprilSimulationExperiment.formulation_ramp[2],
    }
    labels_intervention: ClassVar[dict[str, str]] = {
        "TEST20": "20 mg test",
        "REF20": "20 mg reference",
    }
    #: the observable by the substance of the data
    info: ClassVar[dict[str, str]] = {
        "enalapril": "[Cve_ena]",
        "enalaprilat": "[Cve_eat]",
    }
    #: the lower limit of quantification [ng/ml]
    lloq: ClassVar[float] = 1.0

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig5", "Fig6"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                # the values below the LLOQ after the peak
                t_max = df_label.loc[df_label["mean"].idxmax(), "time"]
                df_label = df_label[
                    (df_label.time <= t_max) | (df_label["mean"] >= self.lloq)
                ]
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
        simulations["po_enamal20"] = Simulation(
            time_unit="hr",
            end=73,
            preinit_changes={
                **self.default_changes(),
                # enalapril maleate
                "PODOSE_ena": Q(20, "mg") * self.Mr.ena / self.Mr.enamal,
            },
        )

        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for name, sid in self.info.items():
            for intervention in self.interventions:
                key = self.to_sid(f"fm_dayyih2017_{name}_{intervention}")
                mappings[key] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(f"{name}_{intervention}"),
                        xid="time",
                        yid="mean",
                        yid_sd=None,
                        count="count",
                    ),
                    observable=FitData(
                        self, task="task_po_enamal20", xid="time", yid=sid
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
            sid="Fig5_Fig6",
            num_rows=1,
            num_cols=2,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        for kp, (name, sid) in enumerate(self.info.items()):
            plots[kp].set_yaxis(self.labels[sid], unit=self.units[sid])
            plots[kp].add_data(
                task="task_po_enamal20",
                xid="time",
                yid=sid,
                label="20 mg",
                color=self.healthy_color,
            )
            for intervention in self.interventions:
                plots[kp].add_data(
                    dataset=self.to_sid(f"{name}_{intervention}"),
                    xid="time",
                    yid="mean",
                    yid_sd=None,
                    count="count",
                    label=self.labels_intervention[intervention],
                    color=self.colors[intervention],
                )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Dayyih2017, output_dir=Dayyih2017.__name__)
