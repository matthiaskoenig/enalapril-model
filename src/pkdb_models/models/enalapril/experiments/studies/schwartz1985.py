"""Simulation experiment of the study Schwartz1985."""

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

from pkdb_models.models.enalapril import MODEL
from pkdb_models.models.enalapril.experiments.base_experiment import (
    EnalaprilSimulationExperiment,
)


class Schwartz1985(EnalaprilSimulationExperiment):
    """Simulation experiment of Schwartz1985.

    Enalapril maleate (MK 421) in congestive heart failure (CHF) and in
    hypertension (HT); serum enalapril and enalaprilat by RIA.

    CHF: 8 patients (NYHA III in 6, IV in 2; BW 77.8 kg; on digoxin, diuretics
    and vasodilators), after an overnight fast 2.5 mg on day 1, 5 mg on day 2
    and 10 mg on day 3 (2 patients did not receive 10 mg), simulated as one
    sequence of doses every 24 hr. Fig1 is one patient (individual), Fig2 the
    group means of the 5 mg day (drug levels without SEM, MAP and heart rate
    with SEM). The cardiac function is the moderate cardiac impairment of
    NYHA III; the mean arterial pressure before the 5 mg dose (85 mmHg) sets
    the blood pressure references of the model.

    HT: 5 patients (BW 96.8 kg) on hydrochlorothiazide 50 mg per day, a placebo
    day before each dose, single doses of 40 mg (24 hr) and 20 mg (12 hr, the
    regimen is 20 mg twice daily, the data after the second dose at 12 hr are
    not used), 3 weeks apart. Fig3 and Fig6 are one representative patient
    each (individuals), Tab2 the MAP and heart rate, Tab3 the systolic and
    diastolic blood pressure (mean and SD), Tab4 the ACE activity, plasma
    renin activity and aldosterone at 0, 4, 12 and 24 hr (mean and SD). The
    supine blood pressure before the dose sets the references of the arm. PRA
    and aldosterone are mapped relative to their value before the dose (the
    absolute levels of the assays are not amounts of the model).

    The heart rate is not a state of the model, it is plotted, not mapped.
    """

    #: the doses of the CHF patients (mg enalapril maleate) and their time (hr)
    chf_doses: ClassVar[dict[str, tuple[float, float]]] = {
        "ENA2.5": (2.5, 0),
        "ENA5": (5, 24),
        "ENA10": (10, 48),
    }
    #: the arms of the HT patients and their dose (mg enalapril maleate)
    ht_doses: ClassVar[dict[str, float]] = {
        "placebo20": 0,
        "ENA20": 20,
        "placebo40": 0,
        "ENA40": 40,
    }
    #: the dose of the arm of a placebo day
    ht_arm: ClassVar[dict[str, str]] = {
        "placebo20": "ENA20",
        "ENA20": "ENA20",
        "placebo40": "ENA40",
        "ENA40": "ENA40",
    }
    #: the supine blood pressure before the dose (Tab3, mmHg)
    ht_sbp: ClassVar[dict[str, float]] = {"ENA20": 149, "ENA40": 138}
    ht_dbp: ClassVar[dict[str, float]] = {"ENA20": 99, "ENA40": 92}
    #: the end of the data of an arm (min): the second 20 mg dose at 12 hr
    ht_end: ClassVar[dict[str, float]] = {"ENA20": 720, "ENA40": 1440}

    #: the supine mean arterial pressure of the CHF patients before the 5 mg
    #: dose (Fig2, mmHg)
    chf_map: ClassVar[float] = 85.24

    positions: ClassVar[list[str]] = ["supine", "standing"]
    position_markers: ClassVar[dict[str, str]] = {"standing": "^", "supine": "o"}

    bodyweights: ClassVar[dict[str, float]] = {
        "CHF": 77.80,
        "HT": 96.80,
    }
    #: NYHA III in 6 of 8 patients
    chf_cardiac_function: ClassVar[float] = EnalaprilSimulationExperiment.cardiac_map[
        "Moderate cardiac impairment"
    ]

    colors: ClassVar[dict[str, str]] = {
        # CHF: shades of the cardiac red by dose
        "ENA2.5": EnalaprilSimulationExperiment.cardiac_ramp[0],
        "ENA5": EnalaprilSimulationExperiment.cardiac_ramp[1],
        "ENA10": EnalaprilSimulationExperiment.cardiac_ramp[2],
        # HT: placebo days grey, dose in yellow shades
        "placebo20": EnalaprilSimulationExperiment.grey_shades[2],
        "placebo40": EnalaprilSimulationExperiment.grey_shades[1],
        **EnalaprilSimulationExperiment.dose_colors(["ENA20", "ENA40"]),
    }

    #: the individual patients of the HT group: figure and doses
    ht_individuals: ClassVar[dict[str, list[str]]] = {
        "Fig3": ["ENA20", "ENA40"],
        "Fig6": ["ENA40"],
    }
    individual_markers: ClassVar[dict[str, str]] = {"Fig3": "o", "Fig6": "D"}

    #: the data of Tab4 divided by their value before the dose: the name of the
    #: data, the name of the dataset and the observable
    ratios: ClassVar[dict[str, tuple[str, str]]] = {
        "renin activity": ("PRA_ratio", "ren_ratio"),
        "aldosterone": ("aldosterone_ratio", "ald_ratio"),
    }

    @staticmethod
    def _ratio(df: pd.DataFrame) -> pd.DataFrame:
        """Divide the data of an arm by its mean at 0 hr.

        Args:
            df: the timecourse of one arm.

        Returns:
            The timecourse relative to the value before the dose.
        """
        df = df.sort_values("time").copy()
        baseline = float(df["mean"].iloc[0])
        for col in ("mean", "mean_pm", "sd", "se"):
            df[col] = df[col] / baseline
        df["unit"] = "dimensionless"
        return df

    def _dataset(self, df: pd.DataFrame, label: str) -> DataSet:
        """Create a dataset, the concentrations of the drugs as amounts.

        Args:
            df: the data.
            label: the label of the data.

        Returns:
            The dataset.
        """
        dset = DataSet.from_df(df, self.ureg)
        if label.endswith(("_enalapril", "_enalaprilat")):
            mr = self.Mr.ena if label.endswith("_enalapril") else self.Mr.eat
            for col in ("mean", "value"):
                if col in dset.columns:
                    dset.unit_conversion(col, 1 / mr)
        return dset

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}

        # CHF: the individual patient (Fig1) and the group (Fig2), the data of
        # a day after its dose
        for fig_id in ["Fig1", "Fig2"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                df_label = df_label.copy()
                dose_time = self.chf_doses[label.split("_")[1]][1]
                df_label["time"] = df_label["time"] + 60 * dose_time
                drug = label.endswith(("_enalapril", "_enalaprilat"))
                key = f"{label}_mean" if fig_id == "Fig2" and drug else label
                dsets[self.to_sid(key)] = self._dataset(df_label, label)

        # HT: the individual patients
        for fig_id in self.ht_individuals:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                if label.endswith(("_enalapril", "_enalaprilat")):
                    dsets[self.to_sid(f"{fig_id}_{label}")] = self._dataset(
                        df_label, label
                    )

        # HT: blood pressure, heart rate, ACE activity, PRA, aldosterone
        for fig_id in ["Tab2", "Tab3", "Tab4"]:
            df = self.load_dataframe(fig_id)
            df = df[df["time"] >= 0]
            for label, df_label in df.groupby("label"):
                label = str(label)
                arm, name = label.split("_", 2)[1:]
                if name == "ACE activity":
                    continue  # the relative ACE activity is mapped
                minutes = df_label["time"] * df_label["time_unit"].map(
                    {"min": 1, "hr": 60}
                )
                df_label = df_label[minutes <= self.ht_end[self.ht_arm[arm]]]
                if name in self.ratios:
                    key = f"HT_{arm}_{self.ratios[name][0]}"
                    dsets[self.to_sid(key)] = DataSet.from_df(
                        self._ratio(df_label), self.ureg
                    )
                    continue
                # the "blood pressure" of Tab2 is the mean arterial pressure
                label = label.replace("_blood pressure_", "_MAP_")
                dsets[self.to_sid(label)] = DataSet.from_df(df_label, self.ureg)

        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        # CHF: 2.5, 5 and 10 mg on consecutive days; SBP and DBP were not
        # reported, the references are scaled to the mean arterial pressure
        f_map = self.chf_map / (80 + (120 - 80) / 3)
        doses = list(self.chf_doses.values())
        simulations["po_ENA_CHF"] = Simulation(
            time_unit="hr",
            end=74,
            preinit_changes={
                **self.default_changes(),
                "BW": Q(self.bodyweights["CHF"], "kg"),
                "f_cardiac_function": Q(self.chf_cardiac_function, "dimensionless"),
                "SBP_ref": Q(120 * f_map, "mmHg"),
                "DBP_ref": Q(80 * f_map, "mmHg"),
                "PODOSE_ena": Q(doses[0][0], "mg")
                * self.Mr.ena
                / self.Mr.enamal,  # enalapril maleate
            },
            changes=[
                self.add_doses(
                    [time],
                    {"PODOSE_ena": Q(dose, "mg") * self.Mr.ena / self.Mr.enamal},
                )
                for dose, time in doses[1:]
            ],
        )
        # HT: placebo days and single doses, on hydrochlorothiazide
        for arm, dose in self.ht_doses.items():
            ref_arm = self.ht_arm[arm]
            simulations[self.to_sid(f"po_{arm}_HT")] = Simulation(
                time_unit="hr",
                end=26,
                preinit_changes={
                    **self.default_changes(),
                    "BW": Q(self.bodyweights["HT"], "kg"),
                    "SBP_ref": Q(self.ht_sbp[ref_arm], "mmHg"),
                    "DBP_ref": Q(self.ht_dbp[ref_arm], "mmHg"),
                    **self.interaction_changes(Coadministration.HCTZ),
                    "PODOSE_ena": Q(dose, "mg")
                    * self.Mr.ena
                    / self.Mr.enamal,  # enalapril maleate
                },
            )

        return simulations

    @staticmethod
    def _metadata_chf(
        tissue: Tissue, dosing: Dosing, data: PKPDData, data_type: DataType
    ) -> PKPDMappingMetaData:
        """Get the metadata of a mapping of the CHF patients.

        Args:
            tissue: the tissue of the data.
            dosing: single (day 1) or multiple (day 2 and 3) doses.
            data: pharmacokinetics or pharmacodynamics.
            data_type: the type of the data.

        Returns:
            The metadata.
        """
        return PKPDMappingMetaData(
            tissue=tissue,
            route=Route.PO,
            application_form=ApplicationForm.NR,
            dosing=dosing,
            health=Health.HEART_FAILURE,
            genotype=Genotype.NR,
            fasting=Fasting.FASTED,
            coadministration=Coadministration.COMEDICATION,
            data=data,
            data_type=data_type,
        )

    @staticmethod
    def _metadata_ht(
        tissue: Tissue, data: PKPDData, data_type: DataType
    ) -> PKPDMappingMetaData:
        """Get the metadata of a mapping of the HT patients.

        Args:
            tissue: the tissue of the data.
            data: pharmacokinetics or pharmacodynamics.
            data_type: the type of the data.

        Returns:
            The metadata.
        """
        return PKPDMappingMetaData(
            tissue=tissue,
            route=Route.PO,
            application_form=ApplicationForm.NR,
            dosing=Dosing.SINGLE,
            health=Health.HYPERTENSION,
            genotype=Genotype.NR,
            fasting=Fasting.NR,
            coadministration=Coadministration.HCTZ,
            data=data,
            data_type=data_type,
        )

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        analytes = [("[Cve_ena]", "enalapril"), ("[Cve_eat]", "enalaprilat")]

        # --- CHF: the individual patient on three days (Fig1) ---
        for dose_key in self.chf_doses:
            for sid, name in analytes:
                mappings[self.to_sid(f"fm_{dose_key}_CHF_{name}")] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(f"CHF_{dose_key}_{name}"),
                        xid="time",
                        yid="value",
                        yid_sd=None,
                        count="count",
                    ),
                    observable=FitData(
                        self, task="task_po_ENA_CHF", xid="time", yid=sid
                    ),
                    metadata=self._metadata_chf(
                        Tissue.SERUM,
                        Dosing.SINGLE if dose_key == "ENA2.5" else Dosing.MULTIPLE,
                        PKPDData.PK,
                        DataType.INDIVIDUAL,
                    ),
                )

        # --- CHF: the group on the 5 mg day (Fig2) ---
        for sid, name in analytes:
            mappings[self.to_sid(f"fm_ENA5_CHF_{name}_mean")] = FitMapping(
                self,
                reference=FitData(
                    self,
                    dataset=self.to_sid(f"CHF_ENA5_{name}_mean"),
                    xid="time",
                    yid="mean",
                    # the drug levels are means without SEM
                    yid_sd=None,
                    count="count",
                ),
                observable=FitData(self, task="task_po_ENA_CHF", xid="time", yid=sid),
                metadata=self._metadata_chf(
                    Tissue.SERUM, Dosing.MULTIPLE, PKPDData.PK, DataType.MEAN
                ),
            )
        mappings["fm_ENA5_CHF_MAP_supine"] = FitMapping(
            self,
            reference=FitData(
                self,
                dataset="CHF_ENA5_MAP_supine",
                xid="time",
                yid="mean",
                yid_sd="mean_sd",
                count="count",
            ),
            observable=FitData(self, task="task_po_ENA_CHF", xid="time", yid="MAP"),
            metadata=self._metadata_chf(
                Tissue.NONE, Dosing.MULTIPLE, PKPDData.PD, DataType.MEAN
            ),
        )

        # --- HT: the individual patients (Fig3, Fig6) ---
        for fig_id, dose_keys in self.ht_individuals.items():
            for dose_key in dose_keys:
                for sid, name in analytes:
                    key = self.to_sid(f"fm_{fig_id}_{dose_key}_HT_{name}")
                    mappings[key] = FitMapping(
                        self,
                        reference=FitData(
                            self,
                            dataset=self.to_sid(f"{fig_id}_HT_{dose_key}_{name}"),
                            xid="time",
                            yid="mean",
                            yid_sd=None,
                            count="count",
                        ),
                        observable=FitData(
                            self,
                            task=self.to_sid(f"task_po_{dose_key}_HT"),
                            xid="time",
                            yid=sid,
                        ),
                        metadata=self._metadata_ht(
                            Tissue.SERUM, PKPDData.PK, DataType.INDIVIDUAL
                        ),
                    )

        # --- HT: the supine blood pressure (Tab2 MAP, Tab3 SBP and DBP), the
        # relative ACE activity, PRA and aldosterone (Tab4) ---
        pd_data: list[tuple[str, str, str, Tissue]] = []
        for arm in self.ht_doses:
            pd_data.append((arm, "MAP", "MAP_supine", Tissue.NONE))
            if arm.startswith("ENA"):
                pd_data += [
                    (arm, "SBP", "blood pressure systolic_supine", Tissue.NONE),
                    (arm, "DBP", "blood pressure diastolic_supine", Tissue.NONE),
                ]
            pd_data.append(
                (arm, "ace_activity", "relative ACE activity", Tissue.PLASMA)
            )
            pd_data += [
                (arm, sid, name, Tissue.PLASMA) for name, sid in self.ratios.values()
            ]

        for arm, sid, name, tissue in pd_data:
            mappings[self.to_sid(f"fm_{arm}_HT_{name}")] = FitMapping(
                self,
                reference=FitData(
                    self,
                    dataset=self.to_sid(f"HT_{arm}_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                ),
                observable=FitData(
                    self,
                    task=self.to_sid(f"task_po_{arm}_HT"),
                    xid="time",
                    yid=sid,
                ),
                metadata=self._metadata_ht(tissue, PKPDData.PD, DataType.MEAN),
            )

        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        return {
            **self._figure_chf(),
            **self._figure_ht_pk(),
            **self._figure_ht_pd(),
        }

    def _figure_chf(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig1_CHF",
            num_rows=2,
            num_cols=2,
            name=f"{self.__class__.__name__} (CHF)",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        sids = ["[Cve_ena]", "[Cve_eat]", "MAP", "HR"]
        for kp, sid in enumerate(sids):
            plots[kp].set_yaxis(self.labels[sid], unit=self.units[sid])
            plots[kp].add_data(
                task="task_po_ENA_CHF",
                xid="time",
                yid=sid,
                label="2.5, 5, 10 mg",
                color=self.colors["ENA5"],
            )

        # data: the individual patient (Fig1) and the group (Fig2)
        for kp, name in enumerate(["enalapril", "enalaprilat"]):
            for dose_key in self.chf_doses:
                plots[kp].add_data(
                    dataset=self.to_sid(f"CHF_{dose_key}_{name}"),
                    xid="time",
                    yid="value",
                    yid_sd=None,
                    count="count",
                    label=f"{dose_key} (patient)",
                    color=self.colors[dose_key],
                )
            plots[kp].add_data(
                dataset=self.to_sid(f"CHF_ENA5_{name}_mean"),
                xid="time",
                yid="mean",
                yid_sd=None,
                count="count",
                label="ENA5 (mean)",
                color=self.colors["ENA5"],
                marker="s",
            )
        # data: MAP and heart rate of the 5 mg day (Fig2)
        for kp, name in enumerate(["MAP", "heart rate"]):
            for position in self.positions:
                plots[kp + 2].add_data(
                    dataset=self.to_sid(f"CHF_ENA5_{name}_{position}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=f"ENA5 ({position})",
                    color=self.colors["ENA5"],
                    marker=self.position_markers[position],
                )

        return self.figures_by_sid(fig)

    def _figure_ht_pk(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig1_HT",
            num_rows=2,
            num_cols=1,
            name=f"{self.__class__.__name__} (HT)",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(self.labels["[Cve_ena]"], unit=self.units["[Cve_ena]"])
        plots[1].set_yaxis(self.labels["[Cve_eat]"], unit=self.units["[Cve_eat]"])

        for dose_key in ["ENA20", "ENA40"]:
            for kp, sid in enumerate(["[Cve_ena]", "[Cve_eat]"]):
                plots[kp].add_data(
                    task=self.to_sid(f"task_po_{dose_key}_HT"),
                    xid="time",
                    yid=sid,
                    label=dose_key,
                    color=self.colors[dose_key],
                )
        for fig_id, dose_keys in self.ht_individuals.items():
            for dose_key in dose_keys:
                for kp, name in enumerate(["enalapril", "enalaprilat"]):
                    plots[kp].add_data(
                        dataset=self.to_sid(f"{fig_id}_HT_{dose_key}_{name}"),
                        xid="time",
                        yid="mean",
                        yid_sd=None,
                        count="count",
                        label=f"{dose_key} (patient {fig_id})",
                        color=self.colors[dose_key],
                        marker=self.individual_markers[fig_id],
                    )

        return self.figures_by_sid(fig)

    def _figure_ht_pd(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig2_HT",
            num_rows=4,
            num_cols=2,
            name=f"{self.__class__.__name__} (HT, PD)",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        sids = ["SBP", "DBP", "MAP", "HR", "ace_activity", "ren_ratio", "ald_ratio"]
        for kp, sid in enumerate(sids):
            plots[kp].set_yaxis(self.labels[sid], unit=self.units[sid])
        plots[7].xaxis = None
        for arm in self.ht_doses:
            for kp, sid in enumerate(sids):
                plots[kp].add_data(
                    task=self.to_sid(f"task_po_{arm}_HT"),
                    xid="time",
                    yid=sid,
                    label=arm,
                    color=self.colors[arm],
                )

        # data: SBP, DBP (Tab3), MAP and heart rate (Tab2), supine and standing
        names = [
            "blood pressure systolic",
            "blood pressure diastolic",
            "MAP",
            "heart rate",
        ]
        for kp, name in enumerate(names):
            for arm in self.ht_doses:
                if kp < 2 and not arm.startswith("ENA"):
                    continue  # no SBP and DBP of the placebo days
                for position in self.positions:
                    plots[kp].add_data(
                        dataset=self.to_sid(f"HT_{arm}_{name}_{position}"),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                        label=f"{arm} ({position})",
                        color=self.colors[arm],
                        marker=self.position_markers[position],
                    )

        # data: relative ACE activity, PRA and aldosterone (Tab4)
        for kp, name in enumerate(
            ["relative ACE activity", "PRA_ratio", "aldosterone_ratio"]
        ):
            for arm in self.ht_doses:
                plots[kp + 4].add_data(
                    dataset=self.to_sid(f"HT_{arm}_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=arm,
                    color=self.colors[arm],
                )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Schwartz1985, output_dir=Schwartz1985.__name__)
