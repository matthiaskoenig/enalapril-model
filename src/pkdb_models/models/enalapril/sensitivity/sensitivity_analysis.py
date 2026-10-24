"""Sensitivity analysis of the enalapril model.

The outputs are the pharmacokinetic parameters of enalapril and enalaprilat
after a single oral dose of 10 mg enalapril maleate (the non-compartmental
analysis of `pkpdutils`)
and the extremes of the pharmacodynamics: the ACE inhibition, angiotensin II,
renin and the mean arterial pressure. The parameters are the parameters of the
model with bounds of +-15 % around their value. The analyses are run as a
script, the local analysis by default:

    python -m pkdb_models.models.enalapril.sensitivity.sensitivity_analysis
    python -m pkdb_models.models.enalapril.sensitivity.sensitivity_analysis local sampling

The analyses run on `pkpdsim.sensitivity.SensitivityRunner`, which writes the
table of the parameters into `results/sensitivity` of the model and the tables
and figures of an analysis into `results/sensitivity/<analysis>`.
An analysis does not vary a parameter which one of its groups sets
(`pkpdsim.sensitivity.free_parameters`): `sampling`, over the seven groups,
leaves out `KI__f_renal_function` (`f_cirrhosis` is zero in the control and
not a parameter of the analyses). The environment variable
`PKPDSIM_SENSITIVITY_N` replaces the numbers of samples of the global analyses
for a quick run, see `pkpdsim.sensitivity.sample_size`.

The model without enalapril is stationary, so the simulation of a group starts
with the dose. The dose is followed for `END_HR` hours, long enough for the
terminal phase of enalaprilat, its release from tissue ACE (a half-life of
about 30 hr, 50 hr in severe renal impairment).
"""

from collections.abc import Callable, Mapping

import numpy as np
from pkpdsim.sensitivity import (
    FastAnalysis,
    LocalAnalysis,
    ParameterType,
    SamplingAnalysis,
    SensitivityGroup,
    SensitivityOutput,
    SensitivityParameter,
    SensitivityRunner,
    SobolAnalysis,
    parameters_from_sbml,
    set_bounds,
    set_relative_bounds,
)
from pkpdutils import NCAOptions
from sbmlsim import Q
from sbmlsim.simulation import PK, Custom, Formula, Simulation

from pkdb_models.models.enalapril import MODEL, MODEL_PATH
from pkdb_models.models.enalapril.experiments.base_experiment import (
    EnalaprilSimulationExperiment,
)
from pkdb_models.models.enalapril.fitting.parameters import (
    parameters_all as fit_parameters,
)

_E = EnalaprilSimulationExperiment
#: oral dose of the analysis, 10 mg enalapril maleate as enalapril [mg]
DOSE_ENA = float((Q(10, "mg") * _E.Mr.ena / _E.Mr.enamal).to("mg").magnitude)
#: the hours after the dose
END_HR = 240
#: the limit of quantification of the non-compartmental analysis [mM], about
#: 1e-6 of the maximal concentrations of enalapril and enalaprilat after 10 mg
#: enalapril maleate (1e-4 mM), so that the noise of the integrator is not the
#: terminal phase
LLOQ = 1e-10
#: fraction of the bounds of a parameter relative to its value
BOUNDS_FRACTION = 0.15

#: outputs of the non-compartmental analysis of enalapril -> unit of the output
PK_OUTPUTS_ENA: dict[str, str] = {
    "auc_inf_obs": "mM*min",
    "cmax": "mM",
    "thalf": "min",
    "vz_f": "l",
    "cl_f": "ml/min",
}
#: outputs of the non-compartmental analysis of enalaprilat, the metabolite of
#: the dose: no clearance or volume -> unit of the output
PK_OUTPUTS_EAT: dict[str, str] = {
    "auc_inf_obs": "mM*min",
    "cmax": "mM",
    "tmax": "min",
    "thalf": "min",
}
#: the outputs whose unit has the amount of the dose: the dose is a mass
#: (`PODOSE_ena` in mg), so they are divided by the molecular weight (its value
#: at the start, a value per simulation like the parameter of the analysis)
PK_PER_DOSE_MASS: frozenset[str] = frozenset({"vz_f", "cl_f"})


def max_after_dose(time: np.ndarray, values: dict[str, np.ndarray]) -> float:
    """Get the maximum of a timecourse after the dose (time 0)."""
    (x,) = values.values()
    return float(np.max(x[time >= 0]))


