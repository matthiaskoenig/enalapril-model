"""Kidney model of the renal excretion of enalapril and enalaprilat."""

from sbmlutils.factory import (
    AssignmentRule,
    Compartment,
    FactoryResult,
    Model,
    Parameter,
    Reaction,
    Species,
    UnitDefinition,
    create_model,
)
from sbmlutils.metadata import (
    BQB,
    SBO,
)

from pkdb_models.models.enalapril.models import annotations, templates
from pkdb_models.models.enalapril.models.fits import FITS


class U(templates.U):
    """Units of the kidney model."""

    ml_per_min = UnitDefinition("ml_per_min", "ml/min")
    l_per_ml = UnitDefinition("l_per_ml", "l/ml")


mid = "enalapril_kidney"

_m = Model(
    sid=mid,
    name="Model for renal enalapril and enalaprilat excretion.",
    notes="""
    Model for the renal excretion of enalapril and enalaprilat.

    Enalapril and enalaprilat are excreted unchanged in the urine (filtration
    and tubular secretion), no other metabolites are found. After 10 mg of
    enalapril maleate about 25 % of the dose are recovered as enalapril and
    35 % as enalaprilat {Ishizaki1988, Ohnishi1989}, 45 % after 20 mg
    (3.41 mg enalapril, 3.78 mg enalaprilat) {Burckhardt2015}.

    The renal clearances are given relative to the filtration of the unbound
    fraction, `GFR * fu`, and scale with the renal function: `GFR =
    f_renal_function * GFR_base`, the healthy GFR `GFR_base` (101 ml/min at
    75 kg) is replaced by the body model.
    """
    + templates.terms_of_use,
    creators=templates.creators,
    units=U,
    model_units=templates.model_units,
    annotations=[
        # tissue
        (BQB.OCCURS_IN, "fma/FMA:7203"),  # kidney
        (BQB.OCCURS_IN, "bto/BTO:0000671"),
        (BQB.OCCURS_IN, "ncit/C12415"),
        (BQB.HAS_PROPERTY, "ncit/C79372"),  # Pharmacokinetics: Excretion
        *annotations.model,
    ],
)

_m.compartments = [
    Compartment(
        "Vext",
        value=1.5,
        unit=U.liter,
        name="plasma",
        constant=True,
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        annotations=annotations.compartments["plasma"],
        port=True,
    ),
    Compartment(
        "Vki",
        value=0.3,  # 0.4 % of bodyweight
        unit=U.liter,
        name="kidney",
        constant=True,
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        annotations=annotations.compartments["ki"],
        port=True,
    ),
    Compartment(
        "Vurine",
        1.0,
        name="urine",
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        unit=U.liter,
        port=True,
        annotations=annotations.compartments["urine"],
    ),
]

_m.species = [
    Species(
        "ena_ext",
        name="enalapril (plasma)",
        initialConcentration=0.0,
        compartment="Vext",
        substanceUnit=U.mmole,
        hasOnlySubstanceUnits=False,  # this is a concentration
        sboTerm=SBO.SIMPLE_CHEMICAL,
        annotations=annotations.species["ena"],
        port=True,
    ),
    Species(
        "eat_ext",
        name="enalaprilat (plasma)",
        initialConcentration=0.0,
        compartment="Vext",
        substanceUnit=U.mmole,
        hasOnlySubstanceUnits=False,  # this is a concentration
        sboTerm=SBO.SIMPLE_CHEMICAL,
        annotations=annotations.species["eat"],
        port=True,
    ),
    Species(
        "ena_urine",
        name="enalapril (urine)",
        initialConcentration=0.0,
        compartment="Vurine",
        substanceUnit=U.mmole,
        hasOnlySubstanceUnits=True,
        sboTerm=SBO.SIMPLE_CHEMICAL,
        annotations=annotations.species["ena"],
        port=True,
    ),
    Species(
        "eat_urine",
        name="enalaprilat (urine)",
        initialConcentration=0.0,
        compartment="Vurine",
        substanceUnit=U.mmole,
        hasOnlySubstanceUnits=True,  # this is an amount
        sboTerm=SBO.SIMPLE_CHEMICAL,
        annotations=annotations.species["eat"],
        port=True,
    ),
]

