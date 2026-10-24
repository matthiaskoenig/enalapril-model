"""Simulation experiment of the study Niopas2004."""

from typing import ClassVar, override

from pkpdsim.metadata import (
    ApplicationForm,
    Coadministration,
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


class Niopas2004(EnalaprilSimulationExperiment):
    """Simulation experiment of Niopas2004.

    Bioequivalence of two fixed dose combinations of enalapril maleate 20 mg and
    hydrochlorothiazide 12.5 mg (test Penopril, reference) in 24 healthy
    volunteers (BW 73.2 kg, height 176.3 cm), single oral tablet after an
    overnight fast of 10 hr, crossover. Enalaprilat in plasma by GC/MS (Fig1,
    mean and SD), the enalapril was not measured (Arzneimittelforschung
    2004;54:160-5).

    Hydrochlorothiazide does not change the pharmacokinetics of enalapril
    (`INTERACTION_FACTORS`), the arms are validation of the interaction.
    """

    interventions: ClassVar[list[str]] = ["ENA20", "REF20"]
    # formulation: magenta (light = test, dark = reference)
    colors: ClassVar[dict[str, str]] = {
        "ENA20": EnalaprilSimulationExperiment.formulation_ramp[0],
        "REF20": EnalaprilSimulationExperiment.formulation_ramp[2],
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                if label.startswith("enalaprilat_"):
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[label] = dset

        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        simulations["po_enamal20"] = Simulation(
            time_unit="hr",
            end=38,
            preinit_changes={
                **self.default_changes(),
                "BW": Q(73.2, "kg"),  # body weight
                "HEIGHT": Q(176.3, "cm"),  # height
                "PODOSE_ena": Q(20, "mg")
                * self.Mr.ena
                / self.Mr.enamal,  # enalapril maleate
                **self.interaction_changes(Coadministration.HCTZ),
            },
        )

        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for intervention in self.interventions:
            mappings[f"fm_ena20_enalaprilat_{intervention}"] = FitMapping(
                self,
                reference=FitData(
                    self,
                    dataset=f"enalaprilat_{intervention}",
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                ),
                observable=FitData(
                    self,
                    task="task_po_enamal20",
                    xid="time",
                    yid="[Cve_eat]",
                ),
                metadata=PKPDMappingMetaData(
                    tissue=Tissue.PLASMA,
                    route=Route.PO,
                    application_form=ApplicationForm.TABLET,
                    dosing=Dosing.SINGLE,
                    health=Health.HEALTHY,
                    genotype=Genotype.NR,
                    fasting=Fasting.FASTED,
                    coadministration=Coadministration.HCTZ,
                    data=PKPDData.PK,
                ),
            )

        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig1",
            num_rows=1,
            num_cols=1,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(self.labels["[Cve_eat]"], unit=self.units["[Cve_eat]"])

        # simulation
        plots[0].add_data(
            task="task_po_enamal20",
            xid="time",
            yid="[Cve_eat]",
            label="enalaprilat",
            color="black",
        )
        # data
        for kp, name in enumerate(["enalaprilat"]):
            for intervention in self.interventions:
                plots[kp].add_data(
                    dataset=f"{name}_{intervention}",
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=f"{name} ({intervention})",
                    color=self.colors[intervention],
                )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Niopas2004, output_dir=Niopas2004.__name__)
