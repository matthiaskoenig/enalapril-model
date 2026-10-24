"""Enalapril intestine model."""

import numpy as np
from sbmlutils.factory import (
    AssignmentRule,
    Compartment,
    Model,
    Parameter,
    RateRule,
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
    """Units of the intestine model."""

    per_hr = UnitDefinition("per_hr", "1/hr")
    mg_per_min = UnitDefinition("mg_per_min", "mg/min")


_m = Model(
    "enalapril_intestine",
    name="Model for enalapril absorption in the small intestine",
    notes="""
    # Model for enalapril absorption

    The oral dose of enalapril (the maleate salt, dosed as enalapril) dissolves
    and passes the stomach (`Ka_dis_ena`, replaced by the body model) into the
    lumen of the small intestine, from where the fraction `F_ena_abs` is
    absorbed into the portal plasma and the rest is excreted in the feces.

    - 56 +- 6 % of an oral dose of 14C-enalapril are recovered in the urine,
      39 +- 5 % in the feces, i.e. about 60 % are absorbed {Ulm1982, Ball1987}
    - the bioavailability of enalaprilat after enalapril is about 40 %, the
      absorption of enalapril about 60-64 % {Hockings1986, Dickstein1987}
    - food (a high fat breakfast) slows the absorption: Cmax of enalapril
      falls to 0.54 at an AUC of 0.86 {Moffett2014}, the exposure to
      enalaprilat and its urinary recovery do not change after a tablet with a
      meal {Swanson1984}; the fed state slows the dissolution and the gastric
      emptying (`fed`, `FED_f_dissolution`)
    """
    + templates.terms_of_use,
    creators=templates.creators,
    units=U,
    model_units=templates.model_units,
    annotations=[
        # tissue
        (BQB.OCCURS_IN, "bto/BTO:0000545"),  # gut
        (BQB.OCCURS_IN, "ncit/C12736"),  # intestine
        (BQB.OCCURS_IN, "fma/FMA:7199"),  # intestine
        (BQB.OCCURS_IN, "bto/BTO:0000648"),  # intestine
        (BQB.HAS_PROPERTY, "ncit/C79369"),  # Pharmacokinetics: Absorption
        (BQB.HAS_PROPERTY, "ncit/C79372"),  # Pharmacokinetics: Excretion
        *annotations.model,
    ],
)

_m.compartments = [
    Compartment(
        "Vext",
        1.0,
        name="plasma",
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        unit=U.liter,
        port=True,
        annotations=annotations.compartments["plasma"],
    ),
    Compartment(
        "Vgu",
        1.2825,  # 0.0171 [l/kg] * 75 kg
        name="intestine",
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        unit=U.liter,
        port=True,
        annotations=annotations.compartments["gu"],
    ),
    Compartment(
        "Vlumen",
        1.2825 * 0.9,  # 0.0171 [l/kg] * 75 kg * 0.9
        name="intestinal lumen (inner part of intestine)",
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        unit=U.liter,
        constant=False,
        port=True,
        annotations=annotations.compartments["gu_lumen"],
    ),
    Compartment(
        "Vfeces",
        metaId="meta_Vfeces",
        value=1,
        unit=U.liter,
        constant=True,
        name="feces",
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        port=True,
        annotations=annotations.compartments["feces"],
    ),
    Compartment(
        "Vstomach",
        metaId="meta_Vstomach",
        value=1,
        unit=U.liter,
        constant=True,
        name="stomach",
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        port=True,
        annotations=annotations.compartments["stomach"],
    ),
]

_m.species = [
    Species(
        "ena_stomach",
        metaId="meta_ena_stomach",
        initialConcentration=0.0,
        compartment="Vstomach",
        substanceUnit=U.mmole,
        name="enalapril (stomach)",
        hasOnlySubstanceUnits=True,
        sboTerm=SBO.SIMPLE_CHEMICAL,
        annotations=annotations.species["ena"],
        boundaryCondition=True,
    ),
    Species(
        "ena_lumen",
        initialConcentration=0.0,
        name="enalapril (intestinal lumen)",
        compartment="Vlumen",
        substanceUnit=U.mmole,
        hasOnlySubstanceUnits=False,
        sboTerm=SBO.SIMPLE_CHEMICAL,
        annotations=annotations.species["ena"],
        port=True,
    ),
    Species(
        "ena_ext",
        initialConcentration=0.0,
        name="enalapril (plasma)",
        compartment="Vext",
        substanceUnit=U.mmole,
        hasOnlySubstanceUnits=False,
        sboTerm=SBO.SIMPLE_CHEMICAL,
        annotations=annotations.species["ena"],
        port=True,
    ),
    Species(
        "ena_feces",
        initialConcentration=0.0,
        name="enalapril (feces)",
        compartment="Vfeces",
        substanceUnit=U.mmole,
        hasOnlySubstanceUnits=True,
        sboTerm=SBO.SIMPLE_CHEMICAL,
        annotations=annotations.species["ena"],
        port=True,
    ),
]

_m.parameters = [
    Parameter(
        "F_ena_abs",
        **FITS.parameter("GU__F_ena_abs", unit=U.dimensionless),
        constant=True,
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        name="fraction absorbed enalapril",
        notes="""
        Fraction absorbed, i.e., only a fraction of the enalapril in the
        intestinal lumen is absorbed, `(1 - F_ena_abs)` is excreted in the
        feces. 56 +- 6 % of an oral dose of 14C-enalapril are recovered in the
        urine and 39 +- 5 % in the feces {Ulm1982, Ball1987}; the absorption is
        60-64 % {Hockings1986, Dickstein1987}.
        """,
    ),
    Parameter(
        "ENAABS_k",
        **FITS.parameter("GU__ENAABS_k", unit=U.per_min),
        name="rate of enalapril absorption",
        sboTerm=SBO.KINETIC_CONSTANT,
        notes="""
        With the dissolution and gastric emptying `Ka_dis_ena` a chain of two
        first order steps, which gives the delayed and steep rise of
        enalapril (tmax about 1 hr).
        """,
    ),
    Parameter(
        "fed",
        0.0,
        unit=U.dimensionless,
        name="fed state (0 fasted, 1 fed)",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        notes="""
        The dose is taken in the fasted state (0) or with a high fat meal (1).
        The effect of food on the dissolution and gastric emptying is
        `FED_f_dissolution`; the fraction absorbed does not change
        {Swanson1984}.
        """,
    ),
    Parameter(
        "FED_f_dissolution",
        **FITS.parameter("GU__FED_f_dissolution", unit=U.dimensionless),
        name="fed effect on the dissolution and gastric emptying",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
        notes="""
        Factor of the rate of dissolution and gastric emptying with a high fat
        meal: Cmax of enalapril 0.54, AUC 0.86, tmax 0.3-1 hr later
        {Moffett2014}.
        """,
    ),
    Parameter(
        "f_dissolution",
        np.nan,
        unit=U.dimensionless,
        constant=False,
        name="factor of the dissolution and gastric emptying",
        sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
    ),
]

_m.rules.extend(
    [
        AssignmentRule(
            "absorption",
            value="ENAABS_k * Vgu * ena_lumen",
            unit=U.mmole_per_min,
            name="transit of enalapril (absorption and fecal excretion)",
        ),
        AssignmentRule(
            "f_dissolution",
            "1 dimensionless + fed * (FED_f_dissolution - 1 dimensionless)",
            unit=U.dimensionless,
        ),
    ]
)

_m.reactions = [
    Reaction(
        "ENAABS",
        name="absorption enalapril",
        equation="ena_lumen -> ena_ext",
        sboTerm=SBO.TRANSPORT_REACTION,
        compartment="Vgu",
        formula=("F_ena_abs * absorption", U.mmole_per_min),
    ),
    Reaction(
        sid="ENAEXC",
        name="excretion enalapril (feces)",
        compartment="Vlumen",
        equation="ena_lumen -> ena_feces",
        sboTerm=SBO.TRANSPORT_REACTION,
        formula=(
            "(1 dimensionless - F_ena_abs) * absorption",
            U.mmole_per_min,
        ),
    ),
]

_m.parameters.extend(
    [
        Parameter(
            "PODOSE_ena",
            0,
            U.mg,
            constant=False,
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            name="oral dose enalapril [mg]",
            port=True,
        ),
        Parameter(
            "Ka_dis_ena",
            2.0,
            U.per_hr,
            constant=True,
            sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
            name="Ka_dis [1/hr] dissolution enalapril",
            notes="""
            Dissolution of the tablet and gastric emptying; replaced by the
            body model.
            """,
            port=True,
        ),
        Parameter(
            "Mr_ena",
            376.4467,
            U.g_per_mole,
            constant=True,
            name="Molecular weight enalapril [g/mole]",
            sboTerm=SBO.MOLECULAR_MASS,
            notes="Replaced by the molecular weight of the body model.",
            port=True,
        ),
    ]
)

# -------------------------------------
# Dissolution of tablet/dose in stomach
# -------------------------------------
_m.reactions.extend(
    [
        # fraction dose available for absorption from stomach
        Reaction(
            sid="dissolution_ena",
            name="dissolution enalapril",
            formula=(
                "f_dissolution * Ka_dis_ena/60 min_per_hr * PODOSE_ena/Mr_ena",
                U.mmole_per_min,
            ),
            equation="ena_stomach -> ena_lumen",
            compartment="Vgu",
            notes="""Swallowing, dissolution of tablet, and transport into intestine.
            Overall process describing the rates of this processes.
            """,
        ),
    ]
)
_m.rate_rules.extend(
    [
        # the dose leaves the stomach with the dissolution
        RateRule("PODOSE_ena", "-dissolution_ena * Mr_ena", U.mg_per_min),
    ]
)

model_intestine = _m


if __name__ == "__main__":
    from pkdb_models.models.enalapril import MODEL_BASE_PATH

    result = create_model(
        filepath=MODEL_BASE_PATH / f"{model_intestine.sid}.xml",
        model=model_intestine,
        sbml_level=3,
        sbml_version=2,
    )
