"""Parameters to optimize in the enalapril fits.

The start values are the values of the model before its fits, chosen by hand
(a least squares of the model to the literature values of the studies of the
model) so that the model reproduces the literature: enalapril and enalaprilat
after 10 and 20 mg of enalapril maleate (Cmax, tmax, AUC, the enalaprilat at
24, 48, 72 and 96 hr), the urinary recovery of enalapril (18-26 %) and
enalaprilat (27-38 %) and the feces (33-39 %), the renal clearances, and the
enalaprilat after 10 mg i.v. {Hockings1986}. The model takes the fitted values
from the records of the adopted fits (`models/fits.py`). The bounds contain the
literature values.
"""

from sbmlsim.fit import FitParameter

#: the absorption of enalapril: the dissolution and gastric emptying
#: (`Ka_dis_ena`) and the absorption from the lumen (`GU__ENAABS_k`) are a
#: chain of two first order steps, which gives the delayed and steep rise of
#: enalapril (tmax 0.9-1.1 hr at a Cmax of 60-68 ng/ml after 10 mg); the
#: fraction absorbed splits the dose between the feces (33-39 %) and the body.
#: Food slows the dissolution (`GU__FED_f_dissolution`: Cmax 0.54, AUC 0.86,
#: tmax 0.3-1 hr later after a high fat breakfast {Moffett2014})
parameters_pk_po: list[FitParameter] = [
    FitParameter(
        pid="Ka_dis_ena",
        start_value=1.2,
        lower_bound=0.1,
        upper_bound=20,
        unit="1/hr",
    ),
    FitParameter(
        pid="GU__ENAABS_k",
        start_value=0.02,
        lower_bound=1e-3,
        upper_bound=1,
        unit="1/min",
    ),
    # 56 +- 6 % of 14C in the urine, 39 +- 5 % in the feces {Ulm1982}
    FitParameter(
        pid="GU__F_ena_abs",
        start_value=0.65,
        lower_bound=0.4,
        upper_bound=0.9,
        unit="dimensionless",
    ),
    FitParameter(
        pid="GU__FED_f_dissolution",
        start_value=0.3,
        lower_bound=0.05,
        upper_bound=1,
        unit="dimensionless",
    ),
]

#: the distribution, the hydrolysis and the renal excretion of enalapril. The
#: hepatic uptake (`LI__ENAIM`) and the Michaelis constants are not fitted:
#: uptake and hydrolysis are serial and linear, only the hydrolysis is
#: identified
parameters_pk_ena: list[FitParameter] = [
    # the volume of enalapril, the steep decline after the peak (half-life
    # 0.6-1.3 hr); the exchange with the tissues is fast, see `model_body`
    FitParameter(
        pid="Kp_ena",
        start_value=0.2,
        lower_bound=0.02,
        upper_bound=5,
        unit="dimensionless",
    ),
    # the ratio of enalaprilat to enalapril (AUC 3-4) and of their urinary
    # recovery
    FitParameter(
        pid="LI__ENA2EAT_Vmax",
        start_value=0.5,
        lower_bound=1e-2,
        upper_bound=50,
        unit="mmole/min/l",
    ),
    # renal clearance of enalapril 252-372 ml/min {Burckhardt2015, Baba1990,
    # Ishizaki1988, Ohnishi1989}, above the GFR (tubular secretion)
    FitParameter(
        pid="KI__ENAEX_f",
        start_value=3.2,
        lower_bound=0.5,
        upper_bound=10,
        unit="dimensionless",
    ),
]

