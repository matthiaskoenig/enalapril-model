"""Model of RAAS blood pressure regulation."""

from dataclasses import dataclass

import numpy as np
from sbmlutils.factory import (
    AssignmentRule,
    Compartment,
    FactoryResult,
    InitialAssignment,
    Model,
    Parameter,
    RateRule,
    Reaction,
    Species,
    UnitDefinition,
    ValidationOptions,
    create_model,
)
from sbmlutils.metadata import (
    BQB,
    SBO,
)

from pkdb_models.models.enalapril.models import annotations, templates
from pkdb_models.models.enalapril.models.fits import FITS


class U(templates.U):
    """Units of the RAAS model."""

    mmHg = UnitDefinition("mmHg", "133.32239 N/m^2")


mid = "enalapril_raas"


_m = Model(
    sid=mid,
    name="Model for RAAS system of blood pressure regulation.",
    notes="""
    Model for RAAS system of blood pressure regulation.
    Enalaprilat is an inhibitor of ACE, so it inhibits conversion of angiotensin I to angiotensin II.

    - components: renin, angiotensinogen, angiotensin I, angiotensin II, ACE, aldosterone, systolic and diastolic blood pressure
    - angiotensin II raises the blood pressure (vasoconstriction) and the
      aldosterone secretion
    - negative feedback loop: angiotensin II inhibits the secretion of renin
    - angiotensin I is converted by ACE or cleared by other peptidases

    """
    + templates.terms_of_use,
    creators=templates.creators,
    units=U,
    model_units=templates.model_units,
    annotations=[
        # tissue - plasma
        (BQB.OCCURS_IN, "bto/BTO:0000131"),
        (BQB.OCCURS_IN, "ncit/C13356"),
        # RAAS
        (BQB.IS, "uberon/UBERON:0018229"),
        (BQB.IS, "mesh/D012084"),
        (BQB.IS, "ncit/C91434"),
        # components
        (BQB.HAS_PROPERTY, "ncit/C54706"),  # blood pressure
        (BQB.HAS_PROPERTY, "ncit/C25298"),  # systolic blood pressure
        (BQB.HAS_PROPERTY, "ncit/C25299"),  # diastolic blood pressure
        (BQB.HAS_PROPERTY, "ncit/C217189"),  # mean blood pressure
        (BQB.HAS_PROPERTY, "ncit/C42791"),  # Pharmacodynamics: Inhibition
        (BQB.HAS_PROPERTY, "ncit/C247"),  # Pharmacodynamics: ACE Inhibition
        *annotations.model,
    ],
)

_m.compartments = [
    Compartment(
        "Vplasma",
        value=5.0,
        unit=U.liter,
        name="plasma",
        constant=True,
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        annotations=annotations.compartments["plasma"],
        port=True,
    ),
]


@dataclass
class Substance:
    """Definition of a substance of the RAAS model.

    Attributes:
        sid: identifier of the species.
        name: name of the species.
        init: initial concentration [mM].
        unit: substance unit.
        boundary: whether the species is a boundary condition.
        port: whether the species is a port of the model.
    """

    sid: str
    name: str
    init: float
    unit: str
    boundary: bool = False
    port: bool = False


# ---------------------------------------------------------------------------------------------------------------------
# Pharmacodynamics
# ---------------------------------------------------------------------------------------------------------------------
# The EC50 of the ACE inhibition by the enalaprilat of the plasma: the
# inhibition of the plasma ACE is 95 % at the peak and 74, 41 and 23 % at 24,
# 48 and 72 hr after 10 mg of enalapril maleate (4.5, 2.2 and 1.6 ng/ml)
# {Biollaz1982}, the in vivo IC50 is 1.7-12.8 ng/ml {Hockings1986} and
# 22.9 +- 6.5 nM (8 ng/ml) in young subjects {MacDonald1993}. The value is
# fitted, see `fits.FITS`.

ald_ref = 250e-9  # [mM]
ren_ref = 1e-9  # [mM]
ace_ref = 1e-9  # [mM]
anggen_ref = 10e-9  # [mM]
ang1_ref = 10e-9  # [mM]
ang2_ref = 8e-9  # [mM]

