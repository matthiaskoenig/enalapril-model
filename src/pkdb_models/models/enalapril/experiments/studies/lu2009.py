"""Simulation experiment of the study Lu2009."""

from typing import override

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


class Lu2009(EnalaprilSimulationExperiment):
    """Simulation experiment of Lu2009.

    20 healthy Chinese men, a single oral dose of two capsules of 5 mg enalapril
    maleate after a 12 hr fast, enalapril and enalaprilat in plasma by
    HPLC-MS/MS (mean +- SD). The dose is 10 mg enalapril maleate: the results
    give "10 mg enalapril" and the capsules "containing 5 mg enalapril each"
    (the "50 mg" of the caption of Fig. 3 is a typo); Chinese capsules are
    labelled by the maleate and the enalaprilat (AUCinf 420 ng*hr/ml) matches
    the other studies of 10 mg enalapril maleate (Moffett2014 443-456,
    MacDonald1993 443 ng*hr/ml), 10 mg enalapril would give about 580. The
    enalapril Cmax of 90.5 ng/ml is higher than in the other studies of 10 mg
    (58-67 ng/ml) and not explained.
    """

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig3"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                if label.endswith("_enalapril"):
                    dset.unit_conversion("mean", 1 / self.Mr.ena)
                elif label.endswith("_enalaprilat"):
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[label] = dset
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        simulations["po_enamal10"] = Simulation(
            time_unit="hr",
            end=38,
            preinit_changes={
                **self.default_changes(),
                "PODOSE_ena": Q(10, "mg")
                * self.Mr.ena
                / self.Mr.enamal,  # enalapril maleate
            },
        )
        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        info = {
            "[Cve_ena]": "enalapril",
            "[Cve_eat]": "enalaprilat",
        }

        mappings = {}
        for sid, name in info.items():
            mappings[self.to_sid(f"fm_lu2009_po_ENA10_{name}")] = FitMapping(
                self,
                reference=FitData(
                    self,
                    dataset=f"ENA10_{name}",
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
                    tissue=Tissue.PLASMA,
                    route=Route.PO,
                    application_form=ApplicationForm.CAPSULE,
                    dosing=Dosing.SINGLE,
                    health=Health.HEALTHY,
                    genotype=Genotype.NR,
                    fasting=Fasting.FASTED,
                    data=PKPDData.PK,
                ),
            )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig3",
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
        for kp, sid in enumerate(["[Cve_ena]", "[Cve_eat]"]):
            plots[kp].add_data(
                task="task_po_enamal10",
                xid="time",
                yid=sid,
                label="ENA 10 mg",
                color=self.healthy_color,
            )
        # data
        for kp, name in enumerate(["enalapril", "enalaprilat"]):
            plots[kp].add_data(
                dataset=f"ENA10_{name}",
                xid="time",
                yid="mean",
                yid_sd="mean_sd",
                count="count",
                label="ENA 10 mg",
                color=self.healthy_color,
            )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Lu2009, output_dir=Lu2009.__name__)
