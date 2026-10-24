"""Simulation experiment of the study Baba1990."""

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


class Baba1990(EnalaprilSimulationExperiment):
    """Simulation experiment of Baba1990.

    A single oral dose of 10 mg enalapril maleate in 10 Japanese male controls
    (49.8 years, GFR 114 ml/min, ICG R15 5.4 %) and 7 men with biopsy proven,
    compensated cirrhosis (52.5 years, GFR 72 ml/min, ICG R15 19.5 %, normal
    albumin, no ascites or encephalopathy). Serum enalaprilat by RIA, enalapril
    as the difference of the RIA before and after hydrolysis (Fig1, mean and SE),
    0-24 h. Form and food are not reported.

    The renal function is the measured GFR over 101 ml/min. The paper gives no
    Child-Pugh class: compensated cirrhosis with normal albumin and an ICG R15 of
    19.5 % ("moderate hepatic dysfunction" in the abstract) is Child-Pugh A, the
    mild cirrhosis of the model.
    """

    groups: ClassVar[list[str]] = ["healthy", "cirrhosis"]
    colors: ClassVar[dict[str, str]] = {
        "healthy": EnalaprilSimulationExperiment.cirrhosis_colors["Control"],
        "cirrhosis": EnalaprilSimulationExperiment.cirrhosis_colors["Mild cirrhosis"],
    }
    #: the renal function, the measured GFR (114 and 72 ml/min) over 101 ml/min
    renal_functions: ClassVar[dict[str, float]] = {
        "healthy": 114 / 101,
        "cirrhosis": 72 / 101,
    }
    #: the degree of cirrhosis, Child-Pugh A for the patients
    cirrhosis_degree: ClassVar[dict[str, float]] = {
        "healthy": EnalaprilSimulationExperiment.cirrhosis_map["Control"],
        "cirrhosis": EnalaprilSimulationExperiment.cirrhosis_map["Mild cirrhosis"],
    }
    #: the observable by the substance of the data
    info: ClassVar[dict[str, str]] = {
        "enalapril": "[Cve_ena]",
        "enalaprilat": "[Cve_eat]",
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                if label.startswith("enalapril_"):
                    dset.unit_conversion("mean", 1 / self.Mr.ena)
                elif label.startswith("enalaprilat_"):
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(label)] = dset

        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        for group in self.groups:
            simulations[f"po_enamal10_{group}"] = Simulation(
                time_unit="hr",
                end=25,
                preinit_changes={
                    **self.default_changes(),
                    "f_cirrhosis": Q(self.cirrhosis_degree[group], "dimensionless"),
                    "KI__f_renal_function": Q(
                        self.renal_functions[group], "dimensionless"
                    ),
                    # enalapril maleate
                    "PODOSE_ena": Q(10, "mg") * self.Mr.ena / self.Mr.enamal,
                },
            )
        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for name, sid in self.info.items():
            for group in self.groups:
                mappings[self.to_sid(f"fm_baba1990_{name}_{group}")] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(f"{name}_{group}"),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                    ),
                    observable=FitData(
                        self,
                        task=f"task_po_enamal10_{group}",
                        xid="time",
                        yid=sid,
                    ),
                    metadata=PKPDMappingMetaData(
                        tissue=Tissue.SERUM,
                        route=Route.PO,
                        application_form=ApplicationForm.NR,
                        dosing=Dosing.SINGLE,
                        health=Health.HEALTHY
                        if group == "healthy"
                        else Health.CIRRHOSIS,
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
            sid="Fig1",
            num_rows=1,
            num_cols=2,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        for kp, (name, sid) in enumerate(self.info.items()):
            plots[kp].set_yaxis(self.labels[sid], unit=self.units[sid])
            for group in self.groups:
                plots[kp].add_data(
                    task=f"task_po_enamal10_{group}",
                    xid="time",
                    yid=sid,
                    label=group,
                    color=self.colors[group],
                )
                plots[kp].add_data(
                    dataset=self.to_sid(f"{name}_{group}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=group,
                    color=self.colors[group],
                )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Baba1990, output_dir=Baba1990.__name__)
