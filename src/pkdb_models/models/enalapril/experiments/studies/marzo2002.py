"""Simulation experiment of the study Marzo2002."""

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


class Marzo2002(EnalaprilSimulationExperiment):
    """Simulation experiment of Marzo2002.

    20 healthy volunteers (66 kg, 171 cm) in two groups of 10, enalapril
    maleate 10 mg (2 x 5 mg tablets) or 20 mg (1 tablet) once daily in the
    morning for 7 days. Enalapril and enalaprilat in plasma on day 7 by
    LC-MS/MS (Fig. 7), the ACE activity in serum relative to the baseline on
    days 1-9 (Table 4), the sitting blood pressure and heart rate (Table 5). The
    baseline heart rate is the resting heart rate of the groups, not an
    increase of the cardiac output. Volunteer 19 of the 20 mg group had only
    very low levels and is part of the means.
    """

    interventions: ClassVar[list[str]] = ["ENA10", "ENA20"]
    doses: ClassVar[dict[str, float]] = {"ENA10": 10, "ENA20": 20}
    # healthy subjects: black for every dose, dose shown by marker
    colors: ClassVar[dict[str, str]] = {
        "ENA10": EnalaprilSimulationExperiment.healthy_color,
        "ENA20": EnalaprilSimulationExperiment.healthy_color,
    }
    markers: ClassVar[dict[str, str]] = EnalaprilSimulationExperiment.dose_markers(
        ["ENA10", "ENA20"]
    )
    linestyles: ClassVar[dict[str, str]] = {"ENA10": "-", "ENA20": "--"}
    SBP_refs: ClassVar[dict[str, float]] = {
        "ENA10": 105,
        "ENA20": 111,
    }
    DBP_refs: ClassVar[dict[str, float]] = {
        "ENA10": 66,
        "ENA20": 73,
    }
    #: the baseline heart rate, the resting heart rate of the group
    HR_refs: ClassVar[dict[str, float]] = {
        "ENA10": 67,
        "ENA20": 68,
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Tab4", "Tab5", "Fig7"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
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

        for intervention in self.interventions:
            # multiple dosing: daily doses for 7 days
            dose_times = [24 * k for k in range(1, 7)]  # [hr]
            # the ACE activity is measured until 192 hr
            simulations[self.to_sid(f"{intervention}")] = Simulation(
                time_unit="hr",
                end=196,
                preinit_changes={
                    **self.default_changes(),
                    "BW": Q(66, "kg"),  # body weight
                    "HEIGHT": Q(171, "cm"),  # height
                    "SBP_ref": Q(self.SBP_refs[intervention], "mmHg"),
                    "DBP_ref": Q(self.DBP_refs[intervention], "mmHg"),
                    "HR": Q(self.HR_refs[intervention], "1/min"),
                    "HRrest": Q(self.HR_refs[intervention], "1/min"),
                    "PODOSE_ena": Q(self.doses[intervention], "mg")
                    * self.Mr.ena
                    / self.Mr.enamal,  # enalapril maleate
                },
                changes=[
                    self.add_doses(
                        dose_times,
                        {
                            "PODOSE_ena": Q(self.doses[intervention], "mg")
                            * self.Mr.ena
                            / self.Mr.enamal,  # enalapril maleate
                        },
                    ),
                ],
            )

        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        info = {
            "[Cve_ena]": "enalapril",
            "[Cve_eat]": "enalaprilat",
            "SBP": "blood pressure systolic",
            "DBP": "blood pressure diastolic",
            "ace_activity": "relative ACE activity",
            "HR": "heart rate",
        }
        tissues = {
            "[Cve_ena]": Tissue.PLASMA,
            "[Cve_eat]": Tissue.PLASMA,
            "ace_activity": Tissue.SERUM,
        }

        mappings = {}
        for intervention in self.interventions:
            for sid, name in info.items():
                key = self.to_sid(f"fm_marzo2002_{intervention}_{name}")
                mappings[key] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(f"{intervention}_{name}"),
                        xid="time",
                        yid="mean",
                        yid_sd=None,
                        count="count",
                    ),
                    observable=FitData(
                        self,
                        task=self.to_sid(f"task_{intervention}"),
                        xid="time",
                        yid=sid,
                    ),
                    metadata=PKPDMappingMetaData(
                        tissue=tissues.get(sid, Tissue.NONE),
                        route=Route.PO,
                        application_form=ApplicationForm.TABLET,
                        dosing=Dosing.MULTIPLE,
                        health=Health.HEALTHY,
                        genotype=Genotype.NR,
                        fasting=Fasting.NR,
                        data=PKPDData.PK
                        if sid in ["[Cve_ena]", "[Cve_eat]"]
                        else PKPDData.PD,
                    ),
                )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        return {**self._figure_pk(), **self._figure_pd()}

    def _figure_pk(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig1",
            num_rows=2,
            num_cols=1,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            # day 7, the last dose at 144 hr
            xaxis=Axis(self.labels["time"], unit=self.units["time"], min=140, max=184),
            legend=True,
        )
        plots[0].set_yaxis(self.labels["[Cve_ena]"], unit=self.units["[Cve_ena]"])
        plots[1].set_yaxis(self.labels["[Cve_eat]"], unit=self.units["[Cve_eat]"])

        # simulation
        for intervention in self.interventions:
            for kp, sid in enumerate(["ena", "eat"]):
                plots[kp].add_data(
                    task=self.to_sid(f"task_{intervention}"),
                    xid="time",
                    yid=f"[Cve_{sid}]",
                    label=f"ENA {self.doses[intervention]:g} mg",
                    color=self.colors[intervention],
                    linestyle=self.linestyles[intervention],
                )

            # data
            for kp, name in enumerate(["enalapril", "enalaprilat"]):
                plots[kp].add_data(
                    dataset=self.to_sid(f"{intervention}_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd=None,
                    count="count",
                    label=f"ENA {self.doses[intervention]:g} mg",
                    color=self.colors[intervention],
                    marker=self.markers[intervention],
                )

        return self.figures_by_sid(fig)

    def _figure_pd(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig2",
            num_rows=2,
            num_cols=2,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(self.labels["SBP"], unit=self.units["SBP"])
        plots[1].set_yaxis(self.labels["DBP"], unit=self.units["DBP"])
        plots[2].set_yaxis(self.labels["ace_activity"], unit=self.units["ace_activity"])
        plots[3].set_yaxis(self.labels["HR"], unit=self.units["HR"], min=40, max=80)

        # simulation
        for intervention in self.interventions:
            for kp, sid in enumerate(["SBP", "DBP", "ace_activity", "HR"]):
                plots[kp].add_data(
                    task=self.to_sid(f"task_{intervention}"),
                    xid="time",
                    yid=sid,
                    label=f"ENA {self.doses[intervention]:g} mg",
                    color=self.colors[intervention],
                    linestyle=self.linestyles[intervention],
                )
        # data
        for kp, name in enumerate(
            [
                "blood pressure systolic",
                "blood pressure diastolic",
                "relative ACE activity",
                "heart rate",
            ]
        ):
            for intervention in self.interventions:
                plots[kp].add_data(
                    dataset=self.to_sid(f"{intervention}_{name}"),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd",
                    count="count",
                    label=f"ENA {self.doses[intervention]:g} mg",
                    color=self.colors[intervention],
                    marker=self.markers[intervention],
                )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Marzo2002, output_dir=Marzo2002.__name__)
