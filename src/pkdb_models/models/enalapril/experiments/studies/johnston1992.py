"""Simulation experiment of the study Johnston1992."""

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
from sbmlsim.simulation import Change, Simulation
from sbmlsim.units import Quantity

from pkdb_models.models.enalapril import MODEL
from pkdb_models.models.enalapril.experiments.base_experiment import (
    EnalaprilSimulationExperiment,
)


class Johnston1992(EnalaprilSimulationExperiment):
    """Simulation experiment of Johnston1992 in congestive heart failure.

    7 patients with congestive heart failure (NYHA III-IV, 69 yr, BW 73.7 kg,
    background therapy diuretics and/or digoxin), 2.5 mg enalapril (maleate)
    once daily on day 1 and days 3-8 (no dose on day 2): 7 doses at 0, 48,
    72, 96, 120, 144 and 168 hr. Serum enalapril (Fig2) and enalaprilat
    (Fig3, RIA) after the first (`ENAs`) and the last dose (`ENAm`), the
    urinary recovery (percent of the dose, Tab2, mean ± SE) over 48 hr after
    the first and the last dose. The data of the last dose are after 168 hr
    in the data copy (curated after 144 hr).

    The heart failure is the severe cardiac impairment of the cardiac map
    (NYHA III-IV), the creatinine clearance is not reported; the renal
    clearance of enalaprilat (33 ml/min after the first dose) is a fifth of
    the one of healthy subjects, the model with the cardiac output alone
    excretes more. The enalapril of Fig2 (5 points 10-50 hr after the dose,
    an AUC about 10 times the 86.9 ng*hr/ml of Table I) is not usable.
    """

    doses: ClassVar[list[str]] = ["ENAs", "ENAm"]
    markers: ClassVar[dict[str, str]] = {
        "ENAs": "o",
        "ENAm": "^",
    }
    dose_labels: ClassVar[dict[str, str]] = {
        "ENAs": "single dose",
        "ENAm": "multiple dose",
    }
    # CHF: shades of the cardiac red, single < multiple dose
    colors: ClassVar[dict[str, str]] = {
        "ENAs": EnalaprilSimulationExperiment.cardiac_ramp[1],
        "ENAm": EnalaprilSimulationExperiment.cardiac_ramp[2],
    }
    #: the dose of enalapril maleate as an amount, the recovery is a fraction of it
    dose_amount: ClassVar[Quantity] = (
        Q(2.5, "mg") / EnalaprilSimulationExperiment.Mr.enamal
    )
    #: the data by the observable
    info: ClassVar[dict[str, str]] = {
        "[Cve_ena]": "enalapril",
        "[Cve_eat]": "enalaprilat",
        "Aurine_ena": "recovery_enalapril",
        "Aurine_eat": "recovery_enalaprilat",
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig2", "Fig3", "Tab2"]:
            df = self.load_dataframe(fig_id)
            # the lisinopril arm, the renal clearances and the cumulative
            # amounts of the curation (percent x mg of the maleate) are not used
            df = df[
                df["label"].str.startswith("ENA")
                & df["measurement_type"].isin(["concentration", "recovery"])
            ]
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

        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        changes = {
            **self.default_changes(),
            "f_cardiac_function": Q(
                self.cardiac_map["Severe cardiac impairment"], "dimensionless"
            ),
            "BW": Q(73.7, "kg"),
            # enalapril maleate
            "PODOSE_ena": Q(2.5, "mg") * self.Mr.ena / self.Mr.enamal,
        }
        dose = {"PODOSE_ena": changes["PODOSE_ena"]}
        return {
            # the first dose, the next dose is at 48 hr
            "po_ENAs": Simulation(time_unit="hr", end=49, preinit_changes=changes),
            # multiple dosing: a dose at 0 hr and every 24 hr from 48 hr to
            # 168 hr, the urine is collected over 48 hr after the last dose
            "po_ENAm": Simulation(
                time_unit="hr",
                end=217,
                preinit_changes=changes,
                changes=[
                    self.add_doses([48, 72, 96, 120, 144, 168], dose),
                    Change(
                        [168],
                        {
                            "Aurine_ena": Q(0, "mmole"),
                            "Aurine_eat": Q(0, "mmole"),
                        },
                    ),
                ],
            ),
        }

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for sid, name in self.info.items():
            for dose in self.doses:
                mappings[self.to_sid(f"fm_johnston1992_po_{dose}_{name}")] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(f"{dose}_{name}"),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd" if "Aurine" in sid else None,
                        count="count",
                    ),
                    observable=FitData(
                        self,
                        task=self.to_sid(f"task_po_{dose}"),
                        xid="time",
                        yid=sid,
                    ),
                    metadata=PKPDMappingMetaData(
                        tissue=Tissue.SERUM if "Cve" in sid else Tissue.URINE,
                        route=Route.PO,
                        application_form=ApplicationForm.NR,
                        dosing=Dosing.SINGLE if dose == "ENAs" else Dosing.MULTIPLE,
                        health=Health.HEART_FAILURE,
                        genotype=Genotype.NR,
                        fasting=Fasting.NR,
                        data=PKPDData.PK,
                        data_type=DataType.MEAN,
                    ),
                )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig2_Fig3_Tab2",
            num_rows=2,
            num_cols=2,
            name=f"{self.__class__.__name__}",
            # the legends inside the panels cover data: one legend per row,
            # right of the grid (the panels show the same simulation and doses)
            settings={"legend_scope": "row"},
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        for kp, (sid, name) in enumerate(self.info.items()):
            plots[kp].set_yaxis(self.labels[sid], unit=self.units[sid])
            # the multiple dose first, the single dose (dashed) on top of it
            for dose in reversed(self.doses):
                plots[kp].add_data(
                    task=f"task_po_{dose}",
                    xid="time",
                    yid=sid,
                    label=f"{self.dose_labels[dose]} (CHF)",
                    color=self.colors[dose],
                    linestyle="--" if dose == "ENAs" else "-",
                )
            for dose in self.doses:
                plots[kp].add_data(
                    dataset=self.to_sid(f"{dose}_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd" if "Aurine" in sid else None,
                    count="count",
                    label=f"{self.dose_labels[dose]} (CHF)",
                    color=self.colors[dose],
                    marker=self.markers[dose],
                )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Johnston1992, output_dir=Johnston1992.__name__)
