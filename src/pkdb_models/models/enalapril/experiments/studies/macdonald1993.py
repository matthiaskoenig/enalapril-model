"""Simulation experiment of the study MacDonald1993."""

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


class MacDonald1993(EnalaprilSimulationExperiment):
    """Simulation experiment of MacDonald1993.

    9 young (21-39 yr, CLcr 112 ml/min) and 9 elderly (66-76 yr, CLcr 78
    ml/min, normal for the age) healthy normotensive subjects, a single oral
    dose of 10 mg enalapril maleate after an overnight fast (form not
    reported), enalaprilat in plasma by RIA (Fig. 2b) and the ACE inhibition in
    plasma ex vivo (Fig. 1b), means without errors. Both groups are healthy,
    they differ by the measured renal function (CLcr / 101 ml/min).
    """

    groups: ClassVar[list[str]] = ["young", "elder"]
    group_labels: ClassVar[dict[str, str]] = {"young": "young", "elder": "elderly"}

    # healthy subjects: black, the age by the marker (data) and the line style
    # (simulation)
    colors: ClassVar[dict[str, str]] = {
        "young": EnalaprilSimulationExperiment.healthy_color,
        "elder": EnalaprilSimulationExperiment.healthy_color,
    }
    linestyles: ClassVar[dict[str, str]] = {"young": "-", "elder": "--"}
    #: the renal function by the creatinine clearance, CLcr / 101 ml/min
    renal_functions: ClassVar[dict[str, float]] = {
        "young": 112 / 101,
        "elder": 78 / 101,
    }
    SBPref: ClassVar[dict[str, int]] = {
        "young": 127,
        "elder": 147,
    }
    DBPref: ClassVar[dict[str, int]] = {
        "young": 72,
        "elder": 80,
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1", "Fig2"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                dsets[self.to_sid(label)] = dset
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        for group in self.groups:
            simulations[self.to_sid(f"po_ENA10_{group}")] = Simulation(
                time_unit="hr",
                end=74,
                preinit_changes={
                    **self.default_changes(),
                    "SBP_ref": Q(self.SBPref[group], "mmHg"),
                    "DBP_ref": Q(self.DBPref[group], "mmHg"),
                    "KI__f_renal_function": Q(
                        self.renal_functions[group], "dimensionless"
                    ),
                    "PODOSE_ena": Q(10, "mg")
                    * self.Mr.ena
                    / self.Mr.enamal,  # enalapril maleate
                },
            )
        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        info = {
            "[Cve_eat]": "enalaprilat",
            "ace_inhibition": "ACE inhibition",
        }

        mappings = {}
        for sid, name in info.items():
            for group in self.groups:
                key = self.to_sid(f"fm_macdonald1993_po_ENA10_{group}_{name}")
                mappings[key] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(
                            f"{name}_{group}"
                            if name == "enalaprilat"
                            else f"{group}_ENA10_{name}"
                        ),
                        xid="time",
                        yid="mean",
                        yid_sd=None,
                        count="count",
                    ),
                    observable=FitData(
                        self,
                        task=self.to_sid(f"task_po_ENA10_{group}"),
                        xid="time",
                        yid=sid,
                    ),
                    metadata=PKPDMappingMetaData(
                        tissue=Tissue.PLASMA,
                        route=Route.PO,
                        application_form=ApplicationForm.NR,
                        dosing=Dosing.SINGLE,
                        health=Health.HEALTHY,
                        genotype=Genotype.NR,
                        fasting=Fasting.FASTED,
                        data=PKPDData.PK if name == "enalaprilat" else PKPDData.PD,
                    ),
                )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        return {**self._figure_pk(), **self._figure_pd()}

    def _figure_pk(self) -> dict[str, Figure]:
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
        plots[0].set_yaxis(self.labels["[Cve_eat]"], unit=self.units["[Cve_eat]"])

        for group in self.groups:
            # simulation
            plots[0].add_data(
                task=self.to_sid(f"task_po_ENA10_{group}"),
                xid="time",
                yid="[Cve_eat]",
                label=f"ENA 10 mg ({self.group_labels[group]})",
                color=self.colors[group],
                linestyle=self.linestyles[group],
            )
            # data
            plots[0].add_data(
                dataset=self.to_sid(f"enalaprilat_{group}"),
                xid="time",
                yid="mean",
                yid_sd=None,
                count="count",
                label=f"ENA 10 mg ({self.group_labels[group]})",
                color=self.colors[group],
                marker=self.age_markers[group],
            )

        return self.figures_by_sid(fig)

    def _figure_pd(self) -> dict[str, Figure]:
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
        plots[0].set_yaxis(
            self.labels["ace_inhibition"], unit=self.units["ace_inhibition"]
        )

        for group in self.groups:
            # simulation
            plots[0].add_data(
                task=self.to_sid(f"task_po_ENA10_{group}"),
                xid="time",
                yid="ace_inhibition",
                label=f"ENA 10 mg ({self.group_labels[group]})",
                color=self.colors[group],
                linestyle=self.linestyles[group],
            )
            # data
            plots[0].add_data(
                dataset=self.to_sid(f"{group}_ENA10_ACE inhibition"),
                xid="time",
                yid="mean",
                yid_sd=None,
                count="count",
                label=f"ENA 10 mg ({self.group_labels[group]})",
                color=self.colors[group],
                marker=self.age_markers[group],
            )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(MacDonald1993, output_dir=MacDonald1993.__name__)
