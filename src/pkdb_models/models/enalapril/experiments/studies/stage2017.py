"""Simulation experiment of the study Stage2017."""

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


class Stage2017(EnalaprilSimulationExperiment):
    """Simulation experiment of Stage2017.

    43 healthy Danish subjects of six CES1 genotype groups, a single tablet of
    10 mg enalapril maleate after an overnight fast, 1 hr after a standardized
    breakfast. The concentrations are medians of the groups (no dispersion),
    the BW and height medians of the groups (Table 1).
    """

    groups: ClassVar[list[str]] = [
        "control",
        "copies4",
        "copies_normal3",
        "copies_active3",
        "G143E",
        "CES1A1c",
    ]

    #: the names of the groups in the legends
    legends: ClassVar[dict[str, str]] = {
        "control": "control",
        "copies4": "4 CES1 copies",
        "copies_normal3": "3 CES1 copies, normal",
        "copies_active3": "3 CES1 copies, active",
        "G143E": "G143E",
        "CES1A1c": "CES1A1c",
    }

    genotypes: ClassVar[dict[str, Genotype]] = {
        "control": Genotype.CES1_WILD_TYPE,
        # gene duplications (no effect on the hydrolysis, see `ces1_map`)
        "copies4": Genotype.CES1_GAIN_OF_FUNCTION,
        "copies_normal3": Genotype.CES1_GAIN_OF_FUNCTION,
        "copies_active3": Genotype.CES1_GAIN_OF_FUNCTION,
        # G143E heterozygous; CES1A1c homozygous (no change of the protein)
        "G143E": Genotype.CES1_LOSS_OF_FUNCTION,
        "CES1A1c": Genotype.CES1_LOSS_OF_FUNCTION,
    }
    bodyweights: ClassVar[dict[str, float]] = {
        "control": 67.0,
        "copies4": 71.0,
        "copies_normal3": 61.0,
        "copies_active3": 68.5,
        "G143E": 68.0,
        "CES1A1c": 66.0,
    }
    heights: ClassVar[dict[str, float]] = {
        "control": 171,
        "copies4": 175,
        "copies_normal3": 171,
        "copies_active3": 186.5,
        "G143E": 178,
        "CES1A1c": 171,
    }
    #: the substances of the data by observable
    info: ClassVar[dict[str, str]] = {
        "[Cve_ena]": "enalapril",
        "[Cve_eat]": "enalaprilat",
    }

    @override
    def datasets(self) -> dict[str, DataSet]:
        dsets = {}
        for fig_id in ["Fig1", "Fig2"]:
            df = self.load_dataframe(fig_id)
            # the values below the limit of quantification (0.5 ng/ml) and before
            # the dose are curated as 0, they carry no information
            df = df[df["median"] > 0]
            for label, df_label in df.groupby("label"):
                label = str(label)
                dset = DataSet.from_df(df_label, self.ureg)
                if label.endswith("_enalapril"):
                    dset.unit_conversion("median", 1 / self.Mr.ena)
                elif label.endswith("_enalaprilat"):
                    dset.unit_conversion("median", 1 / self.Mr.eat)
                dsets[self.to_sid(label)] = dset
        return dsets

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        for group in self.groups:
            simulations[self.to_sid(f"po_ENA10{group}")] = Simulation(
                time_unit="hr",
                end=72,
                preinit_changes={
                    **self.default_changes(),
                    "BW": Q(self.bodyweights[group], "kg"),
                    "HEIGHT": Q(self.heights[group], "cm"),
                    # CES1 activity
                    "LI__f_ces1": Q(self.ces1_map[group], "dimensionless"),
                    # dosed 1 hr after a standardized breakfast: the stomach is
                    # in the fed state (the medians of the enalapril Cmax are
                    # about half of those of fasted studies, e.g. Tarkiainen2015)
                    "GU__fed": Q(self.fasting_map["fed"], "dimensionless"),
                    # enalapril maleate
                    "PODOSE_ena": Q(10, "mg") * self.Mr.ena / self.Mr.enamal,
                },
            )

        return simulations

    @override
    def fit_mappings(self) -> dict[str, FitMapping]:
        mappings = {}
        for group in self.groups:
            for sid, name in self.info.items():
                mappings[self.to_sid(f"fm_po_ENA10{group}_{name}")] = FitMapping(
                    self,
                    reference=FitData(
                        self,
                        dataset=self.to_sid(f"{group}_{name}"),
                        xid="time",
                        # medians without dispersion
                        yid="median",
                        yid_sd=None,
                        count="count",
                    ),
                    observable=FitData(
                        self,
                        task=self.to_sid(f"task_po_ENA10{group}"),
                        xid="time",
                        yid=sid,
                    ),
                    metadata=PKPDMappingMetaData(
                        tissue=Tissue.PLASMA,
                        route=Route.PO,
                        application_form=ApplicationForm.TABLET,
                        dosing=Dosing.SINGLE,
                        health=Health.HEALTHY,
                        genotype=self.genotypes[group],
                        fasting=Fasting.FED,
                        data=PKPDData.PK,
                    ),
                )
        return mappings

    @override
    def figures(self) -> dict[str, Figure]:
        fig = Figure(
            experiment=self,
            sid="Fig1_Fig2",
            num_rows=2,
            num_cols=2,
            name=f"{self.__class__.__name__}",
        )
        plots = fig.create_plots(
            xaxis=Axis(self.labels["time"], unit=self.units["time"]), legend=True
        )
        # linear (left) and logarithmic (right) concentrations
        for krow, sid in enumerate(self.info):
            for kcol in range(2):
                plots[2 * krow + kcol].set_yaxis(
                    self.labels[sid],
                    unit=self.units[sid],
                    scale="log" if kcol == 1 else "linear",
                    # the limit of quantification is 0.5 ng/ml (1.3e-3 µM)
                    min=3e-4 if kcol == 1 else None,
                )
        # enalapril is below the limit of quantification after 9 hr
        for kp in range(2):
            plots[kp].set_xaxis(
                self.labels["time"], unit=self.units["time"], min=0, max=12
            )

        for group in self.groups:
            for krow, (sid, name) in enumerate(self.info.items()):
                for kcol in range(2):
                    kp = 2 * krow + kcol
                    plots[kp].add_data(
                        task=self.to_sid(f"task_po_ENA10{group}"),
                        xid="time",
                        yid=sid,
                        label=self.legends[group] if kp == 0 else None,
                        color=self.ces1_colors[group],
                    )
                    plots[kp].add_data(
                        dataset=self.to_sid(f"{group}_{name}"),
                        xid="time",
                        yid="median",
                        count="count",
                        label=f"{self.legends[group]} (median)" if kp == 0 else None,
                        color=self.ces1_colors[group],
                    )

        return self.figures_by_sid(fig)


if __name__ == "__main__":
    MODEL.run_experiments(Stage2017, output_dir=Stage2017.__name__)
