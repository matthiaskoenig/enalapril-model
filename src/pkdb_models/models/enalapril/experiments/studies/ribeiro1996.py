"""Simulation experiment of the study Ribeiro1996."""

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


class Ribeiro1996(EnalaprilSimulationExperiment):
    """Simulation experiment of Ribeiro1996.

    Bioequivalence of two enalapril maleate tablets (2 x 10 mg, Eupressin and
    Renitec) in 18 healthy men (BW 70 kg), overnight fast, crossover. Serum
    enalaprilat and total enalapril by RIA (Fig1) and the serum ACE inhibition
    (Fig2), mean and SEM. The total enalapril is measured after the
    de-esterification with esterase against a standard curve of enalapril
    maleate, i.e. in ng/ml of enalapril maleate equivalents.
    """

    interventions: ClassVar[list[str]] = ["EUP20", "REN20"]
    # formulation: magenta (light = test, dark = reference)
    colors: ClassVar[dict[str, str]] = {
        "EUP20": EnalaprilSimulationExperiment.formulation_ramp[0],
        "REN20": EnalaprilSimulationExperiment.formulation_ramp[2],
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1", "Fig2"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                if label.startswith("enalapril+"):
                    # enalapril maleate equivalents
                    dset.unit_conversion("mean", 1 / self.Mr.enamal)
                elif label.startswith("enalaprilat_"):
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(label)] = dset
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        simulations["po_enamal20"] = Simulation(
            time_unit="hr",
            end=25,
            preinit_changes={
                **self.default_changes(),
                "BW": Q(70, "kg"),  # body weight
                "PODOSE_ena": Q(20, "mg")
                * self.Mr.ena
                / self.Mr.enamal,  # enalapril maleate
            },
        )

        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        info = {
            "[Cve_eat]": "enalaprilat",
            "[Cve_ena_eat]": "enalapril+enalaprilat",
            "ace_inhibition": "ACE inhibition",
        }

        mappings = {}
        for sid, name in info.items():
            for intervention in self.interventions:
                mappings[self.to_sid(f"fm_ena20_{name}_{intervention}")] = FitMapping(
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
                        self,
                        task="task_po_enamal20",
                        xid="time",
                        yid=sid,
                    ),
                    metadata=PKPDMappingMetaData(
                        tissue=Tissue.SERUM,
                        route=Route.PO,
                        application_form=ApplicationForm.TABLET,
                        dosing=Dosing.SINGLE,
                        health=Health.HEALTHY,
                        genotype=Genotype.NR,
                        fasting=Fasting.FASTED,
                        data=PKPDData.PD if sid == "ace_inhibition" else PKPDData.PK,
                    ),
                )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        return {**self._figure_pk(), **self._figure_pd()}

    def _figure_pk(self) -> dict[str, Figure]:
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
        plots[0].set_yaxis(self.labels["[Cve_eat]"], unit=self.units["[Cve_eat]"])
        plots[1].set_yaxis(
            self.labels["[Cve_ena_eat]"], unit=self.units["[Cve_ena_eat]"]
        )

        # simulation
        for kp, sid in enumerate(["eat", "ena_eat"]):
            plots[kp].add_data(
                task="task_po_enamal20",
                xid="time",
                yid=f"[Cve_{sid}]",
                label="enalapril maleate 20 mg",
                color="black",
            )
        # data
        for kp, name in enumerate(["enalaprilat", "enalapril+enalaprilat"]):
            for intervention in self.interventions:
                plots[kp].add_data(
                    dataset=self.to_sid(f"{name}_{intervention}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=f"{name} ({intervention})",
                    color=self.colors[intervention],
                )
        return self.figures_by_sid(fig)

    def _figure_pd(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig2",
            num_rows=1,
            num_cols=1,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(
            self.labels["ace_inhibition"], unit=self.units["ace_inhibition"]
        )

        # simulation
        for kp, sid in enumerate(["ace_inhibition"]):
            plots[kp].add_data(
                task="task_po_enamal20",
                xid="time",
                yid=sid,
                label="enalapril maleate 20 mg",
                color="black",
            )
        # data
        for intervention in self.interventions:
            plots[0].add_data(
                dataset=self.to_sid(f"ACE inhibition_{intervention}"),
                xid="time",
                yid="mean",
                yid_sd="mean_sd",
                count="count",
                label=f"{intervention} (ACE inhibition)",
                color=self.colors[intervention],
            )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Ribeiro1996, output_dir=Ribeiro1996.__name__)
