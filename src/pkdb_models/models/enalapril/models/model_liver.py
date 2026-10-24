"""Liver model for the ACE inhibitors."""

import numpy as np
from sbmlutils.factory import (
    Compartment,
    FactoryResult,
    Model,
    Parameter,
    Reaction,
    Species,
    create_model,
)
from sbmlutils.metadata import (
    BQB,
    SBO,
)

from pkdb_models.models.enalapril.models import annotations, templates
from pkdb_models.models.enalapril.models.fits import FITS


class U(templates.U):
    """Units of the liver model."""


mid = "enalapril_liver"

_m = Model(
    sid=mid,
    name="Model for hepatic enalapril metabolism.",
    notes="""
    Model for the hepatic metabolism of enalapril.

    Enalapril is taken up into the hepatocytes by OATP1B1 (`ENAIM`) and
    hydrolysed by the carboxylesterase 1 (CES1) to its active metabolite
    enalaprilat (`ENA2EAT`), which leaves the hepatocytes slowly (`EATEX`):
    the dicarboxylic acid enalaprilat permeates membranes poorly, enalaprilat
    in the plasma peaks 3.5-4.6 hr after an oral dose of enalapril, about
    3 hr after enalapril.

    The concentrations of enalapril and enalaprilat in the liver (0.1-6 µM)
    are far below the Michaelis constants of the transport and the
    conversion (0.4-1.7 mM), so all three are linear and only their ratios
    Vmax/Km act.
    """
    + templates.terms_of_use,
    creators=templates.creators,
    units=U,
    model_units=templates.model_units,
    annotations=[
        # tissue
        (BQB.OCCURS_IN, "fma/FMA:7197"),
        (BQB.OCCURS_IN, "bto/BTO:0000759"),
        (BQB.OCCURS_IN, "ncit/C12392"),
        (BQB.HAS_PROPERTY, "ncit/C79371"),  # Pharmacokinetics: Metabolism
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
        "Vli",
        value=1.5,
        unit=U.liter,
        name="liver",
        constant=True,
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        annotations=annotations.compartments["li"],
        port=True,
    ),
    Compartment(
        "Vmem",
        value=np.nan,
        unit=U.m2,
        name="plasma membrane",
        constant=True,
        sboTerm=SBO.PHYSICAL_COMPARTMENT,
        annotations=annotations.compartments["plasma membrane"],
        spatialDimensions=2,
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
        "ena",
        name="enalapril (liver)",
        initialConcentration=0.0,
        compartment="Vli",
        substanceUnit=U.mmole,
        hasOnlySubstanceUnits=False,  # this is a concentration
        sboTerm=SBO.SIMPLE_CHEMICAL,
        annotations=annotations.species["ena"],
    ),
    Species(
        "eat",
        name="enalaprilat (liver)",
        initialConcentration=0.0,
        compartment="Vli",
        substanceUnit=U.mmole,
        hasOnlySubstanceUnits=False,  # this is a concentration
        sboTerm=SBO.SIMPLE_CHEMICAL,
        annotations=annotations.species["eat"],
    ),
]

