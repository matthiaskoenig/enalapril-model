"""Simulation experiment of the study Wade1992."""

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


class Wade1992(EnalaprilSimulationExperiment):
    """Simulation experiment of Wade1992.

    8 healthy normotensive men (74 kg, 176 cm, CLcr 115 ml/min), a single oral
    dose of 10 mg enalapril (form and fasting not reported) and placebo,
    double-blind crossover. Enalaprilat in plasma by a radioenzymatic assay
    (Fig1, mean ± SD), the ACE inhibition in plasma corrected for placebo (Fig2)
    and the plasma ACE activity relative to the value before the dose (Fig3),
    both without errors, 0-72 hr. The arms with captopril 50 mg twice daily
    (phase 2) are not simulated (no captopril in the model).
    """

    interventions: ClassVar[list[str]] = ["ENA10", "PLACEBO"]
    # healthy subjects: drug black, placebo grey
    colors: ClassVar[dict[str, str]] = {
        "ENA10": EnalaprilSimulationExperiment.healthy_color,
        "PLACEBO": EnalaprilSimulationExperiment.placebo_color,
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1", "Fig2", "Fig3"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                if label.endswith("_enalaprilat"):
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(label)] = dset
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        return {
            f"po_{intervention}": Simulation(
                time_unit="hr",
                end=73,
                preinit_changes={
                    **self.default_changes(),
                    "BW": Q(74, "kg"),
                    "HEIGHT": Q(176, "cm"),
                    "KI__f_renal_function": Q(115 / 101, "dimensionless"),
                    "PODOSE_ena": Q(10 if intervention == "ENA10" else 0, "mg")
                    * self.Mr.ena
                    / self.Mr.enamal,  # enalapril maleate
                },
            )
            for intervention in self.interventions
        }

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        # the ACE inhibition of Fig2 and the relative ACE activity of Fig3 are
        # the same samples (the inhibition corrected for placebo); the placebo
        # arm is plotted only
        info = {
            "[Cve_eat]": ("enalaprilat", "mean_sd"),
            "ace_inhibition": ("ACE inhibition", None),
            "ace_activity": ("relative ACE activity", None),
        }

        mappings = {}
        for sid, (name, yid_sd) in info.items():
            mappings[self.to_sid(f"fm_wade1992_ENA10_{name}")] = FitMapping(
                self,
                reference=FitData(
                    self,
                    dataset=self.to_sid(f"ENA10_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd=yid_sd,
                    count="count",
                ),
                observable=FitData(
                    self,
                    task="task_po_ENA10",
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
                    data=PKPDData.PK if sid == "[Cve_eat]" else PKPDData.PD,
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
            num_cols=3,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(self.labels["[Cve_eat]"], unit=self.units["[Cve_eat]"])
        plots[1].set_yaxis(
            self.labels["ace_inhibition"], unit=self.units["ace_inhibition"]
        )
        plots[2].set_yaxis(self.labels["ace_activity"], unit=self.units["ace_activity"])

        # simulation
        for kp, sid in enumerate(["[Cve_eat]", "ace_inhibition", "ace_activity"]):
            plots[kp].add_data(
                task="task_po_ENA10",
                xid="time",
                yid=sid,
                label="ENA 10 mg",
                color=self.colors["ENA10"],
            )
        plots[2].add_data(
            task="task_po_PLACEBO",
            xid="time",
            yid="ace_activity",
            label="placebo",
            color=self.colors["PLACEBO"],
        )
        # data
        for kp, (name, yid_sd) in enumerate(
            [
                ("enalaprilat", "mean_sd"),
                ("ACE inhibition", None),
                ("relative ACE activity", None),
            ]
        ):
            plots[kp].add_data(
                dataset=self.to_sid(f"ENA10_{name}"),
                xid="time",
                yid="mean",
                yid_sd=yid_sd,
                count="count",
                label="ENA 10 mg",
                color=self.colors["ENA10"],
            )
        plots[2].add_data(
            dataset=self.to_sid("PLACEBO_relative ACE activity"),
            xid="time",
            yid="mean",
            yid_sd=None,
            count="count",
            label="placebo",
            color=self.colors["PLACEBO"],
        )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Wade1992, output_dir=Wade1992.__name__)
