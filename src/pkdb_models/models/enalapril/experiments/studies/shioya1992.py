"""Simulation experiment of the study Shioya1992."""

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


class Shioya1992(EnalaprilSimulationExperiment):
    """Simulation experiment of Shioya1992.

    A method paper (GC/MS): five healthy subjects, a single oral dose of 5 mg
    enalapril maleate (form and fasting not reported), plasma 0-48 hr and urine
    0-48 hr (mean and SD).
    """

    #: the dose of enalapril maleate as an amount, the recovery is a percent of it
    dose_amount: ClassVar[Quantity] = (
        Q(5, "mg") / EnalaprilSimulationExperiment.Mr.enamal
    )

    #: the substances of the plasma and urine data by observable
    info: ClassVar[dict[str, str]] = {
        "[Cve_ena]": "enalapril",
        "[Cve_eat]": "enalaprilat",
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig3", "Fig4"]:
            df = self.load_dataframe(fig_id)
            # the values below the limit of quantification (0.2 ng/ml in plasma)
            # and the zeros before the dose are curated as 0, they carry no
            # information and have no SD
            df = df[df["mean"] > 0]
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                if label.startswith("recovery_"):
                    # the cumulative urinary excretion in percent of the dose (molar)
                    dset.unit_conversion("mean", self.dose_amount)
                elif label.endswith("_enalapril"):
                    dset.unit_conversion("mean", 1 / self.Mr.ena)
                elif label.endswith("_enalaprilat"):
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(label)] = dset
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        simulations["po_ENA5"] = Simulation(
            time_unit="hr",
            end=50,
            preinit_changes={
                **self.default_changes(),
                # enalapril maleate
                "PODOSE_ena": Q(5, "mg") * self.Mr.ena / self.Mr.enamal,
            },
        )

        return simulations

    @staticmethod
    def _metadata(tissue: Tissue) -> PKPDMappingMetaData:
        """Get the metadata of a mapping of the study."""
        return PKPDMappingMetaData(
            tissue=tissue,
            route=Route.PO,
            application_form=ApplicationForm.NR,
            dosing=Dosing.SINGLE,
            health=Health.HEALTHY,
            genotype=Genotype.NR,
            fasting=Fasting.NR,
            data=PKPDData.PK,
        )

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for sid, name in self.info.items():
            mappings[self.to_sid(f"fm_ENA5_{name}")] = FitMapping(
                self,
                reference=FitData(
                    self,
                    dataset=self.to_sid(f"ENA5_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                ),
                observable=FitData(
                    self,
                    task="task_po_ENA5",
                    xid="time",
                    yid=sid,
                ),
                metadata=self._metadata(Tissue.PLASMA),
            )
            mappings[self.to_sid(f"fm_ENA5_urine_{name}")] = FitMapping(
                self,
                reference=FitData(
                    self,
                    dataset=self.to_sid(f"recovery_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                ),
                observable=FitData(
                    self,
                    task="task_po_ENA5",
                    xid="time",
                    # the urinary amount of the substance of the plasma data
                    yid=sid.replace("[Cve_", "Aurine_").rstrip("]"),
                ),
                metadata=self._metadata(Tissue.URINE),
            )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig3_Fig4",
            num_rows=2,
            num_cols=2,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(self.labels["[Cve_ena]"], unit=self.units["[Cve_ena]"])
        plots[1].set_yaxis(self.labels["Aurine_ena"], unit=self.units["Aurine_ena"])
        plots[2].set_yaxis(self.labels["[Cve_eat]"], unit=self.units["[Cve_eat]"])
        plots[3].set_yaxis(self.labels["Aurine_eat"], unit=self.units["Aurine_eat"])

        for krow, (sid, name) in enumerate(self.info.items()):
            urine = sid.replace("[Cve_", "Aurine_").rstrip("]")
            for kcol, (yid, dset) in enumerate(
                [(sid, f"ENA5_{name}"), (urine, f"recovery_{name}")]
            ):
                kp = krow * 2 + kcol
                plots[kp].add_data(
                    task="task_po_ENA5",
                    xid="time",
                    yid=yid,
                    label="5 mg po",
                    color=self.healthy_color,
                )
                plots[kp].add_data(
                    dataset=self.to_sid(dset),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label="5 mg po",
                    color=self.healthy_color,
                    linestyle="" if kcol == 1 else "-",
                )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Shioya1992, output_dir=Shioya1992.__name__)
