"""Parameter fit problems for enalapril.

The data of a fit is selected from the fit mappings of the studies in three
steps, see `sbmlsim.fit.helpers`: the filters on the metadata of the mappings
select the training data of the fit and exclude the rest, the outliers are
named once for all mappings and are the training data which is not usable, and
the validation data is the part of the data a fit is evaluated on but not
fitted to. The metadata of a mapping describes its curve, what a fit does with
the curve is decided here.

The training data are the subjects without a disease which changes the
pharmacokinetics (healthy, not reported, and hypertension, which changes
neither the absorption, the hydrolysis nor the renal excretion of enalapril;
the pharmacodynamics of hypertensive patients are the main data of the blood
pressure), with the wild type of CES1 (or not reported), without a
coadministered drug, fasted, fed (the effect of food on the dissolution is
fitted) or not reported. The validation data has a part per question: the
interactions (`INTERACTION_VALIDATION`, simulated with the documented factors
of `INTERACTION_FACTORS`), the doses (`DOSE_VALIDATION`), the populations
(`POPULATION_VALIDATION`, renal, hepatic and cardiac impairment and the
variants of CES1, which the model describes by the GFR, the degree of
cirrhosis, the cardiac output and the activity of CES1) and the limitations
(`LIMITATION_VALIDATION`, data of a population or a process the model does not
describe). The summaries of data which is fitted one by one are excluded
(`AGGREGATE_MAPPINGS`).
"""

from pkpdsim.fit import mapping_metadata, observable_filter, observable_id
from pkpdsim.metadata import Coadministration, Genotype, Health
from sbmlsim.console import console
from sbmlsim.experiment import SimulationExperiment
from sbmlsim.fit import FitMapping, FitMappingCollection, MappingKind
from sbmlsim.fit.helpers import FitMappings, MappingFilter

from pkdb_models.models.enalapril import DATA_PATHS, ENALAPRIL_PATH
from pkdb_models.models.enalapril.simulations import EXPERIMENTS

#: the keys of fit mappings by study: the keys of the mappings are SIds of their
#: experiment, which two studies can share, so a named mapping is named with
#: its study
type NamedMappings = dict[str, set[str]]

EXPERIMENT_CLASSES: list[type[SimulationExperiment]] = EXPERIMENTS["studies"]

#: observables of the pharmacokinetics
PK_OBSERVABLES = {
    "Cve_ena",
    "Cve_eat",
    "Cve_ena_eat",
    "Aurine_ena",
    "Aurine_eat",
    "Aurine_ena_eat",
    "Afeces_ena",
    "KI__ENAEX",
    "KI__EATEX",
    "KI__ENA_EATEX",
}

#: the health of the training data
TRAINING_HEALTH = {Health.HEALTHY, Health.NR, Health.HYPERTENSION}

#: the genotypes of the training data, the wild type of CES1 or not reported
TRAINING_GENOTYPES = {Genotype.NR, Genotype.CES1_WILD_TYPE}

#: mappings which are not fitted, the data is not usable
OUTLIER_MAPPINGS: NamedMappings = {
    # the enalapril of the ELISA is too high (Cmax 2-3 times the other studies)
    "Matalka2002": {
        "fm_matalka2002_po_ENA10_enalapril",
        "fm_matalka2002_po_ENA20_enalapril",
    },
    # the enzyme immunoassay of Matalka2002, enalapril and enalaprilat far
    # above the LC-MS studies of the same dose
    "Arafat2005": {
        "fm_arafat2005_enalapril_REN10",
        "fm_arafat2005_enalapril_ENA10",
        "fm_arafat2005_enalaprilat_REN10",
        "fm_arafat2005_enalaprilat_ENA10",
    },
    # the enalapril plateau of 6-8 ng/ml from 9 to 72 hr, which no other
    # study has (enalapril half-life about 1 hr)
    "Ghosh2012": {
        "fm_ghosh2012_enamal20_enalapril_late_Test",
        "fm_ghosh2012_enamal20_enalapril_late_Ref",
    },
    # the time courses of Fig2 give an AUC about 10 times the AUC of Table I,
    # the time axis is implausible
    "Johnston1992": {
        "fm_johnston1992_po_ENAs_enalapril",
        "fm_johnston1992_po_ENAm_enalapril",
    },
    # a non-specific bioassay of the ACE inhibition, Cmax 28 ng/ml is 1.6-2.8
    # times the other 5 mg studies, with a double peak
    "Thongnopnua2005": {"fm_thongnopnua2005_ENA5_enalaprilat"},
    # the venous line after the dialyzer, not the systemic plasma
    "Tsuruoka2007": {"fm_tsuruoka2007_enamal2p5_plasma_enalaprilat"},
}

