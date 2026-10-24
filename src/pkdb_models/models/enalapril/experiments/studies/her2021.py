"""Simulation experiment of the study Her2021."""

from typing import ClassVar, override

import pandas as pd
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

from pkdb_models.models.enalapril import MODEL
from pkdb_models.models.enalapril.experiments.base_experiment import (
    EnalaprilSimulationExperiment,
)


class Her2021(EnalaprilSimulationExperiment):
    """Simulation experiment of Her2021.

    21 healthy Caucasian volunteers, 15 non-carriers (control) and 6
    heterozygous carriers of CES1 G143E: 10 mg enalapril maleate (tablet) once
    daily for 7 days (doses at 0-144 hr), fasting 1 hr before and after every
    dose and overnight before the PK study of the 7th dose (plasma for 72 hr,
    Fig3). The body weight is not reported (inclusion >= 50 kg); it is the BMI
    (23.0 and 25.1 kg/m^2) at a height of 1.75 m. The creatinine clearance of
    Cockcroft-Gault (122.7 and 111.6 ml/min) is an estimate of young healthy
    subjects, the renal function is normal.

    The systolic blood pressure (Fig6) is the baseline (day 1, the reference
    of the group) and the lowest value of day 7 (the "average maximum
    reduction" of the paper), which the copy has at 168 hr; it is mapped at the
    time of the enalaprilat Cmax after the 7th dose (147 hr). Enalapril below
    the limit of quantification (0 in Fig3) is not used.
    """

    groups: ClassVar[list[str]] = ["control", "G143E"]
    #: the baseline of the systolic blood pressure [mmHg] (Fig6)
    SBP_refs: ClassVar[dict[str, float]] = {
        "control": 118.012,
        "G143E": 116.096,
    }
    #: the body weight [kg]: BMI 23.0 and 25.1 kg/m^2 at a height of 1.75 m
    body_weights: ClassVar[dict[str, float]] = {
        "control": 23.0 * 1.75**2,
        "G143E": 25.1 * 1.75**2,
    }
    #: the time of the lowest blood pressure on day 7, the enalaprilat Cmax [hr]
    t_sbp_min: ClassVar[float] = 147.0

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig3", "Fig6"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                if label.endswith("_enalapril"):
                    # below the limit of quantification
                    df_label = df_label[df_label["mean"] > 0]
                elif label.endswith("_blood pressure systolic"):
                    df_label = df_label.copy()
                    df_label["time"] = df_label["time"].where(
                        df_label["time"] == 0, self.t_sbp_min
                    )
                dset = DataSet.from_df(pd.DataFrame(df_label), self.ureg)
                if label.endswith("_enalapril"):
                    dset.unit_conversion("mean", 1 / self.Mr.ena)
                elif label.endswith("_enalaprilat"):
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(label)] = dset
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        dose = Q(10, "mg") * self.Mr.ena / self.Mr.enamal  # enalapril maleate
        for group in self.groups:
            # once daily for 7 days, doses at 0, 24, ..., 144 hr
            simulations[self.to_sid(f"po_ENA10m{group}")] = Simulation(
                time_unit="hr",
                end=216,
                preinit_changes={
                    **self.default_changes(),
                    "BW": Q(self.body_weights[group], "kg"),
                    # CES1 activity
                    "LI__f_ces1": Q(self.ces1_map[group], "dimensionless"),
                    "SBP_ref": Q(self.SBP_refs[group], "mmHg"),
                    "PODOSE_ena": dose,
                },
                changes=[
                    self.add_doses([24 * k for k in range(1, 7)], {"PODOSE_ena": dose})
                ],
            )
        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        info = {
            "[Cve_ena]": "enalapril",
            "[Cve_eat]": "enalaprilat",
            "SBP": "blood pressure systolic",
        }

        mappings = {}
        for group in self.groups:
            for sid, name in info.items():
                pk = sid != "SBP"
                mappings[self.to_sid(f"fm_po_ENA10m_{group}_{name}")] = FitMapping(
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
                        task=self.to_sid(f"task_po_ENA10m{group}"),
                        xid="time",
                        yid=sid,
                    ),
                    metadata=PKPDMappingMetaData(
                        tissue=Tissue.PLASMA if pk else Tissue.NONE,
                        route=Route.PO,
                        application_form=ApplicationForm.TABLET,
                        dosing=Dosing.MULTIPLE,
                        health=Health.HEALTHY,
                        genotype=Genotype.CES1_WILD_TYPE
                        if group == "control"
                        else Genotype.CES1_LOSS_OF_FUNCTION,
                        fasting=Fasting.FASTED,
                        data=PKPDData.PK if pk else PKPDData.PD,
                        data_type=DataType.MEAN,
                    ),
                )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        return {**self._figure_pk(), **self._figure_pd()}

    def _figure_pk(self) -> dict[str, Figure]:
        """Enalapril and enalaprilat after the 7th dose (Fig3)."""
        fig = Figure(
            experiment=self,
            sid="Fig3",
            num_rows=2,
            num_cols=2,
            name=f"{self.__class__.__name__} (10 mg PO daily, CES1 G143E)",
            height=self.panel_height * 2,
            width=self.panel_width * 2,
            settings={"legend_scope": "row"},
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"], min=140),
            legend=True,
        )
        for kr, scale in enumerate(["linear", "log"]):
            for kc, (sid, name) in enumerate(
                [("[Cve_ena]", "enalapril"), ("[Cve_eat]", "enalaprilat")]
            ):
                plot = plots[2 * kr + kc]
                plot.set_yaxis(
                    self.labels[sid],
                    unit=self.units[sid],
                    scale=scale,
                    min=1e-4 if scale == "log" else None,
                )
                for group in self.groups:
                    plot.add_data(
                        task=self.to_sid(f"task_po_ENA10m{group}"),
                        xid="time",
                        yid=sid,
                        label=f"sim {group}",
                        color=self.ces1_colors[group],
                    )
                    plot.add_data(
                        dataset=self.to_sid(f"{group}_{name}"),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                        label=f"exp {group}",
                        color=self.ces1_colors[group],
                    )

        return self.figures_by_sid(fig)

    def _figure_pd(self) -> dict[str, Figure]:
        """Systolic blood pressure (Fig6)."""
        fig = Figure(
            experiment=self,
            sid="Fig6",
            num_rows=1,
            num_cols=1,
            name=f"{self.__class__.__name__} (10 mg PO daily, CES1 G143E)",
            height=self.panel_height,
            width=self.panel_width,
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(self.labels["SBP"], unit=self.units["SBP"])

        for group in self.groups:
            plots[0].add_data(
                task=self.to_sid(f"task_po_ENA10m{group}"),
                xid="time",
                yid="SBP",
                label=f"sim {group}",
                color=self.ces1_colors[group],
            )
            plots[0].add_data(
                dataset=self.to_sid(f"{group}_blood pressure systolic"),
                xid="time",
                yid="mean",
                yid_sd="mean_sd",
                count="count",
                label=f"exp {group}",
                color=self.ces1_colors[group],
            )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Her2021, output_dir=Her2021.__name__)
