"""Parameter scans of the enalapril model."""

from typing import Any, ClassVar, NamedTuple, NotRequired, TypedDict, override

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.cm import ScalarMappable
from matplotlib.colors import (
    Colormap,
    LinearSegmentedColormap,
    LogNorm,
    Normalize,
    to_hex,
)
from matplotlib.ticker import FuncFormatter
from matplotlib.typing import ColorType
from pkpdsim.scan import point_band, point_timecourse, scan_dimensions, start_values
from sbmlsim import Q
from sbmlsim.plot.serialization_matplotlib import FigureMPL
from sbmlsim.result import ScanResult
from sbmlsim.simulation import Dimension, Scan, Simulation
from sbmlsim.units import Quantity

from pkdb_models.models.enalapril import MODEL
from pkdb_models.models.enalapril.enalapril_pk import summarize
from pkdb_models.models.enalapril.experiments.base_experiment import (
    EnalaprilSimulationExperiment,
)


class ScanSpec(TypedDict):
    """Definition of a single parameter scan.

    The first value of `range` is the lowest, the last the highest; the
    default is one of the values.
    """

    parameter: str
    default: float
    range: np.ndarray
    scale: str
    units: str
    label: str
    #: the colormap, a matplotlib colormap or the colors at positions from 0
    #: to 1 along the range
    colormap: str | list[tuple[float, str]]
    #: the labels of the ticks of the colorbar, the minimum, the default and
    #: the maximum of the range without
    ticks: NotRequired[dict[float, str]]
    #: the factor from the scanned value to the value of the axes (the dose of
    #: enalapril to the dose of enalapril maleate), 1 without
    factor: NotRequired[float]


class Panel(NamedTuple):
    """A panel of the timecourses of a scan."""

    sid: str
    #: the end of the time axis [hr]
    tend: float
    #: the distance of the ticks of the time axis [hr]
    tick: float
    #: a logarithmic axis
    log: bool


def _position(value: float, vmin: float, vmax: float) -> float:
    """Get the position of a value on a logarithmic axis from vmin to vmax."""
    return float((np.log10(value) - np.log10(vmin)) / (np.log10(vmax) - np.log10(vmin)))


def _with(values: np.ndarray, *extra: float) -> np.ndarray:
    """Get the sorted values of a scan with the values `extra` added."""
    return np.unique(np.concatenate([values, np.asarray(extra, dtype=float)]))


_E = EnalaprilSimulationExperiment
#: the factor of a dose of enalapril to the dose of enalapril maleate
_MALEATE = float((_E.Mr.enamal / _E.Mr.ena).to("dimensionless").magnitude)
#: the diverging colormaps, whose light center is left out
_DIVERGING = {"RdBu", "PuOr"}