#: the validation of the interactions: the arms with a coadministered drug,
#: simulated with the factors of `INTERACTION_FACTORS` of the base experiment.
#: `filter_coadministration` lets the named validation data through, every
#: other coadministration stays out of the selection altogether
INTERACTION_VALIDATION: NamedMappings = {
    # hydrochlorothiazide, no pharmacokinetic interaction
    "Howes1991": {
        "fm_howes1991_po_ENA10_HCTZ25_multi_enalaprilat",
        "fm_howes1991_po_ENA10_HCTZ25_multi_enalaprilat_urine",
        "fm_howes1991_po_ENA10_HCTZ25_combi_enalaprilat",
        "fm_howes1991_po_ENA10_HCTZ25_combi_enalaprilat_urine",
    },
    # cimetidine, no interaction
    "Ishizaki1988": {
        "fm_ishizaki1988_po_CIM400_ENA10_enalapril",
        "fm_ishizaki1988_po_CIM400_ENA10_enalaprilat",
        "fm_ishizaki1988_po_CIM400_ENA10_recovery_enalapril",
        "fm_ishizaki1988_po_CIM400_ENA10_recovery_enalaprilat",
        "fm_ishizaki1988_po_CIM400_ENA10_ACE_inhibition",
        "fm_ishizaki1988_po_CIM400_ENA10_blood_pressure_systolic",
        "fm_ishizaki1988_po_CIM400_ENA10_blood_pressure_diastolic",
    },
    # hydrochlorothiazide, no pharmacokinetic interaction
    "Niopas2004": {"fm_ena20_enalaprilat_ENA20", "fm_ena20_enalaprilat_REF20"},
    # the hypertensive patients on 50 mg hydrochlorothiazide a day
    "Schwartz1985": {
        *(
            f"fm_Fig{fig}_ENA{dose}_HT_{sid}"
            for fig, dose in [("3", "20"), ("3", "40"), ("6", "40")]
            for sid in ["enalapril", "enalaprilat"]
        ),
        *(
            f"fm_{arm}{dose}_HT_{sid}"
            for arm in ["placebo", "ENA"]
            for dose in ["20", "40"]
            for sid in [
                "MAP_supine",
                "relative_ACE_activity",
                "PRA_ratio",
                "aldosterone_ratio",
            ]
        ),
        *(
            f"fm_ENA{dose}_HT_blood_pressure_{bp}_supine"
            for dose in ["20", "40"]
            for bp in ["systolic", "diastolic"]
        ),
    },
    # hydrochlorothiazide in renal impairment; the lower renal clearance of
    # enalaprilat under hydrochlorothiazide (62 -> 43 ml/min) is not modelled
    "Weisser1992": {
        "fm_weisser1992_ENA10_HCTZ25_enalapril",
        "fm_weisser1992_ENA10_HCTZ25_enalaprilat",
        "fm_weisser1992_ENA10_HCTZ25_cumulative_amount_enalapril",
        "fm_weisser1992_ENA10_HCTZ25_cumulative_amount_enalaprilat",
        "fm_weisser1992_ENA10_HCTZ25_relative_ACE_activity",
    },
}

#: the validation of the doses: the repeated doses of the studies of a steady
#: state, which the single doses of the training predict
DOSE_VALIDATION: NamedMappings = {
    "Kelly1986": {"fm_kelly1986_po_ENA10_M1_enalaprilat"},
    "Lees1987a": {
        "fm_lees1987a_po_ENA10_young_day8_enalaprilat",
        "fm_lees1987a_po_ENA10_young_day8_ACE_inhibition",
    },
    "Witte1993": {
        "fm_witte1993_morning_ENAm10_enalapril",
        "fm_witte1993_morning_ENAm10_enalaprilat",
    },
}