#: the distribution, the binding to tissue ACE, the hepatic export and the
#: renal excretion of enalaprilat. The dissociation of enalaprilat from ACE
#: (`EATACE_koff`) is not fitted, a binding in equilibrium; the exchange flow
#: of enalaprilat (`ftissue_eat`) is not fitted, a fast equilibrium with the
#: extracellular space
parameters_pk_eat: list[FitParameter] = [
    # the distribution phase of enalaprilat i.v. {Hockings1986}
    FitParameter(
        pid="Kp_eat",
        start_value=0.04,
        lower_bound=0.005,
        upper_bound=5,
        unit="dimensionless",
    ),
    # enalaprilat peaks 3.5-4.6 hr after an oral dose of enalapril
    FitParameter(
        pid="LI__EATEX_Vmax",
        start_value=1.8e-3,
        lower_bound=1e-5,
        upper_bound=1,
        unit="mmole/min/l",
    ),
    # unbound renal clearance 222 +- 49 ml/min, 1.85 times the inulin
    # clearance {Mujais1992}; renal clearance 125-190 ml/min, i.v. clearance
    # 6.1 l/hr {Hockings1986}
    FitParameter(
        pid="KI__EATEX_f",
        start_value=1.8,
        lower_bound=0.5,
        upper_bound=5,
        unit="dimensionless",
    ),
    # the terminal phase of enalaprilat at 0.5-3 ng/ml (half-life 30-60 hr),
    # almost independent of the dose: 1.75, 1.18, 0.86 and 0.60 ng/ml at 24,
    # 48, 72 and 96 hr after 10 mg enalaprilat i.v. {Hockings1986}, 2-3.4,
    # 1.1-1.3 and 0.4-0.9 ng/ml at 24, 48 and 72 hr after 10 mg enalapril
    # maleate {Moffett2014, Gu2004, Lu2009, VanHecken2020}. The normalized
    # residuals weight these values 10-50 times less than the peak, and the
    # binding which carries them takes up a part of the enalaprilat of the
    # peak, so a fit with an open lower bound trades the terminal phase for the
    # peak (Bmax 2.7e-6 mM: 0.14 instead of 1.75 ng/ml at 24 hr after i.v.
    # enalaprilat, ACE inhibition 16 % instead of 41 % at 48 hr). The lower
    # bound keeps a capacity which gives the terminal phase (about 0.5-1 mg
    # bound), the accumulation of repeated doses and the ACE inhibition after
    # 24 hr depend on it. The upper bound keeps the binding out of the
    # distribution phase: the binding is in equilibrium, a larger capacity
    # takes up the enalaprilat of a bolus within minutes (Bmax 1.75e-4 mM: 23
    # instead of 182 ng/ml at 2 hr after 10 mg i.v. {Hockings1986}) and
    # replaces the distribution volume (`Kp_eat`)
    FitParameter(
        pid="EATACE_Bmax",
        start_value=4e-5,
        lower_bound=2e-5,
        upper_bound=6e-5,
        unit="mM",
    ),
    # in vitro about 0.1-1 nM (1e-7 to 1e-6 mM) {Weisser1992}; the terminal
    # phase at 1.5-9 nM needs a dissociation constant of its order, so that the
    # bound enalaprilat is released over days
    FitParameter(
        pid="EATACE_Kd",
        start_value=1e-6,
        lower_bound=1e-7,
        upper_bound=1e-5,
        unit="mM",
    ),
]

#: the pharmacodynamics: the ACE inhibition by enalaprilat and the response of
#: the RAAS and the blood pressure, on the adopted pharmacokinetics. The
#: half-lives of the RAAS states are not fitted, see `model_raas`. Not fitted
#: either are the fraction of angiotensin I which ACE converts (`f_ang1_ace`,
#: which sets the rise of angiotensin I under the inhibition and the half-life
#: of angiotensin II, 0.4 min / f_ang1_ace) and the fraction of the
#: aldosterone secretion driven by angiotensin II (`f_ald_ang2`): the training
#: data have no aldosterone (`f_ald_ang2` is structurally not identifiable)
#: and only three curves of angiotensin I and II, a fit of all six parameters
#: (PD_20261020_123847__761da) put `f_ang1_ace` at its lower bound 0.01, an
#: angiotensin II half-life of 40 min instead of about 0.5 min. Both keep the
#: values of the same RAAS model fitted to the angiotensin I and II, renin
#: and aldosterone data of ramipril (0.15 and 0.66). The start values are the
#: adopted values of the ramipril model, the EC50 3 ng/ml from the ACE
#: inhibition of Biollaz1982
parameters_pd: list[FitParameter] = [
    # the in vivo IC50 1.7-12.8 ng/ml {Hockings1986}, 22.9 +- 6.5 nM
    # {MacDonald1993}; 74, 41 and 23 % inhibition at 4.5, 2.2 and 1.6 ng/ml
    # {Biollaz1982}
    FitParameter(
        pid="ANG1ANG2_EC50_eat",
        start_value=8.6e-6,
        lower_bound=1e-7,
        upper_bound=1e-4,
        unit="mM",
    ),
    # renin rises 2-19 fold under ACE inhibition {Burckhardt2015}
    FitParameter(
        pid="RENSEC_ang2_E",
        start_value=24.0,
        lower_bound=0.1,
        upper_bound=50,
        unit="dimensionless",
    ),
    # renin follows angiotensin II with a delay, its rise peaks hours after the
    # dose
    FitParameter(
        pid="RENSEC_ang2_t",
        start_value=78.0,
        lower_bound=1.0,
        upper_bound=600.0,
        unit="min",
    ),
    # the blood pressure falls by 5-10 mmHg in normotensive subjects and by
    # 15-25 mmHg in hypertensive patients
    FitParameter(
        pid="BP_ang2_fe",
        start_value=0.13,
        lower_bound=0.01,
        upper_bound=1,
        unit="dimensionless",
    ),
]

parameters_pk: list[FitParameter] = (
    parameters_pk_po + parameters_pk_ena + parameters_pk_eat
)
parameters_all: list[FitParameter] = parameters_pk + parameters_pd
