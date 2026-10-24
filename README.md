[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.11109907.svg)](https://doi.org/10.5281/zenodo.11109907)
[![Release](https://img.shields.io/github/v/release/matthiaskoenig/enalapril-model)](https://github.com/matthiaskoenig/enalapril-model/releases)
[![Documentation](https://github.com/matthiaskoenig/enalapril-model/actions/workflows/docs.yml/badge.svg)](https://matthiaskoenig.github.io/enalapril-model/)
[![CI](https://github.com/matthiaskoenig/enalapril-model/actions/workflows/ci.yml/badge.svg)](https://github.com/matthiaskoenig/enalapril-model/actions/workflows/ci.yml)
[![Docker](https://img.shields.io/docker/v/matthiaskoenig/enalapril?sort=semver&label=docker)](https://hub.docker.com/r/matthiaskoenig/enalapril)
[![Python](https://img.shields.io/badge/python-3.14-blue)](https://www.python.org)
[![Code license: MIT](https://img.shields.io/badge/code%20license-MIT-blue)](https://opensource.org/license/MIT)
[![Model license: CC BY-SA 4.0](https://img.shields.io/badge/model%20license-CC%20BY--SA%204.0-lightgrey)](https://creativecommons.org/licenses/by-sa/4.0/)

# Physiologically based pharmacokinetic/pharmacodynamic (PBPK/PD) model of enalapril

This repository provides the enalapril physiologically based pharmacokinetic/pharmacodynamic (PBPK/PD) model: the absorption of the prodrug enalapril, its hydrolysis by the hepatic carboxylesterase 1 to the active enalaprilat, the distribution of both and the binding of enalaprilat to tissue ACE, their renal excretion relative to the glomerular filtration, and the inhibition of ACE in the renin-angiotensin-aldosterone system with its effect on the blood pressure.

Documentation: <https://matthiaskoenig.github.io/enalapril-model/>

## Quick start

```bash
git clone https://github.com/matthiaskoenig/enalapril-model.git && cd enalapril-model
uv sync
uv run run_simulation pkdb_models.models.enalapril --action all -r results
```

## How to cite

> Palwankar, S. & König, M. (2026). *Physiologically based pharmacokinetic/pharmacodynamic (PBPK/PD) model of enalapril*. Zenodo. https://doi.org/10.5281/zenodo.11109907

## License

* Source Code: [MIT](https://opensource.org/license/MIT)
* Documentation: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
* Models: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)

&copy; 2024-2026 Shubhankar Palwankar and Matthias König
