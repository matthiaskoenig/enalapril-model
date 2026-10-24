"""Simulation experiment of the study Lees1987a."""

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


class Lees1987a(EnalaprilSimulationExperiment):
    """Simulation experiment of Lees1987a.

    6 young (22-31 yr, men, BW 68 kg, creatinine clearance 124 ml/min) and 6
    elderly (65-78 yr, 4 women, BW 65 kg, creatinine clearance 64 ml/min)
    healthy subjects, a tablet of 10 mg enalapril maleate once daily for 8
    days (0-168 hr), an overnight fast before days 1 and 8. Supine blood
    pressure and heart rate (Fig1), serum enalaprilat (RIA) and the
    inhibition of the plasma ACE activity (Fig2) on days 1 and 8 (mean ± SD).
    The elderly have an isolated systolic hypertension (180/96 mmHg) and the
    renal function of their age, the model describes them by the creatinine
    clearance. The references of the blood pressure are the predose values of
    the groups; the heart rate is a constant input of the model and is not
    set (it changes the cardiac output and with it the clearance).
    """

    groups: ClassVar[dict[str, str]] = {"Y": "young", "E": "elder"}
    colors: ClassVar[dict[str, str]] = {
        "Y": EnalaprilSimulationExperiment.renal_colors["Normal renal function"],
        "E": EnalaprilSimulationExperiment.renal_colors["Mild renal impairment"],
    }
    #: creatinine clearance [ml/min]
    crcl: ClassVar[dict[str, float]] = {"Y": 124, "E": 64}
    SBP_refs: ClassVar[dict[str, float]] = {"Y": 118.63, "E": 180.88}
    DBP_refs: ClassVar[dict[str, float]] = {"Y": 59.59, "E": 95.87}
    body_weights: ClassVar[dict[str, float]] = {"Y": 68.0, "E": 65.0}  # [kg]
    #: the study days of the data [hr]: the first and the last dose
    days: ClassVar[dict[str, tuple[float, float]]] = {
        "day1": (0, 100),
        "day8": (100, 200),
    }
    #: the data by the observable
    info: ClassVar[dict[str, str]] = {
        "[Cve_eat]": "enalaprilat",
        "ace_inhibition": "ACE inhibition",
        "SBP": "blood pressure systolic",
        "DBP": "blood pressure diastolic",
        "HR": "heart rate",
    }
    tissues: ClassVar[dict[str, Tissue]] = {
        "[Cve_eat]": Tissue.SERUM,
        "ace_inhibition": Tissue.PLASMA,
        "SBP": Tissue.NONE,
        "DBP": Tissue.NONE,
        "HR": Tissue.NONE,
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1", "Fig2"]:
            df = self.load_dataframe(fig_id)
            # the enalaprilat at -0.04 hr is before the first dose, i.e., before
            # the start of the simulation
            df = df[df["time"] >= 0]
            for label, df_label in df.groupby("label"):
                label = str(label)
                for day, (tmin, tmax) in self.days.items():
                    df_day = df_label[df_label["time"].between(tmin, tmax)]
                    dset = DataSet.from_df(df_day, self.ureg)
                    if label.endswith("_enalaprilat"):
                        dset.unit_conversion("mean", 1 / self.Mr.eat)
                    dsets[self.to_sid(f"{label}_{day}")] = dset

        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        # enalapril maleate
        dose = {"PODOSE_ena": Q(10, "mg") * self.Mr.ena / self.Mr.enamal}
        for group in self.groups:
            simulations[self.to_sid(f"po_ENA10_{group}")] = Simulation(
                time_unit="hr",
                end=198,
                preinit_changes={
                    **self.default_changes(),
                    "BW": Q(self.body_weights[group], "kg"),
                    "SBP_ref": Q(self.SBP_refs[group], "mmHg"),
                    "DBP_ref": Q(self.DBP_refs[group], "mmHg"),
                    "KI__f_renal_function": Q(self.crcl[group] / 101, "dimensionless"),
                    **dose,
                },
                changes=[self.add_doses([24 * k for k in range(1, 8)], dose)],
            )
        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for group, group_name in self.groups.items():
            for sid, name in self.info.items():
                for day in self.days:
                    key = f"fm_lees1987a_po_ENA10_{group_name}_{day}_{name}"
                    mappings[self.to_sid(key)] = FitMapping(
                        self,
                        reference=FitData(
                            self,
                            dataset=self.to_sid(f"{group_name}_{name}_{day}"),
                            xid="time",
                            yid="mean",
                            yid_sd="mean_sd",
                            count="count",
                        ),
                        observable=FitData(
                            self,
                            task=self.to_sid(f"task_po_ENA10_{group}"),
                            xid="time",
                            yid=sid,
                        ),
                        metadata=PKPDMappingMetaData(
                            tissue=self.tissues[sid],
                            route=Route.PO,
                            application_form=ApplicationForm.TABLET,
                            dosing=Dosing.MULTIPLE,
                            health=Health.HEALTHY,
                            genotype=Genotype.NR,
                            fasting=Fasting.FASTED,
                            data=PKPDData.PK if sid == "[Cve_eat]" else PKPDData.PD,
                            data_type=DataType.MEAN,
                        ),
                    )

        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        return {
            **self._figure("Fig1", ["SBP", "DBP", "HR"]),
            **self._figure("Fig2", ["[Cve_eat]", "ace_inhibition"]),
        }

    def _figure(self, fig_id: str, sids: list[str]) -> dict[str, Figure]:
        """Figure of the observables on days 1 and 8 (one row per observable)."""
        fig = Figure(
            experiment=self,
            sid=fig_id,
            num_rows=len(sids),
            num_cols=2,
            name=f"{self.__class__.__name__}",
            settings={"legend_scope": "row"},
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        for ks, sid in enumerate(sids):
            for kd, day in enumerate(self.days):
                plot = plots[2 * ks + kd]
                plot.set_yaxis(self.labels[sid], unit=self.units[sid])
                start = 0 if day == "day1" else 168
                plot.set_xaxis(
                    f"{self.labels['time']} ({'day 1' if day == 'day1' else 'day 8'})",
                    unit=self.units["time"],
                    min=start - 1,
                    max=start + 25,
                )
                for group, group_name in self.groups.items():
                    plot.add_data(
                        task=self.to_sid(f"task_po_ENA10_{group}"),
                        xid="time",
                        yid=sid,
                        label=group_name,
                        color=self.colors[group],
                    )
                    plot.add_data(
                        dataset=self.to_sid(f"{group_name}_{self.info[sid]}_{day}"),
                        xid="time",
                        yid="mean",
                        yid_sd="mean_sd",
                        count="count",
                        label=group_name,
                        color=self.colors[group],
                        marker=self.age_markers[group],
                    )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Lees1987a, output_dir=Lees1987a.__name__)
