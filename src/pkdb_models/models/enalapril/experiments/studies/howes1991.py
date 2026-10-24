"""Simulation experiment of the study Howes1991."""

from typing import ClassVar, override

from pkpdsim.metadata import (
    ApplicationForm,
    Coadministration,
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
from sbmlsim.plot import Axis, Figure, Plot
from sbmlsim.simulation import Simulation

from pkdb_models.models.enalapril import MODEL
from pkdb_models.models.enalapril.experiments.base_experiment import (
    EnalaprilSimulationExperiment,
)


class Howes1991(EnalaprilSimulationExperiment):
    """Simulation experiment of Howes1991.

    12 healthy normotensive volunteers (21-26 yr, BW not reported), a latin
    square crossover of four single oral doses after an overnight fast:
    enalapril 10 mg alone, hydrochlorothiazide (HCTZ) 25 mg alone, both as
    separate tablets (`multi`) and both in one combination tablet (`combi`).
    The enalapril is the tablet of MSD, i.e. enalapril maleate: the 2.9 mg
    enalaprilat in the urine (96 hr) are 41 % of 10 mg of the maleate, the
    recovery of the other studies. Plasma enalaprilat (RIA, Fig1), the urinary
    enalaprilat over 96 hr (Tab1) and the maximal fall of the supine and the
    standing blood pressure at 2-6 hr (Tab3, mapped at 4 hr, the supine
    values only: the model has no posture and the standing values are the
    same subjects).

    HCTZ changes the pharmacokinetics of enalaprilat not significantly (AUC
    and Cmax 12-20 % lower, p=0.053, the urinary recovery unchanged), so the
    arms with HCTZ are simulated with the factors of the interaction of the
    base experiment (none). The model has no effect of HCTZ on the blood
    pressure.
    """

    #: the arms with enalapril: the intervention of the data, the simulation
    arms: ClassVar[dict[str, tuple[str, str]]] = {
        "ENA10": ("ENA10", "po_ENA10"),
        "multi": ("ENA10, HCTZ25_multi", "po_ENA10_HCTZ25"),
        "combi": ("ENA10, HCTZ25_combi", "po_ENA10_HCTZ25"),
    }
    arm_labels: ClassVar[dict[str, str]] = {
        "ENA10": "enalapril",
        "multi": "enalapril + HCTZ (separate tablets)",
        "combi": "enalapril + HCTZ (combination tablet)",
    }
    colors: ClassVar[dict[str, str]] = {
        "ENA10": EnalaprilSimulationExperiment.healthy_color,
        "multi": EnalaprilSimulationExperiment.formulation_ramp[0],
        "combi": EnalaprilSimulationExperiment.formulation_ramp[2],
    }
    markers: ClassVar[dict[str, str]] = {"ENA10": "o", "multi": "s", "combi": "D"}
    #: the blood pressure changes of Tab3 by the observable
    bp_changes: ClassVar[dict[str, str]] = {
        "SBP_change": "blood pressure systolic (change)",
        "DBP_change": "blood pressure diastolic (change)",
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1", "Tab1", "Tab3"]:
            df = self.load_dataframe(fig_id)
            # the parameters of Tab1 have no label; HCTZ (alone) is not in the model
            df = df[df["label"].notna() & df["intervention"].str.startswith("ENA10")]
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                if label.endswith("_enalaprilat"):
                    # plasma ng/ml and urine mg of enalaprilat
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(label)] = dset
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        for sim_id, coadministration in [
            ("po_ENA10", Coadministration.NONE),
            ("po_ENA10_HCTZ25", Coadministration.HCTZ),
        ]:
            simulations[sim_id] = Simulation(
                time_unit="hr",
                end=96,
                preinit_changes={
                    **self.default_changes(),
                    **self.interaction_changes(coadministration),
                    # enalapril maleate
                    "PODOSE_ena": Q(10, "mg") * self.Mr.ena / self.Mr.enamal,
                },
            )
        return simulations

    def _metadata(
        self, arm: str, tissue: Tissue, data: PKPDData
    ) -> PKPDMappingMetaData:
        """Metadata of the mappings of an arm."""
        return PKPDMappingMetaData(
            tissue=tissue,
            route=Route.PO,
            application_form=ApplicationForm.TABLET,
            dosing=Dosing.SINGLE,
            health=Health.HEALTHY,
            genotype=Genotype.NR,
            fasting=Fasting.FASTED,
            coadministration=Coadministration.NONE
            if arm == "ENA10"
            else Coadministration.HCTZ,
            data=data,
            data_type=DataType.MEAN,
        )

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for arm, (intervention, sim_id) in self.arms.items():
            prefix = "fm_howes1991_po_ENA10"
            if arm != "ENA10":
                prefix = f"{prefix}_HCTZ25_{arm}"
            # plasma and urine enalaprilat
            for dataset, yid, tissue, key in [
                (
                    f"{intervention}_enalaprilat",
                    "[Cve_eat]",
                    Tissue.PLASMA,
                    "enalaprilat",
                ),
                (
                    f"{intervention}_cumulative amount_enalaprilat",
                    "Aurine_eat",
                    Tissue.URINE,
                    "enalaprilat_urine",
                ),
            ]:
                mappings[self.to_sid(f"{prefix}_{key}")] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(dataset),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd" if tissue == Tissue.URINE else None,
                        count="count",
                    ),
                    observable=FitData(
                        self, task=f"task_{sim_id}", xid="time", yid=yid
                    ),
                    metadata=self._metadata(arm, tissue, PKPDData.PK),
                )
            # the maximal fall of the supine blood pressure
            for yid, name in self.bp_changes.items():
                mappings[self.to_sid(f"{prefix}_{yid}_supine")] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(f"{intervention}_supine_{name}"),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                    ),
                    observable=FitData(
                        self, task=f"task_{sim_id}", xid="time", yid=yid
                    ),
                    metadata=self._metadata(arm, Tissue.NONE, PKPDData.PD),
                )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        return {**self._figure_pk(), **self._figure_pd()}

    def _add_simulations(self, plots: list[Plot], yids: list[str]) -> None:
        """Add the simulations of the arms (the arms with HCTZ share one)."""
        # dashed: the simulation with HCTZ is the one without (no interaction)
        for sim_id, arm, label, linestyle in [
            ("po_ENA10", "ENA10", "enalapril", "-"),
            ("po_ENA10_HCTZ25", "combi", "enalapril + HCTZ", "--"),
        ]:
            for k, yid in enumerate(yids):
                plots[k].add_data(
                    task=f"task_{sim_id}",
                    xid="time",
                    yid=yid,
                    label=label,
                    color=self.colors[arm],
                    linestyle=linestyle,
                )

    def _figure_pk(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig1",
            num_rows=1,
            num_cols=2,
            name=f"{self.__class__.__name__}",
            # one legend right of the panels, it covers the data otherwise
            settings={"legend_scope": "row"},
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(self.labels["[Cve_eat]"], unit=self.units["[Cve_eat]"])
        plots[1].set_yaxis(self.labels["Aurine_eat"], unit=self.units["Aurine_eat"])
        plots[0].set_xaxis(self.labels["time"], unit=self.units["time"], min=0, max=25)

        self._add_simulations(plots, ["[Cve_eat]", "Aurine_eat"])
        for arm, (intervention, _) in self.arms.items():
            for k, (dataset, yid_sd) in enumerate(
                [
                    (f"{intervention}_enalaprilat", None),
                    (f"{intervention}_cumulative amount_enalaprilat", "mean_sd"),
                ]
            ):
                plots[k].add_data(
                    dataset=self.to_sid(dataset),
                    xid="time",
                    yid="mean",
                    yid_sd=yid_sd,
                    count="count",
                    label=self.arm_labels[arm],
                    color=self.colors[arm],
                    marker=self.markers[arm],
                )
        return self.figures_by_sid(fig)

    def _figure_pd(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Tab3",
            num_rows=1,
            num_cols=2,
            name=f"{self.__class__.__name__}",
            # one legend right of the panels, it covers the data otherwise
            settings={"legend_scope": "row"},
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        for kp, yid in enumerate(self.bp_changes):
            plots[kp].set_yaxis(self.labels[yid], unit=self.units[yid])
            plots[kp].set_xaxis(
                self.labels["time"], unit=self.units["time"], min=0, max=25
            )

        self._add_simulations(plots, list(self.bp_changes))
        # data: the maximal fall of the supine blood pressure at 2-6 hr
        for arm, (intervention, _) in self.arms.items():
            for kp, name in enumerate(self.bp_changes.values()):
                plots[kp].add_data(
                    dataset=self.to_sid(f"{intervention}_supine_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=f"{self.arm_labels[arm]} (supine)",
                    color=self.colors[arm],
                    marker=self.markers[arm],
                )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Howes1991, output_dir=Howes1991.__name__)
