"""Simulation experiment of the study Burckhardt2015."""

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

from pkdb_models.models.enalapril import MODEL
from pkdb_models.models.enalapril.experiments.base_experiment import (
    EnalaprilSimulationExperiment,
)


class Burckhardt2015(EnalaprilSimulationExperiment):
    """Simulation experiment of Burckhardt2015.

    Nine healthy volunteers (6 men, 3 women, 19-30 years, 70 kg, 181 cm) took a
    single 20 mg enalapril maleate tablet after a fast of 10 h. Serum enalapril
    and enalaprilat by LC-MS/MS (Fig6B, mean and SD, every 20 min to 3 h, every
    30 min to 8 h, then 24, 48 and 72 h), the cumulative urinary excretion of
    both (Fig4, the 9 individual curves, mean of the copy), and renin (µIU/ml),
    plasma renin activity, angiotensin I and angiotensin II in plasma (Fig6,
    0-8 h, 24, 48 and 72 h).

    The renin, the plasma renin activity and the angiotensins are mapped as the
    ratio to their value before the dose: the absolute levels of the assays (an
    international unit of renin, an activity in ng/ml/h) are not the amounts of
    the model. The plasma renin activity is the renin of the same samples, an
    aggregate of the renin concentration. The blood pressure (Tab6) is reported
    as the baseline and averages over 0-24 h and 0-72 h, no time course: the
    baseline is the reference of the simulation, the averages are not mapped.
    The saliva (Fig2, 5 subjects) is not mapped, the model has no saliva.
    """

    color: ClassVar[str] = EnalaprilSimulationExperiment.healthy_color
    #: the observable, tissue and data by the label of the data
    info: ClassVar[dict[str, tuple[str, Tissue, PKPDData]]] = {
        "enalapril": ("[Cve_ena]", Tissue.SERUM, PKPDData.PK),
        "enalaprilat": ("[Cve_eat]", Tissue.SERUM, PKPDData.PK),
        "cumulative amount_enalapril": ("Aurine_ena", Tissue.URINE, PKPDData.PK),
        "cumulative amount_enalaprilat": ("Aurine_eat", Tissue.URINE, PKPDData.PK),
        "renin": ("ren_ratio", Tissue.PLASMA, PKPDData.PD),
        "renin activity": ("ren_ratio", Tissue.PLASMA, PKPDData.PD),
        "angiotensin I": ("ang1_ratio", Tissue.PLASMA, PKPDData.PD),
        "angiotensin II": ("ang2_ratio", Tissue.PLASMA, PKPDData.PD),
    }
    #: the data which is mapped as the ratio to the value before the dose
    ratios: ClassVar[set[str]] = {
        "renin",
        "renin activity",
        "angiotensin I",
        "angiotensin II",
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig6", "Fig4Mean", "Tab6"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                if not label.startswith("ENA20_") or "_recovery_" in label:
                    continue
                name = label.removeprefix("ENA20_")
                if fig_id == "Tab6":
                    # the baseline, the other rows are averages over 0-24 and
                    # 0-72 h
                    if name not in {
                        "blood pressure systolic",
                        "blood pressure diastolic",
                    }:
                        continue
                    df_label = df_label[df_label.time == 0]
                if name in self.ratios:
                    df_label = df_label.copy()
                    baseline = df_label.loc[df_label.time == 0, "mean"].iloc[0]
                    for key in ["mean", "sd", "se"]:
                        df_label[key] = df_label[key] / baseline
                    df_label = df_label.drop(
                        columns=["mean_pm", "median", "min", "max"], errors="ignore"
                    )
                    df_label["unit"] = "dimensionless"
                dset = DataSet.from_df(df_label, self.ureg)
                if name.endswith("enalapril"):
                    dset.unit_conversion("mean", 1 / self.Mr.ena)
                elif name.endswith("enalaprilat"):
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(name)] = dset
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        simulations["po_ENA20"] = Simulation(
            time_unit="hr",
            end=73,
            preinit_changes={
                **self.default_changes(),
                "BW": Q(70, "kg"),
                "HEIGHT": Q(181, "cm"),
                # the supine blood pressure before the dose (Tab6)
                "SBP_ref": Q(109.00, "mmHg"),
                "DBP_ref": Q(67.00, "mmHg"),
                # enalapril maleate
                "PODOSE_ena": Q(20, "mg") * self.Mr.ena / self.Mr.enamal,
            },
        )
        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for name, (sid, tissue, data) in self.info.items():
            mappings[self.to_sid(f"fm_burckhardt2015_{name}")] = FitMapping(
                self,
                reference=FitData(
                    self,
                    dataset=self.to_sid(name),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                ),
                observable=FitData(self, task="task_po_ENA20", xid="time", yid=sid),
                metadata=PKPDMappingMetaData(
                    tissue=tissue,
                    route=Route.PO,
                    application_form=ApplicationForm.TABLET,
                    dosing=Dosing.SINGLE,
                    health=Health.HEALTHY,
                    genotype=Genotype.NR,
                    fasting=Fasting.FASTED,
                    data=data,
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
            sid="Fig4_Fig6B",
            num_rows=2,
            num_cols=2,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        names = [
            "enalapril",
            "enalaprilat",
            "cumulative amount_enalapril",
            "cumulative amount_enalaprilat",
        ]
        for kp, name in enumerate(names):
            sid = self.info[name][0]
            plots[kp].set_yaxis(self.labels[sid], unit=self.units[sid])
            plots[kp].add_data(
                task="task_po_ENA20",
                xid="time",
                yid=sid,
                label="20 mg",
                color=self.color,
            )
            plots[kp].add_data(
                dataset=self.to_sid(name),
                xid="time",
                yid="mean",
                yid_sd="mean_sd",
                count="count",
                label="20 mg",
                color=self.color,
            )
        return self.figures_by_sid(fig)

    def _figure_pd(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig6_Tab6",
            num_rows=2,
            num_cols=3,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        panels: list[tuple[str, list[str]]] = [
            ("ren_ratio", ["renin", "renin activity"]),
            ("ang1_ratio", ["angiotensin I"]),
            ("ang2_ratio", ["angiotensin II"]),
            ("ald_ratio", []),
            ("SBP", ["blood pressure systolic"]),
            ("DBP", ["blood pressure diastolic"]),
        ]
        markers = ["o", "s"]
        for kp, (sid, names) in enumerate(panels):
            plots[kp].set_yaxis(self.labels[sid], unit=self.units[sid])
            plots[kp].add_data(
                task="task_po_ENA20",
                xid="time",
                yid=sid,
                label="20 mg",
                color=self.color,
            )
            for k, name in enumerate(names):
                plots[kp].add_data(
                    dataset=self.to_sid(name),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=name,
                    color=self.color,
                    marker=markers[k],
                )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Burckhardt2015, output_dir=Burckhardt2015.__name__)