#: the validation of the populations: renal impairment (the GFR), cirrhosis,
#: cardiac impairment (the cardiac output, and with it the GFR), the elderly
#: and the variants of CES1
POPULATION_VALIDATION: NamedMappings = {
    # cirrhosis (Child-Pugh A)
    "Baba1990": {
        "fm_baba1990_enalapril_cirrhosis",
        "fm_baba1990_enalaprilat_cirrhosis",
    },
    # heart failure on digitalis and diuretics
    "Dickstein1987": {
        "fm_dickstein1987_ENAPO10_CHF_enalapril",
        "fm_dickstein1987_ENAPO10_CHF_enalaprilat",
        "fm_dickstein1987_ENAIV5_CHF_enalaprilat",
        "fm_dickstein1987_EATIV5_CHF_enalaprilat",
        "fm_dickstein1987_ENAPO10_CHF_urine_enalaprilat",
        "fm_dickstein1987_ENAPO10_CHF_urine_enalapril_enalaprilat",
        "fm_dickstein1987_ENAIV5_CHF_urine_enalaprilat",
        "fm_dickstein1987_ENAIV5_CHF_urine_enalapril_enalaprilat",
        "fm_dickstein1987_EATIV5_CHF_urine_enalaprilat",
    },
    # renal impairment, CLcr 51 and 14 ml/min
    "Fruncillo1987": {
        f"fm_ENA5{kind}{group}_{sid}"
        for group in ["2", "3"]
        for kind, sid in [
            ("m", "enalapril"),
            ("m", "enalaprilat"),
            ("s", "urine_enalapril"),
            ("s", "urine_enalaprilat"),
        ]
    },
    # the CES1 variant G143E
    "Her2021": {"fm_po_ENA10m_G143E_enalapril", "fm_po_ENA10m_G143E_enalaprilat"},
    # the elderly, CLcr 66 ml/min
    "Hockings1986": {"fm_EATIV10_elder_enalaprilat", "fm_ENAPO10_elder_enalaprilat"},
    # the blood pressure of normotensive subjects, the blood pressure of the
    # model is fitted to hypertensive patients (the maximal fall at 2-6 hr
    # mapped at 4 hr)
    "Howes1991": {
        "fm_howes1991_po_ENA10_SBP_change_supine",
        "fm_howes1991_po_ENA10_DBP_change_supine",
    },
    "Ishizaki1988": {
        "fm_ishizaki1988_po_ENA10_blood_pressure_systolic",
        "fm_ishizaki1988_po_ENA10_blood_pressure_diastolic",
    },
    # heart failure without a measured renal function
    "Johnston1992": {
        "fm_johnston1992_po_ENAs_enalaprilat",
        "fm_johnston1992_po_ENAm_enalaprilat",
        "fm_johnston1992_po_ENAs_recovery_enalapril",
        "fm_johnston1992_po_ENAs_recovery_enalaprilat",
        "fm_johnston1992_po_ENAm_recovery_enalapril",
        "fm_johnston1992_po_ENAm_recovery_enalaprilat",
    },
    # renal impairment, single (S2-S4) and repeated (M2) doses
    "Kelly1986": {
        *(
            f"fm_kelly1986_po_ENA10_{group}_{sid}"
            for group in ["S2", "S3", "S4"]
            for sid in ["enalaprilat", "enalaprilat_urine"]
        ),
        "fm_kelly1986_po_ENA2p5_M2_enalaprilat",
    },
    # the elderly (CLcr 64 ml/min), and the blood pressure of the normotensive
    # young subjects
    "Lees1987a": {
        *(
            f"fm_lees1987a_po_ENA10_elder_{day}_{sid}"
            for day in ["day1", "day8"]
            for sid in [
                "enalaprilat",
                "ACE_inhibition",
                "blood_pressure_systolic",
                "blood_pressure_diastolic",
            ]
        ),
        *(
            f"fm_lees1987a_po_ENA10_young_{day}_blood_pressure_{bp}"
            for day in ["day1", "day8"]
            for bp in ["systolic", "diastolic"]
        ),
    },
    # renal impairment (group II) and end stage renal disease (group I, 0-24
    # hr before the dialysis), the blood pressure of normotensive group III
    "Lowenthal1985": {
        "fm_lowenthal1985_po_ENA10_II_enalaprilat",
        "fm_lowenthal1985_po_ENA10_II_enalaprilat_urine",
        "fm_lowenthal1985_po_ENA10_II_enalapril_enalaprilat_urine",
        "fm_lowenthal1985_po_ENA10_II_DBP",
        "fm_lowenthal1985_po_ENA10_I_enalaprilat",
        "fm_lowenthal1985_po_ENA10_I_without_dialysis_DBP",
        "fm_lowenthal1985_po_ENA10_III_DBP",
    },
    # the elderly, CLcr 78 ml/min
    "MacDonald1993": {
        "fm_macdonald1993_po_ENA10_elder_enalaprilat",
        "fm_macdonald1993_po_ENA10_elder_ACE_inhibition",
    },
    # renal impairment; group 1 is the hypertensive control of the comparison
    # with a light breakfast, far below the other 5 mg studies
    "Oguchi1993": {
        f"fm_po_ENA5_{group}_{sid}"
        for group in ["1", "2", "3"]
        for sid in [
            "enalapril",
            "enalaprilat",
            "recovery_enalapril",
            "recovery_enalaprilat",
            "ACE_inhibition",
        ]
    },
    # cirrhosis
    "Ohnishi1989": {
        "fm_ENA10_enalapril_cirrhosis",
        "fm_ENA10_enalaprilat_cirrhosis",
        "fm_enalapril_recovery_cirrhosis",
        "fm_enalaprilat_recovery_cirrhosis",
        "fm_ena10_blood_pressure_systolic_cirrhosis",
        "fm_ena10_blood_pressure_diastolic_cirrhosis",
    },
    # heart failure
    "Schwartz1985": {
        *(
            f"fm_ENA{dose}_CHF_{sid}"
            for dose in ["2p5", "5", "10"]
            for sid in ["enalapril", "enalaprilat"]
        ),
        "fm_ENA5_CHF_enalapril_mean",
        "fm_ENA5_CHF_enalaprilat_mean",
    },
    # the CES1 variants
    "Stage2017": {
        f"fm_po_ENA10{arm}_{sid}"
        for arm in ["copies4", "copies_normal3", "copies_active3", "G143E", "CES1A1c"]
        for sid in ["enalapril", "enalaprilat"]
    },
    "Tarkiainen2015": {
        f"fm_ENA10_{sid}_G143E"
        for sid in ["enalapril", "enalaprilat", "urine_enalapril", "urine_enalaprilat"]
    },
    # renal impairment of elderly hypertensive patients, CLcr 45.6 ml/min
    "Weisser1992": {
        "fm_weisser1992_ENA10_enalapril",
        "fm_weisser1992_ENA10_enalaprilat",
        "fm_weisser1992_ENA10_cumulative_amount_enalapril",
        "fm_weisser1992_ENA10_cumulative_amount_enalaprilat",
    },
}