_m.reactions = [
    Reaction(
        sid="ENAIM",
        name="enalapril import (ENAIM) OATP1B1",
        equation="ena_ext <-> ena",
        compartment="Vmem",
        sboTerm=SBO.TRANSPORT_REACTION,
        pars=[
            Parameter(
                "ENAIM_Vmax",
                0.75,
                U.mmole_per_min_l,
                name="Vmax enalapril import",
                sboTerm=SBO.MAXIMAL_VELOCITY,
                notes="""
                Not fitted: the uptake and the conversion are serial and
                linear, the uptake is fast against the conversion.
                """,
            ),
            Parameter(
                "ENAIM_Km_ena",
                0.844,
                U.mM,
                name="Km enalapril import",
                sboTerm=SBO.MICHAELIS_CONSTANT,
                notes="""
                Km = 262 ± 35 µM OATP1B1 [Liu2006]
                Km = 844 ± 430 µM OATP1B1 [Ni2020]
                Km = 286.4 ± 84.3 µM OATP2B1 [Ni2020]
                """,
            ),
        ],
        formula=(
            "ENAIM_Vmax/ENAIM_Km_ena * Vli * (ena_ext - ena)/(1 dimensionless + ena_ext/ENAIM_Km_ena + ena/ENAIM_Km_ena)"
        ),
        notes="""
        Entrance of enalapril in the hepatocyte mediated by the organic anion transporting polypeptides (OATP) 1B1 [Smeets2020]
        Low affinity for OATP1B3 [Liu2006]
        """,
    ),
    Reaction(
        sid="ENA2EAT",
        name="enalapril conversion (ENA2EAT) CES1",
        equation="ena -> eat",
        compartment="Vli",
        sboTerm=SBO.BIOCHEMICAL_REACTION,
        pars=[
            Parameter(
                "ENA2EAT_Vmax",
                **FITS.parameter("LI__ENA2EAT_Vmax", unit=U.mmole_per_min_l),
                name="Vmax enalapril conversion",
                sboTerm=SBO.MAXIMAL_VELOCITY,
            ),
            Parameter(
                "ENA2EAT_Km_ena",
                1.721,
                U.mM,
                name="Km enalapril CES1",
                sboTerm=SBO.MICHAELIS_CONSTANT,
                notes="""[Thomsen2014]""",
            ),
            Parameter(
                "ENA2EAT_Ki_ena",
                2.956,
                U.mM,
                name="Ki enalapril CES1",
                sboTerm=SBO.INHIBITORY_CONSTANT,
                notes="""
                Substrate inhibition [Thomsen2014], without an effect at the
                concentrations of enalapril in the liver (below 10 µM).
                """,
            ),
            Parameter(
                "f_ces1",
                1,
                U.dimensionless,
                name="scaling factor CES1 activity",
                sboTerm=SBO.QUANTITATIVE_SYSTEMS_DESCRIPTION_PARAMETER,
                notes="""Scaling factor to vary CES1 activity.
                1.0: unchanged activity; < 1.0 decreased activity; >1.0 increased activity.
                """,
            ),
        ],
        formula=(
            "f_ces1 * ENA2EAT_Vmax * Vli * ena/(ena + ENA2EAT_Km_ena + power(ena,2)/ENA2EAT_Ki_ena)"
        ),
        notes="""
        Catalyzed via liver carboxylesterase 1 (CES1);
        Catalyzed via CES1 not CES2 [Thomsen2014]
        Enalapril demonstrated substrate inhibition kinetics. Intrinsic clearances were
        1.061, 0.360, and 0.02 ml/min/mg protein for ramipril, trandolapril, and enalapril, respectively. [Thomsen2014]
        """,
    ),
    Reaction(
        sid="EATEX",
        name="enalaprilat export (EATEX)",
        equation="eat <-> eat_ext",
        compartment="Vmem",
        sboTerm=SBO.TRANSPORT_REACTION,
        pars=[
            Parameter(
                "EATEX_Vmax",
                **FITS.parameter("LI__EATEX_Vmax", unit=U.mmole_per_min_l),
                name="Vmax enalaprilat export",
                sboTerm=SBO.MAXIMAL_VELOCITY,
            ),
            Parameter(
                "EATEX_Km_eat",
                0.43,
                U.mM,
                name="Km enalaprilat export",
                sboTerm=SBO.MICHAELIS_CONSTANT,
                notes="""
                Not fitted: the export is linear at the concentrations of
                enalaprilat in the liver, only EATEX_Vmax/EATEX_Km_eat acts.
                """,
            ),
        ],
        formula=(
            "EATEX_Vmax/EATEX_Km_eat * Vli * (eat - eat_ext)/(1 dimensionless + eat_ext/EATEX_Km_eat + eat/EATEX_Km_eat)"
        ),
    ),
]


model_liver = _m

if __name__ == "__main__":
    from pkdb_models.models.enalapril import MODEL_BASE_PATH

    results: FactoryResult = create_model(
        model=model_liver,
        filepath=MODEL_BASE_PATH / f"{model_liver.sid}.xml",
        sbml_level=3,
        sbml_version=2,
    )
