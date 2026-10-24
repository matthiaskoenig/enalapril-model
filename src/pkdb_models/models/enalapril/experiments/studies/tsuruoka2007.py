"""Simulation experiment of the study Tsuruoka2007."""

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
from sbmlsim.simulation import Change, Simulation

from pkdb_models.models.enalapril import MODEL
from pkdb_models.models.enalapril.experiments.base_experiment import (
    EnalaprilSimulationExperiment,
)

#: the start of the dialysis in the time of the data [hr]
DIALYSIS_START = 1344.0


class Tsuruoka2007(EnalaprilSimulationExperiment):
    """Simulation experiment of Tsuruoka2007.

    6 hypertensive patients on chronic hemodialysis (4 hr, 3 times a week),
    enalapril maleate 2.5 mg once daily (Renivace tablets) for at least 8 weeks,
    the last dose 2 hr before the dialysis session (fasting not reported).
    Enalaprilat in plasma by HPLC from the arterial line (before the dialyzer,
    0-4 hr) and the venous line (after the dialyzer, 1-3 hr) during the
    dialysis, the blood pressure before and during the dialysis (Tab3), mean ±
    SE. The patients are anuric (end stage renal disease); the model has no
    dialysis, the data are validation data of the limits of the model.
    """

    #: the start of the dialysis in the time of the data [hr]
    dialysis_start: ClassVar[float] = DIALYSIS_START
    #: 56 daily doses, the last one 2 hr before the dialysis [hr]
    dose_times: ClassVar[list[float]] = [
        DIALYSIS_START - 2 - 24 * k for k in range(55, -1, -1)
    ]

    #: the side of the dialyzer of the plasma samples by the tissue of the data
    sides: ClassVar[dict[str, str]] = {
        "arterial blood": "arterial line (before dialyzer)",
        "plasma": "venous line (after dialyzer)",
    }
    colors: ClassVar[dict[str, str]] = {
        "arterial blood": EnalaprilSimulationExperiment.renal_ramp[4],
        "plasma": EnalaprilSimulationExperiment.renal_ramp[1],
    }
    markers: ClassVar[dict[str, str]] = {"arterial blood": "o", "plasma": "s"}

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1", "Tab3"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                if label.startswith("enalaprilat_"):
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(label)] = dset
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        dose = Q(2.5, "mg") * self.Mr.ena / self.Mr.enamal  # enalapril maleate
        return {
            "po_enamal2p5": Simulation(
                time_unit="hr",
                end=self.dialysis_start + 6,
                preinit_changes={
                    **self.default_changes(),
                    # anuric patients on hemodialysis, the residual GFR is not
                    # reported: end stage renal disease
                    "KI__f_renal_function": Q(
                        self.renal_map["End stage renal disease"], "dimensionless"
                    ),
                    # the blood pressure on treatment (Tab1), the untreated
                    # baseline is not reported
                    "SBP_ref": Q(152, "mmHg"),
                    "DBP_ref": Q(73, "mmHg"),
                },
                changes=[
                    # the first dose sets the empty dose state, the later ones
                    # add to it
                    Change(self.dose_times[:1], {"PODOSE_ena": dose}),
                    self.add_doses(self.dose_times[1:], {"PODOSE_ena": dose}),
                ],
            )
        }

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        # the enalaprilat in the plasma of both lines of the dialyzer; the
        # plasma after the dialyzer is not the systemic plasma
        for tissue in self.sides:
            key = self.to_sid(f"fm_tsuruoka2007_enamal2.5_{tissue}_enalaprilat")
            mappings[key] = FitMapping(
                self,
                reference=FitData(
                    self,
                    dataset=self.to_sid(f"enalaprilat_{tissue}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                ),
                observable=FitData(
                    self, task="task_po_enamal2p5", xid="time", yid="[Cve_eat]"
                ),
                metadata=self._metadata(Tissue.PLASMA, PKPDData.PK),
            )
        for sid, name in {
            "SBP": "blood pressure systolic",
            "DBP": "blood pressure diastolic",
        }.items():
            mappings[self.to_sid(f"fm_tsuruoka2007_enamal2.5_{name}")] = FitMapping(
                self,
                reference=FitData(
                    self,
                    dataset=self.to_sid(f"ENA2.5_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                ),
                observable=FitData(self, task="task_po_enamal2p5", xid="time", yid=sid),
                metadata=self._metadata(Tissue.NONE, PKPDData.PD),
            )
        return mappings

    @staticmethod
    def _metadata(tissue: Tissue, data: PKPDData) -> PKPDMappingMetaData:
        """Get the metadata of a mapping of the study."""
        return PKPDMappingMetaData(
            tissue=tissue,
            route=Route.PO,
            application_form=ApplicationForm.TABLET,
            dosing=Dosing.MULTIPLE,
            health=Health.RENAL_IMPAIRMENT,
            genotype=Genotype.NR,
            fasting=Fasting.NR,
            data=data,
            data_type=DataType.MEAN,
        )

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig1",
            num_rows=1,
            num_cols=3,
            name=f"{self.__class__.__name__}",
        )
        # the last dose and the dialysis session
        plots = fig.create_plots(
            xaxis=Axis(
                self.labels["time"],
                unit=self.units["time"],
                min=self.dose_times[-1] - 2,
                max=self.dialysis_start + 6,
            ),
            legend=True,
        )
        plots[0].set_yaxis(self.labels["[Cve_eat]"], unit=self.units["[Cve_eat]"])
        plots[1].set_yaxis(self.labels["SBP"], unit=self.units["SBP"])
        plots[2].set_yaxis(self.labels["DBP"], unit=self.units["DBP"])

        for kp, sid in enumerate(["[Cve_eat]", "SBP", "DBP"]):
            plots[kp].add_data(
                task="task_po_enamal2p5",
                xid="time",
                yid=sid,
                label="ENA 2.5 mg/day (ESRD, no dialysis)",
                color=self.colors["arterial blood"],
            )
        for tissue, side in self.sides.items():
            plots[0].add_data(
                dataset=self.to_sid(f"enalaprilat_{tissue}"),
                xid="time",
                yid="mean",
                yid_sd="mean_sd",
                count="count",
                label=side,
                color=self.colors[tissue],
                marker=self.markers[tissue],
            )
        for kp, name in [
            (1, "blood pressure systolic"),
            (2, "blood pressure diastolic"),
        ]:
            plots[kp].add_data(
                dataset=self.to_sid(f"ENA2.5_{name}"),
                xid="time",
                yid="mean",
                yid_sd="mean_sd",
                count="count",
                label="ENA 2.5 mg/day",
                color=self.colors["arterial blood"],
            )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Tsuruoka2007, output_dir=Tsuruoka2007.__name__)
