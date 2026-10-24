"""Effect of enalaprilat on the renin-angiotensin-aldosterone system (RAAS)."""

from typing import ClassVar, override

import numpy as np
from sbmlsim import Q
from sbmlsim.plot import Axis, Figure
from sbmlsim.simulation import Change, Simulation

from pkdb_models.models.enalapril import MODEL
from pkdb_models.models.enalapril.experiments.raas_experiment import (
    RaasSimulationExperiment,
)


class RaasExperiment(RaasSimulationExperiment):
    """Concentrations of enalaprilat for 5 hr after a baseline of 5 hr.

    The concentrations are those of the plasma after the doses of the studies
    (3-300 nM), around the EC50 of the ACE inhibition (13 nM, 4.5 ng/ml, fitted).
    """

    eat_unit = "nM"
    eat_values: ClassVar[np.ndarray] = np.array([0.0, 3.0, 10.0, 30.0, 100.0, 300.0])
    colors: ClassVar[list[str]] = [
        "black",
        "tab:blue",
        "tab:orange",
        "tab:red",
        "tab:brown",
        "tab:green",
    ]

    @override
    def simulations(self) -> dict[str, Simulation]:
        simulations = {}

        for k, eat in enumerate(self.eat_values):
            # enalaprilat for 5 hr after a baseline of 5 hr, then 24 hr without
            simulations[f"raas_{k}"] = Simulation(
                time_unit="min",
                end=34 * 60,
                time_shift=-5 * 60,
                preinit_changes={
                    **self.default_changes(),
                    "[eat]": Q(0, self.eat_unit),
                },
                changes=[
                    Change(5 * 60, {"[eat]": Q(eat, self.eat_unit)}),
                    Change(10 * 60, {"[eat]": Q(0, self.eat_unit)}),
                ],
            )

        return simulations

    @override
    def figures(self) -> dict[str, Figure]:
        # the output and the index of its panel
        info = [
            ("[eat]", 0),  # enalaprilat in Vplasma
            ("[ace]", 1),  # ACE concentration
            ("ace_inhibition", 2),  # ACE inhibition
            ("[anggen]", 3),  # angiotensinogen in Vplasma
            ("[ang1]", 4),  # angiotensin I in Vplasma
            ("[ang2]", 5),  # angiotensin II in Vplasma
            ("ANGGEN2ANG1", 6),  # angiotensinogen to angiotensin I (renin)
            ("ANG1ANG2", 7),  # angiotensin I to angiotensin II (ACE)
            ("ANG1DEG", 7),  # angiotensin I degradation (ANG1DEG), dashed
            ("ANG2DEG", 8),  # angiotensin II degradation (ANG2DEG)
            ("[ren]", 9),  # renin in Vplasma
            ("RENSEC", 10),  # renin secretion (RENSEC)
            ("RENDEG", 11),  # renin degradation (RENDEG)
            ("[ald]", 12),  # aldosterone in Vplasma
            ("ALDSEC", 13),  # aldosterone secretion (ALDSEC)
            ("ALDDEG", 14),  # aldosterone degradation (ALDDEG)
            ("SBP", 15),
            ("MAP", 15),
            ("DBP", 15),
            ("SBP_change", 16),
            ("DBP_change", 16),
            ("SBP_ratio", 17),
            ("DBP_ratio", 17),
        ]
        # the blood pressures share a panel, their axis names all of them
        shared_axes = {
            7: ("ANG1ANG2, ANG1DEG", "pmol/min"),
            15: ("SBP, MAP, DBP", "mmHg"),
            16: ("SBP, DBP change", "mmHg"),
            17: ("SBP, DBP ratio", "dimensionless"),
        }

        sid = "Fig_RAAS"
        fig = Figure(
            experiment=self,
            sid=sid,
            num_rows=6,
            num_cols=3,
            name="RAAS",
        )
        # every panel draws the same concentrations of enalaprilat, which the legend
        # of the first panel names; a legend in every panel would cover the curves
        plots = fig.create_plots(xaxis=Axis("time", unit="hour"), legend=False)
        plots[0].legend = True

        for yid, kplot in info:
            label, unit = shared_axes.get(kplot, (self.labels[yid], self.units[yid]))
            plots[kplot].set_yaxis(label=label, unit=unit)
            for k, eat in enumerate(self.eat_values):
                plots[kplot].add_data(
                    task=f"task_raas_{k}",
                    xid="time",
                    yid=yid,
                    label=f"{eat:g} {self.eat_unit}" if kplot == 0 else None,
                    color=self.colors[k],
                    linestyle="dashed" if yid == "ANG1DEG" else "solid",
                )

        return {sid: fig}


if __name__ == "__main__":
    MODEL.run_experiments(RaasExperiment, output_dir=RaasExperiment.__name__)
