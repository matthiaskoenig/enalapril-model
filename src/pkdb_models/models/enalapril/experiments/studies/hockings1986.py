"""Simulation experiment of the study Hockings1986."""

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


class Hockings1986(EnalaprilSimulationExperiment):
    """Simulation experiment of Hockings1986.

    9 young (22-30 yr) and 9 elderly (65-73 yr) healthy volunteers, Latin
    square of 10 mg enalaprilat i.v. (bolus), 10 mg enalapril maleate p.o.
    (tablet) and placebo, after an overnight fast. Plasma enalaprilat (RIA) for
    96 hr after both (Fig1 i.v., Fig2 p.o.; enalapril was not measured). The
    renal function is the measured creatinine clearance relative to the GFR of
    101 ml/min, the body weight the mean of the group:

        young: 92 ml/min, 64 kg
        elderly: 66 ml/min, 70 kg

    The Imax of the Hill fit of the ACE inhibition (Tab4: 93.1 and 97.2 %, C50
    5.8 and 4.4 ng/ml enalaprilat) is a parameter of the effect model of the
    paper, not an observation, and is not mapped.
    """

    #: creatinine clearance [ml/min] and body weight [kg] of the groups
    groups: ClassVar[dict[str, tuple[float, float]]] = {
        "young": (92, 64),
        "elder": (66, 70),
    }
    interventions: ClassVar[list[str]] = ["EATIV10", "ENAPO10"]
    intervention_labels: ClassVar[dict[str, str]] = {
        "EATIV10": "10 mg enalaprilat IV",
        "ENAPO10": "10 mg enalapril maleate PO",
    }
    group_labels: ClassVar[dict[str, str]] = {"young": "young", "elder": "elderly"}
    colors: ClassVar[dict[str, str]] = {
        "young": EnalaprilSimulationExperiment.renal_colors["Normal renal function"],
        "elder": EnalaprilSimulationExperiment.renal_colors["Mild renal impairment"],
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1", "Fig2"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                if label.endswith("_enalaprilat"):
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[self.to_sid(label)] = dset
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        for group, (crcl, bw) in self.groups.items():
            changes = {
                **self.default_changes(),
                "BW": Q(bw, "kg"),
                "KI__f_renal_function": Q(crcl / 101, "dimensionless"),
            }
            simulations[self.to_sid(f"ENAPO10_{group}")] = Simulation(
                time_unit="hr",
                end=98,
                preinit_changes={
                    **changes,
                    # enalapril maleate
                    "PODOSE_ena": Q(10, "mg") * self.Mr.ena / self.Mr.enamal,
                },
            )
            simulations[self.to_sid(f"EATIV10_{group}")] = Simulation(
                time_unit="hr",
                end=98,
                preinit_changes={**changes, "IVDOSE_eat": Q(10, "mg")},
            )

        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for intervention in self.interventions:
            for group in self.groups:
                mappings[self.to_sid(f"fm_{intervention}_{group}_enalaprilat")] = (
                    FitMapping(
                        self,
                        reference=FitData(
                            self,
                            dataset=self.to_sid(f"{intervention}_{group}_enalaprilat"),
                            xid="time",
                            yid="mean",
                            yid_sd=None,
                            count="count",
                        ),
                        observable=FitData(
                            self,
                            task=self.to_sid(f"task_{intervention}_{group}"),
                            xid="time",
                            yid="[Cve_eat]",
                        ),
                        metadata=PKPDMappingMetaData(
                            tissue=Tissue.PLASMA,
                            route=Route.PO if intervention == "ENAPO10" else Route.IV,
                            application_form=(
                                ApplicationForm.TABLET
                                if intervention == "ENAPO10"
                                else ApplicationForm.SOLUTION
                            ),
                            dosing=Dosing.SINGLE,
                            # the elderly are healthy, their renal function is
                            # the measured creatinine clearance
                            health=Health.HEALTHY,
                            genotype=Genotype.NR,
                            fasting=Fasting.FASTED,
                            data=PKPDData.PK,
                            data_type=DataType.MEAN,
                        ),
                    )
                )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig1_2",
            num_rows=2,
            num_cols=2,
            name=f"{self.__class__.__name__} (young and elderly, healthy)",
            height=self.panel_height * 2,
            width=self.panel_width * 2,
            settings={"legend_scope": "row"},
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        # columns: i.v. (Fig1), p.o. (Fig2); rows: linear, log
        for kc, intervention in enumerate(self.interventions):
            for kr, scale in enumerate(["linear", "log"]):
                plot = plots[2 * kr + kc]
                plot.set_title(self.intervention_labels[intervention])
                if scale == "linear":
                    # the distribution and the peak, the late phase on the log axis
                    plot.set_xaxis(
                        self.labels["time"], unit=self.units["time"], min=-1, max=25
                    )
                plot.set_yaxis(
                    self.labels["[Cve_eat]"],
                    unit=self.units["[Cve_eat]"],
                    scale=scale,
                    min=1e-3 if scale == "log" else None,
                )
                for group in self.groups:
                    plot.add_data(
                        task=self.to_sid(f"task_{intervention}_{group}"),
                        xid="time",
                        yid="[Cve_eat]",
                        label=f"sim {self.group_labels[group]}",
                        color=self.colors[group],
                    )
                    plot.add_data(
                        dataset=self.to_sid(f"{intervention}_{group}_enalaprilat"),
                        xid="time",
                        yid="mean",
                        yid_sd=None,
                        count="count",
                        label=f"exp {self.group_labels[group]}",
                        color=self.colors[group],
                        marker=self.age_markers[group],
                    )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Hockings1986, output_dir=Hockings1986.__name__)
