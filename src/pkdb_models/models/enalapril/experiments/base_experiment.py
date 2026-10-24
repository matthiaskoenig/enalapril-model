"""Base class of the enalapril simulation experiments."""

from collections.abc import Mapping, Sequence
from types import MappingProxyType
from typing import ClassVar, NamedTuple

import pandas as pd
from pkpdsim.experiment import PKPDSimulationExperiment
from pkpdsim.impairment import (
    CARDIAC,
    CARDIAC_COLORS,
    CIRRHOSIS,
    RENAL_FUNCTION_GFR,
)
from pkpdsim.metadata import Coadministration
from sbmlsim import Q
from sbmlsim.units import Quantity

from pkdb_models.models.enalapril import MODEL
from pkdb_models.models.enalapril.enalapril_pk import (
    calculate_enalapril_pd,
    calculate_enalapril_pk,
)

#: the factors of the interactions of a coadministration with enalapril, by the
#: parameters of the model (`INTERACTION_PARAMETERS`); a coadministration which
#: is not listed has no interaction (all factors 1). The factors are documented
#: values of the literature, set by the experiments, never fitted; their arms
#: are validation data (`INTERACTION_VALIDATION`). None of the coadministered
#: drugs of the studies changes the pharmacokinetics of enalapril:
INTERACTION_FACTORS: Mapping[Coadministration, Mapping[str, float]] = MappingProxyType(
    {
        # cimetidine (400 mg twice daily) changes neither the enalapril nor
        # the enalaprilat (AUC, Cmax, urinary recovery) nor the ACE
        # inhibition {Ishizaki1988}
        Coadministration.CIMETIDINE: MappingProxyType({}),
        # hydrochlorothiazide does not change the pharmacokinetics of enalapril
        # and enalaprilat (fixed dose combination vs enalapril alone,
        # {Niopas2004}); in hypertensive patients with renal impairment the
        # renal clearance of enalaprilat fell from 62 to 43 ml/min with HCTZ
        # {Weisser1992}, a single study, not modelled
        Coadministration.HCTZ: MappingProxyType({}),
    }
)
#: the parameters of the interactions, 1 without an interaction
INTERACTION_PARAMETERS: tuple[str, ...] = ()


class MolecularWeights(NamedTuple):
    """Molecular weights for the conversion of the data."""

    ena: Quantity
    eat: Quantity
    enamal: Quantity
    ena_eat: Quantity
    ren: Quantity
    anggen: Quantity
    ang1: Quantity
    ang2: Quantity
    ald: Quantity


