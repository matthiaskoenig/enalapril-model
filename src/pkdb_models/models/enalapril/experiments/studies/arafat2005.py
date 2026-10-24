"""Simulation experiment of the study Arafat2005."""

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


class Arafat2005(EnalaprilSimulationExperiment):
    """Simulation experiment of Arafat2005.

    Bioequivalence study in 24 healthy normotensive men (18-43 years,
    76.7 kg): a single oral dose of a 10 mg enalapril maleate tablet of a test
    formulation (`ENA10`, Enalapril) and of the reference (`REN10`, Renitec) in
    a crossover with a week of washout, after a fast of 10 h (a light breakfast
    4 h after the dose). Plasma enalapril (Fig1) and enalaprilat (Fig2) by
    enzyme immunoassays and the systolic and diastolic blood pressure (Fig3) to
    24 h, mean and SE of 24.

    The enzyme immunoassays are those of Matalka2002: the enalapril (Cmax
    310 ng/ml after 10 mg, by the authors "10 times" the literature) and the
    enalaprilat (55-57 ng/ml after 10 mg, the Cmax of 20 mg by LC-MS/MS) are
    not usable (outliers). The blood pressure of the normotensive subjects is
    data of the pharmacodynamics; every arm starts at its own baseline
    (`SBP_ref`, `DBP_ref`). Both arms are the same subjects: the reference arm
    is fitted, the test arm is an aggregate of the same subjects.
    """

    interventions: ClassVar[list[str]] = ["REN10", "ENA10"]
    #: the formulations, magenta (light = test, dark = reference)
    colors: ClassVar[dict[str, str]] = {
        "ENA10": EnalaprilSimulationExperiment.formulation_ramp[0],
        "REN10": EnalaprilSimulationExperiment.formulation_ramp[2],
    }
    labels_intervention: ClassVar[dict[str, str]] = {
        "ENA10": "10 mg test",
        "REN10": "10 mg reference",
    }
    #: the systolic and diastolic blood pressure before the dose [mmHg] (Fig3)
    baselines: ClassVar[dict[str, tuple[float, float]]] = {
        "ENA10": (118.80, 80.95),
        "REN10": (117.15, 80.11),
    }
    #: the observable by the label of the data
    info: ClassVar[dict[str, str]] = {
        "enalapril": "[Cve_ena]",
        "enalaprilat": "[Cve_eat]",
        "blood pressure systolic": "SBP",
        "blood pressure diastolic": "DBP",
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1", "Fig2", "Fig3"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
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
        for intervention in self.interventions:
            sbp, dbp = self.baselines[intervention]
            simulations[intervention] = Simulation(
                time_unit="hr",
                end=25,
                preinit_changes={
                    **self.default_changes(),
                    "BW": Q(76.7, "kg"),
                    "SBP_ref": Q(sbp, "mmHg"),
                    "DBP_ref": Q(dbp, "mmHg"),
                    # enalapril maleate
                    "PODOSE_ena": Q(10, "mg") * self.Mr.ena / self.Mr.enamal,
                },
            )
        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for name, sid in self.info.items():
            pk = sid in {"[Cve_ena]", "[Cve_eat]"}
            for intervention in self.interventions:
                key = self.to_sid(f"fm_arafat2005_{name}_{intervention}")
                mappings[key] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(f"{name}_{intervention}"),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                    ),
                    observable=FitData(
                        self, task=f"task_{intervention}", xid="time", yid=sid
                    ),
                    metadata=PKPDMappingMetaData(
                        tissue=Tissue.PLASMA if pk else Tissue.NONE,
                        route=Route.PO,
                        application_form=ApplicationForm.TABLET,
                        dosing=Dosing.SINGLE,
                        health=Health.HEALTHY,
                        genotype=Genotype.NR,
                        fasting=Fasting.FASTED,
                        data=PKPDData.PK if pk else PKPDData.PD,
                        data_type=DataType.MEAN,
                    ),
                )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig1_Fig2_Fig3",
            num_rows=2,
            num_cols=2,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        for kp, (name, sid) in enumerate(self.info.items()):
            plots[kp].set_yaxis(self.labels[sid], unit=self.units[sid])
            for intervention in self.interventions:
                label = self.labels_intervention[intervention]
                plots[kp].add_data(
                    task=f"task_{intervention}",
                    xid="time",
                    yid=sid,
                    label=label,
                    color=self.colors[intervention],
                )
                plots[kp].add_data(
                    dataset=self.to_sid(f"{name}_{intervention}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=label,
                    color=self.colors[intervention],
                )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Arafat2005, output_dir=Arafat2005.__name__)
