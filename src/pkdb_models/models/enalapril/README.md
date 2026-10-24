# Enalapril

Physiologically based pharmacokinetic/pharmacodynamic (PBPK/PD) model of the angiotensin-converting enzyme (ACE) inhibitor enalapril: the dissolution and absorption of the prodrug enalapril (enalapril maleate) in the intestine, with food as a switch which slows the dissolution, its hydrolysis by the hepatic carboxylesterase 1 (CES1) to the active enalaprilat, the distribution of enalapril and enalaprilat, the saturable binding of enalaprilat to tissue ACE which carries its long terminal phase, the renal excretion of both relative to the glomerular filtration rate (GFR), and the inhibition of ACE in the renin-angiotensin-aldosterone system (RAAS) with its effect on angiotensin I and II, renin, aldosterone and the blood pressure. Renal impairment (the GFR), cirrhosis, heart failure and the CES1 genotype are parameters of the model.

## Structure

- `models/`: the tissue models (`model_intestine.py`, `model_liver.py`, `model_kidney.py`), the RAAS model (`model_raas.py`) and the whole-body model (`model_body.py`). `models/factory.py` creates the SBML models, the flattened whole-body model which is simulated, the ODEs and the COMBINE archive in `models/output/`; the fitted values come from the adopted fits (`models/fits.py`).
- `experiments/`: the simulation experiments of the 49 clinical studies (`studies/`), the dose dependency and the test of the RAAS model (`misc/`) and the scans of the dose, food, cirrhosis, renal function, cardiac function and CES1 activity (`scans/`). The fit mappings are described with the vocabulary of `pkpdsim.metadata`.
- `fitting/`: the fit problems of the pharmacokinetics (`PK`) and the pharmacodynamics (`PD`); `mapping_collections.py` selects the training data and names the validation data by the question they answer (interactions, doses, populations, limitations of the model), the outliers and the aggregates.
- `sensitivity/`: the sensitivity analysis of the pharmacokinetic and pharmacodynamic parameters for the control, renal impairment and cirrhosis.
- `enalapril_pk.py`: the non-compartmental analysis of enalapril and enalaprilat and the extremes of the pharmacodynamics of the scans.
- `data/`: the data of the studies, a subset of the PK-DB studies (`data/collect_data.py`).

## Commands

```bash
# models, simulations
run_simulation pkdb_models.models.enalapril --action factory
run_simulation pkdb_models.models.enalapril --action list_experiments
run_simulation pkdb_models.models.enalapril --action simulate --experiments all
run_simulation pkdb_models.models.enalapril --action simulate --experiments all --uncertainty

# fits, adoption of a fit, reports of stored parameters, identifiability
run_fit pkdb_models.models.enalapril --subset=PK --runs=3 --cores=3 --method=DE
run_fit pkdb_models.models.enalapril --adopt PK_<fit id>
run_report pkdb_models.models.enalapril --subset=PK results/fit/PK_<fit id>/parameters.json
run_identifiability pkdb_models.models.enalapril --subset=PK results/fit/PK_<fit id>/parameters.json

# sensitivity analysis (local by default)
python -m pkdb_models.models.enalapril.sensitivity.sensitivity_analysis
```

The results are written into `results/` of the model.

## Adopted fits and uncertainty

The values of the fitted parameters come from the adopted fits of the model,
not from numbers in the code: the pharmacokinetics
`PK_20261020_114902__1f0f7` and the pharmacodynamics
`PD_20261020_125416__5ce99`, fitted on the adopted pharmacokinetics.
`run_fit pkdb_models.models.enalapril --adopt <fit id>` copies the record of a
finished fit (its parameters, problem, profile likelihood and Fisher
information) into `models/output/fits/<fit id>/`, which is tracked; the ids of
the adopted fits are listed in `fits` of the model object (`__init__.py`). The
factory takes the fitted values and their uncertainty from the records
(`models/fits.py`) and writes the uncertainty into the SBML
(`distrib:uncertainty`). `run_simulation ... --uncertainty` runs the
experiments over draws of these distributions and draws the simulations as the
median with a band of quantiles into `results/simulation_uncertainty`. A refit
is: fit, adopt, replace the id in `fits`, rebuild the model. The open issues of
the model are in `TODO.md`.
