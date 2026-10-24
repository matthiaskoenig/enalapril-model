"""Simulation experiment of the study Ishizaki1988."""

from typing import ClassVar, override

import pandas as pd
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


class Ishizaki1988(EnalaprilSimulationExperiment):
    """Simulation experiment of Ishizaki1988.

    7 healthy normotensive Japanese men (BW 68.3 kg, height 168.1 cm,
    creatinine clearance 117.1 ml/min), a double blind crossover of placebo
    and cimetidine 400 mg twice daily for 3 days and on the study day. A
    tablet of 10 mg enalapril maleate (assay 9.96 mg) after an overnight
    fast which continued until the lunch at 4 hr. Serum enalapril and
    enalaprilat (RIA, Fig1), the urinary recovery of enalapril and
    enalaprilat in percent of the molar dose (Fig2), the seated blood
    pressure and heart rate (Fig3, mean ± SEM) and the serum ACE activity
    before and 4 hr after the dose (Fig4, individual values).

    Cimetidine changes neither the pharmacokinetics of enalapril and
    enalaprilat nor the ACE inhibition, the cimetidine arm is simulated with
    the factors of the interaction of the base experiment (none). The
    references of the blood pressure are the predose values of each arm. The
    heart rate is a constant input of the model (no heart rate model), it is
    not set: a heart rate above the resting rate raises the cardiac output and
    with it the clearance.
    """

    #: the dose of enalapril maleate as an amount, the recovery is a fraction of it
    dose_amount: ClassVar[Quantity] = (
        Q(10, "mg") / EnalaprilSimulationExperiment.Mr.enamal
    )
    #: the arms: the intervention of the data and the coadministration
    arms: ClassVar[dict[str, tuple[str, Coadministration]]] = {
        "ENA10": ("ENA10", Coadministration.NONE),
        "CIM400_ENA10": ("CIM400, ENA10", Coadministration.CIMETIDINE),
    }
    arm_labels: ClassVar[dict[str, str]] = {
        "ENA10": "placebo",
        "CIM400_ENA10": "cimetidine",
    }
    colors: ClassVar[dict[str, str]] = {
        "ENA10": EnalaprilSimulationExperiment.healthy_color,
        "CIM400_ENA10": EnalaprilSimulationExperiment.formulation_ramp[1],
    }
    markers: ClassVar[dict[str, str]] = {"ENA10": "o", "CIM400_ENA10": "s"}
    #: the predose blood pressure (SBP, DBP) of the arms [mmHg] (Fig3, 0 hr)
    blood_pressures: ClassVar[dict[str, tuple[float, float]]] = {
        "ENA10": (119.794, 74.110),
        "CIM400_ENA10": (122.632, 76.770),
    }
    #: the pharmacokinetic data by the observable
    pk_data: ClassVar[dict[str, str]] = {
        "[Cve_ena]": "enalapril",
        "[Cve_eat]": "enalaprilat",
        "Aurine_ena": "recovery_enalapril",
        "Aurine_eat": "recovery_enalaprilat",
    }
    #: the pharmacodynamic data by the observable
    pd_data: ClassVar[dict[str, str]] = {
        "SBP": "blood pressure systolic",
        "DBP": "blood pressure diastolic",
        "HR": "heart rate",
        "ace_inhibition": "ACE inhibition",
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1", "Fig2", "Fig3"]:
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
                elif label.endswith("_enalapril"):
                    dset.unit_conversion("mean", 1 / self.Mr.ena)
                elif label.endswith("_enalaprilat"):
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(label)] = dset

        # the ACE inhibition 4 hr after the dose from the individual serum ACE
        # activities before and after the dose (Fig4)
        df = self.load_dataframe("Fig4")
        df = df[df["substance"] == "angiotensin converting enzyme"]
        for intervention, df_arm in df.groupby("intervention"):
            activity = df_arm.pivot(index="individual", columns="time", values="value")
            inhibition = 100 * (1 - activity[4.0] / activity[0.0])
            dsets[self.to_sid(f"{intervention}_ACE inhibition")] = DataSet.from_df(
                pd.DataFrame(
                    {
                        "time": [4.0],
                        "time_unit": ["hr"],
                        "mean": [inhibition.mean()],
                        "sd": [inhibition.std()],
                        "count": [len(inhibition)],
                        "unit": ["percent"],
                    }
                ),
                self.ureg,
            )
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        for arm, (_, coadministration) in self.arms.items():
            sbp, dbp = self.blood_pressures[arm]
            simulations[f"po_{arm}"] = Simulation(
                time_unit="hr",
                end=25,
                preinit_changes={
                    **self.default_changes(),
                    **self.interaction_changes(coadministration),
                    "BW": Q(68.29, "kg"),
                    "HEIGHT": Q(168.14, "cm"),
                    # creatinine clearance 117.1 ml/min
                    "KI__f_renal_function": Q(117.1 / 101, "dimensionless"),
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
        for arm, (intervention, coadministration) in self.arms.items():
            for yid, name in {**self.pk_data, **self.pd_data}.items():
                if yid.startswith("[Cve_"):
                    tissue = Tissue.SERUM
                elif yid.startswith("Aurine_"):
                    tissue = Tissue.URINE
                elif yid == "ace_inhibition":
                    tissue = Tissue.SERUM
                else:
                    tissue = Tissue.NONE
                mappings[self.to_sid(f"fm_ishizaki1988_po_{arm}_{name}")] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(f"{intervention}_{name}"),
                        xid="time",
                        yid="mean",
                        yid_sd=None if yid in self.pk_data else "mean_sd",
                        count="count",
                    ),
                    observable=FitData(
                        self, task=f"task_po_{arm}", xid="time", yid=yid
                    ),
                    metadata=PKPDMappingMetaData(
                        tissue=tissue,
                        route=Route.PO,
                        application_form=ApplicationForm.TABLET,
                        dosing=Dosing.SINGLE,
                        health=Health.HEALTHY,
                        genotype=Genotype.NR,
                        fasting=Fasting.FASTED,
                        coadministration=coadministration,
                        data=PKPDData.PK if yid in self.pk_data else PKPDData.PD,
                        data_type=DataType.MEAN,
                    ),
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
            num_cols=2,
            name=f"{self.__class__.__name__}",
            settings={"legend_scope": "row"},
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        for kp, yid in enumerate(
            ["[Cve_ena]", "Aurine_ena", "[Cve_eat]", "Aurine_eat"]
        ):
            plots[kp].set_yaxis(self.labels[yid], unit=self.units[yid])
            for arm in self.arms:
                plots[kp].add_data(
                    task=f"task_po_{arm}",
                    xid="time",
                    yid=yid,
                    label=self.arm_labels[arm],
                    color=self.colors[arm],
                    linestyle="-" if arm == "ENA10" else "--",
                )
            for arm, (intervention, _) in self.arms.items():
                plots[kp].add_data(
                    dataset=self.to_sid(f"{intervention}_{self.pk_data[yid]}"),
                    xid="time",
                    yid="mean",
                    yid_sd=None,
                    count="count",
                    label=self.arm_labels[arm],
                    color=self.colors[arm],
                    marker=self.markers[arm],
                )
        return self.figures_by_sid(fig)

    def _figure_pd(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig3_Fig4",
            num_rows=2,
            num_cols=2,
            name=f"{self.__class__.__name__}",
            settings={"legend_scope": "row"},
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        for kp, (yid, name) in enumerate(self.pd_data.items()):
            plots[kp].set_yaxis(self.labels[yid], unit=self.units[yid])
            for arm in self.arms:
                plots[kp].add_data(
                    task=f"task_po_{arm}",
                    xid="time",
                    yid=yid,
                    label=self.arm_labels[arm],
                    color=self.colors[arm],
                    linestyle="-" if arm == "ENA10" else "--",
                )
            for arm, (intervention, _) in self.arms.items():
                plots[kp].add_data(
                    dataset=self.to_sid(f"{intervention}_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=self.arm_labels[arm],
                    color=self.colors[arm],
                    marker=self.markers[arm],
                )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Ishizaki1988, output_dir=Ishizaki1988.__name__)
