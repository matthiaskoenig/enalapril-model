"""Simulation experiment of the study Thongnopnua2005."""

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


class Thongnopnua2005(EnalaprilSimulationExperiment):
    """Simulation experiment of Thongnopnua2005.

    A method paper (indirect HPLC assay of enalaprilat by the inhibition of
    exogenous ACE): 12 healthy men, a single tablet of 5 mg enalapril maleate
    after an overnight fast, plasma enalaprilat 0-12 hr (mean, no dispersion).
    The non-specific bioassay gives a Cmax of 28 ng/ml, 1.6-2.8 times that of
    the other 5 mg studies (Shioya1992, Sunaga1995), with a double peak.
    """

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig7"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                if label.endswith("enalaprilat"):
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(label)] = dset
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        simulations["po_ENA5"] = Simulation(
            time_unit="hr",
            end=13,
            preinit_changes={
                **self.default_changes(),
                "PODOSE_ena": Q(5, "mg")
                * self.Mr.ena
                / self.Mr.enamal,  # enalapril maleate
            },
        )

        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        info = {"[Cve_eat]": "enalaprilat"}

        mappings = {}
        for sid, name in info.items():
            # the key names the study, the mapping is an outlier of the fits
            mappings[self.to_sid(f"fm_thongnopnua2005_ENA5_{name}")] = FitMapping(
                self,
                reference=FitData(
                    self,
                    dataset=self.to_sid(name),
                    xid="time",
                    yid="mean",
                    yid_sd=None,
                    count="count",
                ),
                observable=FitData(
                    self,
                    task="task_po_ENA5",
                    xid="time",
                    yid=sid,
                ),
                metadata=PKPDMappingMetaData(
                    tissue=Tissue.PLASMA,
                    route=Route.PO,
                    application_form=ApplicationForm.TABLET,
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
            sid="Fig7",
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(self.labels["[Cve_eat]"], unit=self.units["[Cve_eat]"])

        # simulation
        for kp, sid in enumerate(["eat"]):
            plots[kp].add_data(
                task="task_po_ENA5",
                xid="time",
                yid=f"[Cve_{sid}]",
                label="5 mg po",
                color=self.healthy_color,
            )
        # data
        for kp, name in enumerate(["enalaprilat"]):
            plots[kp].add_data(
                dataset=self.to_sid(name),
                xid="time",
                yid="mean",
                count="count",
                label="5 mg po",
                color=self.healthy_color,
            )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Thongnopnua2005, output_dir=Thongnopnua2005.__name__)