substances: list[Substance] = [
    # Mr: 360.444 [g/mole]
    # 100 pg/ml {ramipril/Bussien1985} = 100/360.444*1000 [pmol/l] = 277.4 [pmol/l]
    # 80-90 pg/ml {losartan/Christen1991a} = 221.9 - 249.7 [pmol/l]
    # 80-100 pg/ml {losartan/Ohtawa1993} = 221.9 - 277.4 [pmol/l]
    # 600-800 pg/ml {losartan/Doig1993} FIXME: check unit = 1942.0 - 2219.5 [pmol/l]
    Substance("ald", "aldosterone", init=ald_ref, unit="mmole"),
    # Mr: 45057 [g/mole]
    # ~ 50-65 pg/ml {losartan/Azizi1999} = 50-65/45.057 [pmol/l] = 1.11 - 1.44 [pmol/l]
    # ~ 45-75 pg/ml {losartan/Doig1993}
    # 1 ng/mL/h PRA ≈ 7.6 pg/ml (5.5 - 9.7)?
    # ~2 ng/ml/hr {losartan/Goldberg1995} = 15.2 pg/ml = 0.337 [pmol/l]
    # ~2 ng/ml/hr {losartan/Tsuruoka2005} = 0.337 [pmol/l]
    # 1-2 ng/ml/hr {losartan/Ohtawa1993} = 0.169 - 0.337 [pmol/l]
    # 1-2 ng/ml/hr renin activity {losartan/Christen1991a} = 0.169 - 0.337 [pmol/l]
    # 5-6 ng/ml/hr renin activity {losartan/Doig1993} FIXME: check unit = 0.843 - 1.01 [pmol/l]
    Substance("ren", "renin", init=ren_ref, unit="mmole"),
    # Mr: 52670 [g/mole]
    Substance(
        "anggen", "angiotensinogen", init=anggen_ref, unit="mmole", boundary=True
    ),
    # Mr: 1296.5 [g/mole]
    # ~ 11-13 [pg/ml] {losartan/Azizi1999} = 11-13 / 1.2965 [pmol/l] = 8.5 - 10.0 [pmol/l]
    # 10 [pmol/l] {ramipril/Manhem1985}
    Substance("ang1", "angiotensin I", init=ang1_ref, unit="mmole"),
    # Mr: 1046.2 [g/mole]
    # ~ 6-10 [pg/ml] {losartan/Azizi1999} = 6-10 / 1.0462 [pmol/l] = 5.7 - 9.6 [pmol/l]
    # 10 [pmol/l] {ramipril/Manhem1985}
    # 5-6 [fmol/ml] {losartan/Christen1991a} = 5-6 [pmol/l]
    # 4-8 [pg/ml] {losartan/Ohtawa1993} = 4-8 / 1.0462 [pmol/l] = 3.8 - 9.2 [pmol/l]
    Substance("ang2", "angiotensin II", init=ang2_ref, unit="mmole"),
    # Mr: 149715 [g/mole]
    # 6.72 nM activity (Gillian I., 2006)
    # 10 pmol/l: assumption, same order as ang1 and ang and renin
    Substance("ace", "ACE", init=ace_ref, unit="mmole"),
    # modeled substance
    Substance("eat", "enalaprilat", init=0, unit="mmole", port=True),
]

for s in substances:
    _m.species.append(
        Species(
            s.sid,
            name=s.name,
            initialConcentration=s.init,
            compartment="Vplasma",
            substanceUnit=U.mmole,
            hasOnlySubstanceUnits=False,
            boundaryCondition=s.boundary,
            sboTerm=SBO.SIMPLE_CHEMICAL,
            annotations=annotations.species[s.sid],
            port=s.port,
        )
    )
    if s.sid not in {"eat"}:
        _m.assignments.append(InitialAssignment(s.sid, f"{s.sid}_ref", unit=U.mM))

    # changes in variables
    if s.sid in ["anggen", "ang1", "ang2", "ren", "ace", "ald"]:
        # absolute change
        _m.parameters.append(
            Parameter(
                f"{s.sid}_change",
                name=f"{s.name} change",
                value=np.nan,
                unit=U.mM,
                annotations=annotations.species[s.sid],
                constant=False,
                notes=f"Absolute change to baseline {s.name}",
            )
        )
        _m.rules.append(
            AssignmentRule(f"{s.sid}_change", f"{s.sid}-{s.sid}_ref", unit=U.mM)
        )
        # ratio to baseline
        _m.parameters.append(
            Parameter(
                f"{s.sid}_ratio",
                name=f"{s.name} ratio",
                value=np.nan,
                unit=U.dimensionless,
                annotations=annotations.species[s.sid],
                constant=False,
                notes=f"Ratio relative to baseline {s.name}",
            )
        )
        _m.rules.append(
            AssignmentRule(
                f"{s.sid}_ratio", f"{s.sid}/{s.sid}_ref", unit=U.dimensionless
            )
        )

