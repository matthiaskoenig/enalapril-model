"""Simulation experiment of the study Matalka2002."""

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


class Matalka2002(EnalaprilSimulationExperiment):
    """Simulation experiment of Matalka2002.

    48 healthy men (74.1 kg) "received either a 10 or 20 mg oral dose" of
    enalapril maleate in the morning, a light breakfast 2 hr after the dose;
    enalapril and enalaprilat in plasma by two ELISAs (Fig. 2) and the blood
    pressure (Fig. 3), mean +- SE. Whether the arms are parallel (24 each) or a
    crossover (48 each) is not stated, the SD is computed with n = 48 (the
    means do not depend on it). The enalapril of the ELISA is 4 to 5 times the
    enalapril of the LC-MS/MS studies (Cmax 310 vs 58-67 ng/ml at 10 mg), its
    mappings are outliers.
    """

    interventions: ClassVar[list[str]] = ["ENA10", "ENA20"]

    doses: ClassVar[dict[str, int]] = {
        "ENA10": 10,
        "ENA20": 20,
    }
    # healthy subjects: black for every dose, dose shown by marker
    colors: ClassVar[dict[str, str]] = {
        "ENA10": EnalaprilSimulationExperiment.healthy_color,
        "ENA20": EnalaprilSimulationExperiment.healthy_color,
    }
    markers: ClassVar[dict[str, str]] = EnalaprilSimulationExperiment.dose_markers(
        ["ENA10", "ENA20"]
    )
    linestyles: ClassVar[dict[str, str]] = {"ENA10": "-", "ENA20": "--"}
    SBP_refs: ClassVar[dict[str, float]] = {
        "ENA10": 116.62,
        "ENA20": 115.07,
    }
    DBP_refs: ClassVar[dict[str, float]] = {
        "ENA10": 79.96,
        "ENA20": 81.05,
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig2", "Fig3"]:
            df = self.load_dataframe(fig_id)
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
        for intervention in self.interventions:
            simulations[self.to_sid(f"po_{intervention}")] = Simulation(
                time_unit="hr",
                end=24,
                preinit_changes={
                    **self.default_changes(),
                    "BW": Q(74.1, "kg"),  # body weight
                    "SBP_ref": Q(self.SBP_refs[intervention], "mmHg"),
                    "DBP_ref": Q(self.DBP_refs[intervention], "mmHg"),
                    "PODOSE_ena": Q(self.doses[intervention], "mg")
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
            "SBP": "blood pressure systolic",
            "DBP": "blood pressure diastolic",
        }

        mappings = {}
        for intervention in self.interventions:
            for sid, name in info.items():
                mappings[self.to_sid(f"fm_matalka2002_po_{intervention}_{name}")] = (
                    FitMapping(
                        self,
                        reference=FitData(
                            self,
                            dataset=self.to_sid(f"{intervention}_{name}"),
                            xid="time",
                            yid="mean",
                            yid_sd="mean_sd",
                            count="count",
                        ),
                        observable=FitData(
                            self,
                            task=self.to_sid(f"task_po_{intervention}"),
                            xid="time",
                            yid=sid,
                        ),
                        metadata=PKPDMappingMetaData(
                            tissue=Tissue.PLASMA
                            if sid in ["[Cve_ena]", "[Cve_eat]"]
                            else Tissue.NONE,
                            route=Route.PO,
                            application_form=ApplicationForm.NR,
                            dosing=Dosing.SINGLE,
                            health=Health.HEALTHY,
                            genotype=Genotype.NR,
                            fasting=Fasting.NR,
                            data=PKPDData.PK
                            if sid in ["[Cve_ena]", "[Cve_eat]"]
                            else PKPDData.PD,
                        ),
                    )
                )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        return {**self._figure_pk(), **self._figure_pd()}

    def _figure_pk(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig2",
            num_rows=2,
            num_cols=1,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(self.labels["[Cve_ena]"], unit=self.units["[Cve_ena]"])
        plots[1].set_yaxis(self.labels["[Cve_eat]"], unit=self.units["[Cve_eat]"])

        for intervention in self.interventions:
            # simulation
            for kp, sid in enumerate(["ena", "eat"]):
                plots[kp].add_data(
                    task=self.to_sid(f"task_po_{intervention}"),
                    xid="time",
                    yid=f"[Cve_{sid}]",
                    label=f"ENA {self.doses[intervention]} mg",
                    color=self.colors[intervention],
                    linestyle=self.linestyles[intervention],
                )
            # data
            for kp, name in enumerate(["enalapril", "enalaprilat"]):
                plots[kp].add_data(
                    dataset=self.to_sid(f"{intervention}_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=f"ENA {self.doses[intervention]} mg",
                    color=self.colors[intervention],
                    marker=self.markers[intervention],
                )

        return self.figures_by_sid(fig)

    def _figure_pd(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig3",
            num_rows=2,
            num_cols=1,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(self.labels["SBP"], unit=self.units["SBP"])
        plots[1].set_yaxis(self.labels["DBP"], unit=self.units["DBP"])

        for intervention in self.interventions:
            # simulation
            for kp, sid in enumerate(["SBP", "DBP"]):
                plots[kp].add_data(
                    task=self.to_sid(f"task_po_{intervention}"),
                    xid="time",
                    yid=sid,
                    label=f"ENA {self.doses[intervention]} mg",
                    color=self.colors[intervention],
                    linestyle=self.linestyles[intervention],
                )
            # data
            for kp, name in enumerate(
                ["blood pressure systolic", "blood pressure diastolic"]
            ):
                plots[kp].add_data(
                    dataset=self.to_sid(f"{intervention}_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=f"ENA {self.doses[intervention]} mg",
                    color=self.colors[intervention],
                    marker=self.markers[intervention],
                )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Matalka2002, output_dir=Matalka2002.__name__)
