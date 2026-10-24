"""Simulation experiment of the study Till1984."""

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

from pkdb_models.models.enalapril import MODEL
from pkdb_models.models.enalapril.experiments.base_experiment import (
    EnalaprilSimulationExperiment,
)


class Till1984(EnalaprilSimulationExperiment):
    """Simulation experiment of Till1984.

    12 healthy men (BW 60-103 kg, the mean is not reported), one capsule of
    10 mg enalapril maleate every 24 hr for eight doses (0-168 hr) after an
    overnight fast. Serum enalaprilat (RIA) after the first dose (Fig. 1), the
    troughs 24 hr after every dose (Table 1) and after the eighth dose to
    96 hr (Fig. 2), means without dispersion.

    The three datasets are disjoint: the day 8 part of Fig. 1 is the data of
    Fig. 2, and the troughs of Table 1 at 24 hr (Fig. 1), 168 and 192 hr
    (Fig. 2) are in the figures, so only the troughs of days 2-6 (48-144 hr)
    come from Table 1.
    """

    #: the datasets of the fit mappings: the label of the data, the times
    datasets_info: ClassVar[dict[str, tuple[str, float, float]]] = {
        # first dose (Fig. 1, 0-24 hr)
        "day1": ("ENA10m_enalaprilat", 0, 24),
        # the troughs of the doses 2-6 (Table 1)
        "trough": ("ENA10m_trough_enalaprilat", 48, 144),
        # eighth dose (Fig. 2, 168-264 hr)
        "dose8": ("last_enalaprilat", 168, 264),
    }
    markers: ClassVar[dict[str, str]] = {
        "day1": "o",
        "trough": "s",
        "dose8": "v",
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1", "Fig2", "Tab1"]:
            df = self.load_dataframe(fig_id)
            for key, (label, tstart, tend) in self.datasets_info.items():
                df_label = df[
                    (df["label"] == label)
                    & (df["time"] >= tstart)
                    & (df["time"] <= tend)
                ]
                if df_label.empty:
                    continue
                dset = DataSet.from_df(df_label, self.ureg)
                dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(f"{key}_enalaprilat")] = dset

        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        dose = {
            # enalapril maleate
            "PODOSE_ena": Q(10, "mg") * self.Mr.ena / self.Mr.enamal,
        }
        simulations = {}
        # a dose every 24 hr from 0 to 168 hr (8 doses)
        simulations["po_ENA10m"] = Simulation(
            time_unit="hr",
            end=300,
            preinit_changes={**self.default_changes(), **dose},
            changes=[self.add_doses([24 * k for k in range(1, 8)], dose)],
        )

        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for key in self.datasets_info:
            mappings[self.to_sid(f"fm_ENA10m_{key}_enalaprilat")] = FitMapping(
                self,
                reference=FitData(
                    self,
                    dataset=self.to_sid(f"{key}_enalaprilat"),
                    xid="time",
                    yid="mean",
                    yid_sd=None,
                    # 12 subjects (11 on two days of the troughs)
                    count=12,
                ),
                observable=FitData(
                    self,
                    task="task_po_ENA10m",
                    xid="time",
                    yid="[Cve_eat]",
                ),
                metadata=PKPDMappingMetaData(
                    tissue=Tissue.SERUM,
                    route=Route.PO,
                    application_form=ApplicationForm.CAPSULE,
                    dosing=Dosing.MULTIPLE,
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
            sid="Fig1_Fig2",
            num_rows=1,
            num_cols=2,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        # all doses (Fig. 1), the eighth dose on a log scale (Fig. 2)
        plots[0].set_yaxis(self.labels["[Cve_eat]"], unit=self.units["[Cve_eat]"])
        plots[1].set_yaxis(
            self.labels["[Cve_eat]"],
            unit=self.units["[Cve_eat]"],
            scale="log",
            min=1e-3,
        )
        plots[1].set_xaxis(self.labels["time"], unit=self.units["time"], min=166)

        for kp in range(2):
            plots[kp].add_data(
                task="task_po_ENA10m",
                xid="time",
                yid="[Cve_eat]",
                label="10 mg q24h",
                color=self.healthy_color,
            )
            for key in self.datasets_info:
                if kp == 1 and key != "dose8":
                    continue
                plots[kp].add_data(
                    dataset=self.to_sid(f"{key}_enalaprilat"),
                    xid="time",
                    yid="mean",
                    # 12 subjects, 11 on two days of the troughs
                    count=12,
                    label=key,
                    color=self.healthy_color,
                    marker=self.markers[key],
                    linestyle="" if key == "trough" else "--",
                )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Till1984, output_dir=Till1984.__name__)
