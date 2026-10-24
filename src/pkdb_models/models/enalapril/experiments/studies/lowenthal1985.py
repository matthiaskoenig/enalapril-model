"""Simulation experiment of the study Lowenthal1985."""

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
from sbmlsim.units import Quantity

from pkdb_models.models.enalapril import MODEL
from pkdb_models.models.enalapril.experiments.base_experiment import (
    EnalaprilSimulationExperiment,
)


class Lowenthal1985(EnalaprilSimulationExperiment):
    """Simulation experiment of Lowenthal1985 in renal impairment and hemodialysis.

    A single tablet of 10 mg enalapril maleate after an overnight fast in
    three groups: I 10 patients on chronic hemodialysis (creatinine clearance
    < 3 ml/min), II 9 patients with renal insufficiency (creatinine clearance
    32 ± 20 ml/min, 10-79) and III 10 healthy subjects (123 ± 28 ml/min).
    Serum enalaprilat (RIA, II and III; plasma by an enzymatic assay in I,
    the heparin of the dialysis interferes with the RIA, Fig1), the urinary
    recovery of enalaprilat and of the total drug in 48 hr in percent of the
    molar dose (Tab4, II and III) and the sitting diastolic blood pressure
    (Fig3). Group I was studied twice: without dialysis on the day of the dose
    (Fig1; most patients were dialyzed between 24 and 48 hr, the enalaprilat
    at 48 hr is lower by the dialysis) and with a 4 hr dialysis from 1 hr
    after the dose (Fig4, its blood pressure is the one of group I in Fig3).
    The model has no dialysis: the period with dialysis is simulated without
    (`ENA10_I_dialysis`, its own reference of the blood pressure).
    """

    groups: ClassVar[list[str]] = ["III", "II", "I"]
    colors: ClassVar[dict[str, str]] = {
        "III": EnalaprilSimulationExperiment.renal_colors["Normal renal function"],
        "II": EnalaprilSimulationExperiment.renal_colors["Moderate renal impairment"],
        "I": EnalaprilSimulationExperiment.renal_colors["End stage renal disease"],
    }
    group_labels: ClassVar[dict[str, str]] = {
        "III": "III healthy",
        "II": "II CLcr 32",
        "I": "I hemodialysis",
    }
    #: creatinine clearance [ml/min]; group I below 3 ml/min (anuric)
    crcl: ClassVar[dict[str, float]] = {"III": 123, "II": 32, "I": 2}
    #: the predose diastolic blood pressure [mmHg] (Fig3, Fig4)
    DBP_refs: ClassVar[dict[str, float]] = {
        "III": 73.26,
        "II": 104.54,
        "I": 79.0,  # without dialysis
        "I_dialysis": 74.67,
    }
    body_weights: ClassVar[dict[str, float]] = {
        "III": 164.8,
        "II": 155.6,
        "I": 148.9,
    }
    heights: ClassVar[dict[str, float]] = {
        "III": 69.3,
        "II": 67.9,
        "I": 67.9,
    }
    #: the dose of enalapril maleate as an amount, the recovery is a fraction of it
    dose_amount: ClassVar[Quantity] = (
        Q(10, "mg") / EnalaprilSimulationExperiment.Mr.enamal
    )
    #: the urinary recovery by the observable
    urine: ClassVar[dict[str, str]] = {
        "Aurine_eat": "enalaprilat",
        "Aurine_ena_eat": "enalapril+enalaprilat",
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1", "Fig3", "Fig4", "Tab4"]:
            df = self.load_dataframe(fig_id)
            # the recovery in percent of the molar dose is the data, the
            # cumulative amounts of the curation (percent x mg of the maleate)
            # are no amounts of enalapril or enalaprilat
            df = df[df["measurement_type"] != "cumulative amount"]
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                if "_recovery_" in label:
                    # the fraction of the dose excreted in the urine
                    dset.unit_conversion("mean", self.dose_amount)
                elif label.endswith("_enalaprilat"):
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(label)] = dset
                if label == "I_enalaprilat":
                    # without the 48 hr value, after the dialysis at 24-48 hr
                    dset = DataSet.from_df(df_label[df_label["time"] <= 24], self.ureg)
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                    dsets[self.to_sid(f"{label}_0-24")] = dset

        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        for key, dbp in self.DBP_refs.items():
            group = key.split("_")[0]
            simulations[self.to_sid(f"ENA10_{key}")] = Simulation(
                time_unit="hr",
                end=50,
                preinit_changes={
                    **self.default_changes(),
                    "BW": Q(self.body_weights[group], "lb"),
                    "HEIGHT": Q(self.heights[group], "inch"),
                    "KI__f_renal_function": Q(self.crcl[group] / 101, "dimensionless"),
                    "DBP_ref": Q(dbp, "mmHg"),
                    # enalapril maleate
                    "PODOSE_ena": Q(10, "mg") * self.Mr.ena / self.Mr.enamal,
                },
            )
        return simulations

    def _mapping(
        self, dataset: str, task: str, yid: str, group: str, tissue: Tissue
    ) -> FitMapping:
        """Fit mapping of a dataset of a group."""
        return FitMapping(
            self,
            reference=FitData(
                self,
                dataset=self.to_sid(dataset),
                xid="time",
                yid="mean",
                yid_sd="mean_sd" if tissue == Tissue.URINE else None,
                count="count",
            ),
            observable=FitData(self, task=self.to_sid(task), xid="time", yid=yid),
            metadata=PKPDMappingMetaData(
                tissue=tissue,
                route=Route.PO,
                application_form=ApplicationForm.TABLET,
                dosing=Dosing.SINGLE,
                health=Health.HEALTHY if group == "III" else Health.RENAL_IMPAIRMENT,
                genotype=Genotype.NR,
                fasting=Fasting.FASTED,
                data=PKPDData.PD if tissue == Tissue.NONE else PKPDData.PK,
                data_type=DataType.MEAN,
            ),
        )

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for group in self.groups:
            task = f"task_ENA10_{group}"
            prefix = f"fm_lowenthal1985_po_ENA10_{group}"
            # group I: plasma (enzymatic assay), without the value after the
            # dialysis at 24-48 hr
            mappings[self.to_sid(f"{prefix}_enalaprilat")] = self._mapping(
                f"{group}_enalaprilat_0-24" if group == "I" else f"{group}_enalaprilat",
                task,
                "[Cve_eat]",
                group,
                Tissue.PLASMA if group == "I" else Tissue.SERUM,
            )
            # the blood pressure of group I in Fig3 is the period with dialysis
            mappings[self.to_sid(f"{prefix}_DBP")] = self._mapping(
                f"{group}_blood pressure diastolic",
                "task_ENA10_I_dialysis" if group == "I" else task,
                "DBP",
                group,
                Tissue.NONE,
            )
            if group != "I":
                for yid, name in self.urine.items():
                    mappings[self.to_sid(f"{prefix}_{name}_urine")] = self._mapping(
                        f"{group}_recovery_{name}", task, yid, group, Tissue.URINE
                    )

        # group I with and without dialysis (Fig4)
        for treatment, task in [
            ("without dialysis", "task_ENA10_I"),
            ("with dialysis", "task_ENA10_I_dialysis"),
        ]:
            mappings[self.to_sid(f"fm_lowenthal1985_po_ENA10_I_{treatment}_DBP")] = (
                self._mapping(
                    f"{treatment}_blood pressure diastolic",
                    task,
                    "DBP",
                    "I",
                    Tissue.NONE,
                )
            )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        return {**self._figure_pk(), **self._figure_pd()}

    def _figure_pk(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig1_Tab4",
            num_rows=1,
            num_cols=3,
            name=f"{self.__class__.__name__}",
            settings={"legend_scope": "row"},
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        for kp, yid in enumerate(["[Cve_eat]", *self.urine]):
            plots[kp].set_yaxis(self.labels[yid], unit=self.units[yid])

        for group in self.groups:
            groups_yids = ["[Cve_eat]"] if group == "I" else ["[Cve_eat]", *self.urine]
            for kp, yid in enumerate(groups_yids):
                plots[kp].add_data(
                    task=self.to_sid(f"task_ENA10_{group}"),
                    xid="time",
                    yid=yid,
                    label=self.group_labels[group],
                    color=self.colors[group],
                )
            plots[0].add_data(
                dataset=self.to_sid(f"{group}_enalaprilat"),
                xid="time",
                yid="mean",
                yid_sd=None,
                count="count",
                label=self.group_labels[group],
                color=self.colors[group],
            )
            if group != "I":
                for kp, name in enumerate(self.urine.values(), start=1):
                    plots[kp].add_data(
                        dataset=self.to_sid(f"{group}_recovery_{name}"),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                        label=self.group_labels[group],
                        color=self.colors[group],
                    )
        return self.figures_by_sid(fig)

    def _figure_pd(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig3_Fig4",
            num_rows=1,
            num_cols=2,
            name=f"{self.__class__.__name__}",
            settings={"legend_scope": "row"},
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(self.labels["DBP"], unit=self.units["DBP"])
        plots[1].set_yaxis(self.labels["DBP"], unit=self.units["DBP"])

        # Fig3: the groups (group I in the period with dialysis)
        for group in self.groups:
            plots[0].add_data(
                task="task_ENA10_I_dialysis"
                if group == "I"
                else self.to_sid(f"task_ENA10_{group}"),
                xid="time",
                yid="DBP",
                label=self.group_labels[group],
                color=self.colors[group],
            )
            plots[0].add_data(
                dataset=self.to_sid(f"{group}_blood pressure diastolic"),
                xid="time",
                yid="mean",
                yid_sd=None,
                count="count",
                label=self.group_labels[group],
                color=self.colors[group],
            )
        # Fig4: group I with and without dialysis (no dialysis in the model)
        for treatment, task, marker, linestyle in [
            ("without dialysis", "task_ENA10_I", "v", "-"),
            ("with dialysis", "task_ENA10_I_dialysis", "^", "--"),
        ]:
            plots[1].add_data(
                task=task,
                xid="time",
                yid="DBP",
                label=f"I {treatment}",
                color=self.colors["I"],
                linestyle=linestyle,
            )
            plots[1].add_data(
                dataset=self.to_sid(f"{treatment}_blood pressure diastolic"),
                xid="time",
                yid="mean",
                yid_sd=None,
                count="count",
                label=f"I {treatment}",
                color=self.colors["I"],
                marker=marker,
            )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Lowenthal1985, output_dir=Lowenthal1985.__name__)
