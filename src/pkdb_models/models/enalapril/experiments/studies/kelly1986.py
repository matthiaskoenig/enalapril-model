"""Simulation experiment of the study Kelly1986."""

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


class Kelly1986(EnalaprilSimulationExperiment):
    """Simulation experiment of Kelly1986 in renal impairment.

    Single oral doses of 10 mg enalapril maleate (with 250 ml water, fasted,
    a light meal at 2 hr) in four groups of 6 by the GFR (51Cr-EDTA, the
    means of the individual values of Table 1): S1 healthy 115.7, S2 65.7,
    S3 24.8 and S4 7.8 ml/min/1.73 m^2. Serum enalaprilat (RIA, Fig1, mean ±
    SE) and the cumulative urinary enalaprilat in mg (Fig3, mean ± SE; 2485
    µg in S1 over 48 hr, 35 % of the dose). Multiple doses once daily for 7
    days (0-144 hr): M1 6 healthy subjects (GFR > 100) with 10 mg, enalaprilat
    before and 4 hr after every dose; M2 6 patients with a GFR of 7-28 (mean
    13.2) without dialysis with 2.5 mg, enalaprilat before and 9 hr after
    every dose (Fig5). The renal function is the GFR over 101 ml/min.
    """

    groups_single: ClassVar[list[str]] = ["S1", "S2", "S3", "S4"]
    #: the multiple dose groups: the dose of enalapril maleate [mg]
    groups_multi: ClassVar[dict[str, float]] = {"M1": 10, "M2": 2.5}
    #: the GFR of the groups [ml/min/1.73 m^2], the means of Table 1; M1 is
    #: above 100, its values are not reported
    gfr: ClassVar[dict[str, float]] = {
        "S1": 115.7,
        "S2": 65.7,
        "S3": 24.8,
        "S4": 7.8,
        "M1": 101,
        "M2": 13.2,
    }
    colors: ClassVar[dict[str, str]] = {
        "S1": EnalaprilSimulationExperiment.renal_colors["Normal renal function"],
        "S2": EnalaprilSimulationExperiment.renal_colors["Mild renal impairment"],
        "S3": EnalaprilSimulationExperiment.renal_colors["Severe renal impairment"],
        "S4": EnalaprilSimulationExperiment.renal_colors["End stage renal disease"],
        "M1": EnalaprilSimulationExperiment.renal_colors["Normal renal function"],
        "M2": EnalaprilSimulationExperiment.renal_colors["End stage renal disease"],
    }
    group_labels: ClassVar[dict[str, str]] = {
        "S1": "S1 GFR 116",
        "S2": "S2 GFR 66",
        "S3": "S3 GFR 25",
        "S4": "S4 GFR 8",
        "M1": "M1 GFR >100, 10 mg",
        "M2": "M2 GFR 13, 2.5 mg",
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1", "Fig3", "Fig5"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                # serum ng/ml and urine mg of enalaprilat
                dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(label)] = dset

        return dsets

    def _sim_id(self, group: str) -> str:
        """Id of the simulation of a group."""
        dose = self.groups_multi.get(group, 10)
        return self.to_sid(f"po_ENA{dose:g}_{group}")

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        for group in self.groups_single:
            simulations[self._sim_id(group)] = Simulation(
                time_unit="hr",
                end=48,
                preinit_changes={
                    **self.default_changes(),
                    "KI__f_renal_function": Q(self.gfr[group] / 101, "dimensionless"),
                    # enalapril maleate
                    "PODOSE_ena": Q(10, "mg") * self.Mr.ena / self.Mr.enamal,
                },
            )

        for group, dose in self.groups_multi.items():
            # enalapril maleate
            podose = Q(dose, "mg") * self.Mr.ena / self.Mr.enamal
            # a dose every 24 hr from 0 to 144 hr, the data reach 192 hr (M1)
            # and 312 hr (M2)
            simulations[self._sim_id(group)] = Simulation(
                time_unit="hr",
                end=200 if group == "M1" else 320,
                preinit_changes={
                    **self.default_changes(),
                    "KI__f_renal_function": Q(self.gfr[group] / 101, "dimensionless"),
                    "PODOSE_ena": podose,
                },
                changes=[
                    self.add_doses(
                        [24 * k for k in range(1, 7)], {"PODOSE_ena": podose}
                    )
                ],
            )

        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for group in [*self.groups_single, *self.groups_multi]:
            data = [("enalaprilat", "[Cve_eat]", Tissue.SERUM)]
            if group in self.groups_single:
                data.append(("urine", "Aurine_eat", Tissue.URINE))
            for name, yid, tissue in data:
                key = f"fm_kelly1986_{self._sim_id(group)}_enalaprilat"
                if tissue == Tissue.URINE:
                    key = f"{key}_urine"
                mappings[self.to_sid(key)] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(f"{group}_{name}"),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd" if group in self.groups_single else None,
                        count="count",
                    ),
                    observable=FitData(
                        self,
                        task=f"task_{self._sim_id(group)}",
                        xid="time",
                        yid=yid,
                    ),
                    metadata=PKPDMappingMetaData(
                        tissue=tissue,
                        route=Route.PO,
                        application_form=ApplicationForm.NR,
                        dosing=Dosing.SINGLE
                        if group in self.groups_single
                        else Dosing.MULTIPLE,
                        health=Health.HEALTHY
                        if group in ["S1", "M1"]
                        else Health.RENAL_IMPAIRMENT,
                        genotype=Genotype.NR,
                        # the single dose study was fasted
                        fasting=Fasting.FASTED
                        if group in self.groups_single
                        else Fasting.NR,
                        data=PKPDData.PK,
                        data_type=DataType.MEAN,
                    ),
                )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        return {
            **self._figure_single(),
            **self._figure_multi(),
        }

    def _figure_single(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig1_Fig3",
            num_rows=1,
            num_cols=2,
            name=f"{self.__class__.__name__}",
            settings={"legend_scope": "row"},
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(self.labels["[Cve_eat]"], unit=self.units["[Cve_eat]"])
        plots[1].set_yaxis(self.labels["Aurine_eat"], unit=self.units["Aurine_eat"])

        for group in self.groups_single:
            for k, (yid, name) in enumerate(
                [("[Cve_eat]", "enalaprilat"), ("Aurine_eat", "urine")]
            ):
                plots[k].add_data(
                    task=f"task_{self._sim_id(group)}",
                    xid="time",
                    yid=yid,
                    label=self.group_labels[group],
                    color=self.colors[group],
                )
                plots[k].add_data(
                    dataset=self.to_sid(f"{group}_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=self.group_labels[group],
                    color=self.colors[group],
                )

        return self.figures_by_sid(fig)

    def _figure_multi(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig5",
            num_rows=1,
            num_cols=1,
            name=f"{self.__class__.__name__}",
            settings={"legend_scope": "row"},
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(self.labels["[Cve_eat]"], unit=self.units["[Cve_eat]"])
        for group in self.groups_multi:
            plots[0].add_data(
                task=f"task_{self._sim_id(group)}",
                xid="time",
                yid="[Cve_eat]",
                label=self.group_labels[group],
                color=self.colors[group],
            )
            plots[0].add_data(
                dataset=self.to_sid(f"{group}_enalaprilat"),
                xid="time",
                yid="mean",
                yid_sd=None,
                count="count",
                label=self.group_labels[group],
                color=self.colors[group],
                marker="o" if group == "M1" else "s",
            )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Kelly1986, output_dir=Kelly1986.__name__)
