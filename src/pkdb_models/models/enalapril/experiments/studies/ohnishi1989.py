"""Simulation experiment of the study Ohnishi1989."""

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
from sbmlsim.units import Quantity

from pkdb_models.models.enalapril import MODEL
from pkdb_models.models.enalapril.experiments.base_experiment import (
    EnalaprilSimulationExperiment,
)


class Ohnishi1989(EnalaprilSimulationExperiment):
    """Simulation experiment of Ohnishi1989 in liver cirrhosis.

    Enalapril maleate 10 mg p.o. after an overnight fast in 7 healthy male
    volunteers (CLcr 103-126 ml/min, BW not reported) and 7 normotensive
    patients with biopsy-proven cirrhosis (BW 58 kg, CLcr 72 ml/min; bilirubin
    2.1 mg/dl, albumin 3.2 g/dl, prothrombin 67 %, ICG R15 37 %, ascites in 2:
    Child-Pugh B). Serum enalapril and enalaprilat by RIA (Fig1; the enalapril
    is the total drug after hydrolysis minus the enalaprilat, both in
    enalaprilat equivalents), the cumulative urinary recovery in percent of
    the administered enalaprilat equivalents (Fig2, the 24 hr values from
    Tab2), blood pressure and heart rate (Fig3), all mean and SE. The heart
    rate is not a state of the model (only plotted).
    """

    groups: ClassVar[list[str]] = ["healthy", "cirrhosis"]
    colors: ClassVar[dict[str, str]] = {
        "healthy": EnalaprilSimulationExperiment.cirrhosis_colors["Control"],
        "cirrhosis": EnalaprilSimulationExperiment.cirrhosis_colors[
            "Moderate cirrhosis"
        ],
    }
    cirrhosis: ClassVar[dict[str, float]] = {
        "healthy": EnalaprilSimulationExperiment.cirrhosis_map["Control"],
        "cirrhosis": EnalaprilSimulationExperiment.cirrhosis_map["Moderate cirrhosis"],
    }
    #: the creatinine clearance over the GFR of the model (101 ml/min); the
    #: healthy volunteers (103-126 ml/min) have a normal renal function
    renal_functions: ClassVar[dict[str, float]] = {
        "healthy": 1.0,
        "cirrhosis": 72 / 101,
    }
    #: the body weight of the cirrhosis group, not reported for the volunteers
    bodyweights: ClassVar[dict[str, float]] = {"cirrhosis": 58}
    health: ClassVar[dict[str, Health]] = {
        "healthy": Health.HEALTHY,
        "cirrhosis": Health.CIRRHOSIS,
    }
    SBP_refs: ClassVar[dict[str, float]] = {
        "healthy": 119.62,
        "cirrhosis": 123.44,
    }
    DBP_refs: ClassVar[dict[str, float]] = {
        "healthy": 75.13,
        "cirrhosis": 77.26,
    }

    #: the dose of enalapril maleate as an amount, the recovery is a fraction of it
    dose_amount: ClassVar[Quantity] = (
        Q(10, "mg") / EnalaprilSimulationExperiment.Mr.enamal
    )

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1", "Fig2", "Fig3"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                if "_cumulative amount_" in label:
                    # the recovery times the dose in mg of the maleate, not the
                    # amounts of the analytes
                    continue
                dset = DataSet.from_df(df_label, self.ureg)
                if "_recovery_" in label:
                    # the fraction of the dose excreted in the urine (molar)
                    dset.unit_conversion("mean", self.dose_amount)
                elif label.startswith(("enalapril_", "enalaprilat_")):
                    # the RIA measures enalaprilat equivalents
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(f"{label}")] = dset

        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        for group in self.groups:
            simulations[self.to_sid(f"po_ENA10_{group}")] = Simulation(
                time_unit="hr",
                end=25,
                preinit_changes={
                    **self.default_changes(),
                    "SBP_ref": Q(self.SBP_refs[group], "mmHg"),
                    "DBP_ref": Q(self.DBP_refs[group], "mmHg"),
                    "f_cirrhosis": Q(self.cirrhosis[group], "dimensionless"),
                    "KI__f_renal_function": Q(
                        self.renal_functions[group], "dimensionless"
                    ),
                    **(
                        {"BW": Q(self.bodyweights[group], "kg")}
                        if group in self.bodyweights
                        else {}
                    ),
                    "PODOSE_ena": Q(10, "mg")
                    * self.Mr.ena
                    / self.Mr.enamal,  # enalapril maleate
                },
            )

        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        info_pk = {
            "[Cve_ena]": "enalapril",
            "[Cve_eat]": "enalaprilat",
            "Aurine_ena": "enalapril",
            "Aurine_eat": "enalaprilat",
            "Aurine_ena_eat": "enalapril+enalaprilat",
        }
        info_pd = {
            "SBP": "blood pressure systolic",
            "DBP": "blood pressure diastolic",
        }

        mappings = {}
        for group in self.groups:
            for sid, name in info_pk.items():
                urine = sid.startswith("Aurine")
                key = (
                    f"fm_{name}_recovery_{group}"
                    if urine
                    else f"fm_ENA10_{name}_{group}"
                )
                dataset = f"{name}_recovery_{group}" if urine else f"{name}_{group}"
                mappings[self.to_sid(key)] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(dataset),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                    ),
                    observable=FitData(
                        self,
                        task=self.to_sid(f"task_po_ENA10_{group}"),
                        xid="time",
                        yid=sid,
                    ),
                    metadata=PKPDMappingMetaData(
                        tissue=Tissue.URINE if urine else Tissue.SERUM,
                        route=Route.PO,
                        application_form=ApplicationForm.TABLET,
                        dosing=Dosing.SINGLE,
                        health=self.health[group],
                        genotype=Genotype.NR,
                        fasting=Fasting.FASTED,
                        data=PKPDData.PK,
                    ),
                )

            for sid, name in info_pd.items():
                mappings[self.to_sid(f"fm_ena10_{name}_{group}")] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(f"{group}_{name}"),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                    ),
                    observable=FitData(
                        self,
                        task=self.to_sid(f"task_po_ENA10_{group}"),
                        xid="time",
                        yid=sid,
                    ),
                    metadata=PKPDMappingMetaData(
                        tissue=Tissue.NONE,
                        route=Route.PO,
                        application_form=ApplicationForm.TABLET,
                        dosing=Dosing.SINGLE,
                        health=self.health[group],
                        genotype=Genotype.NR,
                        fasting=Fasting.FASTED,
                        data=PKPDData.PD,
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
            num_rows=3,
            num_cols=2,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(legend=True)
        for k in range(6):
            if k != 4:
                plots[k].set_xaxis(self.labels["time"], unit=self.units["time"])
        plots[0].set_yaxis(self.labels["[Cve_ena]"], unit=self.units["[Cve_ena]"])
        plots[1].set_yaxis(self.labels["Aurine_ena"], unit=self.units["Aurine_ena"])
        plots[2].set_yaxis(self.labels["[Cve_eat]"], unit=self.units["[Cve_eat]"])
        plots[3].set_yaxis(self.labels["Aurine_eat"], unit=self.units["Aurine_eat"])
        plots[5].set_yaxis(
            self.labels["Aurine_ena_eat"], unit=self.units["Aurine_ena_eat"]
        )

        for group in self.groups:
            # simulation
            for krow, sid in enumerate(["ena", "eat"]):
                for kcol, yid in enumerate([f"[Cve_{sid}]", f"Aurine_{sid}"]):
                    kp = krow * 2 + kcol
                    plots[kp].add_data(
                        task=self.to_sid(f"task_po_ENA10_{group}"),
                        xid="time",
                        yid=yid,
                        label=group,
                        color=self.colors[group],
                    )

            plots[5].add_data(
                task=self.to_sid(f"task_po_ENA10_{group}"),
                xid="time",
                yid="Aurine_ena_eat",
                label=group,
                color=self.colors[group],
            )

            # data
            for kr, name in enumerate(["enalapril", "enalaprilat"]):
                plots[kr * 2].add_data(
                    dataset=self.to_sid(f"{name}_{group}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=f"{name} ({group})",
                    color=self.colors[group],
                )
                plots[kr * 2 + 1].add_data(
                    dataset=self.to_sid(f"{name}_recovery_{group}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=f"{name} ({group})",
                    color=self.colors[group],
                )

            plots[5].add_data(
                dataset=self.to_sid(f"enalapril+enalaprilat_recovery_{group}"),
                xid="time",
                yid="mean",
                yid_sd="mean_sd",
                count="count",
                label=f"enalapril+enalaprilat ({group})",
                color=self.colors[group],
            )

        return self.figures_by_sid(fig)

    def _figure_pd(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig2",
            num_rows=3,
            num_cols=1,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(self.labels["SBP"], unit=self.units["SBP"])
        plots[1].set_yaxis(self.labels["DBP"], unit=self.units["DBP"])
        plots[2].set_yaxis(self.labels["HR"], unit=self.units["HR"])

        for group in self.groups:
            # simulation
            for kp, sid in enumerate(["SBP", "DBP", "HR"]):
                plots[kp].add_data(
                    task=self.to_sid(f"task_po_ENA10_{group}"),
                    xid="time",
                    yid=sid,
                    label=group,
                    color=self.colors[group],
                )
            # data
            for kp, name in enumerate(
                ["blood pressure systolic", "blood pressure diastolic", "heart rate"]
            ):
                plots[kp].add_data(
                    dataset=self.to_sid(f"{group}_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=f"{group} ({name})",
                    color=self.colors[group],
                )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Ohnishi1989, output_dir=Ohnishi1989.__name__)
