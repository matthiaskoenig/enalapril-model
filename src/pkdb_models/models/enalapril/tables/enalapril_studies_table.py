"""Latex table of the studies of the enalapril model.

The table is created from `enalapril_studies.tsv` and written to
`enalapril_studies.tex`.
"""

from pathlib import Path

import pandas as pd
from sbmlutils.console import console


def create_latex_table(df: pd.DataFrame) -> str:
    """Create the rows of the latex table of the studies.

    The first three columns are the reference of the study, its PK-DB id and its
    PubMed id, which become a citation and links.

    Args:
        df: the studies, one row per study.

    Returns:
        The header and the rows of the table, every second row shaded.
    """
    latex = ""

    columns = df.columns
    columns_formated = ["\\textbf{" + c + "}" for c in columns]
    latex += " & ".join(columns_formated) + " \\\\\n"
    latex += "\n\\hline\n\n"

    for k, (_, row) in enumerate(df.iterrows()):
        if k % 2 == 0:
            latex += "\\rowcolor{Lightgrey}\n"
        values = [
            str(v).replace("TRUE", "\\checkmark").replace("-", "") for v in row.values
        ]

        # references
        values[0] = values[0] + " \\cite{" + values[0] + "}"

        # links
        values[1] = (
            "\\href{https://identifiers.org/pkdb:" + values[1] + "}{" + values[1] + "}"
        )
        values[2] = (
            "\\href{https://pubmed.ncbi.nlm.nih.gov/"
            + values[2]
            + "/}{"
            + values[2]
            + "}"
        )

        latex += " & ".join(values) + "\\\\\n"

    return latex


if __name__ == "__main__":
    tsv_path = Path(__file__).parent / "enalapril_studies.tsv"
    latex_path = Path(__file__).parent / "enalapril_studies.tex"
    df = pd.read_csv(tsv_path, sep="\t")
    console.print(df)
    latex_str = create_latex_table(df)
    console.rule(style="white")
    console.print(latex_str)
    console.rule(style="white")
    with open(latex_path, "w") as f_tex:
        f_tex.write(latex_str)
