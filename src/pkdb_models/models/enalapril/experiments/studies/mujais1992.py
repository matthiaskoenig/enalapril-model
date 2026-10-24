"""Simulation experiment of the study Mujais1992."""

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
from sbmlsim.simulation import Change, Simulation

from pkdb_models.models.enalapril import MODEL
from pkdb_models.models.enalapril.experiments.base_experiment import (
    EnalaprilSimulationExperiment,
)


class Mujais1992(EnalaprilSimulationExperiment):
    """Simulation experiment of Mujais1992.

    12 healthy men (73.3 kg, 178.6 cm, CLcr 123 ml/min) after an overnight fast:
    an i.v. loading dose of 1.5 mg enalaprilat followed by an infusion of
    0.475 µg/kg/min, total enalaprilat in plasma by RIA at 45-135 min (Fig. 1).
    The unbound fraction of enalaprilat is 0.621 and its unbound renal clearance
    222 ml/min, 1.85 times the inulin clearance (tubular secretion). The paper
    gives no end of the infusion, the last sample is at 135 min; the infusion
    is stopped at 150 min, after the data. The oral water load (20 ml/kg, water
    diuresis) is not modelled, the renal clearance of enalaprilat does not
    depend on the urine flow.
    """

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1"]:
            df = self.load_dataframe(fig_id)
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                if label.endswith("enalaprilat"):
                    dset.unit_conversion("mean", 1 / self.Mr.eat)
                dsets[label] = dset
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        bodyweight = Q(73.3, "kg")

        # enalaprilat infusion after bolus dose
        # A loading dose of enalaprilat of 1.5 mg was administered, followed
        # immediately by a sustaining infusion 0.475 µg/kg/min for ~ 2.5h.
        simulations["EATB_EATINF"] = Simulation(
            time_unit="min",
            end=210,
            preinit_changes={
                **self.default_changes(),
                "BW": bodyweight,  # body weight
                "HEIGHT": Q(178.6, "cm"),  # height
                "Ri_eat": Q(0.475, "µg/min/kg") * bodyweight,
                "IVDOSE_eat": Q(1.5, "mg"),
            },
            changes=[
                Change(
                    150,
                    {
                        "Ri_eat": Q(0, "µg/min/kg") * bodyweight,
                    },
                ),
            ],
        )
        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        mappings["fm_mujais1992_EATB_EATINF_enalaprilat"] = FitMapping(
            self,
            reference=FitData(
                self,
                dataset="enalaprilat",
                xid="time",
                yid="mean",
                yid_sd="mean_sd",
                count="count",
            ),
            observable=FitData(
                self,
                task="task_EATB_EATINF",
                xid="time",
                yid="[Cve_eat]",
            ),
            metadata=PKPDMappingMetaData(
                tissue=Tissue.PLASMA,
                route=Route.IV,
                application_form=ApplicationForm.SOLUTION,
                dosing=Dosing.CONSTANT_INFUSION,
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
            sid="Fig1",
            num_rows=1,
            num_cols=1,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_yaxis(self.labels["[Cve_eat]"], unit=self.units["[Cve_eat]"])

        # simulation
        plots[0].add_data(
            task="task_EATB_EATINF",
            xid="time",
            yid="[Cve_eat]",
            label="EAT 1.5 mg + 0.475 µg/kg/min",
            color=self.healthy_color,
        )
        # data
        plots[0].add_data(
            dataset="enalaprilat",
            xid="time",
            yid="mean",
            yid_sd="mean_sd",
            count="count",
            label="EAT 1.5 mg + 0.475 µg/kg/min",
            color=self.healthy_color,
        )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Mujais1992, output_dir=Mujais1992.__name__)
