"""Simulation experiment of the study Najib2003a."""

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


class Najib2003a(EnalaprilSimulationExperiment):
    """Simulation experiment of Najib2003a.

    Bioequivalence study, 2-period crossover in 24 healthy men (73.38 kg,
    175.96 cm): a single tablet of 20 mg enalapril maleate, test Narapril
    (Julphar) and reference Renitec (MSD), after a 10 hr fast; enalapril and
    enalaprilat in plasma by LC-MS/MS, means without errors. Both formulations
    are one simulation (bioequivalent, AUC 103 %).
    """

    doses: ClassVar[list[str]] = ["NAR20", "REN20"]
    dose_labels: ClassVar[dict[str, str]] = {
        "NAR20": "Narapril (test)",
        "REN20": "Renitec (reference)",
    }
    # formulation: magenta (light = test, dark = reference)
    colors: ClassVar[dict[str, str]] = {
        "NAR20": EnalaprilSimulationExperiment.formulation_ramp[0],
        "REN20": EnalaprilSimulationExperiment.formulation_ramp[2],
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1"]:
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
        simulations["po_enamal20"] = Simulation(
            time_unit="hr",
            end=50,
            preinit_changes={
                **self.default_changes(),
                "BW": Q(73.38, "kg"),
                "HEIGHT": Q(175.96, "cm"),
                "PODOSE_ena": Q(20, "mg")
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
        for sid, name in info.items():
            for dose in self.doses:
                key = self.to_sid(f"fm_najib2003a_po_ENA20_{name}_{dose}")
                mappings[key] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=f"{name}_{dose}",
                        xid="time",
                        yid="mean",
                        yid_sd=None,
                        count="count",
                    ),
                    observable=FitData(
                        self,
                        task="task_po_enamal20",
                        xid="time",
                        yid=sid,
                    ),
                    metadata=PKPDMappingMetaData(
                        tissue=Tissue.PLASMA,
                        route=Route.PO,
                        application_form=ApplicationForm.TABLET,
                        dosing=Dosing.SINGLE,
                        health=Health.HEALTHY,
                        genotype=Genotype.NR,
                        fasting=Fasting.FASTED,
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
        for kp, sid in enumerate(["[Cve_ena]", "[Cve_eat]"]):
            plots[kp].add_data(
                task="task_po_enamal20",
                xid="time",
                yid=sid,
                label="ENA 20 mg",
                color=self.healthy_color,
            )

        # data
        for dose in self.doses:
            for kp, name in enumerate(["enalapril", "enalaprilat"]):
                plots[kp].add_data(
                    dataset=f"{name}_{dose}",
                    xid="time",
                    yid="mean",
                    yid_sd=None,
                    count="count",
                    label=f"ENA 20 mg {self.dose_labels[dose]}",
                    color=self.colors[dose],
                )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Najib2003a, output_dir=Najib2003a.__name__)