#: the validation of the limitations of the model: valid data of a population
#: or a process the model does not describe, which would distort the fitted
#: parameters of the processes it does describe
LIMITATION_VALIDATION: NamedMappings = {
    # heart failure: the model lowers the cardiac output, but has no activated
    # RAAS of heart failure, the blood pressure falls 2.5-3 times more
    "Dickstein1987a": {
        "fm_dickstein1987a_ENAPO10_CHF_MAP_change",
        "fm_dickstein1987a_ENAIV5_CHF_MAP_change",
        "fm_dickstein1987a_EATIV5_CHF_MAP_change",
    },
    "Schwartz1985": {"fm_ENA5_CHF_MAP_supine"},
    # the placebo (a fall of the blood pressure without drug, no circadian
    # rhythm in the model) and one patient (P3)
    "Donnelly1990": {
        "fm_PLAC_blood_pressure_systolic",
        "fm_PLAC_blood_pressure_diastolic",
        "fm_PLAC_relative_ACE_activity",
        "fm_ENAs20_P3_enalaprilat",
        "fm_ENAs20_P3_blood_pressure_systolic__change_",
        "fm_ENAs20_P3_relative_ACE_activity",
    },
    # hemodialysis (anuric), the dialysis is not modelled
    "Fruncillo1987": {"fm_ENA5m4_enalapril", "fm_ENA5m4_enalaprilat"},
    # the lowest systolic pressure of day 7 mapped at an assumed time
    "Her2021": {
        "fm_po_ENA10m_control_blood_pressure_systolic",
        "fm_po_ENA10m_G143E_blood_pressure_systolic",
    },
    # the effect of hydrochlorothiazide on the blood pressure, not modelled
    "Howes1991": {
        f"fm_howes1991_po_ENA10_HCTZ25_{arm}_{bp}_change_supine"
        for arm in ["multi", "combi"]
        for bp in ["SBP", "DBP"]
    },
    # the heart rate is a constant input of the model
    "Ishizaki1988": {
        "fm_ishizaki1988_po_ENA10_heart_rate",
        "fm_ishizaki1988_po_CIM400_ENA10_heart_rate",
    },
    "Lees1987a": {
        f"fm_lees1987a_po_ENA10_{group}_{day}_heart_rate"
        for group in ["young", "elder"]
        for day in ["day1", "day8"]
    },
    # the blood pressure with dialysis
    "Lowenthal1985": {"fm_lowenthal1985_po_ENA10_I_with_dialysis_DBP"},
    # the heart rate, and the sitting predose blood pressure of normotensive
    # subjects on 7 days, changes of 5-10 mmHg within the day to day variation
    "Marzo2002": {
        f"fm_marzo2002_ENA{dose}_{sid}"
        for dose in ["10", "20"]
        for sid in [
            "heart_rate",
            "blood_pressure_systolic",
            "blood_pressure_diastolic",
        ]
    },
    # the enalaprilat of an ELISA of unclear specificity (its enalapril is an
    # outlier), Cmax 1.3-1.6 times the LC-MS studies
    "Matalka2002": {
        "fm_matalka2002_po_ENA10_enalaprilat",
        "fm_matalka2002_po_ENA20_enalaprilat",
    },
    # the dose in the evening and the placebo, chronopharmacology and the
    # circadian rhythm of the blood pressure are not modelled
    "Sunaga1995": {
        "fm_ENA5_night_enalaprilat",
        "fm_ENA5_night_enalapril_enalaprilat",
        "fm_ENA5_night_blood_pressure_systolic",
        "fm_ENA5_night_blood_pressure_diastolic",
        "fm_PLACEBO_day_blood_pressure_systolic",
        "fm_PLACEBO_day_blood_pressure_diastolic",
        "fm_PLACEBO_night_blood_pressure_systolic",
        "fm_PLACEBO_night_blood_pressure_diastolic",
    },
    # hemodialysis, the dialysis is not modelled
    "Tsuruoka2007": {
        "fm_tsuruoka2007_enamal2p5_arterial_blood_enalaprilat",
        "fm_tsuruoka2007_enamal2p5_blood_pressure_systolic",
        "fm_tsuruoka2007_enamal2p5_blood_pressure_diastolic",
    },
    # the ACE activity measured in vitro in a 1:11 diluted sample, which
    # dissociates the enalaprilat
    "Weisser1992": {"fm_weisser1992_ENA10_relative_ACE_activity"},
    # the blood pressure with a circadian rhythm and the diluted ACE activity
    "Witte1993": {
        f"fm_witte1993_morning_{arm}_{sid}"
        for arm in ["ENAs10", "ENAm10"]
        for sid in [
            "blood_pressure_systolic",
            "blood_pressure_diastolic",
            "relative_ACE_activity",
        ]
    },
}