class EnalaprilParameterScan(EnalaprilSimulationExperiment):
    """Scan the effect of parameters on the pharmacokinetics and the pharmacodynamics.

    A single oral dose of 10 mg enalapril maleate (the tablet of the studies),
    simulated for 7 days: enalaprilat bound to tissue ACE is released slowly,
    its terminal phase lasts days and longer in renal impairment. The figures
    show enalapril and enalaprilat in the first day, enalaprilat in the 7 days
    after the dose (logarithmic), the excretion, the ACE inhibition, the RAAS
    and the blood pressure in the first 3 days, the pharmacokinetic parameters
    of the non-compartmental analysis (`enalapril_pk`) of enalapril and
    enalaprilat and the extremes of the pharmacodynamics over the scanned
    parameter.

    In a run over the draws of the fitted parameters (`run_simulation
    pkdb_models.models.enalapril --uncertainty`) every point of a scan is
    simulated for every draw; the figures draw the median of the draws with
    the band of their quantiles.
    """

    #: pharmacokinetic parameters of the scans by simulation key, set by
    #: `figures_mpl`
    pk_dfs: dict[str, pd.DataFrame]
    #: pharmacodynamic parameters of the scans by simulation key, set by
    #: `figures_mpl`
    pd_dfs: dict[str, dict[str, pd.DataFrame]]

    #: the end of the simulations [hr], 7 days
    tend = 7 * 24
    #: the output times of a run over the draws [hr]: every 0.05 hr in the
    #: first day (absorption and maximum, tmax 1 hr and 3-4 hr), every 0.5 hr
    #: after it
    times_uncertainty: ClassVar[tuple[float, ...]] = tuple(
        np.unique(
            np.concatenate([np.linspace(0, 24, 481), np.linspace(24, tend, 289)])
        ).tolist()
    )
    #: the end of the timecourses of the first day, of the pharmacodynamics
    #: and of the excretion [hr]
    tend_day = 24
    tend_pd = 72
    tend_plot = tend
    #: the decades of the logarithmic axes of the concentrations
    log_decades = 4
    #: the oral dose of the scans, enalapril maleate [mg]
    dose_enamal = 10.0
    #: the opacity of the bands of the draws of the fitted parameters
    band_alpha = 0.15

    #: the variables of the figures and of the parameters, the scanned
    #: parameters at the end
    selections = (
        "time",
        "PODOSE_ena",
        "[Cve_ena]",
        "[Cve_eat]",
        "[Cve_ena_eat]",
        "Aurine_ena",
        "Aurine_eat",
        "Aurine_ena_eat",
        "Afeces_ena",
        "ace_inhibition",
        "[ren]",
        "[ang1]",
        "[ang2]",
        "[ald]",
        "SBP",
        "DBP",
        "KI__f_renal_function",
        "f_cardiac_function",
        "f_cirrhosis",
        "LI__f_ces1",
        "GU__fed",
    )

    #: the panels of the timecourses
    panels: ClassVar[tuple[Panel, ...]] = (
        Panel("[Cve_ena]", tend_day, 4, log=False),
        Panel("[Cve_eat]", tend_day, 4, log=False),
        Panel("[Cve_eat]", tend_plot, 24, log=True),
        Panel("ace_inhibition", tend_pd, 12, log=False),
        Panel("Aurine_ena", tend_plot, 24, log=False),
        Panel("Aurine_eat", tend_plot, 24, log=False),
        Panel("Afeces_ena", tend_plot, 24, log=False),
        Panel("[ren]", tend_pd, 12, log=False),
        Panel("[ang1]", tend_pd, 12, log=False),
        Panel("[ang2]", tend_pd, 12, log=False),
        Panel("[ald]", tend_pd, 12, log=False),
        Panel("SBP", tend_pd, 12, log=False),
    )
    #: the columns of the panels of the timecourses
    ncols = 4

    #: the pharmacokinetic parameters by substance of `enalapril_pk`
    pk_parameters: ClassVar[dict[str, tuple[str, ...]]] = {
        "enalapril": ("auc_inf_obs", "cmax", "tmax", "thalf", "cl_renal"),
        "enalaprilat": ("auc_inf_obs", "cmax", "tmax", "thalf", "cl_renal"),
    }
    #: the pharmacodynamic parameters, the extreme of an effect
    pd_parameters: ClassVar[tuple[tuple[str, str], ...]] = (
        ("ace_inhibition", "max"),
        ("[ren]", "max"),
        ("[ang2]", "min"),
        ("[ald]", "min"),
        ("SBP", "min"),
        ("DBP", "min"),
    )

    scan_map: ClassVar[dict[str, ScanSpec]] = {
        "dose_scan": {
            "parameter": "PODOSE_ena",
            "default": dose_enamal,
            # the doses of enalapril maleate of the studies
            "range": np.array([1.25, 2.5, 5, 10, 20, 30, 40]) / _MALEATE,
            "factor": _MALEATE,
            "scale": "linear",
            "units": "mg",
            "label": "enalapril maleate dose [mg]",
            "colormap": "Purples",
        },
        "food_scan": {
            "parameter": "GU__fed",
            "default": 0.0,
            # fasted (0) to a high fat meal (1)
            "range": np.linspace(0, 1, num=11),
            "scale": "linear",
            "units": "dimensionless",
            "label": "fed state [-]",
            "colormap": "YlOrBr",
            "ticks": {0.0: "0\nfasted", 0.5: "0.5", 1.0: "1\nfed"},
        },
        "hepatic_scan": {
            "parameter": "f_cirrhosis",
            "default": 0.0,
            # with the degrees of the Child-Pugh classes
            "range": _with(
                np.array([0, 0.1, 0.2, 0.3, 0.5, 0.6, 0.9]),
                *_E.cirrhosis_map.values(),
            ),
            "scale": "linear",
            "units": "dimensionless",
            "label": "cirrhosis degree [-]",
            # the colors of the classes at their degrees (of 0 to 0.9)
            "colormap": [
                (0.0, "#d0e1f2"),
                *(
                    (_E.cirrhosis_map[key] / 0.9, _E.cirrhosis_colors[key])
                    for key in (
                        "Mild cirrhosis",
                        "Moderate cirrhosis",
                        "Severe cirrhosis",
                    )
                ),
                (1.0, "#002b44"),
            ],
            "ticks": {
                0.0: "0",
                _E.cirrhosis_map["Mild cirrhosis"]: "CPT A",
                _E.cirrhosis_map["Moderate cirrhosis"]: "CPT B",
                _E.cirrhosis_map["Severe cirrhosis"]: "CPT C",
            },
        },
        "renal_scan": {
            "parameter": "KI__f_renal_function",
            "default": 1.0,
            # 0.1 to 2, with the limits of the classes of the GFR
            "range": _with(
                np.array([0.1, 0.14, 0.27, 0.7, 1.4, 2.0]),
                *(v for k, v in _E.renal_map.items() if k != "End stage renal disease"),
            ),
            "scale": "log",
            "units": "dimensionless",
            "label": "renal function [-]",
            # the colors of the classes at their renal function (of 0.1 to 2),
            # light greens for a normal and an increased renal function
            "colormap": [
                (0.0, _E.renal_colors["End stage renal disease"]),
                *(
                    (_position(_E.renal_map[key], 0.1, 2), _E.renal_colors[key])
                    for key in (
                        "Severe renal impairment",
                        "Moderate renal impairment",
                        "Mild renal impairment",
                    )
                ),
                (_position(1.0, 0.1, 2), "#a1d99b"),
                (1.0, "#d9f0d3"),
            ],
            "ticks": {0.1: "0.1", 1.0: "1", 2.0: "2"},
        },
        "cardiac_scan": {
            "parameter": "f_cardiac_function",
            "default": 1.0,
            # with the cardiac function of the classes of cardiac impairment
            "range": _with(np.array([0.4, 0.8, 1.2, 1.5]), *_E.cardiac_map.values()),
            "scale": "linear",
            "units": "dimensionless",
            "label": "cardiac function [-]",
            "colormap": "RdBu",
            "ticks": {0.4: "0.4", 0.5: "CHF", 1.0: "1", 1.5: "1.5"},
        },
        "ces1_scan": {
            "parameter": "LI__f_ces1",
            "default": 1.0,
            # the hepatic activity of CES1, heterozygous G143E 0.55
            "range": _with(np.linspace(0.1, 1.0, num=10), _E.ces1_map["G143E"]),
            "scale": "linear",
            "units": "dimensionless",
            "label": "CES1 activity [-]",
            "colormap": "YlGnBu",
            "ticks": {
                0.1: "0.1",
                _E.ces1_map["G143E"]: "G143E",
                1.0: "1\n*1/*1",
            },
        },
    }

    @override
    def simulations(self) -> dict[str, Scan]:
        scans = {}
        grid: dict[str, Any] = (
            {} if self.uncertainty is None else {"times": self.times_uncertainty}
        )
        for scan_key, scan_data in self.scan_map.items():
            # the simulation does not set what the dimension scans (the dose
            # of the dose scan), the dimension would replace it
            preinit_changes = {
                **self.default_changes(),
                "PODOSE_ena": Q(self.dose_enamal / _MALEATE, "mg"),
            }
            preinit_changes.pop(scan_data["parameter"], None)
            scans[f"scan_po_{scan_key}"] = Scan(
                simulation=Simulation(
                    time_unit="hr",
                    end=self.tend,
                    preinit_changes=preinit_changes,
                    **grid,
                ),
                dimensions=[
                    Dimension(
                        "dim_scan",
                        values={
                            scan_data["parameter"]: Q(
                                scan_data["range"], scan_data["units"]
                            )
                        },
                    ),
                ],
            )

        return scans

    def _across(self) -> str | None:
        """Get the dimension of the draws of the fitted parameters, `None` without."""
        return None if self.uncertainty is None else self.uncertainty.id

    def _scanned(self, res: ScanResult, scan: ScanSpec) -> np.ndarray:
        """Get the values of the scanned parameter on the axes at the points of a scan."""
        parameter_id = scan["parameter"]
        values = start_values(res, parameter_id)
        across = self._across()
        if across is not None:
            values = values.isel({across: 0})
        scanned = Q(values.values, res.units[parameter_id]).to(scan["units"])
        return scanned.magnitude * scan.get("factor", 1.0)

    def _colormap(self, scan: ScanSpec) -> tuple[Colormap, Normalize]:
        """Get the colormap of a scan and the normalization of its values on the axes.

        The scans of the cirrhosis and of the renal function have the colors
        of the classes of the impairments (`pkpdsim.impairment`) at the values
        of the classes. The colormaps of matplotlib leave out their lightest
        colors, so that every curve is visible on white: the start of a
        sequential colormap, the center of a diverging one.
        """
        factor = scan.get("factor", 1.0)
        rmin = factor * float(scan["range"][0])
        rmax = factor * float(scan["range"][-1])
        colormap = scan["colormap"]
        if isinstance(colormap, str):
            base = matplotlib.colormaps[colormap]
            positions = (
                np.concatenate([np.linspace(0, 0.4, 128), np.linspace(0.6, 1, 128)])
                if colormap in _DIVERGING
                else np.linspace(0.3, 1.0, 256)
            )
            cmap: Colormap = LinearSegmentedColormap.from_list(
                f"{colormap}_visible", [base(v) for v in positions]
            )
        else:
            cmap = LinearSegmentedColormap.from_list("impairment", colormap)
        if scan["scale"] == "linear":
            return cmap, Normalize(vmin=rmin, vmax=rmax, clip=False)
        return cmap, LogNorm(vmin=rmin, vmax=rmax, clip=False)

    def _timecourse(
        self,
        ax: Axes,
        res: ScanResult,
        panel: Panel,
        point: dict[str, int],
        color: ColorType,
    ) -> tuple[np.ndarray, np.ndarray, float, float]:
        """Draw the timecourse of a point of a scan with the band of its draws.

        Returns:
            The time and the values (the median of the draws in a run over
            them) until the end of the panel, and the lowest value at the end
            of the panel and the highest value, of the band in a run over the
            draws.
        """
        sid = panel.sid
        run = self.uncertainty
        if run is None:
            time, values = point_timecourse(res, sid, **point)
            lower = upper = values
        else:
            time, lower, values, upper = point_band(
                res, sid, across=run.id, quantiles=run.quantiles, **point
            )
        t = Q(time, res.units["time"]).to(self.units["time"]).magnitude
        shown = t <= panel.tend

        def convert(v: np.ndarray) -> np.ndarray:
            """Get the values until the end of the panel in the unit of the figure."""
            return Q(v[shown], res.units[sid]).to(self.units[sid]).magnitude

        c, c_lower, c_upper = convert(values), convert(lower), convert(upper)
        if run is not None:
            ax.fill_between(
                t[shown],
                c_lower,
                c_upper,
                color=color,
                alpha=self.band_alpha,
                linewidth=0,
            )
        ax.plot(t[shown], c, color=color, linewidth=2.0)
        return t[shown], c, float(c_lower[-1]), float(np.max(c_upper))

    @override
    def figures_mpl(self) -> dict[str, FigureMPL]:
        """Matplotlib figures."""
        # the parameters, per draw in a run over the draws
        self.pk_dfs = self.calculate_enalapril_pk()
        self.pd_dfs = self.calculate_enalapril_pd()

        return {
            **self._figures_mpl_timecourses(),
            **self._figures_mpl_pharmacokinetics(),
            **self._figures_mpl_pharmacodynamics(),
        }

    def _colorbar(self, f: FigureMPL, axes: np.ndarray, scan: ScanSpec) -> None:
        """Draw the colorbar of a scan above its panels, the default in black."""
        cmap, norm = self._colormap(scan)
        cbar = f.colorbar(
            ScalarMappable(norm=norm, cmap=cmap),
            ax=axes.ravel().tolist(),
            location="top",
            shrink=0.4,
            aspect=30,
        )
        # the gradient as vector cells: matplotlib rasterizes it into an
        # embedded image, which some SVG viewers do not show; the edges of
        # the cells in their color close the seams between them
        if cbar.solids is not None:
            cbar.solids.set_rasterized(False)
            cbar.solids.set_edgecolor("face")
        factor = scan.get("factor", 1.0)
        rmin = factor * float(scan["range"][0])
        rmax = factor * float(scan["range"][-1])
        ticks = scan.get(
            "ticks",
            {value: f"{value:g}" for value in sorted({rmin, rmax, scan["default"]})},
        )
        cbar.ax.minorticks_off()
        cbar.set_ticks(list(ticks), labels=list(ticks.values()))
        cbar.ax.tick_params(labelsize=self.tick_font_size)
        cbar.ax.axvline(x=scan["default"], color="black", linewidth=4)
        cbar.set_label(scan["label"], size=self.tick_font_size + 3, weight="bold")

    def _figures_mpl_timecourses(self) -> dict[str, FigureMPL]:
        """Timecourses of the variables for the values of every scan.

        The default of the scanned parameter is black and drawn on top; the
        axes include the bands of the draws.
        """
        figures = {}
        nrows = len(self.panels) // self.ncols
        for scan_key, scan_data in self.scan_map.items():
            cmap, norm = self._colormap(scan_data)
            f, axes = plt.subplots(
                nrows=nrows,
                ncols=self.ncols,
                figsize=(6 * self.ncols, 5 * nrows + 1),
                dpi=150,
                layout="constrained",
                squeeze=False,
            )
            res = self.results[f"task_scan_po_{scan_key}"]
            (scandim,) = scan_dimensions(res, self._across())
            par_vec = self._scanned(res, scan_data)

            for ax, panel in zip(axes.flatten(), self.panels, strict=True):
                bottom, top = np.inf, 0.0
                default: tuple[np.ndarray, np.ndarray] | None = None
                for k_par, par in enumerate(par_vec):
                    is_default = bool(np.isclose(scan_data["default"], par))
                    color = "black" if is_default else cmap(norm(par))
                    t, c, end, cmax = self._timecourse(
                        ax, res, panel, {scandim: k_par}, color
                    )
                    top = max(top, cmax)
                    if end > 0:
                        bottom = min(bottom, end)
                    if is_default:
                        default = (t, c)

                # the default on top
                if default is not None:
                    ax.plot(*default, color="black", linewidth=2.0)

                ax.set_xlim(0, panel.tend)
                ax.set_xticks(np.arange(0, panel.tend + 1, panel.tick))
                if panel.log and top > 0:
                    # from the lowest value at the end to the highest value,
                    # at most `log_decades` below it (the lower quantile of
                    # the draws can end at zero)
                    ax.set_yscale("log")
                    floor = 10.0 ** (-self.log_decades) * top
                    ax.set_ylim(
                        max(0.5 * bottom, floor) if np.isfinite(bottom) else floor,
                        2.0 * top,
                    )
                elif panel.sid != "SBP":
                    # the blood pressure keeps the range of its values
                    ax.set_ylim(0, 1.05 * top if top > 0 else 1.0)
                unit = self.units[panel.sid].replace("dimensionless", "-")
                ax.set_xlabel(
                    f"{self.label_time} [{self.units['time']}]", fontdict=self.font
                )
                ax.set_ylabel(f"{self.labels[panel.sid]} [{unit}]", fontdict=self.font)
                ax.tick_params(axis="both", labelsize=self.tick_font_size)

            self._colorbar(f, axes, scan_data)
            figures[f"timecourse__{scan_key}"] = f

        return figures

    def _summary(
        self, df: pd.DataFrame, key: str, unit: str, target: str
    ) -> tuple[Quantity, Quantity, Quantity]:
        """Get a parameter at the points of a scan, the median and the band of the draws.

        Returns:
            The values (the median of the draws in a run over them), and the
            lower and the upper quantile, the values without draws.
        """
        run = self.uncertainty
        if run is None:
            values = Q(df[key].to_numpy(dtype=float), unit).to(target)
            return values, values, values
        summary = summarize(df, key, run.quantiles)
        median, lower, upper = (
            Q(summary[column].to_numpy(), unit).to(target)
            for column in ["median", "lower", "upper"]
        )
        return median, lower, upper

    def _parameter_panel(
        self,
        ax: Axes,
        scan: ScanSpec,
        x: np.ndarray,
        values: tuple[Quantity, Quantity, Quantity],
        ylabel: str,
        title: str | None = None,
        from_zero: bool = True,
    ) -> None:
        """Draw a parameter over the scanned parameter, with the band of the draws.

        The points have the colors of the timecourses, the default is black; a
        positive parameter has its axis from zero with `from_zero`.
        """
        cmap, norm = self._colormap(scan)
        y, y_lower, y_upper = values
        ax.axvline(x=scan["default"], color="grey", linestyle="--", zorder=1)
        if self.uncertainty is not None:
            ax.fill_between(
                x,
                y_lower.magnitude,
                y_upper.magnitude,
                color="black",
                alpha=self.band_alpha,
                linewidth=0,
            )
        ax.plot(x, y.magnitude, color="black", linewidth=2.0, zorder=2)
        colors = [
            "black" if np.isclose(v, scan["default"]) else to_hex(cmap(norm(v)))
            for v in x
        ]
        ax.scatter(
            x,
            y.magnitude,
            s=80,
            c=colors,
            edgecolors="black",
            linewidths=1.5,
            zorder=3,
        )
        ax.set_xscale(scan["scale"])
        if scan["scale"] == "log":
            # 0.1, 1 and 2 instead of the powers of ten
            ax.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:g}"))
        lower = float(np.nanmin(y_lower.magnitude))
        upper = float(np.nanmax(y_upper.magnitude))
        if from_zero and lower >= 0:
            ax.set_ylim(0, 1.1 * upper if upper > 0 else 1.0)
        ax.set_xlabel(scan["label"], fontdict=self.scan_font)
        ax.set_ylabel(ylabel, fontdict=self.scan_font)
        if title is not None:
            ax.set_title(title, fontdict=self.scan_font)
        ax.tick_params(axis="both", labelsize=self.tick_font_size)

    def _figures_mpl_pharmacokinetics(self) -> dict[str, FigureMPL]:
        """Pharmacokinetic parameters over the scanned parameter.

        A row per substance, enalapril and enalaprilat in plasma.
        """
        figures = {}
        ncols = max(len(keys) for keys in self.pk_parameters.values())
        for scan_key, scan_data in self.scan_map.items():
            f, axes = plt.subplots(
                nrows=len(self.pk_parameters),
                ncols=ncols,
                figsize=(5 * ncols, 5 * len(self.pk_parameters)),
                dpi=150,
                layout="constrained",
                squeeze=False,
            )
            sim_key = f"scan_po_{scan_key}"
            x = self._scanned(self.results[f"task_{sim_key}"], scan_data)
            df_all = self.pk_dfs[sim_key]
            for krow, (substance, keys) in enumerate(self.pk_parameters.items()):
                df = df_all[df_all.substance == substance]
                for k, ax in enumerate(axes[krow]):
                    if k >= len(keys):
                        ax.set_visible(False)
                        continue
                    pk_key = keys[k]
                    self._parameter_panel(
                        ax,
                        scan_data,
                        x,
                        self._summary(
                            df,
                            pk_key,
                            df[f"{pk_key}_unit"].iloc[0],
                            self.pk_units[pk_key],
                        ),
                        ylabel=f"{self.pk_labels[pk_key]} [{self.pk_units[pk_key]}]",
                        title=substance,
                    )
            figures[f"pk_{scan_key}"] = f

        return figures

    def _figures_mpl_pharmacodynamics(self) -> dict[str, FigureMPL]:
        """Extremes of the pharmacodynamics over the scanned parameter."""
        figures = {}
        ncols = len(self.pd_parameters)
        for scan_key, scan_data in self.scan_map.items():
            f, axes = plt.subplots(
                nrows=1,
                ncols=ncols,
                figsize=(5 * ncols, 5),
                dpi=150,
                layout="constrained",
                squeeze=False,
            )
            sim_key = f"scan_po_{scan_key}"
            x = self._scanned(self.results[f"task_{sim_key}"], scan_data)
            for ax, (sid, extreme) in zip(axes[0], self.pd_parameters, strict=True):
                df = self.pd_dfs[sim_key][sid]
                unit = self.units[sid]
                self._parameter_panel(
                    ax,
                    scan_data,
                    x,
                    self._summary(df, extreme, df["unit"].iloc[0], unit),
                    ylabel=(
                        f"{extreme} {self.labels[sid]} "
                        f"[{unit.replace('dimensionless', '-')}]"
                    ),
                    # the blood pressure keeps the range of its values
                    from_zero=sid not in {"SBP", "DBP"},
                )
            figures[f"pd_{scan_key}"] = f

        return figures


if __name__ == "__main__":
    MODEL.run_experiments(
        EnalaprilParameterScan, output_dir=EnalaprilParameterScan.__name__
    )