_m.parameters.extend(
    [
        Parameter(
            "f_renal_function",
            name="renal function",
            value=1.0,
            unit=U.dimensionless,
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            notes="""
            >1.0: increased kidney function
            1.0: normal kidney function (healthy control)
            <1.0: decreased kidney function

            Renal function relative to the healthy glomerular filtration rate
            GFR_base, which is 101 ml/min at 75 kg; a measured creatinine
            clearance of X ml/min is the renal function X/101.
            """,
        ),
        Parameter(
            "GFR_base",
            101,
            U.ml_per_min,
            name="glomerular filtration rate (healthy)",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            port=True,
        ),
        Parameter(
            "fu_ena",
            1.0,
            U.dimensionless,
            constant=True,
            name="fraction unbound in plasma enalapril",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            notes="Replaced by the body model.",
            port=True,
        ),
        Parameter(
            "fu_eat",
            0.62,
            U.dimensionless,
            constant=True,
            name="fraction unbound in plasma enalaprilat",
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            notes="Replaced by the body model.",
            port=True,
        ),
        # fitted: the renal clearance of enalapril is 252-372 ml/min
        # {Burckhardt2015, Baba1990, Ishizaki1988, Ohnishi1989}, a net tubular
        # secretion (OAT3)
        Parameter(
            "ENAEX_f",
            **FITS.parameter("KI__ENAEX_f", unit=U.dimensionless),
            name="renal clearance of unbound enalapril relative to the GFR",
            sboTerm=SBO.KINETIC_CONSTANT,
            notes="""
            The renal clearance of enalapril is ENAEX_f times the filtration
            of its unbound fraction, fu_ena * GFR: 1 is filtration alone, above
            1 a net secretion, below 1 a net reabsorption.
            """,
        ),
        # fitted: the unbound renal clearance of enalaprilat is 222 +- 49
        # ml/min, 1.85 times the inulin clearance {Mujais1992}, the renal
        # clearance 125-190 ml/min {Burckhardt2015, Baba1990, Ohnishi1989,
        # Ishizaki1988}
        Parameter(
            "EATEX_f",
            **FITS.parameter("KI__EATEX_f", unit=U.dimensionless),
            name="renal clearance of unbound enalaprilat relative to the GFR",
            sboTerm=SBO.KINETIC_CONSTANT,
            notes="""
            The renal clearance of enalaprilat is EATEX_f times the filtration
            of its unbound fraction, fu_eat * GFR: 1 is filtration alone, above
            1 a net secretion, below 1 a net reabsorption.
            """,
        ),
    ]
)

_m.rules.extend(
    [
        AssignmentRule(
            "GFR",
            "f_renal_function * GFR_base",
            unit=U.ml_per_min,
            name="glomerular filtration rate",
        ),
    ]
)

_m.reactions = [
    Reaction(
        sid="ENAEX",
        name="enalapril renal excretion (ENAEX)",
        equation="ena_ext -> ena_urine",
        compartment="Vki",
        sboTerm=SBO.TRANSPORT_REACTION,
        # [ml/min] * [l/ml] * [-] * [-] * [mmole/l]
        formula=(
            "GFR * 0.001 l_per_ml * fu_ena * ENAEX_f * ena_ext",
            U.mmole_per_min,
        ),
    ),
    Reaction(
        sid="EATEX",
        name="enalaprilat renal excretion (EATEX)",
        equation="eat_ext -> eat_urine",
        compartment="Vki",
        sboTerm=SBO.TRANSPORT_REACTION,
        # [ml/min] * [l/ml] * [-] * [-] * [mmole/l]
        formula=(
            "GFR * 0.001 l_per_ml * fu_eat * EATEX_f * eat_ext",
            U.mmole_per_min,
        ),
    ),
]

_m.rules.append(
    AssignmentRule(
        "ENA_EATEX",
        "ENAEX + EATEX",
        U.mmole_per_min,
        name="renal excretion of enalapril and enalaprilat",
    )
)


model_kidney = _m

if __name__ == "__main__":
    from pkdb_models.models.enalapril import MODEL_BASE_PATH

    results: FactoryResult = create_model(
        model=model_kidney,
        filepath=MODEL_BASE_PATH / f"{model_kidney.sid}.xml",
        sbml_level=3,
        sbml_version=2,
    )
