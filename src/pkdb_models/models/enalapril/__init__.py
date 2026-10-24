"""Enalapril: PBPK/PD model of enalapril and the renin-angiotensin-aldosterone system.

The paths of the model and its model object `MODEL`, which the commands
`run_simulation`, `run_fit`, `run_report` and `run_identifiability` of pkpdsim
run by its package `pkdb_models.models.enalapril`.
"""

from pathlib import Path

from pkpdsim.model import FigureSettings, PKPDModel, SimulatorSettings
from pkpdsim.release.settings import Author, ReleaseSettings

from pkdb_models.models.enalapril.tolerances import ABSOLUTE_TOLERANCE

ENALAPRIL_PATH = Path(__file__).parent

MODEL_BASE_PATH = ENALAPRIL_PATH / "models" / "output" / "models"
MODEL_PATH = MODEL_BASE_PATH / "enalapril_body_flat.xml"

# the subset of the PK-DB studies the model uses, see `data/collect_data.py`
DATA_PATH_BASE = ENALAPRIL_PATH / "data"
DATA_PATH_ENALAPRIL = DATA_PATH_BASE / "enalapril"
DATA_PATH_LISINOPRIL = DATA_PATH_BASE / "lisinopril"
DATA_PATH_HYDROCHLOROTHIAZIDE = DATA_PATH_BASE / "hydrochlorothiazide"
DATA_PATHS = [
    DATA_PATH_ENALAPRIL,
    DATA_PATH_LISINOPRIL,
    DATA_PATH_HYDROCHLOROTHIAZIDE,
]

MODEL = PKPDModel(
    name="enalapril",
    package=__name__,
    title="Enalapril PBPK/PD model",
    path=ENALAPRIL_PATH,
    model_path=MODEL_PATH,
    data_paths=tuple(DATA_PATHS),
    archive_path=MODEL_BASE_PATH.parent / "enalapril_model.omex",
    factory=".models.factory:create_enalapril_models",
    experiments=".simulations:EXPERIMENTS",
    fit_definitions=".fitting.fitting:FIT_DEFINITIONS",
    simulator=SimulatorSettings(
        absolute_tolerance=ABSOLUTE_TOLERANCE, relative_tolerance=1e-10
    ),
    figures=FigureSettings(formats=("svg",), fig_dpi=300, legend_fontsize=10),
    fit_identifiability=True,
    # the adopted fits, whose values and uncertainties the factory takes
    fits=("PK_20261020_114902__1f0f7", "PD_20261020_125416__5ce99"),
    # the release of the model repository (concept DOI of the Zenodo record of
    # matthiaskoenig/enalapril-model)
    release=ReleaseSettings(
        title=(
            "Physiologically based pharmacokinetic/pharmacodynamic (PBPK/PD) model"
            " of enalapril"
        ),
        repository="matthiaskoenig/enalapril-model",
        doi="10.5281/zenodo.11109907",
        authors=(
            Author(
                "Palwankar, Shubhankar",
                "0009-0007-3431-463X",
                "Humboldt-Universität zu Berlin, Institute for Theoretical Biology, Berlin, Germany",
            ),
            Author(
                "König, Matthias",
                "0000-0003-1725-179X",
                (
                    "Humboldt-Universität zu Berlin, Faculty of Life Sciences, Department of Biology, Institute of Theoretical Biology, Systems Medicine of the Liver; University of Stuttgart, Institute of Structural Mechanics and Dynamics in Aerospace Engineering; University of Southern Denmark, Clinical Pharmacology, Pharmacy and Environmental Medicine, Department of Public Health; University Hospital Schleswig-Holstein, Campus Lübeck, First Department of Medicine, Lübeck, Germany"
                ),
            ),
        ),
        keywords=(
            "model",
            "enalapril",
            "enalaprilat",
            "ACE inhibitor",
            "carboxylesterase 1",
            "renin-angiotensin-aldosterone system",
            "pharmacokinetics",
            "pharmacodynamics",
            "PBPK/PD",
            "physiologically based pharmacokinetic/ pharmacodynamic model",
            "SBML",
        ),
        docker_image="matthiaskoenig/enalapril",
        funding=(
            "Matthias König was supported by the Federal Ministry of Research, Technology and Space (BMFTR, Germany) within ATLAS by grant number 031L0304B and by the German Research Foundation (DFG) within the Research Unit Program FOR 5151 QuaLiPerF (Quantifying Liver Perfusion-Function Relationship in Complex Resection - A Systems Medicine Approach) by grant number 436883643 and by grant number 465194077 (Priority Programme SPP 2311, Subproject SimLivA). This work was supported by the BMBF-funded de.NBI Cloud within the German Network for Bioinformatics Infrastructure (de.NBI) (031A537B, 031A533A, 031A538A, 031A533B, 031A535A, 031A537C, 031A534A, 031A532B)."
        ),
        description=(
            "This repository provides the enalapril physiologically based"
            " pharmacokinetic/pharmacodynamic (PBPK/PD) model: the absorption of"
            " the prodrug enalapril, its hydrolysis by the hepatic carboxylesterase"
            " 1 to the active enalaprilat, the distribution of both and the binding"
            " of enalaprilat to tissue ACE, their renal excretion relative to the"
            " glomerular filtration, and the inhibition of ACE in the"
            " renin-angiotensin-aldosterone system with its effect on the blood"
            " pressure."
        ),
        first_year=2024,
    ),
)
"""The enalapril model: its commands, see `pkpdsim.model`."""
