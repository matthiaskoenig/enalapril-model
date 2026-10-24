"""Simulation experiment of the study Tarkiainen2015."""

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

from pkdb_models.models.enalapril import MODEL
from pkdb_models.models.enalapril.experiments.base_experiment import (
    EnalaprilSimulationExperiment,
)


class Tarkiainen2015(EnalaprilSimulationExperiment):
    """Simulation experiment of Tarkiainen2015 in carriers of the CES1 variant G143E.

    22 healthy Finnish subjects, CES1 c.428G/G (control, n=12) and c.428G/A
    (G143E heterozygous, n=10), a single dose of 10 mg enalapril maleate after
    an overnight fast. The concentrations (Fig. 2) and the amounts excreted in
    the urine 0-12 hr (Table 1) are geometric means adjusted to a BW of 70 kg,
    so both groups are simulated with 70 kg. The blood pressure of Table 2 is
    the baseline and the average over 0-12 hr (not a time course), it sets the
    reference of the blood pressure and is not mapped.
    """

    groups: ClassVar[list[str]] = ["control", "G143E"]

    SBP_refs: ClassVar[dict[str, float]] = {
        "control": 120.0,
        "G143E": 124.0,
    }
    DBP_refs: ClassVar[dict[str, float]] = {
        "control": 73.0,
        "G143E": 78.0,
    }
    #: the data are adjusted to 70 kg
    bodyweight: ClassVar[float] = 70.0
    heights: ClassVar[dict[str, float]] = {
        "control": 174.00,
        "G143E": 177.00,
    }
    genotypes: ClassVar[dict[str, Genotype]] = {
        "control": Genotype.CES1_WILD_TYPE,
        "G143E": Genotype.CES1_LOSS_OF_FUNCTION,
    }
    #: the substances of the plasma and urine data by observable
    info: ClassVar[dict[str, tuple[str, str]]] = {
        "enalapril": ("[Cve_ena]", "Aurine_ena"),
        "enalaprilat": ("[Cve_eat]", "Aurine_eat"),
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig2", "Tab1"]:
            df = self.load_dataframe(fig_id)
            # the predose zeros carry no information and have no dispersion
            df = df[df["mean"] > 0]
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
        simulations = {}
        for group in self.groups:
            simulations[self.to_sid(f"po_ENA10{group}")] = Simulation(
                time_unit="hr",
                end=50,
                preinit_changes={
                    **self.default_changes(),
                    "BW": Q(self.bodyweight, "kg"),
                    "HEIGHT": Q(self.heights[group], "cm"),
                    "SBP_ref": Q(self.SBP_refs[group], "mmHg"),
                    "DBP_ref": Q(self.DBP_refs[group], "mmHg"),
                    # CES1 activity
                    "LI__f_ces1": Q(self.ces1_map[group], "dimensionless"),
                    # enalapril maleate
                    "PODOSE_ena": Q(10, "mg") * self.Mr.ena / self.Mr.enamal,
                },
            )
        return simulations

    def _metadata(self, group: str, tissue: Tissue) -> PKPDMappingMetaData:
        """Get the metadata of a mapping of a group."""
        return PKPDMappingMetaData(
            tissue=tissue,
            route=Route.PO,
            application_form=ApplicationForm.NR,
            dosing=Dosing.SINGLE,
            health=Health.HEALTHY,
            genotype=self.genotypes[group],
            fasting=Fasting.FASTED,
            data=PKPDData.PK,
        )

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for group in self.groups:
            task = self.to_sid(f"task_po_ENA10{group}")
            for name, (sid, sid_urine) in self.info.items():
                mappings[self.to_sid(f"fm_ENA10_{name}_{group}")] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(f"{group}_ENA10_{name}"),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                    ),
                    observable=FitData(self, task=task, xid="time", yid=sid),
                    metadata=self._metadata(group, Tissue.PLASMA),
                )
                # the amount excreted 0-12 hr (Table 1)
                mappings[self.to_sid(f"fm_ENA10_urine_{name}_{group}")] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(f"{group}_ENA10_urine_{name}"),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                    ),
                    observable=FitData(self, task=task, xid="time", yid=sid_urine),
                    metadata=self._metadata(group, Tissue.URINE),
                )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig2_Tab1",
            num_rows=2,
            num_cols=3,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        # rows: enalapril, enalaprilat; columns: linear, log (insets), urine
        for krow, (sid, sid_urine) in enumerate(self.info.values()):
            plots[3 * krow].set_yaxis(self.labels[sid], unit=self.units[sid])
            plots[3 * krow + 1].set_yaxis(
                self.labels[sid], unit=self.units[sid], scale="log", min=1e-3
            )
            plots[3 * krow + 2].set_yaxis(
                self.labels[sid_urine], unit=self.units[sid_urine]
            )
        # enalapril 0-12 hr, the urine 0-12 hr
        for kp in [0, 1, 2, 5]:
            plots[kp].set_xaxis(
                self.labels["time"], unit=self.units["time"], min=0, max=12.5
            )

        for group in self.groups:
            task = self.to_sid(f"task_po_ENA10{group}")
            color = self.ces1_colors[group]
            for krow, (name, (sid, sid_urine)) in enumerate(self.info.items()):
                for kcol in range(2):
                    plots[3 * krow + kcol].add_data(
                        task=task, xid="time", yid=sid, label=group, color=color
                    )
                    plots[3 * krow + kcol].add_data(
                        dataset=self.to_sid(f"{group}_ENA10_{name}"),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                        label=f"{group} (geometric mean)",
                        color=color,
                    )
                plots[3 * krow + 2].add_data(
                    task=task, xid="time", yid=sid_urine, label=group, color=color
                )
                plots[3 * krow + 2].add_data(
                    dataset=self.to_sid(f"{group}_ENA10_urine_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=f"{group} (geometric mean)",
                    color=color,
                    linestyle="",
                )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Tarkiainen2015, output_dir=Tarkiainen2015.__name__)
