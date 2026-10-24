"""Simulation experiment of the study Dickstein1987a."""

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
from sbmlsim.plot import Axis, Figure
from sbmlsim.simulation import Simulation
from sbmlsim.units import Quantity

from pkdb_models.models.enalapril import MODEL
from pkdb_models.models.enalapril.experiments.base_experiment import (
    EnalaprilSimulationExperiment,
)
from pkdb_models.models.enalapril.experiments.studies.dickstein1987 import (
    F_CARDIAC_CHF,
)


class Dickstein1987a(EnalaprilSimulationExperiment):
    """Simulation experiment of Dickstein1987a.

    The pharmacodynamics of the 12 patients with chronic heart failure of
    Dickstein1987 (on digitalis and diuretics, NYHA II-IV), the same three
    treatments in the fasting state: 10 mg enalapril maleate p.o. (`ENAPO10`),
    5 mg enalapril maleate i.v. (`ENAIV5`) and 5 mg enalaprilat i.v.
    (`EATIV5`). The change of the intra-arterial mean arterial pressure from
    its baseline every 15 min for 6 h (Tab1, mean and SD; 11 patients of the
    enalaprilat arm from 45 min on). The lisinopril study of the paper is not
    simulated.

    The patients have the cardiac function of Dickstein1987 (`F_CARDIAC_CHF`).
    The blood pressure of the model changes relative to its reference: every
    arm starts at its baseline mean arterial pressure (90, 85 and 87 mmHg), as a
    systolic and diastolic pressure with an assumed pulse pressure of 40 mmHg
    (not reported). The renin-angiotensin system of heart failure on diuretics
    is activated, which the model does not describe: the data is a validation
    of a limitation of the model.
    """

    doses: ClassVar[list[str]] = ["ENAPO10", "ENAIV5", "EATIV5"]
    # CHF = reds; route/analyte variants as shades
    colors: ClassVar[dict[str, str]] = {
        "ENAPO10": EnalaprilSimulationExperiment.cardiac_ramp[2],
        "ENAIV5": EnalaprilSimulationExperiment.cardiac_ramp[1],
        "EATIV5": EnalaprilSimulationExperiment.cardiac_ramp[0],
    }
    labels_dose: ClassVar[dict[str, str]] = {
        "ENAPO10": "10 mg EM p.o.",
        "ENAIV5": "5 mg EM i.v.",
        "EATIV5": "5 mg ET i.v.",
    }
    #: the mean arterial pressure before the dose [mmHg] (Tab1)
    map_baseline: ClassVar[dict[str, float]] = {
        "ENAPO10": 90,
        "ENAIV5": 85,
        "EATIV5": 87,
    }
    #: the assumed pulse pressure [mmHg]
    pulse_pressure: ClassVar[float] = 40

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Tab1"]:
            df = self.load_dataframe(fig_id)
            # the baseline before the dose is digitized at -0.01 hr, it is the
            # value at the dose
            df.loc[df["time"] < 0, "time"] = 0.0
            for label, df_label in df.groupby("label"):
                dsets[self.to_sid(str(label))] = DataSet.from_df(df_label, self.ureg)

        return dsets

    def _dose(self, dose: str) -> dict[str, Quantity]:
        """Get the dose of an intervention."""
        if dose == "ENAPO10":
            # enalapril maleate
            return {"PODOSE_ena": Q(10, "mg") * self.Mr.ena / self.Mr.enamal}
        if dose == "ENAIV5":
            # enalapril maleate
            return {"IVDOSE_ena": Q(5, "mg") * self.Mr.ena / self.Mr.enamal}
        return {"IVDOSE_eat": Q(5, "mg")}

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        for dose in self.doses:
            dbp = self.map_baseline[dose] - self.pulse_pressure / 3
            simulations[f"{dose}_CHF"] = Simulation(
                time_unit="hr",
                end=7,
                preinit_changes={
                    **self.default_changes(),
                    **self.interaction_changes(Coadministration.COMEDICATION),
                    "f_cardiac_function": Q(F_CARDIAC_CHF, "dimensionless"),
                    "SBP_ref": Q(dbp + self.pulse_pressure, "mmHg"),
                    "DBP_ref": Q(dbp, "mmHg"),
                    **self._dose(dose),
                },
            )

        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for dose in self.doses:
            mappings[self.to_sid(f"fm_dickstein1987a_{dose}_CHF_MAP_change")] = (
                FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(f"{dose}_MAP (change absolute)"),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                    ),
                    observable=FitData(
                        self, task=f"task_{dose}_CHF", xid="time", yid="MAP_change"
                    ),
                    metadata=PKPDMappingMetaData(
                        tissue=Tissue.NONE,
                        route=Route.PO if dose == "ENAPO10" else Route.IV,
                        application_form=ApplicationForm.NR
                        if dose == "ENAPO10"
                        else ApplicationForm.SOLUTION,
                        dosing=Dosing.SINGLE,
                        health=Health.HEART_FAILURE,
                        genotype=Genotype.NR,
                        fasting=Fasting.FASTED,
                        coadministration=Coadministration.COMEDICATION,
                        data=PKPDData.PD,
                        data_type=DataType.MEAN,
                    ),
                )
            )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Tab1",
            num_rows=1,
            num_cols=len(self.doses),
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]),
            yaxis=Axis(self.labels["MAP_change"], unit=self.units["MAP_change"]),
            legend=True,
        )
        for kp, dose in enumerate(self.doses):
            plots[kp].set_title(self.labels_dose[dose])
            plots[kp].add_data(
                task=f"task_{dose}_CHF",
                xid="time",
                yid="MAP_change",
                label=self.labels_dose[dose],
                color=self.colors[dose],
            )
            plots[kp].add_data(
                dataset=self.to_sid(f"{dose}_MAP (change absolute)"),
                xid="time",
                yid="mean",
                yid_sd="mean_sd",
                count="count",
                label=self.labels_dose[dose],
                color=self.colors[dose],
            )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Dickstein1987a, output_dir=Dickstein1987a.__name__)
