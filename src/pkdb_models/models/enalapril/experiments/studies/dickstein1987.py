"""Simulation experiment of the study Dickstein1987."""

from typing import ClassVar, override

from pkpdsim.impairment import CARDIAC
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

#: the cardiac function of the 12 patients with chronic heart failure of
#: Dickstein1987 and Dickstein1987a, the mean of the classes of their NYHA
#: classes (3 NYHA II as mild, 6 NYHA III as moderate, 3 NYHA IV as severe
#: cardiac impairment): 0.70. Their creatinine clearance is not reported.
F_CARDIAC_CHF: float = (
    3 * CARDIAC["Mild cardiac impairment"]
    + 6 * CARDIAC["Moderate cardiac impairment"]
    + 3 * CARDIAC["Severe cardiac impairment"]
) / 12


class Dickstein1987(EnalaprilSimulationExperiment):
    """Simulation experiment of Dickstein1987.

    Twelve hospitalized men with chronic heart failure (66 years, NYHA II-IV, on
    digitalis and diuretics) took 10 mg enalapril maleate p.o. (`ENAPO10`),
    5 mg enalapril maleate i.v. (`ENAIV5`) and 5 mg enalaprilat i.v.
    (`EATIV5`), boluses, in a crossover with 72 h of washout, in the fasting
    state at 08:00 (food withheld for 2 h). Arterial serum enalaprilat by RIA,
    enalapril as the difference of the RIA before and after hydrolysis (Fig1,
    Fig4, Fig5, means), and the urinary recovery of enalaprilat and of the total
    drug (enalapril plus enalaprilat) to 72 h in percent of the dose as
    enalaprilat equivalents (Tab1, n = 10, 11 and 10, incomplete collections
    excluded). The normal subjects (n = 10, Fig3-5) are an unpublished study of
    MSD (age, sex and food not reported).

    The urinary amounts are the recovery times the molar dose (the curated
    amounts in mg were the percent of the mass of the maleate). The patients
    have the cardiac function of their NYHA classes (`F_CARDIAC_CHF`); their
    background therapy is a comedication without an interaction with
    enalapril. The higher enalaprilat of the patients (1.5 to 2 times the
    normal subjects) is attributed by the authors to the age and the heart
    failure; their GFR is not reported.
    """

    groups: ClassVar[list[str]] = ["normal", "CHF"]
    doses: ClassVar[list[str]] = ["ENAPO10", "ENAIV5", "EATIV5"]
    # healthy = greys, CHF = reds; route/analyte variants as shades
    colors: ClassVar[dict[str, str]] = {
        "ENAPO10_normal": EnalaprilSimulationExperiment.grey_shades[0],
        "ENAPO10_CHF": EnalaprilSimulationExperiment.cardiac_ramp[2],
        "ENAIV5_normal": EnalaprilSimulationExperiment.grey_shades[1],
        "ENAIV5_CHF": EnalaprilSimulationExperiment.cardiac_ramp[1],
        "EATIV5_normal": EnalaprilSimulationExperiment.grey_shades[2],
        "EATIV5_CHF": EnalaprilSimulationExperiment.cardiac_ramp[0],
    }
    labels_dose: ClassVar[dict[str, str]] = {
        "ENAPO10": "10 mg EM p.o.",
        "ENAIV5": "5 mg EM i.v.",
        "EATIV5": "5 mg ET i.v.",
    }
    cardiac_function: ClassVar[dict[str, float]] = {
        "normal": 1.0,
        "CHF": F_CARDIAC_CHF,
    }
    #: the serum data: substance, observable, doses with data of the normal
    #: subjects and of the patients
    serum: ClassVar[dict[str, tuple[str, list[str]]]] = {
        "enalapril": ("[Cve_ena]", ["ENAPO10"]),
        "enalaprilat": ("[Cve_eat]", ["ENAPO10", "ENAIV5", "EATIV5"]),
    }
    #: the urine data of the patients: substance, observable, doses
    urine: ClassVar[dict[str, tuple[str, list[str]]]] = {
        "enalaprilat": ("Aurine_eat", ["ENAPO10", "ENAIV5", "EATIV5"]),
        "enalapril+enalaprilat": ("Aurine_ena_eat", ["ENAPO10", "ENAIV5"]),
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1", "Fig3", "Fig4", "Fig5", "Tab1_Mean"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                if "_recovery_" in label:
                    continue
                dset = DataSet.from_df(df_label, self.ureg)
                if label.endswith("_enalapril"):
                    dset.unit_conversion("mean", 1 / self.Mr.ena)
                elif label.endswith("enalaprilat"):
                    # the total drug of the urine in enalaprilat equivalents
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(label)] = dset
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
        for group in self.groups:
            for dose in self.doses:
                simulations[self.to_sid(f"{dose}_{group}")] = Simulation(
                    time_unit="hr",
                    end=74,
                    preinit_changes={
                        **self.default_changes(),
                        **self.interaction_changes(
                            Coadministration.COMEDICATION
                            if group == "CHF"
                            else Coadministration.NONE
                        ),
                        "f_cardiac_function": Q(
                            self.cardiac_function[group], "dimensionless"
                        ),
                        **self._dose(dose),
                    },
                )
        return simulations

    def _metadata(self, dose: str, group: str, tissue: Tissue) -> PKPDMappingMetaData:
        """Get the metadata of a mapping of a dose and group."""
        chf = group == "CHF"
        return PKPDMappingMetaData(
            tissue=tissue,
            route=Route.PO if dose == "ENAPO10" else Route.IV,
            application_form=ApplicationForm.NR
            if dose == "ENAPO10"
            else ApplicationForm.SOLUTION,
            dosing=Dosing.SINGLE,
            health=Health.HEART_FAILURE if chf else Health.HEALTHY,
            genotype=Genotype.NR,
            fasting=Fasting.FASTED if chf else Fasting.NR,
            # digitalis and diuretics (some warfarin, mexiletine, amiodarone)
            coadministration=Coadministration.COMEDICATION
            if chf
            else Coadministration.NONE,
            data=PKPDData.PK,
            data_type=DataType.MEAN,
        )

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for name, (sid, doses) in self.serum.items():
            for dose in doses:
                for group in self.groups:
                    key = self.to_sid(f"fm_dickstein1987_{dose}_{group}_{name}")
                    mappings[key] = FitMapping(
                        self,
                        reference=FitData(
                            self,
                            dataset=self.to_sid(f"{dose}_{group}_{name}"),
                            xid="time",
                            yid="mean",
                            yid_sd=None,
                            count="count",
                        ),
                        observable=FitData(
                            self,
                            task=self.to_sid(f"task_{dose}_{group}"),
                            xid="time",
                            yid=sid,
                        ),
                        metadata=self._metadata(dose, group, Tissue.SERUM),
                    )
        for name, (sid, doses) in self.urine.items():
            for dose in doses:
                key = self.to_sid(f"fm_dickstein1987_{dose}_CHF_urine_{name}")
                mappings[key] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(f"{dose}_CHF_cumulative amount_{name}"),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                    ),
                    observable=FitData(
                        self,
                        task=self.to_sid(f"task_{dose}_CHF"),
                        xid="time",
                        yid=sid,
                    ),
                    metadata=self._metadata(dose, "CHF", Tissue.URINE),
                )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig1_Fig3_Fig4_Fig5_Tab1",
            num_rows=3,
            num_cols=2,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        # the serum of the normal subjects (first row) and of the patients
        # (second row), the urine of the patients (third row)
        panels: list[tuple[str, str, str, dict[str, tuple[str, list[str]]]]] = [
            ("normal", "[Cve_ena]", "enalapril", self.serum),
            ("normal", "[Cve_eat]", "enalaprilat", self.serum),
            ("CHF", "[Cve_ena]", "enalapril", self.serum),
            ("CHF", "[Cve_eat]", "enalaprilat", self.serum),
            ("CHF", "Aurine_eat", "enalaprilat", self.urine),
            ("CHF", "Aurine_ena_eat", "enalapril+enalaprilat", self.urine),
        ]
        for kp, (group, sid, name, info) in enumerate(panels):
            urine = info is self.urine
            plots[kp].set_title("normal subjects" if group == "normal" else "CHF")
            if sid == "[Cve_eat]":
                # the i.v. bolus of enalaprilat and the oral doses on one axis
                plots[kp].set_yaxis(
                    self.labels[sid], unit=self.units[sid], scale="log", min=1e-3
                )
            else:
                plots[kp].set_yaxis(self.labels[sid], unit=self.units[sid])
            for dose in info[name][1]:
                key = f"{dose}_{group}"
                label = self.labels_dose[dose]
                plots[kp].add_data(
                    task=self.to_sid(f"task_{key}"),
                    xid="time",
                    yid=sid,
                    label=label,
                    color=self.colors[key],
                )
                plots[kp].add_data(
                    dataset=self.to_sid(
                        f"{key}_cumulative amount_{name}" if urine else f"{key}_{name}"
                    ),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd" if urine else None,
                    count="count",
                    label=label,
                    color=self.colors[key],
                )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Dickstein1987, output_dir=Dickstein1987.__name__)