#: the summaries of data which the fits use one by one, excluded from every
#: fit: a mean of subjects would count the subjects twice
AGGREGATE_MAPPINGS: NamedMappings = {
    # the test tablet of a bioequivalence crossover, the same subjects as the
    # reference
    "Arafat2005": {
        "fm_arafat2005_blood_pressure_systolic_ENA10",
        "fm_arafat2005_blood_pressure_diastolic_ENA10",
    },
    "Dayyih2017": {
        "fm_dayyih2017_enalapril_TEST20",
        "fm_dayyih2017_enalaprilat_TEST20",
    },
    "Ghosh2012": {
        "fm_ghosh2012_enamal20_enalapril_Test",
        "fm_ghosh2012_enamal20_enalaprilat_Test",
    },
    "Najib2003a": {
        "fm_najib2003a_po_ENA20_enalapril_NAR20",
        "fm_najib2003a_po_ENA20_enalaprilat_NAR20",
    },
    "VanHecken2020": {
        f"fm_vanhecken2020_{arm}_{sid}"
        for arm in ["ENA10", "ENAw10"]
        for sid in ["enalapril", "enalaprilat"]
    },
    # the oral solution, the same subjects as the tablet, the same simulation
    "Moffett2014": {
        "fm_moffett2014_ENAfast10_enalapril",
        "fm_moffett2014_ENAfast10_enalaprilat",
    },
    # the same subjects and samples as Ulm1982
    "Biollaz1982": {"fm_biollaz1982_enalapril", "fm_biollaz1982_enalaprilat"},
    # the plasma renin activity of the samples of the renin
    "Burckhardt2015": {"fm_burckhardt2015_renin_activity"},
    # the Fig3 series of group I is the Fig4 series with dialysis
    "Lowenthal1985": {"fm_lowenthal1985_po_ENA10_I_DBP"},
    # the sum of the mapped enalapril and enalaprilat
    "Ohnishi1989": {
        "fm_enalapril_enalaprilat_recovery_healthy",
        "fm_enalapril_enalaprilat_recovery_cirrhosis",
    },
    "Ulm1982": {"fm_ulm1982_enamal9p8_enalapril_enalaprilat_urine"},
    # the mean arterial pressure of the mapped systolic and diastolic pressure
    "Shionoiri1985": {"fm_ENA10_MAP"},
    # the ACE inhibition of the samples of the relative ACE activity
    "Wade1992": {"fm_wade1992_ENA10_ACE_inhibition"},
    # the dose in the evening, the same subjects (no circadian model)
    "Weisser1991": {
        "fm_weisser1991_po_ENA10_enalapril_evening",
        "fm_weisser1991_po_ENA10_enalaprilat_evening",
    },
    "Witte1993": {
        f"fm_witte1993_night_{arm}_{sid}"
        for arm in ["ENAs10", "ENAm10"]
        for sid in [
            "enalapril",
            "enalaprilat",
            "blood_pressure_systolic",
            "blood_pressure_diastolic",
            "relative_ACE_activity",
        ]
    },
}

