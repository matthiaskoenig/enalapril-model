"""Simulation experiment of the study Moffett2014."""

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


class Moffett2014(EnalaprilSimulationExperiment):
    """Simulation experiment of Moffett2014.

    Single dose 3-way crossover in 53 healthy adults (42 M/11 F, median BMI
    25.4; the body weight of at least 50 kg is the inclusion criterion, not the
    weight of the cohort, which is simulated with the default 75 kg): 10 mg
    enalapril maleate as oral solution (Epaned) fasted (A), as tablet (Vasotec)
    fasted (B) and as oral solution after a high fat breakfast (C, started 30 min
    before the dose). Enalapril and enalaprilat in plasma by LC-MS/MS (mean +
    SEM, n = 48, 45 for B). The fasted arms are one simulation (the model has no
    difference of the formulations, bioequivalence shown), the fed arm switches
    the intestine to the fed state (`GU__fed`).
    """

    interventions: ClassVar[list[str]] = ["ENAfast10", "VAS10", "ENAfed10"]
    labels_interventions: ClassVar[dict[str, str]] = {
        "ENAfast10": "solution fasted",
        "VAS10": "tablet fasted",
        "ENAfed10": "solution fed",
    }
    #: the food state of the arms, see `fasting_map`
    fasting: ClassVar[dict[str, str]] = {
        "ENAfast10": "fasted",
        "VAS10": "fasted",
        "ENAfed10": "fed",
    }
    #: the simulation of an arm, by its food state
    fasting_tasks: ClassVar[dict[str, str]] = {
        "fasted": "task_po_ENA10",
        "fed": "task_po_ENA10_fed",
    }
    colors: ClassVar[dict[str, str]] = {
        "ENAfast10": EnalaprilSimulationExperiment.fasting_colors["fasted"],
        "VAS10": EnalaprilSimulationExperiment.fasting_colors["fasted"],
        "ENAfed10": EnalaprilSimulationExperiment.fasting_colors["fed"],
    }
    # the formulation by the marker
    markers: ClassVar[dict[str, str]] = {
        "ENAfast10": "o",
        "VAS10": "s",
        "ENAfed10": "o",
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1", "Fig2"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                if label.startswith("enalapril_"):
                    dset.unit_conversion("mean", 1 / self.Mr.ena)
                elif label.startswith("enalaprilat_"):
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[label] = dset

        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        for fasting, key in [("fasted", "po_ENA10"), ("fed", "po_ENA10_fed")]:
            simulations[key] = Simulation(
                time_unit="hr",
                end=74,
                preinit_changes={
                    **self.default_changes(),
                    "GU__fed": Q(self.fasting_map[fasting], "dimensionless"),
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
        for intervention in self.interventions:
            fasting = self.fasting[intervention]
            for sid, name in info.items():
                key = self.to_sid(f"fm_moffett2014_{intervention}_{name}")
                mappings[key] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=f"{name}_{intervention}",
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                    ),
                    observable=FitData(
                        self,
                        task=self.fasting_tasks[fasting],
                        xid="time",
                        yid=sid,
                    ),
                    metadata=PKPDMappingMetaData(
                        tissue=Tissue.PLASMA,
                        route=Route.PO,
                        application_form=ApplicationForm.TABLET
                        if intervention == "VAS10"
                        else ApplicationForm.SOLUTION,
                        dosing=Dosing.SINGLE,
                        health=Health.HEALTHY,
                        genotype=Genotype.NR,
                        fasting=Fasting.FASTED if fasting == "fasted" else Fasting.FED,
                        data=PKPDData.PK,
                    ),
                )

        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig1",
            num_rows=2,
            num_cols=1,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(self.labels["[Cve_ena]"], unit=self.units["[Cve_ena]"])
        plots[1].set_yaxis(self.labels["[Cve_eat]"], unit=self.units["[Cve_eat]"])
        plots[0].set_xaxis(self.labels["time"], unit=self.units["time"], max=24)

        # simulation
        for fasting, color in [
            ("fasted", self.fasting_colors["fasted"]),
            ("fed", self.fasting_colors["fed"]),
        ]:
            for kp, sid in enumerate(["[Cve_ena]", "[Cve_eat]"]):
                plots[kp].add_data(
                    task=self.fasting_tasks[fasting],
                    xid="time",
                    yid=sid,
                    label=f"ENA 10 mg {fasting}",
                    color=color,
                )
        # data
        for kp, name in enumerate(["enalapril", "enalaprilat"]):
            for intervention in self.interventions:
                plots[kp].add_data(
                    dataset=f"{name}_{intervention}",
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=f"ENA 10 mg {self.labels_interventions[intervention]}",
                    color=self.colors[intervention],
                    marker=self.markers[intervention],
                )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Moffett2014, output_dir=Moffett2014.__name__)