_m.parameters.extend(
    [
        Parameter(
            "anggen_ref",
            anggen_ref,
            U.mM,
            name="reference concentration of angiotensinogen",
            sboTerm=SBO.KINETIC_CONSTANT,
        ),
        Parameter(
            "ang1_ref",
            ang1_ref,
            U.mM,
            name="reference concentration of angiotensin I",
            sboTerm=SBO.KINETIC_CONSTANT,
        ),
        Parameter(
            "ang2_ref",
            ang2_ref,
            U.mM,
            name="reference concentration of angiotensin II",
            sboTerm=SBO.KINETIC_CONSTANT,
        ),
        Parameter(
            "ren_ref",
            ren_ref,
            U.mM,
            name="reference concentration of renin",
            sboTerm=SBO.KINETIC_CONSTANT,
        ),
        Parameter(
            "ace_ref",
            ace_ref,
            U.mM,
            name="reference concentration of ACE",
            sboTerm=SBO.KINETIC_CONSTANT,
        ),
        Parameter(
            "ald_ref",
            ald_ref,
            U.mM,
            name="reference concentration of aldosterone",
            sboTerm=SBO.KINETIC_CONSTANT,
        ),
    ]
)


# The turnover of the RAAS: every state starts in the steady state of its
# reference concentration (`<sid>_ref`), the rates of synthesis follow from the
# rates of degradation and the references, so a study which sets a reference
# starts in the steady state of its own reference. The degradation rates are
# the clearances of the plasma volume for the half-lives of the states: renin
# 15 min, angiotensin I 0.5 min, aldosterone 20 min; the half-life of
# angiotensin II follows from them, 0.4 min / f_ang1_ace.
_m.parameters.extend(
    [
        Parameter(
            "RENDEG_k",
            np.log(2) / 15 * 5.0,  # [1/min] * [l]
            U.l_per_min,
            name="rate renin degradation",
            sboTerm=SBO.KINETIC_CONSTANT,
            notes="Clearance of renin, a half-life of 15 min in 5 l plasma.",
        ),
        Parameter(
            "RENSEC_k",
            "RENDEG_k * ren_ref",
            U.mmole_per_min,
            name="rate renin secretion",
            sboTerm=SBO.KINETIC_CONSTANT,
            notes="Renin secretion in the steady state of the reference.",
        ),
        Parameter(
            "RENSEC_ang2_E",
            **FITS.parameter("RENSEC_ang2_E", unit=U.dimensionless),
            name="maximum increase of the renin secretion without angiotensin II",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            notes="""
            Angiotensin II inhibits the renin secretion through its AT1
            receptors on the juxtaglomerular cells (short-loop feedback):
            without angiotensin II the secretion is 1 + RENSEC_ang2_E times
            the one of the reference. The secretion follows angiotensin II
            with a delay (`ang2_feedback`).
            """,
        ),
        Parameter(
            "RENSEC_ang2_t",
            **FITS.parameter("RENSEC_ang2_t", unit=U.min),
            name="half-life of the delay of the renin feedback",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            notes="""
            The renin secretion responds to a change of angiotensin II with a
            delay of this half-life (the signalling of the AT1 receptors and
            the release of renin from its granules), while angiotensin II
            itself has a half-life of about 0.5 min.
            """,
        ),
        Parameter(
            "ang2_feedback",
            np.nan,
            U.mM,
            constant=False,
            name="angiotensin II of the renin feedback",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            notes="""
            Angiotensin II which the renin secretion senses, a first order
            delay of angiotensin II with the half-life RENSEC_ang2_t.
            """,
        ),
        Parameter(
            "ANG1CL",
            np.log(2) / 0.5 * 5.0,  # [1/min] * [l]
            U.l_per_min,
            name="clearance of angiotensin I",
            sboTerm=SBO.KINETIC_CONSTANT,
            notes="""
            Clearance of angiotensin I by ACE and the other peptidases, a
            half-life of 0.5 min in 5 l plasma.
            """,
        ),
        Parameter(
            "ANGGEN2ANG1_k",
            "ANG1CL * ang1_ref/anggen_ref",
            U.l_per_min,
            name="rate angiotensinogen to angiotensin I conversion (renin)",
            sboTerm=SBO.KINETIC_CONSTANT,
        ),
        Parameter(
            "f_ang1_ace",
            0.15,
            U.dimensionless,
            name="fraction of angiotensin I converted by ACE",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            notes="""
            Fraction of the angiotensin I which ACE converts to angiotensin II
            in the reference state, the rest is cleared by other peptidases
            (neprilysin, aminopeptidases). Not fitted: the value of the same
            RAAS model fitted to the angiotensin I and II data of ramipril
            (0.154); the three curves of angiotensin I and II of the enalapril
            studies do not identify it.
            """,
        ),
        Parameter(
            "ANG1ANG2_k",
            "f_ang1_ace * ANG1CL",
            U.l_per_min,
            name="rate angiotensin I to angiotensin II conversion (ACE)",
            sboTerm=SBO.KINETIC_CONSTANT,
        ),
        Parameter(
            "ANG1DEG_k",
            "(1 dimensionless - f_ang1_ace) * ANG1CL",
            U.l_per_min,
            name="rate angiotensin I degradation",
            sboTerm=SBO.KINETIC_CONSTANT,
        ),
        Parameter(
            "ANG2DEG_k",
            "f_ang1_ace * ANG1CL * ang1_ref/ang2_ref",
            U.l_per_min,
            name="rate angiotensin II degradation",
            sboTerm=SBO.KINETIC_CONSTANT,
        ),
        Parameter(
            "ALDDEG_k",
            np.log(2) / 20 * 5.0,  # [1/min] * [l]
            U.l_per_min,
            name="rate aldosterone degradation",
            sboTerm=SBO.KINETIC_CONSTANT,
            notes="Clearance of aldosterone, a half-life of 20 min in 5 l plasma.",
        ),
        Parameter(
            "ALDSEC_k",
            "ALDDEG_k * ald_ref",
            U.mmole_per_min,
            name="rate aldosterone secretion",
            sboTerm=SBO.KINETIC_CONSTANT,
            notes="Aldosterone secretion in the steady state of the reference.",
        ),
        Parameter(
            "f_ald_ang2",
            0.66,
            U.dimensionless,
            name="fraction of the aldosterone secretion driven by angiotensin II",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            notes="""
            Angiotensin II stimulates the aldosterone secretion through AT1
            receptors of the zona glomerulosa; the rest of the secretion
            (potassium, ACTH) does not depend on it. Not fitted: the value of
            the same RAAS model fitted to the aldosterone data of ramipril
            (0.664); the training data of enalapril have no aldosterone.
            """,
        ),
    ]
)

