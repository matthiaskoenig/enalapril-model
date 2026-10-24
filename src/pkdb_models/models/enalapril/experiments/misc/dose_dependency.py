"""Dependency of the pharmacokinetics and pharmacodynamics on the dose."""

from typing import ClassVar, override

from sbmlsim import Q
from sbmlsim.plot import Axis, Figure
from sbmlsim.simulation import Simulation

from pkdb_models.models.enalapril import MODEL
from pkdb_models.models.enalapril.experiments.base_experiment import (
    EnalaprilSimulationExperiment,
)


class DoseDependencyExperiment(EnalaprilSimulationExperiment):
    """Doses of enalapril (PO, IV) and infusions of enalaprilat (IV)."""

    doses: ClassVar[list[float]] = [2.5, 5, 10, 20, 40]  # [mg]
    #: the applications of the doses: the prefix of their simulations and
    #: their label, by the key of the figures
    applications: ClassVar[dict[str, tuple[str, str]]] = {
        "PO": ("ena_PO", "mg enalapril maleate PO"),
        "IV": ("ena_IV", "mg enalapril IV"),
        "IVeat": ("eat_IV", "mg enalaprilat IV"),
    }
    # infusion rates of enalaprilat [µg/min/kg]
    infusion_rates: ClassVar[list[float]] = [0.2, 0.4, 0.6, 0.8, 1.0]
    colors: ClassVar[list[str]] = [
        "black",
        "tab:blue",
        "tab:orange",
        "tab:green",
        "tab:red",
        "tab:purple",
    ]

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}
        bodyweight = Q(70, "kg")

        for dose in self.doses:
            simulations[self.to_sid(f"ena_PO_{dose}")] = Simulation(
                time_unit="hr",
                end=24,
                preinit_changes={
                    **self.default_changes(),
                    # enalapril maleate
                    "PODOSE_ena": Q(dose, "mg") * self.Mr.ena / self.Mr.enamal,
                },
            )
            simulations[self.to_sid(f"ena_IV_{dose}")] = Simulation(
                time_unit="hr",
                end=24,
                preinit_changes={
                    **self.default_changes(),
                    "IVDOSE_ena": Q(dose, "mg"),  # enalapril
                },
            )
            simulations[self.to_sid(f"eat_IV_{dose}")] = Simulation(
                time_unit="hr",
                end=24,
                preinit_changes={
                    **self.default_changes(),
                    "IVDOSE_eat": Q(dose, "mg"),  # enalaprilat
                },
            )
        for rid in self.infusion_rates:
            simulations[self.to_sid(f"eat_IVRi_{rid}")] = Simulation(
                time_unit="hr",
                end=24,
                preinit_changes={
                    **self.default_changes(),
                    "Ri_eat": Q(rid, "µg/min/kg") * bodyweight,  # enalaprilat
                },
            )

        return simulations

    @override
    def figures(self) -> dict[str, Figure]:
        return {
            **self.pk_figures(),
            **self.pd_figures(),
        }

    def pk_figures(self) -> dict[str, Figure]:
        """Timecourses of the concentrations and the amounts in urine."""
        figures = []
        sids = ["ena", "eat"]

        # the doses of enalapril (PO, IV) and enalaprilat (IV)
        for route, (prefix, unit) in self.applications.items():
            name = f"Dependency of timecourses on the dose ({unit})"
            fig = Figure(
                experiment=self,
                sid=self.to_sid(f"Fig_pk_application_{route}"),
                num_rows=2,
                num_cols=len(sids),
                name=name,
                settings={"legend_scope": "row"},
            )
            plots = fig.create_plots(xaxis=Axis("time", unit="hr"), legend=True)

            for k, sid in enumerate(sids):
                plots[k].set_yaxis(
                    label=self.labels[f"[Cve_{sid}]"], unit=self.units[f"[Cve_{sid}]"]
                )
                plots[len(sids) + k].set_yaxis(
                    label=self.labels[f"Aurine_{sid}"], unit=self.units[f"Aurine_{sid}"]
                )

            for k, sid in enumerate(sids):
                for kdose, dose in enumerate(self.doses):
                    plots[k].add_data(
                        task=self.to_sid(f"task_{prefix}_{dose}"),
                        xid="time",
                        yid=f"[Cve_{sid}]",
                        label=f"{dose} {unit}",
                        color=self.colors[kdose],
                    )
                    plots[len(sids) + k].add_data(
                        task=self.to_sid(f"task_{prefix}_{dose}"),
                        xid="time",
                        yid=f"Aurine_{sid}",
                        label=f"{dose} {unit}",
                        color=self.colors[kdose],
                    )

            figures.append(fig)

        # infusion route (Ri)
        name_ri = "Dependency of timecourses on enalaprilat infusions (Ri)"
        fig_ri = Figure(
            experiment=self,
            sid="Fig_pk_application_Ri",
            num_rows=2,
            num_cols=len(sids),
            name=name_ri,
            settings={"legend_scope": "row"},
        )
        plots_ri = fig_ri.create_plots(xaxis=Axis("time", unit="hr"), legend=True)

        for k, sid in enumerate(sids):
            plots_ri[k].set_yaxis(
                label=self.labels[f"[Cve_{sid}]"], unit=self.units[f"[Cve_{sid}]"]
            )
            plots_ri[len(sids) + k].set_yaxis(
                label=self.labels[f"Aurine_{sid}"], unit=self.units[f"Aurine_{sid}"]
            )

        for k, sid in enumerate(sids):
            for kdose, rid in enumerate(self.infusion_rates):
                plots_ri[k].add_data(
                    task=self.to_sid(f"task_eat_IVRi_{rid}"),
                    xid="time",
                    yid=f"[Cve_{sid}]",
                    label=f"{rid} µg/min/kg IVRi",
                    color=self.colors[kdose],
                )
                plots_ri[len(sids) + k].add_data(
                    task=self.to_sid(f"task_eat_IVRi_{rid}"),
                    xid="time",
                    yid=f"Aurine_{sid}",
                    label=f"{rid} µg/min/kg IVRi",
                    color=self.colors[kdose],
                )

        figures.append(fig_ri)

        return self.figures_by_sid(*figures)

    def pd_figures(self) -> dict[str, Figure]:
        """Timecourses of the RAAS and the blood pressure."""
        figures = []
        sids = [
            "ace_inhibition",
            "ace_activity",
            "[ren]",
            "[ang1]",
            "[ang2]",
            "[ald]",
            "MAP",
            "SBP",
            "DBP",
        ]

        # the doses of enalapril (PO, IV) and enalaprilat (IV)
        for route, (prefix, unit) in self.applications.items():
            name = f"PD dose dependency ({unit})"
            fig = Figure(
                experiment=self,
                sid=self.to_sid(f"Fig_pd_application_{route}"),
                num_rows=3,
                num_cols=3,
                name=name,
                settings={"legend_scope": "row"},
            )
            plots = fig.create_plots(xaxis=Axis("time", unit="hr"), legend=True)

            for k, sid in enumerate(sids):
                plots[k].set_yaxis(label=self.labels[sid], unit=self.units[sid])

            for k, sid in enumerate(sids):
                for kdose, dose in enumerate(self.doses):
                    plots[k].add_data(
                        task=self.to_sid(f"task_{prefix}_{dose}"),
                        xid="time",
                        yid=sid,
                        label=f"{dose} {unit}",
                        color=self.colors[kdose],
                    )
            figures.append(fig)

        # infusion route (Ri)
        name_ri = "PD dose dependency (enalaprilat infusions, Ri)"
        fig_ri = Figure(
            experiment=self,
            sid="Fig_pd_application_Ri",
            num_rows=3,
            num_cols=3,
            name=name_ri,
            settings={"legend_scope": "row"},
        )
        plots_ri = fig_ri.create_plots(xaxis=Axis("time", unit="hr"), legend=True)

        for k, sid in enumerate(sids):
            plots_ri[k].set_yaxis(label=self.labels[sid], unit=self.units[sid])

        for k, sid in enumerate(sids):
            for kdose, rid in enumerate(self.infusion_rates):
                plots_ri[k].add_data(
                    task=self.to_sid(f"task_eat_IVRi_{rid}"),
                    xid="time",
                    yid=sid,
                    label=f"{rid} µg/min/kg IVRi",
                    color=self.colors[kdose],
                )

        figures.append(fig_ri)

        return self.figures_by_sid(*figures)


if __name__ == "__main__":
    MODEL.run_experiments(
        DoseDependencyExperiment, output_dir=DoseDependencyExperiment.__name__
    )