#: the validation data by the question it answers
VALIDATION_QUESTIONS: dict[str, NamedMappings] = {
    "interactions": INTERACTION_VALIDATION,
    "doses": DOSE_VALIDATION,
    "populations": POPULATION_VALIDATION,
    "limitations": LIMITATION_VALIDATION,
}

#: the validation data
VALIDATION_MAPPINGS: NamedMappings = {
    study: set().union(
        *(mappings.get(study, set()) for mappings in VALIDATION_QUESTIONS.values())
    )
    for mappings in VALIDATION_QUESTIONS.values()
    for study in mappings
}


def study(fit_mapping: FitMapping) -> str:
    """Get the study of a fit mapping, the id of its experiment."""
    return fit_mapping.reference.experiment.sid


def named(
    mappings: NamedMappings, fit_mapping_key: str, fit_mapping: FitMapping
) -> bool:
    """Check whether a fit mapping is one of the named mappings of its study."""
    return fit_mapping_key in mappings.get(study(fit_mapping), set())


def check_named(mappings: NamedMappings, fit_mappings: FitMappings) -> None:
    """Check that the named mappings are fit mappings of their studies.

    Raises:
        ValueError: for a study which is no experiment, or a key which is no fit
            mapping of its study.
    """
    for sid, keys in mappings.items():
        experiment = fit_mappings.experiments.get(sid)
        if experiment is None:
            raise ValueError(f"'{sid}' is no experiment of the fits.")
        if unknown := sorted(keys - set(experiment._fit_mappings)):
            raise ValueError(f"'{unknown}' are no fit mappings of '{sid}'.")


def filter_aggregates(fit_mapping_key: str, fit_mapping: FitMapping) -> bool:
    """No summaries of data which is fitted one by one, see `AGGREGATE_MAPPINGS`."""
    return not named(AGGREGATE_MAPPINGS, fit_mapping_key, fit_mapping)


def filter_coadministration(fit_mapping_key: str, fit_mapping: FitMapping) -> bool:
    """No coadministered drug, besides the named validation data.

    The interactions are validated with their factors, the populations with
    their background therapy (heart failure on diuretics and digitalis).
    """
    if named(VALIDATION_MAPPINGS, fit_mapping_key, fit_mapping):
        return True
    return mapping_metadata(fit_mapping).coadministration == Coadministration.NONE


