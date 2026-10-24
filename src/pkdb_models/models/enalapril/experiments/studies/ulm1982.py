"""Simulation experiment of the study Ulm1982."""

from typing import ClassVar, NamedTuple, override

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


class Data(NamedTuple):
    """A dataset of the study with the observable it is compared with."""

    fig_id: str
    label: str
    yid: str
    tissue: Tissue


class Ulm1982(EnalaprilSimulationExperiment):
    """Simulation experiment of Ulm1982.

    12 healthy male volunteers (69.4 kg), a single oral dose of 20 µmol
    enalapril maleate (9.8 mg, hard gelatin capsules) after an overnight fast,
    in crossover with lisinopril (not simulated). Enalapril and enalaprilat
    (MK-422) in serum by RIA (Fig2, enalapril as the difference after
    esterolysis, molar), cumulative urinary excretion 0-72 hr (Tab2, nmol) and
    the total fecal drug (Tab1 and text, 31 % of the dose, n = 11). The data of
    lisinopril of the study are not loaded.
    """

    #: the dose of enalapril maleate, 20 µmol (9.8 mg)
    dose_umol: ClassVar[float] = 20.0

    #: the datasets by their key
    study_data: ClassVar[dict[str, Data]] = {
        "enalapril": Data("Fig2", "enalapril", "[Cve_ena]", Tissue.SERUM),
        "enalaprilat": Data("Fig2", "enalaprilat", "[Cve_eat]", Tissue.SERUM),
        "enalapril_urine": Data("Tab2", "enalapril_urine", "Aurine_ena", Tissue.URINE),
        "enalaprilat_urine": Data(
            "Tab2", "enalaprilat_urine", "Aurine_eat", Tissue.URINE
        ),
        # the sum of the two series of urine above
        "enalapril_enalaprilat_urine": Data(
            "Tab2", "enalapril+enalaprilat_urine", "Aurine_ena_eat", Tissue.URINE
        ),
        # the total fecal drug, enalapril and enalaprilat; the model has only
        # the unabsorbed enalapril in the feces (enalaprilat is not secreted
        # into the gut), so the total is compared with it
        "enalapril_enalaprilat_feces": Data(
            "Tab1", "enalapril+enalaprilat_feces", "Afeces_ena", Tissue.FECES
        ),
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dfs = {
            fig_id: self.load_dataframe(fig_id) for fig_id in ["Fig2", "Tab1", "Tab2"]
        }
        dsets = {}
        for key, data in self.study_data.items():
            df = dfs[data.fig_id]
            # serum in nM, urine in nmol, feces in µmol: molar, no conversion
            dsets[self.to_sid(key)] = DataSet.from_df(
                df[df["label"] == data.label], self.ureg
            )
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        return {
            "po_enamal9p8": Simulation(
                time_unit="hr",
                end=98,
                preinit_changes={
                    **self.default_changes(),
                    "BW": Q(69.4, "kg"),
                    # 20 µmol enalapril maleate
                    "PODOSE_ena": (Q(self.dose_umol, "µmole") * self.Mr.ena).to("mg"),
                },
            )
        }

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for key, data in self.study_data.items():
            # the serum and the feces have no errors
            has_sd = data.fig_id == "Tab2"
            mappings[self.to_sid(f"fm_ulm1982_enamal9.8_{key}")] = FitMapping(
                self,
                reference=FitData(
                    self,
                    dataset=self.to_sid(key),
                    xid="time",
                    yid="mean",
                    yid_sd="mean_sd" if has_sd else None,
                    count="count",
                ),
                observable=FitData(
                    self, task="task_po_enamal9p8", xid="time", yid=data.yid
                ),
                metadata=PKPDMappingMetaData(
                    tissue=data.tissue,
                    route=Route.PO,
                    application_form=ApplicationForm.CAPSULE,
                    dosing=Dosing.SINGLE,
                    health=Health.HEALTHY,
                    genotype=Genotype.NR,
                    fasting=Fasting.FASTED,
                    data=PKPDData.PK,
                    data_type=DataType.MEAN,
                ),
            )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig1",
            num_rows=2,
            num_cols=3,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        plots[0].set_xaxis(self.labels["time"], unit=self.units["time"], min=0, max=12)
        for kp, data in enumerate(self.study_data.values()):
            plots[kp].set_yaxis(self.labels[data.yid], unit=self.units[data.yid])
        plots[5].set_yaxis("enalapril feces", unit=self.units["Afeces_ena"])

        for kp, (key, data) in enumerate(self.study_data.items()):
            plots[kp].add_data(
                task="task_po_enamal9p8",
                xid="time",
                yid=data.yid,
                label="ENA 9.8 mg",
                color=self.healthy_color,
            )
            plots[kp].add_data(
                dataset=self.to_sid(key),
                xid="time",
                yid="mean",
                yid_sd="mean_sd" if data.fig_id == "Tab2" else None,
                count="count",
                label="enalapril+enalaprilat (total fecal drug)"
                if data.tissue == Tissue.FECES
                else "ENA 9.8 mg",
                color=self.healthy_color,
            )
        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Ulm1982, output_dir=Ulm1982.__name__)