def min_after_dose(time: np.ndarray, values: dict[str, np.ndarray]) -> float:
    """Get the minimum of a timecourse after the dose (time 0)."""
    (x,) = values.values()
    return float(np.min(x[time >= 0]))


#: the extremes of the pharmacodynamics after the dose: id -> function,
#: selection, unit
EXTREMES: dict[
    str, tuple[Callable[[np.ndarray, dict[str, np.ndarray]], float], str, str]
] = {
    "max_ace_inhibition": (max_after_dose, "ace_inhibition", "dimensionless"),
    "min_ang2_ratio": (min_after_dose, "ang2_ratio", "dimensionless"),
    "max_ren_ratio": (max_after_dose, "ren_ratio", "dimensionless"),
    "min_MAP_change": (min_after_dose, "MAP_change", "mmHg"),
}

#: the outputs with their ids and names
OUTPUTS: list[SensitivityOutput] = [
    SensitivityOutput("ena_auc_inf_obs", "enalapril AUC∞"),
    SensitivityOutput("ena_cmax", "enalapril Cmax"),
    SensitivityOutput("ena_thalf", "enalapril Half-life"),
    SensitivityOutput("ena_vz_f", "enalapril Vz/F"),
    SensitivityOutput("ena_cl_f", "enalapril CL/F"),
    SensitivityOutput("eat_auc_inf_obs", "enalaprilat AUC∞"),
    SensitivityOutput("eat_cmax", "enalaprilat Cmax"),
    SensitivityOutput("eat_tmax", "enalaprilat tmax"),
    SensitivityOutput("eat_thalf", "enalaprilat Half-life"),
    SensitivityOutput("max_ace_inhibition", "max ACE inhibition"),
    SensitivityOutput("min_ang2_ratio", "min angiotensin II ratio"),
    SensitivityOutput("max_ren_ratio", "max renin ratio"),
    SensitivityOutput("min_MAP_change", "change mean arterial pressure"),
]


def _pk_observables(sid: str, outputs: Mapping[str, str]) -> list:
    """Get the non-compartmental analysis of a substance and its outputs."""
    pk_id = f"pk_{sid}"
    return [
        PK(
            pk_id,
            f"[Cve_{sid}]",
            dose="PODOSE_ena",
            route="oral",
            options=NCAOptions(lloq=LLOQ),
            parameters=list(outputs),
        ),
        *(
            Formula(
                f"{sid}_{key}",
                f"{pk_id}.{key} / at(Mr_ena, 0)"
                if key in PK_PER_DOSE_MASS
                else f"{pk_id}.{key}",
                unit=unit,
            )
            for key, unit in outputs.items()
        ),
    ]


#: the observables of a simulation, the outputs with their units; the ids of
#: the analyses (`pk_ena`, `pk_eat`) are no species of the model
OBSERVABLES = [
    *_pk_observables("ena", PK_OUTPUTS_ENA),
    *_pk_observables("eat", PK_OUTPUTS_EAT),
    *(
        Custom(key, function, unit, symbols=[selection])
        for key, (function, selection, unit) in EXTREMES.items()
    ),
]

#: the output times [hr]: every 0.02 hr in the first day after the dose
#: (absorption and maximum), every 0.5 hr after it
TIMES_HR: tuple[float, ...] = tuple(
    np.unique(
        np.concatenate(
            [
                np.linspace(0, 24, 1201),
                np.linspace(24, END_HR, 2 * (END_HR - 24) + 1),
            ]
        )
    ).tolist()
)


def sensitivity_simulation(changes: Mapping[str, float]) -> Simulation:
    """Get the simulation of a group: a single oral dose of enalapril at time 0."""
    return Simulation(
        start=0,
        end=END_HR,
        times=TIMES_HR,
        time_unit="hr",
        preinit_changes={**changes, "PODOSE_ena": Q(DOSE_ENA, "mg")},
    )