_m.reactions = [
    # renin turnover
    Reaction(
        sid="RENSEC",
        name="renin secretion (RENSEC)",
        equation="-> ren",
        compartment="Vplasma",
        sboTerm=SBO.TRANSPORT_REACTION,
        formula=(
            "RENSEC_k * (1 dimensionless + RENSEC_ang2_E)"
            " / (1 dimensionless + RENSEC_ang2_E * ang2_feedback/ang2_ref)",
            U.mmole_per_min,
        ),
    ),
    Reaction(
        sid="RENDEG",
        name="renin degradation (RENDEG)",
        equation="ren ->",
        compartment="Vplasma",
        sboTerm=SBO.DEGRADATION,
        formula=("RENDEG_k * ren", U.mmole_per_min),
    ),
    # aldosterone turnover
    Reaction(
        sid="ALDSEC",
        name="aldosterone secretion (ALDSEC)",
        equation="-> ald [ang2]",
        compartment="Vplasma",
        sboTerm=SBO.TRANSPORT_REACTION,
        formula=(
            "ALDSEC_k * (1 dimensionless - f_ald_ang2 + f_ald_ang2 * ang2/ang2_ref)",
            U.mmole_per_min,
        ),
        notes="""
        - angiotensin II activates aldosterone secretion by binding to AT1 receptors
        """,
    ),
    Reaction(
        sid="ALDDEG",
        name="aldosterone degradation (ALDDEG)",
        equation="ald ->",
        compartment="Vplasma",
        sboTerm=SBO.DEGRADATION,
        formula=("ALDDEG_k * ald", U.mmole_per_min),
    ),
    # ===============================================
    # MAIN CHAIN
    # anggen -> ang1 -> ang2 ->
    # ===============================================
    Reaction(
        sid="ANGGEN2ANG1",
        name="angiotensinogen to angiotensin I (renin)",
        equation="anggen -> ang1 [ren]",
        compartment="Vplasma",
        sboTerm=SBO.BIOCHEMICAL_REACTION,
        formula=("ANGGEN2ANG1_k * anggen * ren/ren_ref", U.mmole_per_min),
    ),
    Reaction(
        sid="ANG1ANG2",
        name="angiotensin I to angiotensin II (ACE)",
        equation="ang1 -> ang2 [ace, eat]",
        compartment="Vplasma",
        sboTerm=SBO.BIOCHEMICAL_REACTION,
        # the concentrations of angiotensin I are far below the Km of ACE
        # (16-80 µM), the conversion is first order; the activity of ACE is
        # the one measured in the plasma under enalaprilat
        formula=(
            "ANG1ANG2_k * ang1 * ace/ace_ref * ace_activity",
            U.mmole_per_min,
        ),
    ),
    Reaction(
        sid="ANG1DEG",
        name="angiotensin I degradation (ANG1DEG)",
        equation="ang1 ->",
        compartment="Vplasma",
        sboTerm=SBO.DEGRADATION,
        formula=("ANG1DEG_k * ang1", U.mmole_per_min),
    ),
    Reaction(
        sid="ANG2DEG",
        name="angiotensin II degradation (ANG2DEG)",
        equation="ang2 ->",
        compartment="Vplasma",
        sboTerm=SBO.DEGRADATION,
        formula=("ANG2DEG_k * ang2", U.mmole_per_min),
    ),
]

