"""Base class of the simulation experiments of the RAAS model.

The RAAS model (`enalapril_raas.xml`) is the renin-angiotensin-aldosterone
system with enalaprilat in plasma, without the pharmacokinetics of the body.
"""

from collections.abc import Mapping
from pathlib import Path
from typing import ClassVar, override

from pkpdsim.experiment import PKPDSimulationExperiment
from sbmlsim.data import Data
from sbmlsim.model import AbstractModel
from sbmlsim.task import Task
from sbmlsim.units import Quantity

from pkdb_models.models.enalapril import MODEL, MODEL_BASE_PATH


class RaasSimulationExperiment(PKPDSimulationExperiment):
    """Base class of the simulation experiments of the RAAS model."""

    pkpd_model = MODEL

    font: ClassVar[dict[str, str | int]] = {"weight": "bold", "size": 22}
    scan_font: ClassVar[dict[str, str | int]] = {"weight": "bold", "size": 15}
    tick_font_size = 15
    legend_font_size = 13
    suptitle_font_size = 40

    units: ClassVar[Mapping[str, str]] = {
        "time": "hr",
        "[eat]": "nM",  # enalaprilat in Vplasma
        "[anggen]": "pM",  # angiotensinogen in Vplasma
        "[ang1]": "pM",  # angiotensin I in Vplasma
        "[ang2]": "pM",  # angiotensin II in Vplasma
        "[ace]": "pM",  # ACE concentration in Vplasma
        "[ren]": "pM",  # renin in Vplasma
        "[ald]": "pM",  # aldosterone in Vplasma
        "ace_activity": "dimensionless",  # [-] ACE activity
        "ace_inhibition": "dimensionless",  # [-] ACE inhibition
        "ANGGEN2ANG1": "pmol/min",  # angiotensinogen to angiotensin I (renin)
        "ANG1ANG2": "pmol/min",  # angiotensin I to angiotensin II (ACE)
        "ANG1DEG": "pmol/min",  # angiotensin I degradation (ANG1DEG)
        "ANG2DEG": "pmol/min",  # angiotensin II degradation (ANG2DEG)
        "RENSEC": "pmol/min",  # renin secretion (RENSEC)
        "RENDEG": "pmol/min",  # renin degradation (RENDEG)
        "ALDSEC": "pmol/min",  # aldosterone secretion (ALDSEC)
        "ALDDEG": "pmol/min",  # aldosterone degradation (ALDDEG)
        "SBP": "mmHg",
        "DBP": "mmHg",
        "MAP": "mmHg",
        "SBP_change": "mmHg",
        "DBP_change": "mmHg",
        "MAP_change": "mmHg",
        "SBP_ratio": "dimensionless",
        "DBP_ratio": "dimensionless",
        "MAP_ratio": "dimensionless",
    }
    labels: ClassVar[Mapping[str, str]] = {
        "time": "hr",
        "[eat]": "enalaprilat",  # in Vplasma
        "[anggen]": "angiotensinogen",  # angiotensinogen in Vplasma
        "[ang1]": "angiotensin I",  # angiotensin I in Vplasma
        "[ang2]": "angiotensin II",  # angiotensin II in Vplasma
        "[ace]": "ACE",  # ACE concentration in Vplasma
        "[ren]": "renin",  # renin in Vplasma
        "[ald]": "aldosterone",  # aldosterone in Vplasma
        "ace_activity": "ACE activity",  # [-] ACE activity
        "ace_inhibition": "ACE inhibition",  # [-] ACE inhibition
        "ANGGEN2ANG1": "ANGGEN2ANG1",  # angiotensinogen to angiotensin I (renin)
        "ANG1ANG2": "ANG1ANG2",  # angiotensin I to angiotensin II (ANG1ANG2)
        "ANG1DEG": "ANG1DEG",  # angiotensin I degradation (ANG1DEG)
        "ANG2DEG": "ANG2DEG",  # angiotensin II degradation (ANG2DEG)
        "RENSEC": "renin secretion\n(RENSEC)",  # renin secretion (RENSEC)
        "RENDEG": "renin degradation\n(RENDEG)",  # renin degradation (RENDEG)
        "ALDSEC": "aldosterone secretion\n(ALDSEC)",  # aldosterone secretion (ALDSEC)
        "ALDDEG": "aldosterone degradation\n(ALDDEG)",  # aldosterone degradation (ALDDEG)
        "SBP": "systolic blood pressure",
        "DBP": "diastolic blood pressure",
        "MAP": "mean arterial blood pressure",
        "SBP_change": "systolic blood pressure change",
        "DBP_change": "diastolic blood pressure change",
        "MAP_change": "mean arterial blood pressure change",
        "SBP_ratio": "systolic blood pressure ratio",
        "DBP_ratio": "diastolic blood pressure ratio",
        "MAP_ratio": "mean arterial blood pressure ratio",
    }

    @override
    def models(self) -> dict[str, AbstractModel | Path]:
        return {
            "model": AbstractModel(
                source=MODEL_BASE_PATH / "enalapril_raas.xml",
                language_type=AbstractModel.LanguageType.SBML,
                changes={},
            )
        }

    def default_changes(self) -> dict[str, Quantity | float]:
        """Changes of every simulation of the experiments, none."""
        return {}

    @override
    def tasks(self) -> dict[str, Task]:
        return {
            f"task_{key}": Task(model="model", simulation=key)
            for key in self.simulations()
        }

    @override
    def data(self) -> dict[str, Data]:
        self.add_selections_data(
            selections=[
                "time",
                "[eat]",
                "[anggen]",
                "[ang1]",
                "[ang2]",
                "[ace]",
                "[ren]",
                "[ald]",
                "ace_activity",
                "ace_inhibition",
                "ANGGEN2ANG1",
                "ANG1ANG2",
                "ANG1DEG",
                "ANG2DEG",
                "RENSEC",
                "RENDEG",
                "ALDSEC",
                "ALDDEG",
                "SBP",
                "DBP",
                "MAP",
                "SBP_change",
                "DBP_change",
                "MAP_change",
                "SBP_ratio",
                "DBP_ratio",
                "MAP_ratio",
            ]
        )
        return {}
