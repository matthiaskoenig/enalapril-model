"""Pharmacokinetic and pharmacodynamic parameters of the enalapril scans.

The pharmacokinetic parameters are the non-compartmental analysis of
`pkpdutils`, named like the variables of its `NCAResult` (e.g. `auc_last`,
`auc_inf_obs`, `cmax`, `tmax`, `thalf`, `lambda_z`, `cl_f`, `vz_f`), with the
unit of every parameter in `<name>_unit`, for enalapril, enalaprilat and their
sum in the venous plasma after an oral dose of enalapril; the clearance and the
volume of all three refer to the dose of enalapril. The renal clearance
(`cl_renal`) is the amount in the urine at the end of the simulation over
`auc_last`. The concentrations below `LLOQ_FRACTION` of the maximum are below
the limit of quantification, so that the noise of the integrator is not the
terminal phase.

The pharmacodynamic parameters are the minimum and the maximum of the effects.

A scan has one dimension, the scanned parameter; a run over the draws of the
fitted parameters (`run_simulation pkdb_models.models.enalapril --uncertainty`)
adds the dimension of the draws. The parameters are calculated for every point
of every dimension, a row per point with its position along each dimension
(the columns `point` and, with draws, `draw`), see `summarize`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd
from pkpdsim.pk import nca_frame, scan_nca
from pkpdsim.scan import end_values, scan_dimensions, start_values
from pkpdutils import Route, ureg
from sbmlsim import Q
from sbmlsim.result import ScanResult

if TYPE_CHECKING:
    from pkdb_models.models.enalapril.experiments.base_experiment import (
        EnalaprilSimulationExperiment,
    )

#: oral dose of the scans
DOSE = "PODOSE_ena"
#: the substances of the pharmacokinetic parameters by the id of their
#: concentration `[Cve_<sid>]`
SUBSTANCES: dict[str, str] = {
    "ena": "enalapril",
    "eat": "enalaprilat",
    "ena_eat": "enalapril + enalaprilat",
}
#: the limit of quantification relative to the maximal concentration: the
#: terminal phase of enalaprilat (the enalaprilat bound to tissue ACE) is
#: about 1e-2 of its maximum
LLOQ_FRACTION = 1e-6
#: the effects whose minimum and maximum are the pharmacodynamic parameters
EFFECTS: list[str] = [
    "[ren]",
    "[ang1]",
    "[ang2]",
    "ace_inhibition",
    "[ald]",
    "SBP",
    "DBP",
]


def _point_dimension(res: ScanResult, across: str | None) -> str:
    """Get the dimension of the scan besides the draws `across`.

    Raises:
        ValueError: if the scan has not one dimension besides the draws.
    """
    dims = scan_dimensions(res, across)
    if len(dims) != 1:
        raise ValueError(
            f"A scan of one dimension is required, not of {dims} (draws: {across})."
        )
    return dims[0]


def _position_names(point: str, across: str | None) -> dict[str, str]:
    """Get the names of the columns of the position, `point` and `draw`."""
    return {point: "point", **({across: "draw"} if across is not None else {})}


def calculate_enalapril_pk(
    experiment: EnalaprilSimulationExperiment,
    res: ScanResult,
    across: str | None = None,
) -> pd.DataFrame:
    """Calculate the pharmacokinetic parameters of every simulation of a scan.

    The non-compartmental analysis of all simulations at once per substance
    (`pkpdsim.pk.scan_nca`), with the dose of enalapril in the substance unit
    of the concentration, which `cl_f` and `vz_f` require.

    Args:
        experiment: experiment of the scan, for the molecular weight.
        res: result of the scan.
        across: the dimension of the draws of the fitted parameters, `None`
            for a scan without draws.

    Returns:
        One row per simulation of the scan and substance, with its position
        (`point`, and `draw` with draws) and the substance, the substances of
        a simulation after each other.
    """
    point = _point_dimension(res, across)
    units = res.units
    dose_mass = Q(start_values(res, DOSE).values, units[DOSE])
    dose = (dose_mass / experiment.Mr.ena).to("mmole")
    frames = []
    for sid, substance in SUBSTANCES.items():
        result = scan_nca(
            res,
            f"[Cve_{sid}]",
            dose=dose,
            route=Route.ORAL,
            substance=substance,
            lloq_fraction=LLOQ_FRACTION,
        )
        df = nca_frame(result).drop(columns="nca_flags")
        df.insert(len(res.dims), "substance", substance)
        position = tuple(df[dim].to_numpy() for dim in res.dims)
        urine = f"Aurine_{sid}"
        amount = ureg.Quantity(
            end_values(res, urine).values[position], str(units[urine])
        )
        auc_last = ureg.Quantity(df["auc_last"].to_numpy(), df["auc_last_unit"].iloc[0])
        for key, value in [
            (urine, amount),
            ("cl_renal", (amount / auc_last).to("ml/min")),
        ]:
            df[key] = value.magnitude
            df[f"{key}_unit"] = str(value.units)
        frames.append(df)
    # the substances of a point after each other
    n = len(frames[0])
    order = np.arange(n * len(frames)).reshape(len(frames), n).T.ravel()
    df = pd.concat(frames, ignore_index=True).iloc[order].reset_index(drop=True)
    return df.rename(columns=_position_names(point, across))


def calculate_enalapril_pd(
    res: ScanResult, across: str | None = None
) -> dict[str, pd.DataFrame]:
    """Calculate the pharmacodynamic parameters of every simulation of a scan.

    The extremes of the timecourses of all simulations at once, with the state
    after a change at its time (`ScanResult.to_timecourses`).

    Args:
        res: result of the scan.
        across: the dimension of the draws of the fitted parameters, `None`
            for a scan without draws.

    Returns:
        By effect, one row per simulation with its position (`point`, and
        `draw` with draws), the minimum, the maximum and the unit.
    """
    point = _point_dimension(res, across)
    dims = list(res.dims)
    shape = tuple(res.ds.sizes[dim] for dim in dims)
    positions = np.unravel_index(np.arange(int(np.prod(shape))), shape)
    dfs: dict[str, pd.DataFrame] = {}
    for sid in EFFECTS:
        values = res.to_timecourses(sid).ds["value"]
        times = [dim for dim in values.dims if dim not in dims]
        dfs[sid] = pd.DataFrame(
            {
                **dict(zip(dims, positions, strict=True)),
                "sid": sid,
                "min": values.min(dim=times).transpose(*dims).values.ravel(),
                "max": values.max(dim=times).transpose(*dims).values.ravel(),
                "unit": str(res.units[sid]),
            }
        ).rename(columns=_position_names(point, across))
    return dfs


def summarize(
    df: pd.DataFrame, key: str, quantiles: tuple[float, float]
) -> pd.DataFrame:
    """Get the median and the quantiles of a parameter over the draws of every point.

    Args:
        df: the parameters with the columns `point` and `draw` (of one
            substance).
        key: the parameter.
        quantiles: the lower and the upper quantile.

    Returns:
        One row per point (the index), the columns `lower`, `median`, `upper`.
    """
    low, high = quantiles
    grouped = df.groupby("point")[key]
    return pd.DataFrame(
        {
            "lower": grouped.quantile(low),
            "median": grouped.median(),
            "upper": grouped.quantile(high),
        }
    ).astype(np.float64)