# --- ACE inhibition ---

_m.parameters.extend(
    [
        # parameters enalaprilat effect
        Parameter(
            sid="ANG1ANG2_EC50_eat",
            name="EC50 of the ACE inhibition by enalaprilat",
            **FITS.parameter("ANG1ANG2_EC50_eat", unit=U.mM),
            sboTerm=SBO.INHIBITORY_CONSTANT,
            notes="""
            Concentration of enalaprilat in the plasma for half of the
            inhibition of the plasma ACE activity; the in vivo IC50 is
            1.7-12.8 ng/ml {Hockings1986}, 22.9 +- 6.5 nM in young subjects
            {MacDonald1993}, the in vitro IC50 of enalaprilat about 1 nM.
            """,
        ),
        Parameter(
            sid="ANG1ANG2_Emax_eat",
            name="maximum inhibition of ACE by enalaprilat",
            value=1,
            unit=U.dimensionless,
            sboTerm=SBO.INHIBITORY_CONSTANT,
            notes="""Complete inhibition at high concentrations {Biollaz1982}.""",
        ),
        Parameter(
            "ace_activity",
            name="ACE activity",
            value=np.nan,
            unit=U.dimensionless,
            annotations=annotations.species["ace"],
            constant=False,
            notes="ACE activity",
        ),
        Parameter(
            "ace_inhibition",
            name="ACE inhibition",
            value=np.nan,
            unit=U.dimensionless,
            annotations=annotations.species["ace"],
            constant=False,
            notes="ACE inhibition",
        ),
    ]
)
# the delayed angiotensin II of the renin feedback, in the steady state of the
# reference at the start
_m.assignments.append(InitialAssignment("ang2_feedback", "ang2_ref", unit=U.mM))
_m.rate_rules.append(
    RateRule(
        "ang2_feedback",
        "ln(2 dimensionless) / RENSEC_ang2_t * (ang2 - ang2_feedback)",
        unit=U.mmole_per_min_l,
    )
)
_m.rules.extend(
    [
        AssignmentRule(
            "ace_inhibition",
            "ANG1ANG2_Emax_eat * eat / (eat + ANG1ANG2_EC50_eat)",
            unit=U.dimensionless,
        ),
        AssignmentRule(
            "ace_activity", "1 dimensionless - ace_inhibition", unit=U.dimensionless
        ),
    ]
)

