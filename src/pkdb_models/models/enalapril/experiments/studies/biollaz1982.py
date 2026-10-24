"""Simulation experiment of the study Biollaz1982."""

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


class Biollaz1982(EnalaprilSimulationExperiment):
    """Simulation experiment of Biollaz1982.

    Twelve normotensive men (22-33 years) took a 10 mg enalapril maleate capsule
    and, a week apart, 10 mg lisinopril (not simulated) after an overnight fast.
    Serum enalaprilat by RIA, enalapril as the difference of the RIA before and
    after hydrolysis, and the inhibition of the plasma ACE activity
    (radioenzymatic) to 72 h (Fig1, mean and SE).

    The volunteers and the samples are those of Ulm1982 (the same centre and
    design, cited as the companion paper on the disposition), whose serum
    concentrations to 96 h are the same curves: the enalapril and enalaprilat of
    this study are an aggregate of Ulm1982, the ACE inhibition is its own data.
    """

    color: ClassVar[str] = EnalaprilSimulationExperiment.healthy_color
    #: the observable and tissue by the label of the data
    info: ClassVar[dict[str, tuple[str, Tissue]]] = {
        "enalapril": ("[Cve_ena]", Tissue.SERUM),
        "enalaprilat": ("[Cve_eat]", Tissue.SERUM),
        "ACE inhibition": ("ace_inhibition", Tissue.PLASMA),
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                if not label.startswith("ENA_"):
                    # the lisinopril arm
                    continue
                dset = DataSet.from_df(df_label, self.ureg)
                if label.endswith("_enalapril"):
                    dset.unit_conversion("mean", 1 / self.Mr.ena)
                elif label.endswith("_enalaprilat"):
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(label)] = dset
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        simulations["ENA10"] = Simulation(
            time_unit="hr",
            end=73,
            preinit_changes={
                **self.default_changes(),
                # enalapril maleate
                "PODOSE_ena": Q(10, "mg") * self.Mr.ena / self.Mr.enamal,
            },
        )

        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for name, (sid, tissue) in self.info.items():
            mappings[self.to_sid(f"fm_biollaz1982_{name}")] = FitMapping(
                self,
                reference=FitData(
                    self,
                    dataset=self.to_sid(f"ENA_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                ),
                observable=FitData(self, task="task_ENA10", xid="time", yid=sid),
                metadata=PKPDMappingMetaData(
                    tissue=tissue,
                    route=Route.PO,
                    application_form=ApplicationForm.CAPSULE,
                    dosing=Dosing.SINGLE,
                    health=Health.HEALTHY,
                    genotype=Genotype.NR,
                    fasting=Fasting.FASTED,
                    data=PKPDData.PD if sid == "ace_inhibition" else PKPDData.PK,
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
            num_cols=3,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        for kp, (name, (sid, _)) in enumerate(self.info.items()):
            plots[kp].set_yaxis(self.labels[sid], unit=self.units[sid])
            plots[kp].add_data(
                task="task_ENA10",
                xid="time",
                yid=sid,
                label="10 mg",
                color=self.color,
            )
            plots[kp].add_data(
                dataset=self.to_sid(f"ENA_{name}"),
                xid="time",
                yid="mean",
                yid_sd="mean_sd",
                count="count",
                label="10 mg",
                color=self.color,
            )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Biollaz1982, output_dir=Biollaz1982.__name__)
