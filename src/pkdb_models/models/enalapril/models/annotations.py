"""Annotations of the enalapril models: the model and its species.

The body, intestine, liver, kidney and RAAS models of enalapril are annotated
with this module. The compartments are the shared ones of
`pkpdsim.annotations`.
"""

from pkpdsim.annotations import compartments
from sbmlutils.metadata import (
    BQB,
)

__all__ = ["compartments", "model", "species"]

model = [
    # model
    # (BQM.IS, "biomodels.db/MODEL2510140001"), FIXME
    # taxonomy
    (BQB.HAS_TAXON, "taxonomy/9606"),  # human
    (BQB.HAS_TAXON, "snomedct/337915000"),  # human
    # modelling approach
    (BQB.HAS_PROPERTY, "mamo/MAMO_0000046"),  # ordinary differential equation model
    # biological process explained by model (GO/NCIT)
    (BQB.HAS_PROPERTY, "ncit/C62027"),  # enalapril
    (BQB.HAS_PROPERTY, "ncit/C47510"),  # enalaprilat
    (BQB.HAS_PROPERTY, "ncit/C270"),  # Antihypertensive Agent
    (BQB.HAS_PROPERTY, "ncit/C247"),  # ACE Inhibitor
    (BQB.HAS_PROPERTY, "ncit/C15299"),  # pharmacokinetics
    (BQB.HAS_PROPERTY, "ncit/C15720"),  # pharmacodynamics
    # model relevance to a particular area
    (BQB.HAS_PROPERTY, "ncit/C3117"),  # Hypertension
    (BQB.HAS_PROPERTY, "ncit/C3478"),  # Essential Hypertension
    (BQB.HAS_PROPERTY, "ncit/C172184"),  # Antihypertensive Therapy
    # model reference
    (BQB.IS_DESCRIBED_BY, "doi/10.5281/zenodo.11109907"),
]

species = {
    "ena": [  # enalapril
        (BQB.IS, "chebi/CHEBI:4784"),
        (BQB.IS, "pubchem.compound/5388962"),
        (BQB.IS, "inchikey/GBXSMTUPTTWBMN-XIRDDKMYSA-N"),
        (BQB.IS, "ncit/C62027"),
    ],
    "eat": [  # enalaprilat
        (BQB.IS, "chebi/CHEBI:4786"),  # enalaprilat (anhydrous)
        (BQB.IS, "pubchem.compound/5462501"),
        (BQB.IS, "inchikey/LZFZMUMEGBBDTC-QEJZJMRPSA-N"),
        (BQB.IS, "ncit/C47510"),
    ],
    # enalapril + enalaprilat, the total drug of the radioimmunoassays after
    # the hydrolysis of enalapril
    "ena_eat": [
        (BQB.HAS_PART, "chebi/CHEBI:4784"),
        (BQB.HAS_PART, "chebi/CHEBI:4786"),
    ],
    # enalaprilat bound to tissue ACE, a complex of ACE
    "eatace": [
        (BQB.IS_VERSION_OF, "uniprot/P12821"),  # EC 3.4.15.1
        (BQB.IS_VERSION_OF, "ncit/C91297"),
        (BQB.HAS_PART, "chebi/CHEBI:4786"),
    ],
    "ace": [
        (BQB.IS, "uniprot/P12821"),  # EC 3.4.15.1
        (BQB.IS, "ncit/C91297"),
    ],
    "anggen": [
        (BQB.IS, "chebi/CHEBI:2720"),
        (BQB.IS, "ncit/C136723"),
        (BQB.IS, "uniprot/P01019"),
        (BQB.IS, "snomedct/54592005"),
    ],
    "ang1": [
        (BQB.IS, "chebi/CHEBI:147350"),
        (BQB.IS, "ncit/C248"),
        (BQB.IS, "snomedct/88368002"),
    ],
    "ang2": [
        (BQB.IS, "chebi/CHEBI:58506"),
        (BQB.IS, "ncit/C107562"),
        (BQB.IS, "snomedct/85267009"),
    ],
    "ald": [
        (BQB.IS, "chebi/CHEBI:27584"),
        (BQB.IS, "ncit/C219"),
        (BQB.IS, "snomedct/42605004"),
    ],
    "ren": [
        (BQB.IS, "uniprot/P00797"),
        (BQB.IS, "ncit/C113591"),
        (BQB.IS, "snomedct/112052004"),
    ],
}