#: the groups the analyses are run for: the control, the stages of renal
#: impairment and of cirrhosis of the simulation experiments
SENSITIVITY_GROUPS: list[SensitivityGroup] = [
    SensitivityGroup("control", "Control", sensitivity_simulation({}), "dimgrey"),
    *(
        SensitivityGroup(
            uid,
            name,
            sensitivity_simulation({"KI__f_renal_function": _E.renal_map[name]}),
            _E.renal_colors[name],
        )
        for uid, name in [
            ("mildRI", "Mild renal impairment"),
            ("modRI", "Moderate renal impairment"),
            ("sevRI", "Severe renal impairment"),
        ]
    ),
    *(
        SensitivityGroup(
            uid,
            name,
            sensitivity_simulation({"f_cirrhosis": _E.cirrhosis_map[name]}),
            _E.cirrhosis_colors[name],
        )
        for uid, name in [
            ("mildCirrhosis", "Mild cirrhosis"),
            ("moderateCirrhosis", "Moderate cirrhosis"),
            ("severeCirrhosis", "Severe cirrhosis"),
        ]
    ),
]


def sensitivity_parameters() -> list[SensitivityParameter]:
    """Get the parameters of the analyses with their bounds and references."""
    parameters = parameters_from_sbml(
        MODEL_PATH,
        exclude_ids={
            # conversion factors
            "conversion_min_per_day",
            # molecular weights
            "Mr_ena",
            "Mr_eat",
            # reference values
            "BW_ref",
            # unchangeable values
            "FQlu",
            "FVhv",
            "FVpo",
            # dosing parameters
            "PODOSE_ena",
            "IVDOSE_ena",
            "IVDOSE_eat",
            "ti_ena",
            "ti_eat",
            "Ri_ena",
            "Ri_eat",
            # unused volumes
            "Vurine",
            "Vfeces",
            "Vstomach",
            # the maximal inhibition is complete (1), above 1 the activity of
            # ACE would be negative
            "ANG1ANG2_Emax_eat",
        },
        exclude_na=True,
        exclude_zero=True,
    )

    # the fitted parameters, their bounds are set relative to the value below
    set_bounds(
        parameters,
        [(fp.pid, np.nan, np.nan, ParameterType.FIT) for fp in fit_parameters],
    )
    # the scaling factors of the organ functions
    set_bounds(
        parameters,
        [
            (uid, 1 - BOUNDS_FRACTION, 1 + BOUNDS_FRACTION, ParameterType.SCALING)
            for uid in ["f_cardiac_function", "KI__f_renal_function"]
        ],
    )

    # the references of the values from the literature
    references = {
        "BW": r"\cite{Ogden2004, Jones2013, Thompson2009, Brown1997}",
        "FQgu": r"\cite{Jones2013, Thompson2009, Brown1997}",
        "FQh": r"\cite{Jones2013, Wynne1989, Thompson2009, Brown1997}",
        "FQki": r"\cite{Jones2013, Thompson2009, Brown1997}",
        "FVar": r"\cite{Jones2013, Thompson2009, Brown1997}",
        "FVgu": r"\cite{Jones2013, Thompson2009, Brown1997}",
        "FVki": r"\cite{Jones2013, Thompson2009, Brown1997}",
        "FVli": r"\cite{Jones2013, Wynne1989, Thompson2009, Brown1997}",
        "FVlu": r"\cite{Jones2013, Thompson2009, Brown1997}",
        "FVve": r"\cite{Jones2013, Thompson2009, Brown1997}",
        "COBW": r"\cite{Cattermole2017, Patel2021, Collis2001}",
        "KI__f_renal_function": r"\cite{Stevens2024}",
    }
    by_uid = {p.uid: p for p in parameters}
    for uid, reference in references.items():
        p = by_uid[uid]
        p.reference = reference
        if p.type == ParameterType.NA:
            p.type = ParameterType.DATA

    # every parameter without bounds varies around its value
    set_relative_bounds(parameters, BOUNDS_FRACTION)
    return parameters


#: the analyses of the script, with their groups and numbers of samples
SENSITIVITY = SensitivityRunner(
    model=MODEL,
    parameters=sensitivity_parameters,
    outputs=OUTPUTS,
    observables=OBSERVABLES,
    analyses={
        "local": LocalAnalysis(groups=SENSITIVITY_GROUPS[:1], delta=0.01),
        "sampling": SamplingAnalysis(groups=SENSITIVITY_GROUPS, n=1000),
        "fast": FastAnalysis(groups=SENSITIVITY_GROUPS[:1], n=1000),
        "sobol": SobolAnalysis(groups=SENSITIVITY_GROUPS[:1], n=4096),
    },
    default=("local",),
)


if __name__ == "__main__":
    SENSITIVITY.main()
