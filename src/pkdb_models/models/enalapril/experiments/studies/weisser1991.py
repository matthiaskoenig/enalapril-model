"""Simulation experiment of the study Weisser1991."""

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


class Weisser1991(EnalaprilSimulationExperiment):
    """Simulation experiment of Weisser1991.

    8 healthy normotensive subjects (27-41 yr, 52-80 kg) on a diet of 150 mmol
    sodium per day, a single 10 mg enalapril maleate tablet at 08:00 or at
    20:00 (crossover, 6 weeks apart), 2 hr after a light meal. Enalaprilat in
    serum by RIA, enalapril indirectly (total drug after hydrolysis minus
    enalaprilat, in enalaprilat equivalents), mean ± SEM (Fig1). The model has
    no circadian time: both arms are simulated alike, the evening arm (the same
    subjects, supine at night) is the same simulation.
    """

    phases: ClassVar[tuple[str, str]] = ("morning", "evening")
    phase_labels: ClassVar[dict[str, str]] = {
        "morning": "08:00",
        "evening": "20:00",
    }
    markers: ClassVar[dict[str, str]] = {
        "morning": EnalaprilSimulationExperiment.time_markers["morning"],
        "evening": EnalaprilSimulationExperiment.time_markers["evening"],
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                # the enalapril of the indirect RIA is in enalaprilat
                # equivalents, both are converted with the Mr of enalaprilat
                dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(label)] = dset

        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        simulations["po_ENA10"] = Simulation(
            time_unit="hr",
            end=25,
            preinit_changes={
                **self.default_changes(),
                "BW": Q(66, "kg"),  # the middle of the range 52-80 kg
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
        for phase in self.phases:
            for sid, name in info.items():
                key = self.to_sid(f"fm_weisser1991_po_ENA10_{name}_{phase}")
                mappings[key] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(f"{phase}_{name}"),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                    ),
                    observable=FitData(
                        self,
                        task="task_po_ENA10",
                        xid="time",
                        yid=sid,
                    ),
                    metadata=PKPDMappingMetaData(
                        tissue=Tissue.SERUM,
                        route=Route.PO,
                        application_form=ApplicationForm.TABLET,
                        dosing=Dosing.SINGLE,
                        health=Health.HEALTHY,
                        genotype=Genotype.NR,
                        # 2 hr after a light meal; the stomach is empty at the
                        # dose (tmax and Cmax as fasted), no food effect is
                        # simulated
                        fasting=Fasting.LIGHT_BREAKFAST,
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

        # simulation
        for kp, sid in enumerate(["[Cve_ena]", "[Cve_eat]"]):
            plots[kp].add_data(
                task="task_po_ENA10",
                xid="time",
                yid=sid,
                label="ENA 10 mg",
                color=self.healthy_color,
            )
        # data
        for phase in self.phases:
            for kp, name in enumerate(["enalapril", "enalaprilat"]):
                plots[kp].add_data(
                    dataset=self.to_sid(f"{phase}_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=f"ENA 10 mg ({self.phase_labels[phase]})",
                    color=self.healthy_color,
                    marker=self.markers[phase],
                )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Weisser1991, output_dir=Weisser1991.__name__)