def filter_health(fit_mapping_key: str, fit_mapping: FitMapping) -> bool:
    """Only the health of the training, besides the named validation data."""
    if named(VALIDATION_MAPPINGS, fit_mapping_key, fit_mapping):
        return True
    return mapping_metadata(fit_mapping).health in TRAINING_HEALTH


def filter_genotype(fit_mapping_key: str, fit_mapping: FitMapping) -> bool:
    """Only the wild type of CES1 or not reported, besides the named validation data."""
    if named(VALIDATION_MAPPINGS, fit_mapping_key, fit_mapping):
        return True
    return mapping_metadata(fit_mapping).genotype in TRAINING_GENOTYPES


#: Only the pharmacokinetic data.
filter_pk = observable_filter(PK_OBSERVABLES)


def filter_pd(fit_mapping_key: str, fit_mapping: FitMapping) -> bool:
    """Only the pharmacodynamic data."""
    return observable_id(fit_mapping) not in PK_OBSERVABLES


def mapping_collections(
    filters: MappingFilter | list[MappingFilter],
    validation: NamedMappings = VALIDATION_MAPPINGS,
) -> dict[str, list[FitMappingCollection]]:
    """Select the data of a fit from the fit mappings of the studies.

    The filters select the training data, the mappings which fail them are
    excluded, and so are the summaries of data which is fitted one by one
    (`AGGREGATE_MAPPINGS`), the arms with a coadministered drug
    (`filter_coadministration`), the populations besides the training
    (`filter_health`) and the variants of CES1 (`filter_genotype`), unless
    they are named validation data. The outliers are `OUTLIER_MAPPINGS`, the
    validation data is `VALIDATION_MAPPINGS`. Neither kind enters the cost;
    both are simulated and evaluated with the training data, so a report says
    how the fitted parameters describe data they were not fitted on.

    Args:
        filters: filters of the training data.
        validation: the keys of the validation data by study.

    Returns:
        The fit mapping collections of all kinds by experiment id.
    """
    fit_mappings = FitMappings(
        experiment_classes=EXPERIMENT_CLASSES,
        base_path=ENALAPRIL_PATH,
        data_path=DATA_PATHS,
    )
    for mappings in [OUTLIER_MAPPINGS, AGGREGATE_MAPPINGS, validation]:
        check_named(mappings, fit_mappings)
    # sbmlsim selects the outliers by their keys alone, which must name one
    # mapping of all studies
    outliers = {key for keys in OUTLIER_MAPPINGS.values() for key in keys}
    for key in outliers:
        studies = [
            sid
            for sid, experiment in fit_mappings.experiments.items()
            if key in experiment._fit_mappings
        ]
        if len(studies) != 1:
            raise ValueError(f"The outlier '{key}' is a mapping of {studies}.")
    selection = fit_mappings.select(
        filters=[
            *(filters if isinstance(filters, list) else [filters]),
            filter_aggregates,
            filter_coadministration,
            filter_health,
            filter_genotype,
        ],
        outliers=outliers,
        validation=lambda key, fit_mapping: named(validation, key, fit_mapping),
        print_info=False,
    )
    # the counts per experiment and kind, not the single mappings
    selection.print(detail=False)
    # the validation mappings by the question they answer
    selected = {
        (sid, key)
        for sid, kinds in selection.kinds.items()
        for key, kind in kinds.items()
        if kind is MappingKind.VALIDATION
    }

    def pairs(mappings: NamedMappings) -> set[tuple[str, str]]:
        return {(sid, key) for sid, keys in mappings.items() for key in keys}

    console.print(
        "validation: "
        + ", ".join(
            f"{len(selected & pairs(mappings))} {question}"
            for question, mappings in VALIDATION_QUESTIONS.items()
        )
    )
    return selection.collections


def f_collections_pk() -> dict[str, list[FitMappingCollection]]:
    """Pharmacokinetic data."""
    return mapping_collections([filter_pk])


def f_collections_pd() -> dict[str, list[FitMappingCollection]]:
    """Pharmacodynamic data."""
    return mapping_collections([filter_pd])


if __name__ == "__main__":
    for f in [f_collections_pk, f_collections_pd]:
        console.rule(title=f.__name__, align="left", style="white")
        f()