class EnalaprilSimulationExperiment(PKPDSimulationExperiment):
    """Base class of the enalapril simulation experiments."""

    pkpd_model = MODEL
    selections = (
        "time",
        # dosing
        "IVDOSE_ena",
        "IVDOSE_eat",
        "PODOSE_ena",
        # venous
        "[Cve_ena]",
        "[Cve_eat]",
        "[Cve_ena_eat]",
        "[eat]",
        # liver
        "[LI__ena]",
        "[LI__eat]",
        # the enalaprilat bound to tissue ACE
        "Xre_eat_ace",
        "f_ace_occupancy",
        # urine
        "Aurine_ena",
        "Aurine_eat",
        "Aurine_ena_eat",
        "KI__ENAEX",
        "KI__EATEX",
        "KI__ENA_EATEX",
        # feces
        "Afeces_ena",
        # cases
        "KI__f_renal_function",
        "KI__GFR",
        "f_cardiac_function",
        "GU__F_ena_abs",
        "GU__fed",
        "LI__f_ces1",
        "f_cirrhosis",
        # pharmacodynamics
        "[anggen]",
        "[ang1]",
        "ang1_change",
        "ang1_ratio",
        "[ang2]",
        "ang2_change",
        "ang2_ratio",
        "[ren]",
        "ren_change",
        "ren_ratio",
        "ren_ref",
        "[ace]",
        "ace_activity",
        "ace_inhibition",
        "[ald]",
        "ald_change",
        "ald_ratio",
        "ald_ref",
        "ANGGEN2ANG1",
        "ANG1ANG2",
        "ANG1DEG",
        "ANG2DEG",
        "RENSEC",
        "RENDEG",
        "ALDSEC",
        "ALDDEG",
        "SBP",
        "SBP_ref",
        "SBP_change",
        "SBP_ratio",
        "SBP_change_relative",
        "DBP",
        "DBP_ref",
        "DBP_change",
        "DBP_ratio",
        "DBP_change_relative",
        "MAP",
        "MAP_change",
        "MAP_ratio",
        "MAP_change_relative",
        "HR",
        "HRrest",
    )

    label_time = "time"

    font: ClassVar[dict[str, str | int]] = {"weight": "bold", "size": 22}
    scan_font: ClassVar[dict[str, str | int]] = {"weight": "bold", "size": 15}
    tick_font_size = 15
    legend_font_size = 13
    suptitle_font_size = 40
    panel_width = 7.7
    panel_height = 5.7

    units: ClassVar[Mapping[str, str]] = {
        "time": "hr",
        "[Cve_ena]": "µM",
        "[Cve_eat]": "µM",
        "[Cve_ena_eat]": "µM",
        "Aurine_ena": "µmole",
        "Aurine_eat": "µmole",
        "Aurine_ena_eat": "µmole",
        "Afeces_ena": "µmole",
        "Xre_eat_ace": "mg",
        "f_ace_occupancy": "dimensionless",
        "KI__GFR": "ml/min",
        "KI__ENAEX": "µmol/min",
        "KI__EATEX": "µmol/min",
        "KI__ENA_EATEX": "µmol/min",
        "[anggen]": "pM",  # angiotensinogen in Vplasma
        "[ang1]": "pM",  # angiotensin I in Vplasma
        "ang1_change": "pM",
        "ang1_ratio": "dimensionless",
        "[ang2]": "pM",  # angiotensin II in Vplasma
        "ang2_change": "pM",
        "ang2_ratio": "dimensionless",
        "[ren]": "pM",  # renin in Vplasma
        "ren_change": "pM",
        "ren_ratio": "dimensionless",
        "[ace]": "pM",
        "ace_activity": "%",
        "ace_inhibition": "%",
        "[ald]": "nM",  # aldosterone in Vplasma
        "ald_change": "nM",
        "ald_ratio": "dimensionless",
        "SBP": "mmHg",
        "DBP": "mmHg",
        "SBP_change": "mmHg",
        "DBP_change": "mmHg",
        "SBP_change_relative": "dimensionless",
        "DBP_change_relative": "dimensionless",
        "MAP": "mmHg",
        "MAP_change": "mmHg",
        "MAP_ratio": "dimensionless",
        "MAP_change_relative": "dimensionless",
        "SBP_ratio": "dimensionless",
        "DBP_ratio": "dimensionless",
        "HR": "1/min",
    }

    labels: ClassVar[Mapping[str, str]] = {
        "time": "time",
        "[Cve_ena]": "enalapril",
        "[Cve_eat]": "enalaprilat",
        "[Cve_ena_eat]": "enalapril+enalaprilat",
        "Aurine_ena": "enalapril urine",
        "Aurine_eat": "enalaprilat urine",
        "Aurine_ena_eat": "enalapril+enalaprilat\nurine",
        "Afeces_ena": "enalapril feces",
        "Xre_eat_ace": "enalaprilat bound to tissue ACE",
        "f_ace_occupancy": "tissue ACE occupancy",
        "KI__GFR": "GFR",
        "KI__ENAEX": "enalapril excretion\nurine",
        "KI__EATEX": "enalaprilat excretion\nurine",
        "KI__ENA_EATEX": "enalapril+enalaprilat excretion\nurine",
        "[anggen]": "angiotensinogen",  # angiotensinogen in Vplasma
        "[ang1]": "angiotensin I",  # angiotensin I in Vplasma
        "ang1_change": "angiotensin I change",
        "ang1_ratio": "angiotensin I ratio",
        "[ang2]": "angiotensin II",  # angiotensin II in Vplasma
        "ang2_change": "angiotensin II change",
        "ang2_ratio": "angiotensin II ratio",
        "[ren]": "renin",  # renin in Vplasma
        "ren_change": "renin change",
        "ren_ratio": "renin ratio",
        "[ace]": "ACE",
        "ace_activity": "ACE activity",
        "ace_inhibition": "ACE inhibition",
        "[ald]": "aldosterone",  # aldosterone in Vplasma
        "ald_change": "aldosterone change",
        "ald_ratio": "aldosterone ratio",
        "SBP": "SBP",
        "DBP": "DBP",
        "SBP_change": "SBP change",
        "DBP_change": "DBP change",
        "SBP_change_relative": "SBP change relative to baseline",
        "DBP_change_relative": "DBP change relative to baseline",
        "MAP": "MAP",
        "MAP_change": "MAP change",
        "MAP_ratio": "MAP ratio",
        "MAP_change_relative": "MAP change relative to baseline",
        "SBP_ratio": "SBP ratio",
        "DBP_ratio": "DBP ratio",
        "HR": "heart rate",
    }

    # ------------------------------------------------------------------
    # Colour scheme: one hue per condition, shades for severity / dose.
    #   healthy           : black for ANY enalapril dose (doses differ by marker,
    #                       not by colour)
    #   placebo / no drug : grey
    #   cardiac (heart)   : red
    #   hepatic (liver)   : blue
    #   renal (kidney)    : green
    #   CES1              : turquoise
    #   dose variation    : marker in healthy subjects; yellow (gold) shades only
    #                       in the patient cohorts that compare doses
    #   time of day       : marker (square = day/morning, triangle = night/evening)
    #   age (young/elder) : marker (circle = young, diamond = elder); the
    #                       physiological condition (e.g. renal function) sets the colour
    #   formulation       : magenta (light = test, dark = reference)
    #   food              : brown (fasting stays black)
    # Ramps run light -> dark with increasing severity / dose. All shades
    # have >= 3:1 contrast against white; condition hue takes precedence,
    # i.e. a dose series inside a condition uses shades of that condition.
    # ------------------------------------------------------------------
    healthy_color: ClassVar[str] = "#000000"
    placebo_color: ClassVar[str] = "#767676"  # no-drug arm (placebo, untreated day)
    grey_shades: ClassVar[list[str]] = ["#000000", "#4D4D4D", "#767676"]

    cardiac_ramp: ClassVar[list[str]] = ["#FE5647", "#D62525", "#A10412", "#690003"]
    hepatic_ramp: ClassVar[list[str]] = ["#0A98E2", "#0F78B3", "#055987", "#003D5E"]
    renal_ramp: ClassVar[list[str]] = [
        "#07A82C",
        "#028A3F",
        "#036D40",
        "#035138",
        "#02382A",
    ]
    # hue varies (teal-green <-> cyan) as well as lightness so that up to five variants
    # plus the black control stay distinguishable (pairwise dE >= 18, also for deuteranopes)
    ces1_ramp: ClassVar[list[str]] = [
        "#09A38C",
        "#169FAF",
        "#026E76",
        "#007152",
        "#004640",
    ]
    dose_ramp: ClassVar[list[str]] = ["#AF8D04", "#917401", "#735C02", "#574500"]
    formulation_ramp: ClassVar[list[str]] = ["#FB44B7", "#C00787", "#790153"]
    food_color: ClassVar[str] = "#C28254"

    # markers for group variables that do not get a colour
    time_markers: ClassVar[dict[str, str]] = {
        "day": "s",
        "morning": "s",
        "night": "v",
        "evening": "v",
    }
    age_markers: ClassVar[dict[str, str]] = {
        "young": "o",
        "Y": "o",
        "elder": "D",
        "E": "D",
    }

    @classmethod
    def dose_markers(cls, keys: Sequence[str]) -> dict[str, str]:
        """Data markers for up to four doses in healthy subjects.

        The colour of healthy subjects stays black for every dose, the doses
        differ by marker.

        Args:
            keys: keys of the doses, lowest dose first.

        Returns:
            The marker by key.
        """
        return dict(zip(keys, ["o", "^", "s", "D"], strict=False))

    @classmethod
    def dose_colors(cls, keys: Sequence[str]) -> dict[str, str]:
        """Yellow shades for one to four doses, light (first key) to dark (last key).

        Args:
            keys: keys of the doses, lowest dose first.

        Returns:
            The colour by key.
        """
        steps = {1: [1], 2: [0, 2], 3: [0, 1, 3], 4: [0, 1, 2, 3]}[len(keys)]
        return {key: cls.dose_ramp[k] for key, k in zip(keys, steps, strict=True)}

    #: the renal function by the GFR: a measured creatinine clearance (or GFR)
    #: of X ml/min is the renal function X/101 (`KI__f_renal_function`), the
    #: classes are the limits of the GFR of the classes
    renal_map: ClassVar[Mapping[str, float]] = RENAL_FUNCTION_GFR
    renal_colors: ClassVar[Mapping[str, str]] = {
        "Control": healthy_color,
        "Normal renal function": healthy_color,
        "NRF": healthy_color,
        "Mild renal impairment": renal_ramp[0],
        "Moderate renal impairment": renal_ramp[1],
        "Severe renal impairment": renal_ramp[2],
        "SRI": renal_ramp[3],
        "End stage renal disease": renal_ramp[4],
        "ESRD": renal_ramp[4],
    }

    #: the cardiac function (`f_cardiac_function`) of the classes of cardiac
    #: impairment; it lowers the cardiac output, the blood flows and with the
    #: renal blood flow the GFR. A group with a measured creatinine clearance
    #: sets `KI__f_renal_function = CLcr / (101 * f_cardiac_function)`, so that
    #: its GFR is the measured clearance
    cardiac_map: ClassVar[Mapping[str, float]] = CARDIAC
    cardiac_colors: ClassVar[Mapping[str, str]] = {
        **CARDIAC_COLORS,
        "Control": healthy_color,
    }

    #: the degree of cirrhosis (`f_cirrhosis`) of the Child-Pugh classes
    cirrhosis_map: ClassVar[Mapping[str, float]] = CIRRHOSIS
    cirrhosis_colors: ClassVar[Mapping[str, str]] = {
        "Control": healthy_color,
        "Mild cirrhosis": hepatic_ramp[0],  # CPT A
        "Moderate cirrhosis": hepatic_ramp[1],  # CPT B
        "Severe cirrhosis": hepatic_ramp[2],  # CPT C
    }

    #: the fed state of the intestine (`GU__fed`): a high fat meal slows the
    #: dissolution and the gastric emptying (`GU__FED_f_dissolution`, fitted
    #: from Moffett2014), the fraction absorbed does not change {Swanson1984};
    #: a light breakfast is assumed to have half the effect
    fasting_map: ClassVar[Mapping[str, float]] = {
        "not reported": 0.0,  # assuming fasted state if nothing is reported
        "fasted": 0.0,
        "light breakfast": 0.5,
        "fed": 1.0,
    }

    fasting_colors: ClassVar[dict[str, str]] = {
        "fasting": healthy_color,
        "fasted": healthy_color,
        "nonfasting": food_color,
        "fed": food_color,
        "not reported": healthy_color,
    }

    # --- CES1 activity ---
    #: the activity of CES1 per allele (`LI__f_ces1`, *1/*1 = 1): G143E (rs71647871)
    #: is a loss of function allele, the activity of a heterozygous carrier
    #: about 0.55 of the wild type {Tarkiainen2015, Her2021}; CES1A1c and the
    #: copy number of CES1 (CES1A2 is transcribed at about 2 % of CES1A1) do not
    #: change the hydrolysis of enalapril {Stage2017}
    wt_f = 1.0  # wildtype
    g143e_f = 0.1  # loss of function

    ces1_map: ClassVar[dict[str, float]] = {
        # *1/*1
        "control": (wt_f + wt_f) / 2,
        # gene duplications, no effect {Stage2017}
        "copies4": 1.0,
        "copies_normal3": 1.0,
        "copies_active3": 1.0,
        # decreased
        "G143E": (wt_f + g143e_f) / 2,  # heterozygous
        "CES1A1c": 1.0,  # homozygous, no change of the protein {Stage2017}
    }

    # ordered by activity: lightest = highest activity, darkest = lowest
    ces1_colors: ClassVar[dict[str, str]] = {
        "control": healthy_color,
        "copies4": ces1_ramp[0],
        "copies_active3": ces1_ramp[1],
        "copies_normal3": ces1_ramp[2],
        "CES1A1c": ces1_ramp[3],
        "G143E": ces1_ramp[4],
    }

    sex_markers: ClassVar[dict[str, str]] = {"females": "s", "males": "o"}

    #: labels of the pharmacokinetic parameters, by their name in pkpdutils,
    #: see `enalapril_pk`
    pk_labels: ClassVar[Mapping[str, str]] = {
        "auc_last": "AUCend",
        "auc_inf_obs": "AUC∞",
        "cl_f": "Apparent clearance",
        "cl_renal": "Renal clearance",
        "cmax": "Cmax",
        "tmax": "tmax",
        "thalf": "Half-life",
        "lambda_z": "λz",
        "vz_f": "Apparent volume",
        "Aurine_ena": "Enalapril urine",
        "Aurine_eat": "Enalaprilat urine",
        "Aurine_ena_eat": "Enalapril + enalaprilat urine",
    }
    pk_units: ClassVar[Mapping[str, str]] = {
        "auc_last": "nmole/liter*hr",
        "auc_inf_obs": "nmole/liter*hr",
        "cl_f": "l/hr",
        "cl_renal": "ml/min",
        "cmax": "nmole/liter",
        "tmax": "hr",
        "thalf": "hr",
        "lambda_z": "1/hr",
        "vz_f": "l",
        "Aurine_ena": "µmole",
        "Aurine_eat": "µmole",
        "Aurine_ena_eat": "µmole",
    }

    # molecular weights of enalapril, enalaprilat and the RAAS; not needed for
    # a conversion of the data: ACE 149715 g/mole
    Mr: ClassVar[MolecularWeights] = MolecularWeights(
        ena=Q(376.44670, "g/mole"),
        eat=Q(348.39360, "g/mole"),
        enamal=Q(492.51890, "g/mole"),
        # enalapril + enalaprilat (estimation of Mr); the total drug of the
        # radioimmunoassays after hydrolysis is in enalaprilat equivalents
        # (`eat`) where the publication says so
        ena_eat=Q((376.44670 + 348.39360) / 2, "g/mole"),
        ren=Q(45057, "g/mole"),
        anggen=Q(52670, "g/mole"),
        ang1=Q(1296.499, "g/mole"),
        ang2=Q(1046.179, "g/mole"),
        ald=Q(360.444, "g/mole"),
    )

    def interaction_changes(
        self, coadministration: Coadministration
    ) -> dict[str, Quantity]:
        """Get the changes of the interaction parameters of a coadministration.

        Every parameter of `INTERACTION_PARAMETERS` is set, to its factor of
        `INTERACTION_FACTORS` or to 1 without an interaction, so that the arms
        of a study differ only in the coadministration.

        Args:
            coadministration: the coadministered drug, `Coadministration.NONE`
                for the arm without.

        Returns:
            The changes of the interaction parameters.
        """
        factors = INTERACTION_FACTORS.get(coadministration, {})
        return {
            pid: Q(factors.get(pid, 1.0), "dimensionless")
            for pid in INTERACTION_PARAMETERS
        }

    def calculate_enalapril_pk(
        self, scans: Sequence[str] = ()
    ) -> dict[str, pd.DataFrame]:
        """Calculate the pharmacokinetic parameters of the scans.

        Args:
            scans: keys of the scans, all simulations of the experiment if empty.

        Returns:
            The parameters of every simulation of a scan and substance by the
            key of the scan, per draw of the fitted parameters in a run over
            them (`uncertainty`).
        """
        across = None if self.uncertainty is None else self.uncertainty.id
        return {
            key: calculate_enalapril_pk(
                experiment=self, res=self.results[f"task_{key}"], across=across
            )
            for key in (scans or self._simulations.keys())
        }

    def calculate_enalapril_pd(
        self, scans: Sequence[str] = ()
    ) -> dict[str, dict[str, pd.DataFrame]]:
        """Calculate the pharmacodynamic parameters of the scans.

        Args:
            scans: keys of the scans, all simulations of the experiment if empty.

        Returns:
            The parameters of every simulation of a scan by effect and by the
            key of the scan, per draw of the fitted parameters in a run over
            them (`uncertainty`).
        """
        across = None if self.uncertainty is None else self.uncertainty.id
        return {
            key: calculate_enalapril_pd(res=self.results[f"task_{key}"], across=across)
            for key in (scans or self._simulations.keys())
        }
