"""Collect the data of the enalapril studies from the PK-DB study folders.

The studies are copied from a `pkdb_data` checkout (`PKDB_DATA`, else
`../pkdb_data`, see `pkpdsim.data.studies_dir`) into the data folder of the
model, see `pkpdsim.data.collect_tsv_files`.
Besides the enalapril studies, two studies of other substances have enalapril
groups: Ulm1982 (lisinopril) and Howes1991 (hydrochlorothiazide).
"""

from pathlib import Path

from pkpdsim.data import collect_tsv_files
from pkpdsim.data import studies_dir as pkdb_studies_dir

from pkdb_models.models.enalapril import (
    DATA_PATH_ENALAPRIL,
    DATA_PATH_HYDROCHLOROTHIAZIDE,
    DATA_PATH_LISINOPRIL,
)

#: the studies of other substances which the enalapril experiments use
LISINOPRIL_STUDIES = {"Ulm1982"}
HYDROCHLOROTHIAZIDE_STUDIES = {"Howes1991"}


def collect_data(studies_dir: Path | None = None) -> None:
    """Copy the data of the enalapril studies into the data folder of the model.

    Args:
        studies_dir: the `studies` folder of pkdb_data, by default the one of
            the checkout `pkpdsim.data.studies_dir` finds.
    """
    if studies_dir is None:
        studies_dir = pkdb_studies_dir()
    collect_tsv_files(
        source_dir=studies_dir / "enalapril", target_dir=DATA_PATH_ENALAPRIL
    )
    collect_tsv_files(
        source_dir=studies_dir / "lisinopril",
        target_dir=DATA_PATH_LISINOPRIL,
        filter_study=lambda study: study in LISINOPRIL_STUDIES,
    )
    collect_tsv_files(
        source_dir=studies_dir / "hydrochlorothiazide",
        target_dir=DATA_PATH_HYDROCHLOROTHIAZIDE,
        filter_study=lambda study: study in HYDROCHLOROTHIAZIDE_STUDIES,
    )


if __name__ == "__main__":
    collect_data()