# blood pressure model
_m.parameters.extend(
    [
        Parameter(
            "SBP_ref",
            120,
            U.mmHg,
            name="reference systolic blood pressure [mmHg]",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        ),
        Parameter(
            "DBP_ref",
            80,
            U.mmHg,
            name="reference diastolic blood pressure [mmHg]",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        ),
        Parameter(
            "SBP",
            np.nan,
            U.mmHg,
            name="systolic blood pressure [mmHg]",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            constant=False,
        ),
        Parameter(
            "DBP",
            np.nan,
            U.mmHg,
            name="diastolic blood pressure [mmHg]",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            constant=False,
        ),
        Parameter(
            "MAP",
            np.nan,
            U.mmHg,
            constant=False,
            name="mean arterial pressure [mmHg]",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        ),
        Parameter(
            "BP_ang2_fe",
            **FITS.parameter("BP_ang2_fe", unit=U.dimensionless),
            name="effect of angiotensin II on blood pressure [-]",
            notes="""
            Relative change of the blood pressure per relative change of
            angiotensin II, the vasoconstriction through AT1 receptors: without
            angiotensin II the pressure falls by BP_ang2_fe of its reference.
            """,
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        ),
    ]
)
_m.rules.extend(
    [
        AssignmentRule(
            "SBP",
            "SBP_ref * (1 dimensionless + BP_ang2_fe * (ang2-ang2_ref)/ang2_ref)",
            unit=U.mmHg,
        ),
        AssignmentRule(
            "DBP",
            "DBP_ref * (1 dimensionless + BP_ang2_fe * (ang2-ang2_ref)/ang2_ref)",
            unit=U.mmHg,
        ),
        AssignmentRule("MAP", "DBP + (SBP - DBP)/3 dimensionless", unit=U.mmHg),
        AssignmentRule(
            "MAP_ref", "DBP_ref + (SBP_ref - DBP_ref)/3 dimensionless", unit=U.mmHg
        ),
    ]
)

# blood pressure changes
for sid in ["SBP", "DBP", "MAP"]:
    # absolute change
    _m.parameters.append(
        Parameter(
            f"{sid}_change",
            name=f"{sid} change",
            value=np.nan,
            unit=U.mmHg,
            constant=False,
            notes=f"Absolute change to baseline {sid}",
        )
    )
    _m.rules.append(AssignmentRule(f"{sid}_change", f"{sid}-{sid}_ref", unit=U.mmHg))
    # relative change
    _m.parameters.append(
        Parameter(
            f"{sid}_ratio",
            name=f"{sid} ratio",
            value=np.nan,
            unit=U.dimensionless,
            constant=False,
            notes=f"Ratio relative to baseline {sid}",
        )
    )
    _m.rules.append(
        AssignmentRule(f"{sid}_ratio", f"{sid}/{sid}_ref", unit=U.dimensionless)
    )
    # relative change
    _m.parameters.append(
        Parameter(
            f"{sid}_change_relative",
            name=f"{sid} change relative",
            value=np.nan,
            unit=U.dimensionless,
            constant=False,
            notes=f"Change relative to baseline {sid}",
        )
    )
    _m.rules.append(
        AssignmentRule(
            f"{sid}_change_relative", f"{sid}_change/{sid}_ref", unit=U.dimensionless
        )
    )


model_raas = _m


if __name__ == "__main__":
    from sbmlode import OdeSystem

    from pkdb_models.models.enalapril import MODEL_BASE_PATH

    results: FactoryResult = create_model(
        model=model_raas,
        filepath=MODEL_BASE_PATH / f"{model_raas.sid}.xml",
        sbml_level=3,
        sbml_version=2,
        validation_options=ValidationOptions(units_consistency=True),
    )
    # create differential equations
    md_path = MODEL_BASE_PATH / f"{model_raas.sid}.md"
    ode_system = OdeSystem.from_sbml(results.sbml_path)
    ode_system.write(md_path)
