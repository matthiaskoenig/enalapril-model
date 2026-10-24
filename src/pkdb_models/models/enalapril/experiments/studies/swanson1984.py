"""Simulation experiment of the study Swanson1984."""

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


class Swanson1984(EnalaprilSimulationExperiment):
    """Simulation experiment of Swanson1984.

    12 healthy men, randomized crossover of a single 40 mg tablet of enalapril
    maleate fasted (from midnight) or immediately after a standard breakfast
    (egg, toast, bacon or sausage, milk or juice, coffee). Serum enalaprilat
    0-48 hr, the urinary excretion rates of enalaprilat and of the total drug
    (enalaprilat after hydrolysis, in enalaprilat equivalents) and the
    recovery 0-48 hr in percent of the enalaprilat equivalents of the tablet.
    The assay of the tablet was 42.02 mg enalapril maleate (29.88 mg
    enalaprilat equivalents), which is simulated.
    """

    groups: ClassVar[list[str]] = ["fasting", "fed"]
    colors: ClassVar[dict[str, str]] = {
        "fasting": EnalaprilSimulationExperiment.fasting_colors["fasting"],
        "fed": EnalaprilSimulationExperiment.fasting_colors["fed"],
    }
    #: the state of the intestine of the groups (`GU__fed`): the standard
    #: breakfast directly before the dose is a fed state
    fed: ClassVar[dict[str, str]] = {"fasting": "fasted", "fed": "fed"}
    fastings: ClassVar[dict[str, Fasting]] = {
        "fasting": Fasting.FASTED,
        "fed": Fasting.FED,
    }

    #: the assayed amount of enalapril maleate of the tablet (nominal 40 mg)
    dose: ClassVar[Quantity] = Q(42.02, "mg")
    #: the dose as an amount, the recovery is a percent of it (molar)
    dose_amount: ClassVar[Quantity] = (
        Q(42.02, "mg") / EnalaprilSimulationExperiment.Mr.enamal
    )

    #: the substances of the urine data by the observables of the cumulative
    #: amount and of the excretion rate
    info_urine: ClassVar[dict[str, tuple[str, str]]] = {
        "enalaprilat": ("Aurine_eat", "KI__EATEX"),
        "enalapril+enalaprilat": ("Aurine_ena_eat", "KI__ENA_EATEX"),
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1", "Fig2", "Fig3", "Tab1B"]:
            df = self.load_dataframe(fig_id)
            if fig_id == "Tab1B":
                # the recovery 0 before the dose has no SD and no information
                df = df[df["mean"] > 0]
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                if "_recovery_" in label:
                    # the cumulative urinary excretion in percent of the dose
                    dset.unit_conversion("mean", self.dose_amount)
                else:
                    # enalaprilat, and the total drug of the RIA after
                    # hydrolysis in enalaprilat equivalents
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(label)] = dset
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        for group in self.groups:
            simulations[self.to_sid(f"po_ENA40_{group}")] = Simulation(
                time_unit="hr",
                end=49,
                preinit_changes={
                    **self.default_changes(),
                    "GU__fed": Q(self.fasting_map[self.fed[group]], "dimensionless"),
                    # enalapril maleate, the assay of the tablet
                    "PODOSE_ena": self.dose * self.Mr.ena / self.Mr.enamal,
                },
            )

        return simulations

    def _metadata(self, group: str, tissue: Tissue) -> PKPDMappingMetaData:
        """Get the metadata of a mapping of a group."""
        return PKPDMappingMetaData(
            tissue=tissue,
            route=Route.PO,
            application_form=ApplicationForm.TABLET,
            dosing=Dosing.SINGLE,
            health=Health.HEALTHY,
            genotype=Genotype.NR,
            fasting=self.fastings[group],
            data=PKPDData.PK,
        )

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for group in self.groups:
            task = self.to_sid(f"task_po_ENA40_{group}")
            mappings[self.to_sid(f"fm_ENA40_{group}_enalaprilat")] = FitMapping(
                self,
                reference=FitData(
                    self,
                    dataset=self.to_sid(f"enalaprilat_{group}"),
                    xid="time",
                    yid="mean",
                    # the means of the figure have no SD
                    yid_sd=None,
                    count="count",
                ),
                observable=FitData(self, task=task, xid="time", yid="[Cve_eat]"),
                metadata=self._metadata(group, Tissue.SERUM),
            )
            # the urinary recovery 0-48 hr; the excretion rates are the same
            # urine, they are shown, not fitted
            for name, (yid, _) in self.info_urine.items():
                mappings[self.to_sid(f"fm_ENA40_{group}_urine_{name}")] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(f"{name}_urine_recovery_{group}"),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                    ),
                    observable=FitData(self, task=task, xid="time", yid=yid),
                    metadata=self._metadata(group, Tissue.URINE),
                )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig1_Fig2_Fig3",
            num_rows=3,
            num_cols=2,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        # serum enalaprilat, linear and logarithmic (Fig1)
        for kp in range(2):
            plots[kp].set_yaxis(
                self.labels["[Cve_eat]"],
                unit=self.units["[Cve_eat]"],
                scale="log" if kp == 1 else "linear",
                min=1e-3 if kp == 1 else None,
            )
        # excretion rates (Fig2, Fig3) and cumulative amounts (Table 1)
        for kcol, (yid_amount, yid_rate) in enumerate(self.info_urine.values()):
            plots[2 + kcol].set_yaxis(self.labels[yid_rate], unit=self.units[yid_rate])
            plots[2 + kcol].set_xaxis(
                self.labels["time"], unit=self.units["time"], min=0, max=24
            )
            plots[4 + kcol].set_yaxis(
                self.labels[yid_amount], unit=self.units[yid_amount]
            )

        for group in self.groups:
            task = self.to_sid(f"task_po_ENA40_{group}")
            color = self.colors[group]
            for kp in range(2):
                plots[kp].add_data(
                    task=task, xid="time", yid="[Cve_eat]", label=group, color=color
                )
                plots[kp].add_data(
                    dataset=self.to_sid(f"enalaprilat_{group}"),
                    xid="time",
                    yid="mean",
                    count="count",
                    label=group,
                    color=color,
                )
            for kcol, (name, (yid_amount, yid_rate)) in enumerate(
                self.info_urine.items()
            ):
                plots[2 + kcol].add_data(
                    task=task, xid="time", yid=yid_rate, label=group, color=color
                )
                plots[2 + kcol].add_data(
                    dataset=self.to_sid(f"{name}_urine_rate_{group}"),
                    xid="time",
                    yid="mean",
                    count="count",
                    label=f"{group} (interval mean)",
                    color=color,
                    linestyle="",
                )
                plots[4 + kcol].add_data(
                    task=task, xid="time", yid=yid_amount, label=group, color=color
                )
                plots[4 + kcol].add_data(
                    dataset=self.to_sid(f"{name}_urine_recovery_{group}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=group,
                    color=color,
                    linestyle="",
                )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Swanson1984, output_dir=Swanson1984.__name__)
