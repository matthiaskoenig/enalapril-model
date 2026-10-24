"""Simulation experiment of the study Sunaga1995."""

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


class Sunaga1995(EnalaprilSimulationExperiment):
    """Simulation experiment of Sunaga1995.

    12 inpatients with essential hypertension (BW 63 kg), randomized crossover
    of placebo and a single tablet of 5 mg enalapril maleate at 10:00 (day
    trial) or 22:00 (night trial), both 2 hr after a standard meal (protein
    25 g, lipid 15 g). Serum enalaprilat and total drug (enalapril +
    enalaprilat, RIA after hydrolysis, in enalaprilat equivalents) and the
    blood pressure 0-24 hr (mean and SD).
    """

    groups: ClassVar[list[str]] = ["day", "night"]
    # colour = intervention (drug black, placebo grey), marker = day / night
    colors: ClassVar[dict[str, str]] = {
        "PLACEBO": EnalaprilSimulationExperiment.placebo_color,
        "ENA5": EnalaprilSimulationExperiment.healthy_color,
    }
    markers: ClassVar[dict[str, str]] = {
        "day": EnalaprilSimulationExperiment.time_markers["day"],
        "night": EnalaprilSimulationExperiment.time_markers["night"],
    }
    linestyles: ClassVar[dict[str, str]] = {"day": "-", "night": "--"}
    interventions: ClassVar[list[str]] = ["PLACEBO", "ENA5"]
    doses: ClassVar[dict[str, float]] = {"PLACEBO": 0, "ENA5": 5}
    #: the baseline (predose) of the blood pressure of the trials
    SBP_refs: ClassVar[dict[str, float]] = {
        "day_PLACEBO": 127.6,
        "day_ENA5": 127.9,
        "night_PLACEBO": 129.2,
        "night_ENA5": 128.9,
    }
    DBP_refs: ClassVar[dict[str, float]] = {
        "day_PLACEBO": 72.6,
        "day_ENA5": 74.7,
        "night_PLACEBO": 74.8,
        "night_ENA5": 72.7,
    }
    #: the substances of the serum data by observable
    info_pk: ClassVar[dict[str, str]] = {
        "[Cve_eat]": "enalaprilat",
        "[Cve_ena_eat]": "enalapril+enalaprilat",
    }
    #: the blood pressure data by observable
    info_pd: ClassVar[dict[str, str]] = {
        "SBP": "blood pressure systolic",
        "DBP": "blood pressure diastolic",
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1", "Fig2", "Fig4"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                # the total drug of the RIA after hydrolysis is in enalaprilat
                # equivalents (the assay of Ishizaki1988)
                if label.endswith("enalaprilat"):
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(label)] = dset
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        for group in self.groups:
            for intervention, dose in self.doses.items():
                key = f"{group}_{intervention}"
                simulations[self.to_sid(f"po_{intervention}_{group}")] = Simulation(
                    time_unit="hr",
                    end=24,
                    preinit_changes={
                        **self.default_changes(),
                        "BW": Q(63, "kg"),
                        "SBP_ref": Q(self.SBP_refs[key], "mmHg"),
                        "DBP_ref": Q(self.DBP_refs[key], "mmHg"),
                        # dosed 2 hr after a standard meal (protein 25 g, lipid
                        # 15 g), the stomach partly emptied: half the effect of
                        # a meal, as a light breakfast
                        "GU__fed": Q(
                            self.fasting_map["light breakfast"], "dimensionless"
                        ),
                        # enalapril maleate
                        "PODOSE_ena": Q(dose, "mg") * self.Mr.ena / self.Mr.enamal,
                    },
                )
        return simulations

    @staticmethod
    def _metadata(tissue: Tissue, data: PKPDData) -> PKPDMappingMetaData:
        """Get the metadata of a mapping of the study."""
        return PKPDMappingMetaData(
            tissue=tissue,
            route=Route.PO,
            application_form=ApplicationForm.TABLET,
            dosing=Dosing.SINGLE,
            health=Health.HYPERTENSION,
            genotype=Genotype.NR,
            fasting=Fasting.FED,
            data=data,
        )

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for group in self.groups:
            for sid, name in self.info_pk.items():
                mappings[self.to_sid(f"fm_ENA5_{group}_{name}")] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(f"{group}_ENA5_{name}"),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                    ),
                    observable=FitData(
                        self,
                        task=self.to_sid(f"task_po_ENA5_{group}"),
                        xid="time",
                        yid=sid,
                    ),
                    metadata=self._metadata(Tissue.SERUM, PKPDData.PK),
                )
            for sid, name in self.info_pd.items():
                for intervention in self.interventions:
                    mappings[self.to_sid(f"fm_{intervention}_{group}_{name}")] = (
                        FitMapping(
                            self,
                            reference=FitData(
                                self,
                                dataset=self.to_sid(f"{group}_{intervention}_{name}"),
                                xid="time",
                                yid="mean",
                                yid_sd="mean_sd",
                                count="count",
                            ),
                            observable=FitData(
                                self,
                                task=self.to_sid(f"task_po_{intervention}_{group}"),
                                xid="time",
                                yid=sid,
                            ),
                            metadata=self._metadata(Tissue.NONE, PKPDData.PD),
                        )
                    )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        return {**self._figure_pk(), **self._figure_pd()}

    def _figure_pk(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig1_Fig2",
            num_rows=2,
            num_cols=1,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        for kp, (sid, name) in enumerate(self.info_pk.items()):
            plots[kp].set_yaxis(self.labels[sid], unit=self.units[sid])
            for group in self.groups:
                plots[kp].add_data(
                    task=self.to_sid(f"task_po_ENA5_{group}"),
                    xid="time",
                    yid=sid,
                    label=f"5 mg {group}",
                    color=self.colors["ENA5"],
                    linestyle=self.linestyles[group],
                )
                plots[kp].add_data(
                    dataset=self.to_sid(f"{group}_ENA5_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=f"5 mg {group}",
                    color=self.colors["ENA5"],
                    marker=self.markers[group],
                    linestyle=self.linestyles[group],
                )
        return self.figures_by_sid(fig)

    def _figure_pd(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig4",
            num_rows=2,
            num_cols=2,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        # rows: SBP, DBP; columns: day, night trial
        for krow, (sid, name) in enumerate(self.info_pd.items()):
            for kcol, group in enumerate(self.groups):
                kp = 2 * krow + kcol
                plots[kp].set_title(f"{group} trial")
                plots[kp].set_yaxis(self.labels[sid], unit=self.units[sid])
                for intervention in self.interventions:
                    label = "placebo" if intervention == "PLACEBO" else "5 mg"
                    plots[kp].add_data(
                        task=self.to_sid(f"task_po_{intervention}_{group}"),
                        xid="time",
                        yid=sid,
                        label=label,
                        color=self.colors[intervention],
                    )
                    plots[kp].add_data(
                        dataset=self.to_sid(f"{group}_{intervention}_{name}"),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                        label=label,
                        color=self.colors[intervention],
                        marker=self.markers[group],
                    )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Sunaga1995, output_dir=Sunaga1995.__name__)
