"""Simulation experiment of the study Shionoiri1985."""

from typing import ClassVar, override

import pandas as pd
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


class Shionoiri1985(EnalaprilSimulationExperiment):
    """Simulation experiment of Shionoiri1985.

    Enalapril maleate 10 mg (capsule) in 13 inpatients with essential
    hypertension (WHO I-II, baseline 175.4/111.3 mmHg, PRA 2.2 ng/ml/hr, sodium
    diet 100 mEq/day, BW not reported). Serum enalapril and enalaprilat by the
    inhibition of ACE (Fig2), blood pressure and plasma renin activity (Fig3),
    serum ACE activity and plasma angiotensin II (Fig4), mean and SE. The PRA
    (an angiotensin I generation rate) and the angiotensin II are mapped
    relative to their value before the dose, the ACE activity relative to the
    activity before the dose.
    """

    #: the data which are divided by their value before the dose: the label of
    #: the data, the key of the dataset and the observable
    ratios: ClassVar[tuple[tuple[str, str, str], ...]] = (
        ("ENA10_renin activity", "ENA10_PRA_ratio", "ren_ratio"),
        ("ENA10_angiotensin II", "ENA10_angiotensin II_ratio", "ang2_ratio"),
    )
    #: the names of the simulated observables of Fig2 in the legends
    legends_pd: ClassVar[dict[str, str]] = {
        "SBP": "SBP",
        "DBP": "DBP",
        "MAP": "MAP",
        "ace_activity": "ACE activity",
        "ang2_ratio": "angiotensin II ratio",
        "ren_ratio": "PRA ratio",
    }

    @staticmethod
    def _ratio(df: pd.DataFrame) -> pd.DataFrame:
        """Divide the data by its mean at 0 hr.

        Args:
            df: the timecourse of one group.

        Returns:
            The timecourse relative to the value before the dose.
        """
        df = df.sort_values("time").copy()
        baseline = float(df["mean"].iloc[0])
        for col in ("mean", "mean_pm", "sd", "se"):
            df[col] = df[col] / baseline
        df["unit"] = "dimensionless"
        return df

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        ratios = {label: dset_id for label, dset_id, _ in self.ratios}
        for fig_id in ["Fig2", "Fig3", "Fig4"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                if label in ratios:
                    dsets[self.to_sid(ratios[label])] = DataSet.from_df(
                        self._ratio(df_label), self.ureg
                    )
                    continue
                if label.endswith(("_renin activity", "_angiotensin II")):
                    continue
                dset = DataSet.from_df(df_label, self.ureg)
                if label.endswith("_enalapril"):
                    dset.unit_conversion("mean", 1 / self.Mr.ena)
                elif label.endswith("_enalaprilat"):
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(f"{label}")] = dset

        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        simulations["po_enamal10"] = Simulation(
            time_unit="hr",
            end=25,
            preinit_changes={
                **self.default_changes(),
                "SBP_ref": Q(175.4, "mmHg"),
                "DBP_ref": Q(111.3, "mmHg"),
                "PODOSE_ena": Q(10, "mg")
                * self.Mr.ena
                / self.Mr.enamal,  # enalapril maleate
            },
        )

        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        info: dict[str, tuple[str, Tissue, PKPDData]] = {
            "[Cve_ena]": ("ENA10_enalapril", Tissue.PLASMA, PKPDData.PK),
            "[Cve_eat]": ("ENA10_enalaprilat", Tissue.PLASMA, PKPDData.PK),
            "SBP": ("ENA10_blood pressure systolic", Tissue.NONE, PKPDData.PD),
            "DBP": ("ENA10_blood pressure diastolic", Tissue.NONE, PKPDData.PD),
            "MAP": ("ENA10_MAP", Tissue.NONE, PKPDData.PD),
            "ace_activity": (
                "ENA10_relative ACE activity",
                Tissue.SERUM,
                PKPDData.PD,
            ),
            "ren_ratio": ("ENA10_PRA_ratio", Tissue.PLASMA, PKPDData.PD),
            "ang2_ratio": ("ENA10_angiotensin II_ratio", Tissue.PLASMA, PKPDData.PD),
        }

        mappings = {}
        for sid, (dset_id, tissue, data) in info.items():
            mappings[self.to_sid(f"fm_{dset_id}")] = FitMapping(
                self,
                reference=FitData(
                    self,
                    dataset=self.to_sid(dset_id),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                ),
                observable=FitData(
                    self,
                    task="task_po_enamal10",
                    xid="time",
                    yid=sid,
                ),
                metadata=PKPDMappingMetaData(
                    tissue=tissue,
                    route=Route.PO,
                    application_form=ApplicationForm.CAPSULE,
                    dosing=Dosing.SINGLE,
                    health=Health.HYPERTENSION,
                    genotype=Genotype.NR,
                    fasting=Fasting.NR,
                    data=data,
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
        plots[0].set_yaxis(self.labels["[Cve_ena]"], unit=self.units["[Cve_ena]"])
        plots[1].set_yaxis(self.labels["[Cve_eat]"], unit=self.units["[Cve_eat]"])

        # simulation
        for kp, (sid, name) in enumerate(
            [("ena", "enalapril"), ("eat", "enalaprilat")]
        ):
            plots[kp].add_data(
                task="task_po_enamal10",
                xid="time",
                yid=f"[Cve_{sid}]",
                label=f"Sim {name}",
                color="black",
            )

        # data
        for kp, name in enumerate(["enalapril", "enalaprilat"]):
            plots[kp].add_data(
                dataset=self.to_sid(f"ENA10_{name}"),
                xid="time",
                yid="mean",
                yid_sd="mean_sd",
                count="count",
                label=f"{name}",
                color="black",
            )

        return self.figures_by_sid(fig)

    def _figure_pd(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig2",
            num_rows=2,
            num_cols=3,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(self.labels["SBP"], unit=self.units["SBP"])
        plots[1].set_yaxis(self.labels["DBP"], unit=self.units["DBP"])
        plots[2].set_yaxis(self.labels["MAP"], unit=self.units["MAP"])
        plots[3].set_yaxis(self.labels["ace_activity"], unit=self.units["ace_activity"])
        plots[4].set_yaxis(self.labels["ang2_ratio"], unit=self.units["ang2_ratio"])
        plots[5].set_yaxis(self.labels["ren_ratio"], unit=self.units["ren_ratio"])

        # simulation
        for kp, (sid, legend) in enumerate(self.legends_pd.items()):
            plots[kp].add_data(
                task="task_po_enamal10",
                xid="time",
                yid=sid,
                label=legend,
                color="black",
            )
        # data
        for kp, name in enumerate(
            [
                "blood pressure systolic",
                "blood pressure diastolic",
                "MAP",
                "relative ACE activity",
                "angiotensin II_ratio",
                "PRA_ratio",
            ]
        ):
            plots[kp].add_data(
                dataset=self.to_sid(f"ENA10_{name}"),
                xid="time",
                yid="mean",
                yid_sd="mean_sd",
                count="count",
                label="enalapril maleate 10 mg",
                color="black",
            )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Shionoiri1985, output_dir=Shionoiri1985.__name__)
