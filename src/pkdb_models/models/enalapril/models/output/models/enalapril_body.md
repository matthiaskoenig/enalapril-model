# Enalapril body model

Model `enalapril_body`, SBML Level 3 Version 2, read from enalapril\_body.xml, written by sbmlode 0.3.0.

Physiologically based pharmacokinetic (PBPK) model of enalapril (body model)

Comments

enalapril (the maleate salt, dosed as enalapril) is given orally or intravenously, enalaprilat intravenously

enalapril is hydrolysed by CES1 in the liver to its active metabolite enalaprilat (LI\_\_ENA2EAT)

enalapril and enalaprilat distribute into the tissues (Kp\_ena, Kp\_eat); enalaprilat binds with high affinity and low capacity to tissue ACE (EATACE), which gives its long terminal phase

enalapril and enalaprilat are excreted unchanged by the kidneys, relative to the GFR (KI\_\_ENAEX, KI\_\_EATEX)

the enalaprilat of the venous plasma inhibits ACE of the RAAS

The content of this model has been carefully created in a manual research effort.

Terms of use

Copyright © 2026 Matthias König.

This work is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License.

Redistribution and use of any part of this model, with or without modification, are permitted provided that the following conditions are met:

Redistributions of this SBML file must retain the above copyright notice, this list of conditions and the following disclaimer.

Redistributions in a different form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

This model is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

## Units

| Time | Substance | Extent | Volume | Area | Length |
| --- | --- | --- | --- | --- | --- |
| min | mmol | mmol | l | m<sup>2</sup> | m |

## Compartments

| Symbol | Id | Name | Size | Unit | Constant |
| --- | --- | --- | --- | --- | :---: |
| $\mathrm{Vplasma}$ | `Vplasma` | plasma | $5$ | l | ✓ |
| $\mathrm{Vre}$ | `Vre` | rest of body |  | l |  |
| $\mathrm{Vgu}$ | `Vgu` | gut |  | l |  |
| $\mathrm{Vki}$ | `Vki` | kidney |  | l |  |
| $\mathrm{Vli}$ | `Vli` | liver |  | l |  |
| $\mathrm{Vlu}$ | `Vlu` | lung |  | l |  |
| $\mathrm{Vve}$ | `Vve` | venous blood |  | l |  |
| $\mathrm{Var}$ | `Var` | arterial blood |  | l |  |
| $\mathrm{Vurine}$ | `Vurine` | urine | $1$ | l | ✓ |
| $\mathrm{Vfeces}$ | `Vfeces` | feces | $1$ | l | ✓ |
| $\mathrm{Vstomach}$ | `Vstomach` | stomach | $1$ | l | ✓ |
| $\mathrm{Vpo}$ | `Vpo` | portal plasma |  | l |  |
| $\mathrm{Vhv}$ | `Vhv` | hepatic venous plasma |  | l |  |
| $\mathrm{Vki}_{\mathrm{tissue}}$ | `Vki_tissue` | ki tissue |  | l |  |
| $\mathrm{Vki}_{\mathrm{plasma}}$ | `Vki_plasma` | ki plasma |  | l |  |
| $\mathrm{Vli}_{\mathrm{tissue}}$ | `Vli_tissue` | li tissue |  | l |  |
| $\mathrm{Vli}_{\mathrm{plasma}}$ | `Vli_plasma` | li plasma |  | l |  |
| $\mathrm{Vlu}_{\mathrm{tissue}}$ | `Vlu_tissue` | lu tissue |  | l |  |
| $\mathrm{Vlu}_{\mathrm{plasma}}$ | `Vlu_plasma` | lu plasma |  | l |  |
| $\mathrm{Vgu}_{\mathrm{tissue}}$ | `Vgu_tissue` | gu tissue |  | l |  |
| $\mathrm{Vgu}_{\mathrm{plasma}}$ | `Vgu_plasma` | gu plasma |  | l |  |
| $\mathrm{Vre}_{\mathrm{tissue}}$ | `Vre_tissue` | re tissue |  | l |  |
| $\mathrm{Vre}_{\mathrm{plasma}}$ | `Vre_plasma` | re plasma |  | l |  |
| $\mathrm{LI}_{\mathrm{\_Vmem}}$ | `LI__Vmem` | plasma membrane | $\mathrm{NaN}$ | m<sup>2</sup> | ✓ |
| $\mathrm{GU}_{\mathrm{\_Vlumen}}$ | `GU__Vlumen` | intestinal lumen (inner part of intestine) | $1.15425$ | l |  |
| $\mathrm{GU}_{\mathrm{\_Vstomach}}$ | `GU__Vstomach` | stomach | $1$ | l | ✓ |

## Species

| Symbol | Id | Name | Compartment | Value | Unit | Properties |
| --- | --- | --- | --- | --- | --- | --- |
| $\mathrm{ald}$ | `ald` | aldosterone | $\mathrm{Vplasma}$ | $2.5 \times 10^{-7}$ | mmol/l | concentration |
| $\mathrm{ren}$ | `ren` | renin | $\mathrm{Vplasma}$ | $10^{-9}$ | mmol/l | concentration |
| $\mathrm{anggen}$ | `anggen` | angiotensinogen | $\mathrm{Vplasma}$ | $10^{-8}$ | mmol/l | concentration, boundary |
| $\mathrm{ang}_{1}$ | `ang1` | angiotensin I | $\mathrm{Vplasma}$ | $10^{-8}$ | mmol/l | concentration |
| $\mathrm{ang}_{2}$ | `ang2` | angiotensin II | $\mathrm{Vplasma}$ | $8 \times 10^{-9}$ | mmol/l | concentration |
| $\mathrm{ace}$ | `ace` | ACE | $\mathrm{Vplasma}$ | $10^{-9}$ | mmol/l | concentration |
| $\mathrm{eat}$ | `eat` | enalaprilat | $\mathrm{Vplasma}$ |  | mmol/l | concentration |
| $\mathrm{Cki}_{\mathrm{plasma\_ena}}$ | `Cki_plasma_ena` | enalapril (kidney plasma) | $\mathrm{Vki}_{\mathrm{plasma}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cli}_{\mathrm{plasma\_ena}}$ | `Cli_plasma_ena` | enalapril (liver plasma) | $\mathrm{Vli}_{\mathrm{plasma}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Clu}_{\mathrm{plasma\_ena}}$ | `Clu_plasma_ena` | enalapril (lung plasma) | $\mathrm{Vlu}_{\mathrm{plasma}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cgu}_{\mathrm{plasma\_ena}}$ | `Cgu_plasma_ena` | enalapril (gut plasma) | $\mathrm{Vgu}_{\mathrm{plasma}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cre}_{\mathrm{plasma\_ena}}$ | `Cre_plasma_ena` | enalapril (rest plasma) | $\mathrm{Vre}_{\mathrm{plasma}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Car}_{\mathrm{ena}}$ | `Car_ena` | enalapril (arterial blood plasma) | $\mathrm{Var}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cve}_{\mathrm{ena}}$ | `Cve_ena` | enalapril (venous blood plasma) | $\mathrm{Vve}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cpo}_{\mathrm{ena}}$ | `Cpo_ena` | enalapril (portal vein plasma) | $\mathrm{Vpo}$ | $0$ | mmol/l | concentration |
| $\mathrm{Chv}_{\mathrm{ena}}$ | `Chv_ena` | enalapril (hepatic vein plasma) | $\mathrm{Vhv}$ | $0$ | mmol/l | concentration |
| $\mathrm{Clu}_{\mathrm{ena}}$ | `Clu_ena` | enalapril (lung) | $\mathrm{Vlu}_{\mathrm{tissue}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cre}_{\mathrm{ena}}$ | `Cre_ena` | enalapril (rest) | $\mathrm{Vre}_{\mathrm{tissue}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Aurine}_{\mathrm{ena}}$ | `Aurine_ena` | enalapril (urine) | $\mathrm{Vurine}$ |  | mmol | amount |
| $\mathrm{Afeces}_{\mathrm{ena}}$ | `Afeces_ena` | enalapril (feces) | $\mathrm{Vfeces}$ |  | mmol | amount |
| $\mathrm{Cgu}_{\mathrm{ena}}$ | `Cgu_ena` | enalapril (gut) | $\mathrm{Vgu}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cki}_{\mathrm{plasma\_eat}}$ | `Cki_plasma_eat` | enalaprilat (kidney plasma) | $\mathrm{Vki}_{\mathrm{plasma}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cli}_{\mathrm{plasma\_eat}}$ | `Cli_plasma_eat` | enalaprilat (liver plasma) | $\mathrm{Vli}_{\mathrm{plasma}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Clu}_{\mathrm{plasma\_eat}}$ | `Clu_plasma_eat` | enalaprilat (lung plasma) | $\mathrm{Vlu}_{\mathrm{plasma}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cgu}_{\mathrm{plasma\_eat}}$ | `Cgu_plasma_eat` | enalaprilat (gut plasma) | $\mathrm{Vgu}_{\mathrm{plasma}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cre}_{\mathrm{plasma\_eat}}$ | `Cre_plasma_eat` | enalaprilat (rest plasma) | $\mathrm{Vre}_{\mathrm{plasma}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Car}_{\mathrm{eat}}$ | `Car_eat` | enalaprilat (arterial blood plasma) | $\mathrm{Var}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cve}_{\mathrm{eat}}$ | `Cve_eat` | enalaprilat (venous blood plasma) | $\mathrm{Vve}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cpo}_{\mathrm{eat}}$ | `Cpo_eat` | enalaprilat (portal vein plasma) | $\mathrm{Vpo}$ | $0$ | mmol/l | concentration |
| $\mathrm{Chv}_{\mathrm{eat}}$ | `Chv_eat` | enalaprilat (hepatic vein plasma) | $\mathrm{Vhv}$ | $0$ | mmol/l | concentration |
| $\mathrm{Clu}_{\mathrm{eat}}$ | `Clu_eat` | enalaprilat (lung) | $\mathrm{Vlu}_{\mathrm{tissue}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Cre}_{\mathrm{eat}}$ | `Cre_eat` | enalaprilat (rest) | $\mathrm{Vre}_{\mathrm{tissue}}$ | $0$ | mmol/l | concentration |
| $\mathrm{Aurine}_{\mathrm{eat}}$ | `Aurine_eat` | enalaprilat (urine) | $\mathrm{Vurine}$ |  | mmol | amount |
| $\mathrm{Aurine}_{\mathrm{ena\_eat}}$ | `Aurine_ena_eat` | enalapril + enalaprilat (urine) | $\mathrm{Vurine}$ |  | mmol | amount |
| $\mathrm{Cve}_{\mathrm{ena\_eat}}$ | `Cve_ena_eat` | enalapril+enalaprilat (plasma) | $\mathrm{Vve}$ |  | mmol/l | concentration |
| $\mathrm{Cre}_{\mathrm{eat\_ace}}$ | `Cre_eat_ace` | enalaprilat bound to ACE (rest of body) | $\mathrm{Vre}_{\mathrm{tissue}}$ | $0$ | mmol/l | concentration |
| $\mathrm{LI}_{\mathrm{\_ena}}$ | `LI__ena` | enalapril (liver) | $\mathrm{Vli}_{\mathrm{tissue}}$ | $0$ | mmol/l | concentration |
| $\mathrm{LI}_{\mathrm{\_eat}}$ | `LI__eat` | enalaprilat (liver) | $\mathrm{Vli}_{\mathrm{tissue}}$ | $0$ | mmol/l | concentration |
| $\mathrm{GU}_{\mathrm{\_ena\_stomach}}$ | `GU__ena_stomach` | enalapril (stomach) | $\mathrm{GU}_{\mathrm{\_Vstomach}}$ |  | mmol | amount, boundary |

## Parameters

| Symbol | Id | Name | Value | Unit | Constant |
| --- | --- | --- | --- | --- | :---: |
| $\mathrm{ald}_{\mathrm{change}}$ | `ald_change` | aldosterone change |  | mmol/l |  |
| $\mathrm{ald}_{\mathrm{ratio}}$ | `ald_ratio` | aldosterone ratio |  | \- |  |
| $\mathrm{ren}_{\mathrm{change}}$ | `ren_change` | renin change |  | mmol/l |  |
| $\mathrm{ren}_{\mathrm{ratio}}$ | `ren_ratio` | renin ratio |  | \- |  |
| $\mathrm{anggen}_{\mathrm{change}}$ | `anggen_change` | angiotensinogen change |  | mmol/l |  |
| $\mathrm{anggen}_{\mathrm{ratio}}$ | `anggen_ratio` | angiotensinogen ratio |  | \- |  |
| $\mathrm{ang1}_{\mathrm{change}}$ | `ang1_change` | angiotensin I change |  | mmol/l |  |
| $\mathrm{ang1}_{\mathrm{ratio}}$ | `ang1_ratio` | angiotensin I ratio |  | \- |  |
| $\mathrm{ang2}_{\mathrm{change}}$ | `ang2_change` | angiotensin II change |  | mmol/l |  |
| $\mathrm{ang2}_{\mathrm{ratio}}$ | `ang2_ratio` | angiotensin II ratio |  | \- |  |
| $\mathrm{ace}_{\mathrm{change}}$ | `ace_change` | ACE change |  | mmol/l |  |
| $\mathrm{ace}_{\mathrm{ratio}}$ | `ace_ratio` | ACE ratio |  | \- |  |
| $\mathrm{anggen}_{\mathrm{ref}}$ | `anggen_ref` | reference concentration of angiotensinogen | $10^{-8}$ | mmol/l | ✓ |
| $\mathrm{ang1}_{\mathrm{ref}}$ | `ang1_ref` | reference concentration of angiotensin I | $10^{-8}$ | mmol/l | ✓ |
| $\mathrm{ang2}_{\mathrm{ref}}$ | `ang2_ref` | reference concentration of angiotensin II | $8 \times 10^{-9}$ | mmol/l | ✓ |
| $\mathrm{ren}_{\mathrm{ref}}$ | `ren_ref` | reference concentration of renin | $10^{-9}$ | mmol/l | ✓ |
| $\mathrm{ace}_{\mathrm{ref}}$ | `ace_ref` | reference concentration of ACE | $10^{-9}$ | mmol/l | ✓ |
| $\mathrm{ald}_{\mathrm{ref}}$ | `ald_ref` | reference concentration of aldosterone | $2.5 \times 10^{-7}$ | mmol/l | ✓ |
| $\mathrm{RENDEG}_{\mathrm{k}}$ | `RENDEG_k` | rate renin degradation | $0.231049060186648$ | l/min | ✓ |
| $\mathrm{RENSEC}_{\mathrm{k}}$ | `RENSEC_k` | rate renin secretion |  | mmol/min | ✓ |
| $\mathrm{RENSEC}_{\mathrm{ang2\_E}}$ | `RENSEC_ang2_E` | maximum increase of the renin secretion without angiotensin II | $5.15703048226548$ | \- | ✓ |
| $\mathrm{RENSEC}_{\mathrm{ang2\_t}}$ | `RENSEC_ang2_t` | half-life of the delay of the renin feedback | $70.8696066698419$ | min | ✓ |
| $\mathrm{ang2}_{\mathrm{feedback}}$ | `ang2_feedback` | angiotensin II of the renin feedback | $\mathrm{NaN}$ | mmol/l |  |
| $\mathrm{ANG1CL}$ | `ANG1CL` | clearance of angiotensin I | $6.93147180559945$ | l/min | ✓ |
| $\mathrm{ANGGEN2ANG1}_{\mathrm{k}}$ | `ANGGEN2ANG1_k` | rate angiotensinogen to angiotensin I conversion (renin) |  | l/min | ✓ |
| $f_{\mathrm{ang1\_ace}}$ | `f_ang1_ace` | fraction of angiotensin I converted by ACE | $0.15$ | \- | ✓ |
| $\mathrm{ANG1ANG2}_{\mathrm{k}}$ | `ANG1ANG2_k` | rate angiotensin I to angiotensin II conversion (ACE) |  | l/min | ✓ |
| $\mathrm{ANG1DEG}_{\mathrm{k}}$ | `ANG1DEG_k` | rate angiotensin I degradation |  | l/min | ✓ |
| $\mathrm{ANG2DEG}_{\mathrm{k}}$ | `ANG2DEG_k` | rate angiotensin II degradation |  | l/min | ✓ |
| $\mathrm{ALDDEG}_{\mathrm{k}}$ | `ALDDEG_k` | rate aldosterone degradation | $0.173286795139986$ | l/min | ✓ |
| $\mathrm{ALDSEC}_{\mathrm{k}}$ | `ALDSEC_k` | rate aldosterone secretion |  | mmol/min | ✓ |
| $f_{\mathrm{ald\_ang2}}$ | `f_ald_ang2` | fraction of the aldosterone secretion driven by angiotensin II | $0.66$ | \- | ✓ |
| $\mathrm{ANG1ANG2}_{\mathrm{EC50\_eat}}$ | `ANG1ANG2_EC50_eat` | EC50 of the ACE inhibition by enalaprilat | $1.28013346069641 \times 10^{-5}$ | mmol/l | ✓ |
| $\mathrm{ANG1ANG2}_{\mathrm{Emax\_eat}}$ | `ANG1ANG2_Emax_eat` | maximum inhibition of ACE by enalaprilat | $1$ | \- | ✓ |
| $\mathrm{ace}_{\mathrm{activity}}$ | `ace_activity` | ACE activity |  | \- |  |
| $\mathrm{ace}_{\mathrm{inhibition}}$ | `ace_inhibition` | ACE inhibition |  | \- |  |
| $\mathrm{SBP}_{\mathrm{ref}}$ | `SBP_ref` | reference systolic blood pressure \[mmHg\] | $120$ | (133.322 N)/m<sup>2</sup> | ✓ |
| $\mathrm{DBP}_{\mathrm{ref}}$ | `DBP_ref` | reference diastolic blood pressure \[mmHg\] | $80$ | (133.322 N)/m<sup>2</sup> | ✓ |
| $\mathrm{SBP}$ | `SBP` | systolic blood pressure \[mmHg\] |  | (133.322 N)/m<sup>2</sup> |  |
| $\mathrm{DBP}$ | `DBP` | diastolic blood pressure \[mmHg\] |  | (133.322 N)/m<sup>2</sup> |  |
| $\mathrm{MAP}$ | `MAP` | mean arterial pressure \[mmHg\] |  | (133.322 N)/m<sup>2</sup> |  |
| $\mathrm{BP}_{\mathrm{ang2\_fe}}$ | `BP_ang2_fe` | effect of angiotensin II on blood pressure \[-\] | $0.157702545492162$ | \- | ✓ |
| $\mathrm{SBP}_{\mathrm{change}}$ | `SBP_change` | SBP change |  | (133.322 N)/m<sup>2</sup> |  |
| $\mathrm{SBP}_{\mathrm{ratio}}$ | `SBP_ratio` | SBP ratio |  | \- |  |
| $\mathrm{SBP}_{\mathrm{change\_relative}}$ | `SBP_change_relative` | SBP change relative |  | \- |  |
| $\mathrm{DBP}_{\mathrm{change}}$ | `DBP_change` | DBP change |  | (133.322 N)/m<sup>2</sup> |  |
| $\mathrm{DBP}_{\mathrm{ratio}}$ | `DBP_ratio` | DBP ratio |  | \- |  |
| $\mathrm{DBP}_{\mathrm{change\_relative}}$ | `DBP_change_relative` | DBP change relative |  | \- |  |
| $\mathrm{MAP}_{\mathrm{change}}$ | `MAP_change` | MAP change |  | (133.322 N)/m<sup>2</sup> |  |
| $\mathrm{MAP}_{\mathrm{ratio}}$ | `MAP_ratio` | MAP ratio |  | \- |  |
| $\mathrm{MAP}_{\mathrm{change\_relative}}$ | `MAP_change_relative` | MAP change relative |  | \- |  |
| $\mathrm{BW}$ | `BW` | body weight \[kg\] | $75$ | kg | ✓ |
| $\mathrm{BW}_{\mathrm{ref}}$ | `BW_ref` | reference body weight \[kg\] | $75$ | kg | ✓ |
| $\mathrm{HEIGHT}$ | `HEIGHT` | height \[cm\] | $170$ | cm | ✓ |
| $\mathrm{HR}$ | `HR` | heart rate \[1/min\] | $70$ | 1/min | ✓ |
| $\mathrm{HRrest}$ | `HRrest` | resting heart rate \[1/min\] | $70$ | 1/min | ✓ |
| $\mathrm{BSA}$ | `BSA` | body surface area \[m^2\] |  | m<sup>2</sup> |  |
| $\mathrm{COBW}$ | `COBW` | cardiac output per bodyweight \[ml/s/kg\] | $1.548$ | ml/s/kg | ✓ |
| $f_{\mathrm{cardiac\_function}}$ | `f_cardiac_function` | heart function | $1$ | \- |  |
| $\mathrm{CO}$ | `CO` | cardiac output \[ml/s\] |  | ml/s |  |
| $\mathrm{QC}$ | `QC` | cardiac output \[l/min\] |  | l/min |  |
| $\mathrm{COHRI}$ | `COHRI` | increase of cardiac output per heartbeat \[ml\] | $150$ | ml | ✓ |
| $\mathrm{Fblood}$ | `Fblood` | blood fraction of organ volume | $0.02$ | \- |  |
| $\mathrm{HCT}$ | `HCT` | hematocrit | $0.51$ | \- | ✓ |
| $\mathrm{FVgu}$ | `FVgu` | gut fractional tissue volume | $0.0171$ | l/kg | ✓ |
| $\mathrm{FVki}$ | `FVki` | kidney fractional tissue volume | $0.0044$ | l/kg | ✓ |
| $\mathrm{FVli}$ | `FVli` | liver fractional tissue volume | $0.021$ | l/kg | ✓ |
| $\mathrm{FVlu}$ | `FVlu` | lung fractional tissue volume | $0.0076$ | l/kg | ✓ |
| $\mathrm{FVre}$ | `FVre` | rest of body fractional tissue volume |  | l/kg |  |
| $\mathrm{FVve}$ | `FVve` | venous fractional tissue volume | $0.0514$ | l/kg | ✓ |
| $\mathrm{FVar}$ | `FVar` | arterial fractional tissue volume | $0.0257$ | l/kg | ✓ |
| $\mathrm{FVpo}$ | `FVpo` | portal fractional tissue volume | $0.001$ | l/kg | ✓ |
| $\mathrm{FVhv}$ | `FVhv` | hepatic venous fractional tissue volume | $0.001$ | l/kg | ✓ |
| $\mathrm{FQgu}$ | `FQgu` | gut fractional tissue blood flow | $0.18$ | \- | ✓ |
| $\mathrm{FQki}$ | `FQki` | kidney fractional tissue blood flow | $0.19$ | \- | ✓ |
| $\mathrm{FQh}$ | `FQh` | hepatic (venous side) fractional tissue blood flow | $0.215$ | \- | ✓ |
| $\mathrm{FQlu}$ | `FQlu` | lung fractional tissue blood flow | $1$ | \- | ✓ |
| $\mathrm{FQre}$ | `FQre` | rest of body fractional tissue blood flow |  | \- |  |
| $\mathrm{conversion}_{\mathrm{min\_per\_day}}$ | `conversion_min_per_day` | conversion factor min to day | $1440$ | min/day | ✓ |
| $f_{\mathrm{cirrhosis}}$ | `f_cirrhosis` | severity of cirrhosis \[0, 0.95\] | $0$ | \- | ✓ |
| $f_{\mathrm{shunts}}$ | `f_shunts` | fraction of portal venous blood shunted by the liver |  | \- |  |
| $f_{\mathrm{tissue\_loss}}$ | `f_tissue_loss` | fraction of lost parenchymal liver volume |  | \- |  |
| $\mathrm{fu}_{\mathrm{ena}}$ | `fu_ena` | fraction unbound in plasma enalapril | $1$ | \- | ✓ |
| $\mathrm{fu}_{\mathrm{eat}}$ | `fu_eat` | fraction unbound in plasma enalaprilat | $0.62$ | \- | ✓ |
| $f_{\mathrm{GFR\_Qki}}$ | `f_GFR_Qki` | relationship GFR and Qki | $76.3105006271061$ | ml/l | ✓ |
| $\mathrm{GFR}_{\mathrm{base}}$ | `GFR_base` | glomerular filtration rate (healthy) |  | ml/min |  |
| $\mathrm{PODOSE}_{\mathrm{ena}}$ | `PODOSE_ena` | oral dose ena \[mg\] | $0$ | mg |  |
| $\mathrm{Ka}_{\mathrm{dis\_ena}}$ | `Ka_dis_ena` | Ka\_dis \[1/hr\] dissolution enalapril | $1.21059750573527$ | 1/hr | ✓ |
| $\mathrm{Mr}_{\mathrm{ena}}$ | `Mr_ena` | Molecular weight ena \[g/mole\] | $376.4467$ | g/mol | ✓ |
| $\mathrm{ftissue}_{\mathrm{ena}}$ | `ftissue_ena` | tissue distribution enalapril | $2$ | l/min | ✓ |
| $\mathrm{Kp}_{\mathrm{ena}}$ | `Kp_ena` | tissue/plasma partition coefficient enalapril | $0.0217554333669896$ | \- | ✓ |
| $\mathrm{IVDOSE}_{\mathrm{ena}}$ | `IVDOSE_ena` | IV bolus dose ena \[mg\] | $0$ | mg |  |
| $\mathrm{ti}_{\mathrm{ena}}$ | `ti_ena` | injection time ena \[s\] | $10$ | s | ✓ |
| $\mathrm{Ki}_{\mathrm{ena}}$ | `Ki_ena` | Ki \[1/min\] injection ena |  | 1/min |  |
| $\mathrm{Ri}_{\mathrm{ena}}$ | `Ri_ena` | Ri \[mg/min\] rate of infusion ena | $0$ | mg/min | ✓ |
| $\mathrm{cum}_{\mathrm{dose\_ena}}$ | `cum_dose_ena` | Cumulative dose due to infusion ena | $0$ | mg |  |
| $\mathrm{Mr}_{\mathrm{eat}}$ | `Mr_eat` | Molecular weight eat \[g/mole\] | $348.3936$ | g/mol | ✓ |
| $\mathrm{ftissue}_{\mathrm{eat}}$ | `ftissue_eat` | tissue distribution enalaprilat | $2$ | l/min | ✓ |
| $\mathrm{Kp}_{\mathrm{eat}}$ | `Kp_eat` | tissue/plasma partition coefficient enalaprilat | $0.0200773169715919$ | \- | ✓ |
| $\mathrm{IVDOSE}_{\mathrm{eat}}$ | `IVDOSE_eat` | IV bolus dose eat \[mg\] | $0$ | mg |  |
| $\mathrm{ti}_{\mathrm{eat}}$ | `ti_eat` | injection time eat \[s\] | $10$ | s | ✓ |
| $\mathrm{Ki}_{\mathrm{eat}}$ | `Ki_eat` | Ki \[1/min\] injection eat |  | 1/min |  |
| $\mathrm{Ri}_{\mathrm{eat}}$ | `Ri_eat` | Ri \[mg/min\] rate of infusion eat | $0$ | mg/min | ✓ |
| $\mathrm{cum}_{\mathrm{dose\_eat}}$ | `cum_dose_eat` | Cumulative dose due to infusion eat | $0$ | mg |  |
| $\mathrm{EATACE}_{\mathrm{Bmax}}$ | `EATACE_Bmax` | capacity of the binding of enalaprilat to tissue ACE | $5.57862077724698 \times 10^{-5}$ | mmol/l | ✓ |
| $\mathrm{EATACE}_{\mathrm{Kd}}$ | `EATACE_Kd` | dissociation constant of enalaprilat and tissue ACE | $8.3900937596074 \times 10^{-7}$ | mmol/l | ✓ |
| $\mathrm{EATACE}_{\mathrm{koff}}$ | `EATACE_koff` | dissociation rate of enalaprilat from tissue ACE | $1$ | 1/min | ✓ |
| $\mathrm{Are}_{\mathrm{eat\_ace}}$ | `Are_eat_ace` | enalaprilat bound to ACE (rest of body) \[mmole\] |  | mmol |  |
| $\mathrm{Xre}_{\mathrm{eat\_ace}}$ | `Xre_eat_ace` | enalaprilat bound to ACE (rest of body) \[mg\] |  | mg |  |
| $f_{\mathrm{ace\_occupancy}}$ | `f_ace_occupancy` | fraction of tissue ACE bound by enalaprilat |  | \- |  |
| $\mathrm{MAP}_{\mathrm{ref}}$ | `MAP_ref` |  |  | (133.322 N)/m<sup>2</sup> |  |
| $\mathrm{Qgu}$ | `Qgu` | gut blood flow |  | l/min |  |
| $\mathrm{Qki}$ | `Qki` | kidney blood flow |  | l/min |  |
| $\mathrm{Qh}$ | `Qh` | hepatic (venous side) blood flow |  | l/min |  |
| $\mathrm{Qha}$ | `Qha` | hepatic artery blood flow |  | l/min |  |
| $\mathrm{Qlu}$ | `Qlu` | lung blood flow |  | l/min |  |
| $\mathrm{Qre}$ | `Qre` | rest of body blood flow |  | l/min |  |
| $\mathrm{Qpo}$ | `Qpo` | portal blood flow |  | l/min |  |
| $\mathrm{Aki}_{\mathrm{plasma\_ena}}$ | `Aki_plasma_ena` | enalapril amount (kidney) \[mmole\] |  | mmol |  |
| $\mathrm{Xki}_{\mathrm{plasma\_ena}}$ | `Xki_plasma_ena` | enalapril amount (kidney) \[mg\] |  | mg |  |
| $\mathrm{Mki}_{\mathrm{plasma\_ena}}$ | `Mki_plasma_ena` | enalapril concentration (kidney) \[mg/l\] |  | mg/l |  |
| $\mathrm{Ali}_{\mathrm{plasma\_ena}}$ | `Ali_plasma_ena` | enalapril amount (liver) \[mmole\] |  | mmol |  |
| $\mathrm{Xli}_{\mathrm{plasma\_ena}}$ | `Xli_plasma_ena` | enalapril amount (liver) \[mg\] |  | mg |  |
| $\mathrm{Mli}_{\mathrm{plasma\_ena}}$ | `Mli_plasma_ena` | enalapril concentration (liver) \[mg/l\] |  | mg/l |  |
| $\mathrm{Alu}_{\mathrm{plasma\_ena}}$ | `Alu_plasma_ena` | enalapril amount (lung) \[mmole\] |  | mmol |  |
| $\mathrm{Xlu}_{\mathrm{plasma\_ena}}$ | `Xlu_plasma_ena` | enalapril amount (lung) \[mg\] |  | mg |  |
| $\mathrm{Mlu}_{\mathrm{plasma\_ena}}$ | `Mlu_plasma_ena` | enalapril concentration (lung) \[mg/l\] |  | mg/l |  |
| $\mathrm{Agu}_{\mathrm{plasma\_ena}}$ | `Agu_plasma_ena` | enalapril amount (gut) \[mmole\] |  | mmol |  |
| $\mathrm{Xgu}_{\mathrm{plasma\_ena}}$ | `Xgu_plasma_ena` | enalapril amount (gut) \[mg\] |  | mg |  |
| $\mathrm{Mgu}_{\mathrm{plasma\_ena}}$ | `Mgu_plasma_ena` | enalapril concentration (gut) \[mg/l\] |  | mg/l |  |
| $\mathrm{Are}_{\mathrm{plasma\_ena}}$ | `Are_plasma_ena` | enalapril amount (rest) \[mmole\] |  | mmol |  |
| $\mathrm{Xre}_{\mathrm{plasma\_ena}}$ | `Xre_plasma_ena` | enalapril amount (rest) \[mg\] |  | mg |  |
| $\mathrm{Mre}_{\mathrm{plasma\_ena}}$ | `Mre_plasma_ena` | enalapril concentration (rest) \[mg/l\] |  | mg/l |  |
| $\mathrm{Aar}_{\mathrm{ena}}$ | `Aar_ena` | enalapril amount (arterial blood) \[mmole\] |  | mmol |  |
| $\mathrm{Xar}_{\mathrm{ena}}$ | `Xar_ena` | enalapril amount (arterial blood) \[mg\] |  | mg |  |
| $\mathrm{Mar}_{\mathrm{ena}}$ | `Mar_ena` | enalapril concentration (arterial blood) \[mg/l\] |  | mg/l |  |
| $\mathrm{Ave}_{\mathrm{ena}}$ | `Ave_ena` | enalapril amount (venous blood) \[mmole\] |  | mmol |  |
| $\mathrm{Xve}_{\mathrm{ena}}$ | `Xve_ena` | enalapril amount (venous blood) \[mg\] |  | mg |  |
| $\mathrm{Mve}_{\mathrm{ena}}$ | `Mve_ena` | enalapril concentration (venous blood) \[mg/l\] |  | mg/l |  |
| $\mathrm{Apo}_{\mathrm{ena}}$ | `Apo_ena` | enalapril amount (portal vein) \[mmole\] |  | mmol |  |
| $\mathrm{Xpo}_{\mathrm{ena}}$ | `Xpo_ena` | enalapril amount (portal vein) \[mg\] |  | mg |  |
| $\mathrm{Mpo}_{\mathrm{ena}}$ | `Mpo_ena` | enalapril concentration (portal vein) \[mg/l\] |  | mg/l |  |
| $\mathrm{Ahv}_{\mathrm{ena}}$ | `Ahv_ena` | enalapril amount (hepatic vein) \[mmole\] |  | mmol |  |
| $\mathrm{Xhv}_{\mathrm{ena}}$ | `Xhv_ena` | enalapril amount (hepatic vein) \[mg\] |  | mg |  |
| $\mathrm{Mhv}_{\mathrm{ena}}$ | `Mhv_ena` | enalapril concentration (hepatic vein) \[mg/l\] |  | mg/l |  |
| $\mathrm{Xurine}_{\mathrm{ena}}$ | `Xurine_ena` | enalapril amount (urine) \[mg\] |  | mg |  |
| $\mathrm{Xfeces}_{\mathrm{ena}}$ | `Xfeces_ena` | enalapril amount (feces) |  | mg |  |
| $\mathrm{Aki}_{\mathrm{plasma\_eat}}$ | `Aki_plasma_eat` | enalaprilat amount (kidney) \[mmole\] |  | mmol |  |
| $\mathrm{Xki}_{\mathrm{plasma\_eat}}$ | `Xki_plasma_eat` | enalaprilat amount (kidney) \[mg\] |  | mg |  |
| $\mathrm{Mki}_{\mathrm{plasma\_eat}}$ | `Mki_plasma_eat` | enalaprilat concentration (kidney) \[mg/l\] |  | mg/l |  |
| $\mathrm{Ali}_{\mathrm{plasma\_eat}}$ | `Ali_plasma_eat` | enalaprilat amount (liver) \[mmole\] |  | mmol |  |
| $\mathrm{Xli}_{\mathrm{plasma\_eat}}$ | `Xli_plasma_eat` | enalaprilat amount (liver) \[mg\] |  | mg |  |
| $\mathrm{Mli}_{\mathrm{plasma\_eat}}$ | `Mli_plasma_eat` | enalaprilat concentration (liver) \[mg/l\] |  | mg/l |  |
| $\mathrm{Alu}_{\mathrm{plasma\_eat}}$ | `Alu_plasma_eat` | enalaprilat amount (lung) \[mmole\] |  | mmol |  |
| $\mathrm{Xlu}_{\mathrm{plasma\_eat}}$ | `Xlu_plasma_eat` | enalaprilat amount (lung) \[mg\] |  | mg |  |
| $\mathrm{Mlu}_{\mathrm{plasma\_eat}}$ | `Mlu_plasma_eat` | enalaprilat concentration (lung) \[mg/l\] |  | mg/l |  |
| $\mathrm{Agu}_{\mathrm{plasma\_eat}}$ | `Agu_plasma_eat` | enalaprilat amount (gut) \[mmole\] |  | mmol |  |
| $\mathrm{Xgu}_{\mathrm{plasma\_eat}}$ | `Xgu_plasma_eat` | enalaprilat amount (gut) \[mg\] |  | mg |  |
| $\mathrm{Mgu}_{\mathrm{plasma\_eat}}$ | `Mgu_plasma_eat` | enalaprilat concentration (gut) \[mg/l\] |  | mg/l |  |
| $\mathrm{Are}_{\mathrm{plasma\_eat}}$ | `Are_plasma_eat` | enalaprilat amount (rest) \[mmole\] |  | mmol |  |
| $\mathrm{Xre}_{\mathrm{plasma\_eat}}$ | `Xre_plasma_eat` | enalaprilat amount (rest) \[mg\] |  | mg |  |
| $\mathrm{Mre}_{\mathrm{plasma\_eat}}$ | `Mre_plasma_eat` | enalaprilat concentration (rest) \[mg/l\] |  | mg/l |  |
| $\mathrm{Aar}_{\mathrm{eat}}$ | `Aar_eat` | enalaprilat amount (arterial blood) \[mmole\] |  | mmol |  |
| $\mathrm{Xar}_{\mathrm{eat}}$ | `Xar_eat` | enalaprilat amount (arterial blood) \[mg\] |  | mg |  |
| $\mathrm{Mar}_{\mathrm{eat}}$ | `Mar_eat` | enalaprilat concentration (arterial blood) \[mg/l\] |  | mg/l |  |
| $\mathrm{Ave}_{\mathrm{eat}}$ | `Ave_eat` | enalaprilat amount (venous blood) \[mmole\] |  | mmol |  |
| $\mathrm{Xve}_{\mathrm{eat}}$ | `Xve_eat` | enalaprilat amount (venous blood) \[mg\] |  | mg |  |
| $\mathrm{Mve}_{\mathrm{eat}}$ | `Mve_eat` | enalaprilat concentration (venous blood) \[mg/l\] |  | mg/l |  |
| $\mathrm{Apo}_{\mathrm{eat}}$ | `Apo_eat` | enalaprilat amount (portal vein) \[mmole\] |  | mmol |  |
| $\mathrm{Xpo}_{\mathrm{eat}}$ | `Xpo_eat` | enalaprilat amount (portal vein) \[mg\] |  | mg |  |
| $\mathrm{Mpo}_{\mathrm{eat}}$ | `Mpo_eat` | enalaprilat concentration (portal vein) \[mg/l\] |  | mg/l |  |
| $\mathrm{Ahv}_{\mathrm{eat}}$ | `Ahv_eat` | enalaprilat amount (hepatic vein) \[mmole\] |  | mmol |  |
| $\mathrm{Xhv}_{\mathrm{eat}}$ | `Xhv_eat` | enalaprilat amount (hepatic vein) \[mg\] |  | mg |  |
| $\mathrm{Mhv}_{\mathrm{eat}}$ | `Mhv_eat` | enalaprilat concentration (hepatic vein) \[mg/l\] |  | mg/l |  |
| $\mathrm{Xurine}_{\mathrm{eat}}$ | `Xurine_eat` | enalaprilat amount (urine) \[mg\] |  | mg |  |
| $\mathrm{KI}_{\mathrm{\_f\_renal\_function}}$ | `KI__f_renal_function` | renal function | $1$ | \- | ✓ |
| $\mathrm{KI}_{\mathrm{\_ENAEX\_f}}$ | `KI__ENAEX_f` | renal clearance of unbound enalapril relative to the GFR | $2.87792398538051$ | \- | ✓ |
| $\mathrm{KI}_{\mathrm{\_EATEX\_f}}$ | `KI__EATEX_f` | renal clearance of unbound enalaprilat relative to the GFR | $2.56410960551508$ | \- | ✓ |
| $\mathrm{KI}_{\mathrm{\_GFR}}$ | `KI__GFR` | glomerular filtration rate |  | ml/min |  |
| $\mathrm{KI}_{\mathrm{\_ENA\_EATEX}}$ | `KI__ENA_EATEX` | renal excretion of enalapril and enalaprilat |  | mmol/min |  |
| $\mathrm{LI}_{\mathrm{\_ENAIM\_Vmax}}$ | `LI__ENAIM_Vmax` | Vmax enalapril import | $0.75$ | mmol/min/l | ✓ |
| $\mathrm{LI}_{\mathrm{\_ENAIM\_Km\_ena}}$ | `LI__ENAIM_Km_ena` | Km enalapril import | $0.844$ | mmol/l | ✓ |
| $\mathrm{LI}_{\mathrm{\_ENA2EAT\_Vmax}}$ | `LI__ENA2EAT_Vmax` | Vmax enalapril conversion | $0.643377167672023$ | mmol/min/l | ✓ |
| $\mathrm{LI}_{\mathrm{\_ENA2EAT\_Km\_ena}}$ | `LI__ENA2EAT_Km_ena` | Km enalapril CES1 | $1.721$ | mmol/l | ✓ |
| $\mathrm{LI}_{\mathrm{\_ENA2EAT\_Ki\_ena}}$ | `LI__ENA2EAT_Ki_ena` | Ki enalapril CES1 | $2.956$ | mmol/l | ✓ |
| $\mathrm{LI}_{\mathrm{\_f\_ces1}}$ | `LI__f_ces1` | scaling factor CES1 activity | $1$ | \- | ✓ |
| $\mathrm{LI}_{\mathrm{\_EATEX\_Vmax}}$ | `LI__EATEX_Vmax` | Vmax enalaprilat export | $0.00145697380767393$ | mmol/min/l | ✓ |
| $\mathrm{LI}_{\mathrm{\_EATEX\_Km\_eat}}$ | `LI__EATEX_Km_eat` | Km enalaprilat export | $0.43$ | mmol/l | ✓ |
| $\mathrm{GU}_{\mathrm{\_F\_ena\_abs}}$ | `GU__F_ena_abs` | fraction absorbed enalapril | $0.577261573734921$ | \- | ✓ |
| $\mathrm{GU}_{\mathrm{\_ENAABS\_k}}$ | `GU__ENAABS_k` | rate of enalapril absorption | $0.02288941081702$ | 1/min | ✓ |
| $\mathrm{GU}_{\mathrm{\_fed}}$ | `GU__fed` | fed state (0 fasted, 1 fed) | $0$ | \- | ✓ |
| $\mathrm{GU}_{\mathrm{\_FED\_f\_dissolution}}$ | `GU__FED_f_dissolution` | fed effect on the dissolution and gastric emptying | $0.42677125646477$ | \- | ✓ |
| $\mathrm{GU}_{\mathrm{\_f\_dissolution}}$ | `GU__f_dissolution` | factor of the dissolution and gastric emptying |  | \- |  |
| $\mathrm{GU}_{\mathrm{\_absorption}}$ | `GU__absorption` | transit of enalapril (absorption and fecal excretion) |  | mmol/min |  |

## Initial assignments and assignment rules

The initial assignments set the values at $t = 0$:

$$
\begin{aligned}
\mathrm{ald} &= \mathrm{ald}_{\mathrm{ref}} \\[1ex]
\mathrm{ren} &= \mathrm{ren}_{\mathrm{ref}} \\[1ex]
\mathrm{anggen} &= \mathrm{anggen}_{\mathrm{ref}} \\[1ex]
\mathrm{ang}_{1} &= \mathrm{ang1}_{\mathrm{ref}} \\[1ex]
\mathrm{ang}_{2} &= \mathrm{ang2}_{\mathrm{ref}} \\[1ex]
\mathrm{ace} &= \mathrm{ace}_{\mathrm{ref}} \\[1ex]
\mathrm{Aurine}_{\mathrm{ena}} &= 0 \cdot \mathrm{Vurine} \\[1ex]
\mathrm{Afeces}_{\mathrm{ena}} &= 0 \cdot \mathrm{Vfeces} \\[1ex]
\mathrm{Aurine}_{\mathrm{eat}} &= 0 \cdot \mathrm{Vurine} \\[1ex]
\mathrm{GU}_{\mathrm{\_ena\_stomach}} &= 0 \cdot \mathrm{GU}_{\mathrm{\_Vstomach}} \\[1ex]
\mathrm{RENSEC}_{\mathrm{k}} &= \mathrm{RENDEG}_{\mathrm{k}} \cdot \mathrm{ren}_{\mathrm{ref}} \\[1ex]
\mathrm{ang2}_{\mathrm{feedback}} &= \mathrm{ang2}_{\mathrm{ref}} \\[1ex]
\mathrm{ANGGEN2ANG1}_{\mathrm{k}} &= \frac{\mathrm{ANG1CL} \cdot \mathrm{ang1}_{\mathrm{ref}}}{\mathrm{anggen}_{\mathrm{ref}}} \\[1ex]
\mathrm{ANG1ANG2}_{\mathrm{k}} &= f_{\mathrm{ang1\_ace}} \cdot \mathrm{ANG1CL} \\[1ex]
\mathrm{ANG1DEG}_{\mathrm{k}} &= \mathopen{}\left(1 - f_{\mathrm{ang1\_ace}}\right) \cdot \mathrm{ANG1CL} \\[1ex]
\mathrm{ANG2DEG}_{\mathrm{k}} &= \frac{f_{\mathrm{ang1\_ace}} \cdot \mathrm{ANG1CL} \cdot \mathrm{ang1}_{\mathrm{ref}}}{\mathrm{ang2}_{\mathrm{ref}}} \\[1ex]
\mathrm{ALDSEC}_{\mathrm{k}} &= \mathrm{ALDDEG}_{\mathrm{k}} \cdot \mathrm{ald}_{\mathrm{ref}}
\end{aligned}
$$

The assignment rules hold at every time $t$:

$$
\begin{aligned}
\mathrm{ald}_{\mathrm{change}} &= \mathrm{ald} - \mathrm{ald}_{\mathrm{ref}} \\[1ex]
\mathrm{ald}_{\mathrm{ratio}} &= \frac{\mathrm{ald}}{\mathrm{ald}_{\mathrm{ref}}} \\[1ex]
\mathrm{ren}_{\mathrm{change}} &= \mathrm{ren} - \mathrm{ren}_{\mathrm{ref}} \\[1ex]
\mathrm{ren}_{\mathrm{ratio}} &= \frac{\mathrm{ren}}{\mathrm{ren}_{\mathrm{ref}}} \\[1ex]
\mathrm{anggen}_{\mathrm{change}} &= \mathrm{anggen} - \mathrm{anggen}_{\mathrm{ref}} \\[1ex]
\mathrm{anggen}_{\mathrm{ratio}} &= \frac{\mathrm{anggen}}{\mathrm{anggen}_{\mathrm{ref}}} \\[1ex]
\mathrm{ang1}_{\mathrm{change}} &= \mathrm{ang}_{1} - \mathrm{ang1}_{\mathrm{ref}} \\[1ex]
\mathrm{ang1}_{\mathrm{ratio}} &= \frac{\mathrm{ang}_{1}}{\mathrm{ang1}_{\mathrm{ref}}} \\[1ex]
\mathrm{ang2}_{\mathrm{change}} &= \mathrm{ang}_{2} - \mathrm{ang2}_{\mathrm{ref}} \\[1ex]
\mathrm{ang2}_{\mathrm{ratio}} &= \frac{\mathrm{ang}_{2}}{\mathrm{ang2}_{\mathrm{ref}}} \\[1ex]
\mathrm{ace}_{\mathrm{change}} &= \mathrm{ace} - \mathrm{ace}_{\mathrm{ref}} \\[1ex]
\mathrm{ace}_{\mathrm{ratio}} &= \frac{\mathrm{ace}}{\mathrm{ace}_{\mathrm{ref}}} \\[1ex]
\mathrm{SBP} &= \mathrm{SBP}_{\mathrm{ref}} \cdot \mathopen{}\left(1 + \frac{\mathrm{BP}_{\mathrm{ang2\_fe}} \cdot \mathopen{}\left(\mathrm{ang}_{2} - \mathrm{ang2}_{\mathrm{ref}}\right)}{\mathrm{ang2}_{\mathrm{ref}}}\right) \\[1ex]
\mathrm{DBP} &= \mathrm{DBP}_{\mathrm{ref}} \cdot \mathopen{}\left(1 + \frac{\mathrm{BP}_{\mathrm{ang2\_fe}} \cdot \mathopen{}\left(\mathrm{ang}_{2} - \mathrm{ang2}_{\mathrm{ref}}\right)}{\mathrm{ang2}_{\mathrm{ref}}}\right) \\[1ex]
\mathrm{MAP} &= \mathrm{DBP} + \frac{\mathrm{SBP} - \mathrm{DBP}}{3} \\[1ex]
\mathrm{MAP}_{\mathrm{ref}} &= \mathrm{DBP}_{\mathrm{ref}} + \frac{\mathrm{SBP}_{\mathrm{ref}} - \mathrm{DBP}_{\mathrm{ref}}}{3} \\[1ex]
\mathrm{SBP}_{\mathrm{change}} &= \mathrm{SBP} - \mathrm{SBP}_{\mathrm{ref}} \\[1ex]
\mathrm{SBP}_{\mathrm{ratio}} &= \frac{\mathrm{SBP}}{\mathrm{SBP}_{\mathrm{ref}}} \\[1ex]
\mathrm{SBP}_{\mathrm{change\_relative}} &= \frac{\mathrm{SBP}_{\mathrm{change}}}{\mathrm{SBP}_{\mathrm{ref}}} \\[1ex]
\mathrm{DBP}_{\mathrm{change}} &= \mathrm{DBP} - \mathrm{DBP}_{\mathrm{ref}} \\[1ex]
\mathrm{DBP}_{\mathrm{ratio}} &= \frac{\mathrm{DBP}}{\mathrm{DBP}_{\mathrm{ref}}} \\[1ex]
\mathrm{DBP}_{\mathrm{change\_relative}} &= \frac{\mathrm{DBP}_{\mathrm{change}}}{\mathrm{DBP}_{\mathrm{ref}}} \\[1ex]
\mathrm{MAP}_{\mathrm{change}} &= \mathrm{MAP} - \mathrm{MAP}_{\mathrm{ref}} \\[1ex]
\mathrm{MAP}_{\mathrm{ratio}} &= \frac{\mathrm{MAP}}{\mathrm{MAP}_{\mathrm{ref}}} \\[1ex]
\mathrm{MAP}_{\mathrm{change\_relative}} &= \frac{\mathrm{MAP}_{\mathrm{change}}}{\mathrm{MAP}_{\mathrm{ref}}} \\[1ex]
\mathrm{Aurine}_{\mathrm{ena\_eat}} &= \mathrm{Aurine}_{\mathrm{ena}} + \mathrm{Aurine}_{\mathrm{eat}} \\[1ex]
f_{\mathrm{shunts}} &= f_{\mathrm{cirrhosis}} \\[1ex]
f_{\mathrm{tissue\_loss}} &= f_{\mathrm{cirrhosis}} \\[1ex]
\mathrm{FVre} &= 1 - \mathrm{FVgu} - \mathrm{FVki} - \mathrm{FVli} \\
&\quad {} - \mathrm{FVlu} - \mathrm{FVve} - \mathrm{FVar} \\[1ex]
\mathrm{FQre} &= 1 - \mathrm{FQki} - \mathrm{FQh} \\[1ex]
\mathrm{BSA} &= 0.024265 \cdot \mathopen{}\left(\frac{\mathrm{BW}}{1}\right)^{0.5378} \cdot \mathopen{}\left(\frac{\mathrm{HEIGHT}}{1}\right)^{0.3964} \\[1ex]
\mathrm{CO} &= f_{\mathrm{cardiac\_function}} \cdot \mathrm{BW} \cdot \mathrm{COBW} + \frac{\mathopen{}\left(\mathrm{HR} - \mathrm{HRrest}\right) \cdot \mathrm{COHRI}}{60} \\[1ex]
\mathrm{QC} &= \frac{\mathrm{CO}}{1000} \cdot 60 \\[1ex]
\mathrm{Vgu} &= \mathrm{BW} \cdot \mathrm{FVgu} \\[1ex]
\mathrm{Vki} &= \mathrm{BW} \cdot \mathrm{FVki} \\[1ex]
\mathrm{Vli} &= \mathrm{BW} \cdot \mathrm{FVli} \\[1ex]
\mathrm{Vlu} &= \mathrm{BW} \cdot \mathrm{FVlu} \\[1ex]
\mathrm{Vre} &= \mathrm{BW} \cdot \mathrm{FVre} \\[1ex]
\mathrm{Vve} &= \mathrm{BW} \cdot \mathrm{FVve} - \frac{\mathrm{FVve}}{\mathrm{FVar} + \mathrm{FVve}} \cdot \mathrm{BW} \cdot \mathrm{Fblood} \cdot \mathopen{}\left(1 - \mathrm{FVve} - \mathrm{FVar}\right) \\[1ex]
\mathrm{Var} &= \mathrm{BW} \cdot \mathrm{FVar} - \frac{\mathrm{FVar}}{\mathrm{FVar} + \mathrm{FVve}} \cdot \mathrm{BW} \cdot \mathrm{Fblood} \cdot \mathopen{}\left(1 - \mathrm{FVve} - \mathrm{FVar}\right) \\[1ex]
\mathrm{Vpo} &= \mathopen{}\left(1 - \mathrm{HCT}\right) \cdot \mathopen{}\left(\mathrm{BW} \cdot \mathrm{FVpo} - \frac{\mathrm{FVpo}}{\mathrm{FVar} + \mathrm{FVve} + \mathrm{FVpo} + \mathrm{FVhv}} \cdot \mathrm{BW} \cdot \mathrm{Fblood} \cdot \mathopen{}\left(1 - \mathrm{FVar} - \mathrm{FVve} - \mathrm{FVpo} - \mathrm{FVhv}\right)\right) \\[1ex]
\mathrm{Vhv} &= \mathopen{}\left(1 - \mathrm{HCT}\right) \cdot \mathopen{}\left(\mathrm{BW} \cdot \mathrm{FVhv} - \frac{\mathrm{FVhv}}{\mathrm{FVar} + \mathrm{FVve} + \mathrm{FVpo} + \mathrm{FVhv}} \cdot \mathrm{BW} \cdot \mathrm{Fblood} \cdot \mathopen{}\left(1 - \mathrm{FVar} - \mathrm{FVve} - \mathrm{FVpo} - \mathrm{FVhv}\right)\right) \\[1ex]
\mathrm{Qgu} &= \mathrm{QC} \cdot \mathrm{FQgu} \\[1ex]
\mathrm{Qki} &= \mathrm{QC} \cdot \mathrm{FQki} \\[1ex]
\mathrm{GFR}_{\mathrm{base}} &= f_{\mathrm{GFR\_Qki}} \cdot \mathrm{Qki} \\[1ex]
\mathrm{Qh} &= \mathrm{QC} \cdot \mathrm{FQh} \\[1ex]
\mathrm{Qha} &= \mathrm{Qh} - \mathrm{Qgu} \\[1ex]
\mathrm{Qlu} &= \mathrm{QC} \cdot \mathrm{FQlu} \\[1ex]
\mathrm{Qre} &= \mathrm{QC} \cdot \mathrm{FQre} \\[1ex]
\mathrm{Qpo} &= \mathrm{Qgu} \\[1ex]
\mathrm{Vki}_{\mathrm{plasma}} &= \mathrm{Vki} \cdot \mathrm{Fblood} \cdot \mathopen{}\left(1 - \mathrm{HCT}\right) \\[1ex]
\mathrm{Vki}_{\mathrm{tissue}} &= \mathrm{Vki} \cdot \mathopen{}\left(1 - \mathrm{Fblood}\right) \\[1ex]
\mathrm{Vli}_{\mathrm{plasma}} &= \mathrm{Vli} \cdot \mathrm{Fblood} \cdot \mathopen{}\left(1 - \mathrm{HCT}\right) \\[1ex]
\mathrm{Vli}_{\mathrm{tissue}} &= \mathrm{Vli} \cdot \mathopen{}\left(1 - f_{\mathrm{tissue\_loss}}\right) \cdot \mathopen{}\left(1 - \mathrm{Fblood}\right) \\[1ex]
\mathrm{Vlu}_{\mathrm{plasma}} &= \mathrm{Vlu} \cdot \mathrm{Fblood} \cdot \mathopen{}\left(1 - \mathrm{HCT}\right) \\[1ex]
\mathrm{Vlu}_{\mathrm{tissue}} &= \mathrm{Vlu} \cdot \mathopen{}\left(1 - \mathrm{Fblood}\right) \\[1ex]
\mathrm{Vgu}_{\mathrm{plasma}} &= \mathrm{Vgu} \cdot \mathrm{Fblood} \cdot \mathopen{}\left(1 - \mathrm{HCT}\right) \\[1ex]
\mathrm{Vgu}_{\mathrm{tissue}} &= \mathrm{Vgu} \cdot \mathopen{}\left(1 - \mathrm{Fblood}\right) \\[1ex]
\mathrm{Vre}_{\mathrm{plasma}} &= \mathrm{Vre} \cdot \mathrm{Fblood} \cdot \mathopen{}\left(1 - \mathrm{HCT}\right) \\[1ex]
\mathrm{Vre}_{\mathrm{tissue}} &= \mathrm{Vre} \cdot \mathopen{}\left(1 - \mathrm{Fblood}\right) \\[1ex]
\mathrm{Ki}_{\mathrm{ena}} &= \frac{0.693}{\mathrm{ti}_{\mathrm{ena}}} \cdot 60 \\[1ex]
\mathrm{Aki}_{\mathrm{plasma\_ena}} &= \mathrm{Cki}_{\mathrm{plasma\_ena}} \cdot \mathrm{Vki}_{\mathrm{plasma}} \\[1ex]
\mathrm{Xki}_{\mathrm{plasma\_ena}} &= \mathrm{Aki}_{\mathrm{plasma\_ena}} \cdot \mathrm{Mr}_{\mathrm{ena}} \\[1ex]
\mathrm{Mki}_{\mathrm{plasma\_ena}} &= \frac{\mathrm{Aki}_{\mathrm{plasma\_ena}}}{\mathrm{Vki}_{\mathrm{plasma}}} \cdot \mathrm{Mr}_{\mathrm{ena}} \\[1ex]
\mathrm{Ali}_{\mathrm{plasma\_ena}} &= \mathrm{Cli}_{\mathrm{plasma\_ena}} \cdot \mathrm{Vli}_{\mathrm{plasma}} \\[1ex]
\mathrm{Xli}_{\mathrm{plasma\_ena}} &= \mathrm{Ali}_{\mathrm{plasma\_ena}} \cdot \mathrm{Mr}_{\mathrm{ena}} \\[1ex]
\mathrm{Mli}_{\mathrm{plasma\_ena}} &= \frac{\mathrm{Ali}_{\mathrm{plasma\_ena}}}{\mathrm{Vli}_{\mathrm{plasma}}} \cdot \mathrm{Mr}_{\mathrm{ena}} \\[1ex]
\mathrm{Alu}_{\mathrm{plasma\_ena}} &= \mathrm{Clu}_{\mathrm{plasma\_ena}} \cdot \mathrm{Vlu}_{\mathrm{plasma}} \\[1ex]
\mathrm{Xlu}_{\mathrm{plasma\_ena}} &= \mathrm{Alu}_{\mathrm{plasma\_ena}} \cdot \mathrm{Mr}_{\mathrm{ena}} \\[1ex]
\mathrm{Mlu}_{\mathrm{plasma\_ena}} &= \frac{\mathrm{Alu}_{\mathrm{plasma\_ena}}}{\mathrm{Vlu}_{\mathrm{plasma}}} \cdot \mathrm{Mr}_{\mathrm{ena}} \\[1ex]
\mathrm{Agu}_{\mathrm{plasma\_ena}} &= \mathrm{Cgu}_{\mathrm{plasma\_ena}} \cdot \mathrm{Vgu}_{\mathrm{plasma}} \\[1ex]
\mathrm{Xgu}_{\mathrm{plasma\_ena}} &= \mathrm{Agu}_{\mathrm{plasma\_ena}} \cdot \mathrm{Mr}_{\mathrm{ena}} \\[1ex]
\mathrm{Mgu}_{\mathrm{plasma\_ena}} &= \frac{\mathrm{Agu}_{\mathrm{plasma\_ena}}}{\mathrm{Vgu}_{\mathrm{plasma}}} \cdot \mathrm{Mr}_{\mathrm{ena}} \\[1ex]
\mathrm{Are}_{\mathrm{plasma\_ena}} &= \mathrm{Cre}_{\mathrm{plasma\_ena}} \cdot \mathrm{Vre}_{\mathrm{plasma}} \\[1ex]
\mathrm{Xre}_{\mathrm{plasma\_ena}} &= \mathrm{Are}_{\mathrm{plasma\_ena}} \cdot \mathrm{Mr}_{\mathrm{ena}} \\[1ex]
\mathrm{Mre}_{\mathrm{plasma\_ena}} &= \frac{\mathrm{Are}_{\mathrm{plasma\_ena}}}{\mathrm{Vre}_{\mathrm{plasma}}} \cdot \mathrm{Mr}_{\mathrm{ena}} \\[1ex]
\mathrm{Aar}_{\mathrm{ena}} &= \mathrm{Car}_{\mathrm{ena}} \cdot \mathrm{Var} \\[1ex]
\mathrm{Xar}_{\mathrm{ena}} &= \mathrm{Aar}_{\mathrm{ena}} \cdot \mathrm{Mr}_{\mathrm{ena}} \\[1ex]
\mathrm{Mar}_{\mathrm{ena}} &= \frac{\mathrm{Aar}_{\mathrm{ena}}}{\mathrm{Var}} \cdot \mathrm{Mr}_{\mathrm{ena}} \\[1ex]
\mathrm{Ave}_{\mathrm{ena}} &= \mathrm{Cve}_{\mathrm{ena}} \cdot \mathrm{Vve} \\[1ex]
\mathrm{Xve}_{\mathrm{ena}} &= \mathrm{Ave}_{\mathrm{ena}} \cdot \mathrm{Mr}_{\mathrm{ena}} \\[1ex]
\mathrm{Mve}_{\mathrm{ena}} &= \frac{\mathrm{Ave}_{\mathrm{ena}}}{\mathrm{Vve}} \cdot \mathrm{Mr}_{\mathrm{ena}} \\[1ex]
\mathrm{Apo}_{\mathrm{ena}} &= \mathrm{Cpo}_{\mathrm{ena}} \cdot \mathrm{Vpo} \\[1ex]
\mathrm{Xpo}_{\mathrm{ena}} &= \mathrm{Apo}_{\mathrm{ena}} \cdot \mathrm{Mr}_{\mathrm{ena}} \\[1ex]
\mathrm{Mpo}_{\mathrm{ena}} &= \frac{\mathrm{Apo}_{\mathrm{ena}}}{\mathrm{Vpo}} \cdot \mathrm{Mr}_{\mathrm{ena}} \\[1ex]
\mathrm{Ahv}_{\mathrm{ena}} &= \mathrm{Chv}_{\mathrm{ena}} \cdot \mathrm{Vhv} \\[1ex]
\mathrm{Xhv}_{\mathrm{ena}} &= \mathrm{Ahv}_{\mathrm{ena}} \cdot \mathrm{Mr}_{\mathrm{ena}} \\[1ex]
\mathrm{Mhv}_{\mathrm{ena}} &= \frac{\mathrm{Ahv}_{\mathrm{ena}}}{\mathrm{Vhv}} \cdot \mathrm{Mr}_{\mathrm{ena}} \\[1ex]
\mathrm{Xurine}_{\mathrm{ena}} &= \mathrm{Aurine}_{\mathrm{ena}} \cdot \mathrm{Mr}_{\mathrm{ena}} \\[1ex]
\mathrm{Xfeces}_{\mathrm{ena}} &= \mathrm{Afeces}_{\mathrm{ena}} \cdot \mathrm{Mr}_{\mathrm{ena}} \\[1ex]
\mathrm{Ki}_{\mathrm{eat}} &= \frac{0.693}{\mathrm{ti}_{\mathrm{eat}}} \cdot 60 \\[1ex]
\mathrm{Aki}_{\mathrm{plasma\_eat}} &= \mathrm{Cki}_{\mathrm{plasma\_eat}} \cdot \mathrm{Vki}_{\mathrm{plasma}} \\[1ex]
\mathrm{Xki}_{\mathrm{plasma\_eat}} &= \mathrm{Aki}_{\mathrm{plasma\_eat}} \cdot \mathrm{Mr}_{\mathrm{eat}} \\[1ex]
\mathrm{Mki}_{\mathrm{plasma\_eat}} &= \frac{\mathrm{Aki}_{\mathrm{plasma\_eat}}}{\mathrm{Vki}_{\mathrm{plasma}}} \cdot \mathrm{Mr}_{\mathrm{eat}} \\[1ex]
\mathrm{Ali}_{\mathrm{plasma\_eat}} &= \mathrm{Cli}_{\mathrm{plasma\_eat}} \cdot \mathrm{Vli}_{\mathrm{plasma}} \\[1ex]
\mathrm{Xli}_{\mathrm{plasma\_eat}} &= \mathrm{Ali}_{\mathrm{plasma\_eat}} \cdot \mathrm{Mr}_{\mathrm{eat}} \\[1ex]
\mathrm{Mli}_{\mathrm{plasma\_eat}} &= \frac{\mathrm{Ali}_{\mathrm{plasma\_eat}}}{\mathrm{Vli}_{\mathrm{plasma}}} \cdot \mathrm{Mr}_{\mathrm{eat}} \\[1ex]
\mathrm{Alu}_{\mathrm{plasma\_eat}} &= \mathrm{Clu}_{\mathrm{plasma\_eat}} \cdot \mathrm{Vlu}_{\mathrm{plasma}} \\[1ex]
\mathrm{Xlu}_{\mathrm{plasma\_eat}} &= \mathrm{Alu}_{\mathrm{plasma\_eat}} \cdot \mathrm{Mr}_{\mathrm{eat}} \\[1ex]
\mathrm{Mlu}_{\mathrm{plasma\_eat}} &= \frac{\mathrm{Alu}_{\mathrm{plasma\_eat}}}{\mathrm{Vlu}_{\mathrm{plasma}}} \cdot \mathrm{Mr}_{\mathrm{eat}} \\[1ex]
\mathrm{Agu}_{\mathrm{plasma\_eat}} &= \mathrm{Cgu}_{\mathrm{plasma\_eat}} \cdot \mathrm{Vgu}_{\mathrm{plasma}} \\[1ex]
\mathrm{Xgu}_{\mathrm{plasma\_eat}} &= \mathrm{Agu}_{\mathrm{plasma\_eat}} \cdot \mathrm{Mr}_{\mathrm{eat}} \\[1ex]
\mathrm{Mgu}_{\mathrm{plasma\_eat}} &= \frac{\mathrm{Agu}_{\mathrm{plasma\_eat}}}{\mathrm{Vgu}_{\mathrm{plasma}}} \cdot \mathrm{Mr}_{\mathrm{eat}} \\[1ex]
\mathrm{Are}_{\mathrm{plasma\_eat}} &= \mathrm{Cre}_{\mathrm{plasma\_eat}} \cdot \mathrm{Vre}_{\mathrm{plasma}} \\[1ex]
\mathrm{Xre}_{\mathrm{plasma\_eat}} &= \mathrm{Are}_{\mathrm{plasma\_eat}} \cdot \mathrm{Mr}_{\mathrm{eat}} \\[1ex]
\mathrm{Mre}_{\mathrm{plasma\_eat}} &= \frac{\mathrm{Are}_{\mathrm{plasma\_eat}}}{\mathrm{Vre}_{\mathrm{plasma}}} \cdot \mathrm{Mr}_{\mathrm{eat}} \\[1ex]
\mathrm{Aar}_{\mathrm{eat}} &= \mathrm{Car}_{\mathrm{eat}} \cdot \mathrm{Var} \\[1ex]
\mathrm{Xar}_{\mathrm{eat}} &= \mathrm{Aar}_{\mathrm{eat}} \cdot \mathrm{Mr}_{\mathrm{eat}} \\[1ex]
\mathrm{Mar}_{\mathrm{eat}} &= \frac{\mathrm{Aar}_{\mathrm{eat}}}{\mathrm{Var}} \cdot \mathrm{Mr}_{\mathrm{eat}} \\[1ex]
\mathrm{Ave}_{\mathrm{eat}} &= \mathrm{Cve}_{\mathrm{eat}} \cdot \mathrm{Vve} \\[1ex]
\mathrm{Xve}_{\mathrm{eat}} &= \mathrm{Ave}_{\mathrm{eat}} \cdot \mathrm{Mr}_{\mathrm{eat}} \\[1ex]
\mathrm{Mve}_{\mathrm{eat}} &= \frac{\mathrm{Ave}_{\mathrm{eat}}}{\mathrm{Vve}} \cdot \mathrm{Mr}_{\mathrm{eat}} \\[1ex]
\mathrm{Apo}_{\mathrm{eat}} &= \mathrm{Cpo}_{\mathrm{eat}} \cdot \mathrm{Vpo} \\[1ex]
\mathrm{Xpo}_{\mathrm{eat}} &= \mathrm{Apo}_{\mathrm{eat}} \cdot \mathrm{Mr}_{\mathrm{eat}} \\[1ex]
\mathrm{Mpo}_{\mathrm{eat}} &= \frac{\mathrm{Apo}_{\mathrm{eat}}}{\mathrm{Vpo}} \cdot \mathrm{Mr}_{\mathrm{eat}} \\[1ex]
\mathrm{Ahv}_{\mathrm{eat}} &= \mathrm{Chv}_{\mathrm{eat}} \cdot \mathrm{Vhv} \\[1ex]
\mathrm{Xhv}_{\mathrm{eat}} &= \mathrm{Ahv}_{\mathrm{eat}} \cdot \mathrm{Mr}_{\mathrm{eat}} \\[1ex]
\mathrm{Mhv}_{\mathrm{eat}} &= \frac{\mathrm{Ahv}_{\mathrm{eat}}}{\mathrm{Vhv}} \cdot \mathrm{Mr}_{\mathrm{eat}} \\[1ex]
\mathrm{Xurine}_{\mathrm{eat}} &= \mathrm{Aurine}_{\mathrm{eat}} \cdot \mathrm{Mr}_{\mathrm{eat}} \\[1ex]
\mathrm{Cve}_{\mathrm{ena\_eat}} &= \mathrm{Cve}_{\mathrm{ena}} + \mathrm{Cve}_{\mathrm{eat}} \\[1ex]
\mathrm{Are}_{\mathrm{eat\_ace}} &= \mathrm{Cre}_{\mathrm{eat\_ace}} \cdot \mathrm{Vre}_{\mathrm{tissue}} \\[1ex]
\mathrm{Xre}_{\mathrm{eat\_ace}} &= \mathrm{Are}_{\mathrm{eat\_ace}} \cdot \mathrm{Mr}_{\mathrm{eat}} \\[1ex]
f_{\mathrm{ace\_occupancy}} &= \frac{\mathrm{Cre}_{\mathrm{eat\_ace}}}{\mathrm{EATACE}_{\mathrm{Bmax}}} \\[1ex]
\mathrm{eat} &= \mathrm{Cve}_{\mathrm{eat}} \\[1ex]
\mathrm{ace}_{\mathrm{inhibition}} &= \frac{\mathrm{ANG1ANG2}_{\mathrm{Emax\_eat}} \cdot \mathrm{eat}}{\mathrm{eat} + \mathrm{ANG1ANG2}_{\mathrm{EC50\_eat}}} \\[1ex]
\mathrm{ace}_{\mathrm{activity}} &= 1 - \mathrm{ace}_{\mathrm{inhibition}} \\[1ex]
\mathrm{KI}_{\mathrm{\_GFR}} &= \mathrm{KI}_{\mathrm{\_f\_renal\_function}} \cdot \mathrm{GFR}_{\mathrm{base}} \\[1ex]
\mathrm{GU}_{\mathrm{\_absorption}} &= \mathrm{GU}_{\mathrm{\_ENAABS\_k}} \cdot \mathrm{Vgu} \cdot \mathrm{Cgu}_{\mathrm{ena}} \\[1ex]
\mathrm{GU}_{\mathrm{\_f\_dissolution}} &= 1 + \mathrm{GU}_{\mathrm{\_fed}} \cdot \mathopen{}\left(\mathrm{GU}_{\mathrm{\_FED\_f\_dissolution}} - 1\right) \\[1ex]
\mathrm{KI}_{\mathrm{\_ENA\_EATEX}} &= v_{\mathrm{KI\_\_ENAEX}} + v_{\mathrm{KI\_\_EATEX}}
\end{aligned}
$$

## Reactions

| Rate | Id | Name | Equation | Modifiers |
| --- | --- | --- | --- | --- |
| $v_{\mathrm{RENSEC}}$ | `RENSEC` | renin secretion (RENSEC) | $\varnothing \longrightarrow \mathrm{ren}$ |  |
| $v_{\mathrm{RENDEG}}$ | `RENDEG` | renin degradation (RENDEG) | $\mathrm{ren} \longrightarrow \varnothing$ |  |
| $v_{\mathrm{ALDSEC}}$ | `ALDSEC` | aldosterone secretion (ALDSEC) | $\varnothing \longrightarrow \mathrm{ald}$ | $\mathrm{ang}_{2}$ |
| $v_{\mathrm{ALDDEG}}$ | `ALDDEG` | aldosterone degradation (ALDDEG) | $\mathrm{ald} \longrightarrow \varnothing$ |  |
| $v_{\mathrm{ANGGEN2ANG1}}$ | `ANGGEN2ANG1` | angiotensinogen to angiotensin I (renin) | $\mathrm{anggen} \longrightarrow \mathrm{ang}_{1}$ | $\mathrm{ren}$ |
| $v_{\mathrm{ANG1ANG2}}$ | `ANG1ANG2` | angiotensin I to angiotensin II (ACE) | $\mathrm{ang}_{1} \longrightarrow \mathrm{ang}_{2}$ | $\mathrm{ace}, \mathrm{eat}$ |
| $v_{\mathrm{ANG1DEG}}$ | `ANG1DEG` | angiotensin I degradation (ANG1DEG) | $\mathrm{ang}_{1} \longrightarrow \varnothing$ |  |
| $v_{\mathrm{ANG2DEG}}$ | `ANG2DEG` | angiotensin II degradation (ANG2DEG) | $\mathrm{ang}_{2} \longrightarrow \varnothing$ |  |
| $v_{\mathrm{transport\_lu\_ena}}$ | `transport_lu_ena` | transport enalapril | $\mathrm{Clu}_{\mathrm{plasma\_ena}} \rightleftharpoons \mathrm{Clu}_{\mathrm{ena}}$ |  |
| $v_{\mathrm{transport\_re\_ena}}$ | `transport_re_ena` | transport enalapril | $\mathrm{Cre}_{\mathrm{plasma\_ena}} \rightleftharpoons \mathrm{Cre}_{\mathrm{ena}}$ |  |
| $v_{\mathrm{iv\_ena}}$ | `iv_ena` | iv enalapril | $\varnothing \longrightarrow \mathrm{Cve}_{\mathrm{ena}}$ |  |
| $v_{\mathrm{Flow\_ar\_ki\_ena}}$ | `Flow_ar_ki_ena` | inflow kidney enalapril | $\mathrm{Car}_{\mathrm{ena}} \longrightarrow \mathrm{Cki}_{\mathrm{plasma\_ena}}$ |  |
| $v_{\mathrm{Flow\_ki\_ve\_ena}}$ | `Flow_ki_ve_ena` | outflow kidney enalapril | $\mathrm{Cki}_{\mathrm{plasma\_ena}} \longrightarrow \mathrm{Cve}_{\mathrm{ena}}$ |  |
| $v_{\mathrm{Flow\_arli\_li\_ena}}$ | `Flow_arli_li_ena` | arterial inflow liver enalapril | $\mathrm{Car}_{\mathrm{ena}} \longrightarrow \mathrm{Cli}_{\mathrm{plasma\_ena}}$ |  |
| $v_{\mathrm{Flow\_arli\_hv\_ena}}$ | `Flow_arli_hv_ena` | flow arterial shunts | $\mathrm{Car}_{\mathrm{ena}} \longrightarrow \mathrm{Chv}_{\mathrm{ena}}$ |  |
| $v_{\mathrm{Flow\_po\_li\_ena}}$ | `Flow_po_li_ena` | outflow po enalapril | $\mathrm{Cpo}_{\mathrm{ena}} \longrightarrow \mathrm{Cli}_{\mathrm{plasma\_ena}}$ |  |
| $v_{\mathrm{Flow\_po\_hv\_ena}}$ | `Flow_po_hv_ena` | flow portal shunts | $\mathrm{Cpo}_{\mathrm{ena}} \longrightarrow \mathrm{Chv}_{\mathrm{ena}}$ |  |
| $v_{\mathrm{Flow\_li\_hv\_ena}}$ | `Flow_li_hv_ena` | outflow liver enalapril | $\mathrm{Cli}_{\mathrm{plasma\_ena}} \longrightarrow \mathrm{Chv}_{\mathrm{ena}}$ |  |
| $v_{\mathrm{Flow\_hv\_ve\_ena}}$ | `Flow_hv_ve_ena` | outflow hepatic vein enalapril | $\mathrm{Chv}_{\mathrm{ena}} \longrightarrow \mathrm{Cve}_{\mathrm{ena}}$ |  |
| $v_{\mathrm{Flow\_ve\_lu\_ena}}$ | `Flow_ve_lu_ena` | inflow lung enalapril | $\mathrm{Cve}_{\mathrm{ena}} \longrightarrow \mathrm{Clu}_{\mathrm{plasma\_ena}}$ |  |
| $v_{\mathrm{Flow\_lu\_ar\_ena}}$ | `Flow_lu_ar_ena` | outflow lung enalapril | $\mathrm{Clu}_{\mathrm{plasma\_ena}} \longrightarrow \mathrm{Car}_{\mathrm{ena}}$ |  |
| $v_{\mathrm{Flow\_ar\_gu\_ena}}$ | `Flow_ar_gu_ena` | inflow gut enalapril | $\mathrm{Car}_{\mathrm{ena}} \longrightarrow \mathrm{Cgu}_{\mathrm{plasma\_ena}}$ |  |
| $v_{\mathrm{Flow\_gu\_po\_ena}}$ | `Flow_gu_po_ena` | outflow gut enalapril | $\mathrm{Cgu}_{\mathrm{plasma\_ena}} \longrightarrow \mathrm{Cpo}_{\mathrm{ena}}$ |  |
| $v_{\mathrm{Flow\_ar\_re\_ena}}$ | `Flow_ar_re_ena` | inflow rest enalapril | $\mathrm{Car}_{\mathrm{ena}} \longrightarrow \mathrm{Cre}_{\mathrm{plasma\_ena}}$ |  |
| $v_{\mathrm{Flow\_re\_ve\_ena}}$ | `Flow_re_ve_ena` | outflow rest enalapril | $\mathrm{Cre}_{\mathrm{plasma\_ena}} \longrightarrow \mathrm{Cve}_{\mathrm{ena}}$ |  |
| $v_{\mathrm{transport\_lu\_eat}}$ | `transport_lu_eat` | transport enalaprilat | $\mathrm{Clu}_{\mathrm{plasma\_eat}} \rightleftharpoons \mathrm{Clu}_{\mathrm{eat}}$ |  |
| $v_{\mathrm{transport\_re\_eat}}$ | `transport_re_eat` | transport enalaprilat | $\mathrm{Cre}_{\mathrm{plasma\_eat}} \rightleftharpoons \mathrm{Cre}_{\mathrm{eat}}$ |  |
| $v_{\mathrm{iv\_eat}}$ | `iv_eat` | iv enalaprilat | $\varnothing \longrightarrow \mathrm{Cve}_{\mathrm{eat}}$ |  |
| $v_{\mathrm{Flow\_ar\_ki\_eat}}$ | `Flow_ar_ki_eat` | inflow kidney enalaprilat | $\mathrm{Car}_{\mathrm{eat}} \longrightarrow \mathrm{Cki}_{\mathrm{plasma\_eat}}$ |  |
| $v_{\mathrm{Flow\_ki\_ve\_eat}}$ | `Flow_ki_ve_eat` | outflow kidney enalaprilat | $\mathrm{Cki}_{\mathrm{plasma\_eat}} \longrightarrow \mathrm{Cve}_{\mathrm{eat}}$ |  |
| $v_{\mathrm{Flow\_arli\_li\_eat}}$ | `Flow_arli_li_eat` | arterial inflow liver enalaprilat | $\mathrm{Car}_{\mathrm{eat}} \longrightarrow \mathrm{Cli}_{\mathrm{plasma\_eat}}$ |  |
| $v_{\mathrm{Flow\_arli\_hv\_eat}}$ | `Flow_arli_hv_eat` | flow arterial shunts | $\mathrm{Car}_{\mathrm{eat}} \longrightarrow \mathrm{Chv}_{\mathrm{eat}}$ |  |
| $v_{\mathrm{Flow\_po\_li\_eat}}$ | `Flow_po_li_eat` | outflow po enalaprilat | $\mathrm{Cpo}_{\mathrm{eat}} \longrightarrow \mathrm{Cli}_{\mathrm{plasma\_eat}}$ |  |
| $v_{\mathrm{Flow\_po\_hv\_eat}}$ | `Flow_po_hv_eat` | flow portal shunts | $\mathrm{Cpo}_{\mathrm{eat}} \longrightarrow \mathrm{Chv}_{\mathrm{eat}}$ |  |
| $v_{\mathrm{Flow\_li\_hv\_eat}}$ | `Flow_li_hv_eat` | outflow liver enalaprilat | $\mathrm{Cli}_{\mathrm{plasma\_eat}} \longrightarrow \mathrm{Chv}_{\mathrm{eat}}$ |  |
| $v_{\mathrm{Flow\_hv\_ve\_eat}}$ | `Flow_hv_ve_eat` | outflow hepatic vein enalaprilat | $\mathrm{Chv}_{\mathrm{eat}} \longrightarrow \mathrm{Cve}_{\mathrm{eat}}$ |  |
| $v_{\mathrm{Flow\_ve\_lu\_eat}}$ | `Flow_ve_lu_eat` | inflow lung enalaprilat | $\mathrm{Cve}_{\mathrm{eat}} \longrightarrow \mathrm{Clu}_{\mathrm{plasma\_eat}}$ |  |
| $v_{\mathrm{Flow\_lu\_ar\_eat}}$ | `Flow_lu_ar_eat` | outflow lung enalaprilat | $\mathrm{Clu}_{\mathrm{plasma\_eat}} \longrightarrow \mathrm{Car}_{\mathrm{eat}}$ |  |
| $v_{\mathrm{Flow\_ar\_gu\_eat}}$ | `Flow_ar_gu_eat` | inflow gut enalaprilat | $\mathrm{Car}_{\mathrm{eat}} \longrightarrow \mathrm{Cgu}_{\mathrm{plasma\_eat}}$ |  |
| $v_{\mathrm{Flow\_gu\_po\_eat}}$ | `Flow_gu_po_eat` | outflow gut enalaprilat | $\mathrm{Cgu}_{\mathrm{plasma\_eat}} \longrightarrow \mathrm{Cpo}_{\mathrm{eat}}$ |  |
| $v_{\mathrm{Flow\_ar\_re\_eat}}$ | `Flow_ar_re_eat` | inflow rest enalaprilat | $\mathrm{Car}_{\mathrm{eat}} \longrightarrow \mathrm{Cre}_{\mathrm{plasma\_eat}}$ |  |
| $v_{\mathrm{Flow\_re\_ve\_eat}}$ | `Flow_re_ve_eat` | outflow rest enalaprilat | $\mathrm{Cre}_{\mathrm{plasma\_eat}} \longrightarrow \mathrm{Cve}_{\mathrm{eat}}$ |  |
| $v_{\mathrm{EATACE}}$ | `EATACE` | binding of enalaprilat to tissue ACE | $\mathrm{Cre}_{\mathrm{eat}} \rightleftharpoons \mathrm{Cre}_{\mathrm{eat\_ace}}$ |  |
| $v_{\mathrm{KI\_\_ENAEX}}$ | `KI__ENAEX` | enalapril renal excretion (ENAEX) | $\mathrm{Cki}_{\mathrm{plasma\_ena}} \longrightarrow \mathrm{Aurine}_{\mathrm{ena}}$ |  |
| $v_{\mathrm{KI\_\_EATEX}}$ | `KI__EATEX` | enalaprilat renal excretion (EATEX) | $\mathrm{Cki}_{\mathrm{plasma\_eat}} \longrightarrow \mathrm{Aurine}_{\mathrm{eat}}$ |  |
| $v_{\mathrm{LI\_\_ENAIM}}$ | `LI__ENAIM` | enalapril import (ENAIM) OATP1B1 | $\mathrm{Cli}_{\mathrm{plasma\_ena}} \rightleftharpoons \mathrm{LI}_{\mathrm{\_ena}}$ |  |
| $v_{\mathrm{LI\_\_ENA2EAT}}$ | `LI__ENA2EAT` | enalapril conversion (ENA2EAT) CES1 | $\mathrm{LI}_{\mathrm{\_ena}} \longrightarrow \mathrm{LI}_{\mathrm{\_eat}}$ |  |
| $v_{\mathrm{LI\_\_EATEX}}$ | `LI__EATEX` | enalaprilat export (EATEX) | $\mathrm{LI}_{\mathrm{\_eat}} \rightleftharpoons \mathrm{Cli}_{\mathrm{plasma\_eat}}$ |  |
| $v_{\mathrm{GU\_\_ENAABS}}$ | `GU__ENAABS` | absorption enalapril | $\mathrm{Cgu}_{\mathrm{ena}} \longrightarrow \mathrm{Cgu}_{\mathrm{plasma\_ena}}$ |  |
| $v_{\mathrm{GU\_\_ENAEXC}}$ | `GU__ENAEXC` | excretion enalapril (feces) | $\mathrm{Cgu}_{\mathrm{ena}} \longrightarrow \mathrm{Afeces}_{\mathrm{ena}}$ |  |
| $v_{\mathrm{GU\_\_dissolution\_ena}}$ | `GU__dissolution_ena` | dissolution enalapril | $\mathrm{GU}_{\mathrm{\_ena\_stomach}} \longrightarrow \mathrm{Cgu}_{\mathrm{ena}}$ |  |

The rates of the reactions are:

$$
\begin{aligned}
v_{\mathrm{RENSEC}} &= \frac{\mathrm{RENSEC}_{\mathrm{k}} \cdot \mathopen{}\left(1 + \mathrm{RENSEC}_{\mathrm{ang2\_E}}\right)}{1 + \frac{\mathrm{RENSEC}_{\mathrm{ang2\_E}} \cdot \mathrm{ang2}_{\mathrm{feedback}}}{\mathrm{ang2}_{\mathrm{ref}}}} \\[1ex]
v_{\mathrm{RENDEG}} &= \mathrm{RENDEG}_{\mathrm{k}} \cdot \mathrm{ren} \\[1ex]
v_{\mathrm{ALDSEC}} &= \mathrm{ALDSEC}_{\mathrm{k}} \cdot \mathopen{}\left(1 - f_{\mathrm{ald\_ang2}} + \frac{f_{\mathrm{ald\_ang2}} \cdot \mathrm{ang}_{2}}{\mathrm{ang2}_{\mathrm{ref}}}\right) \\[1ex]
v_{\mathrm{ALDDEG}} &= \mathrm{ALDDEG}_{\mathrm{k}} \cdot \mathrm{ald} \\[1ex]
v_{\mathrm{ANGGEN2ANG1}} &= \frac{\mathrm{ANGGEN2ANG1}_{\mathrm{k}} \cdot \mathrm{anggen} \cdot \mathrm{ren}}{\mathrm{ren}_{\mathrm{ref}}} \\[1ex]
v_{\mathrm{ANG1ANG2}} &= \frac{\mathrm{ANG1ANG2}_{\mathrm{k}} \cdot \mathrm{ang}_{1} \cdot \mathrm{ace}}{\mathrm{ace}_{\mathrm{ref}}} \cdot \mathrm{ace}_{\mathrm{activity}} \\[1ex]
v_{\mathrm{ANG1DEG}} &= \mathrm{ANG1DEG}_{\mathrm{k}} \cdot \mathrm{ang}_{1} \\[1ex]
v_{\mathrm{ANG2DEG}} &= \mathrm{ANG2DEG}_{\mathrm{k}} \cdot \mathrm{ang}_{2} \\[1ex]
v_{\mathrm{transport\_lu\_ena}} &= \frac{\mathrm{ftissue}_{\mathrm{ena}} \cdot \mathrm{BW}}{\mathrm{BW}_{\mathrm{ref}}} \cdot \mathopen{}\left(\mathrm{Clu}_{\mathrm{plasma\_ena}} \cdot \mathrm{Kp}_{\mathrm{ena}} - \mathrm{Clu}_{\mathrm{ena}}\right) \\[1ex]
v_{\mathrm{transport\_re\_ena}} &= \frac{\mathrm{ftissue}_{\mathrm{ena}} \cdot \mathrm{BW}}{\mathrm{BW}_{\mathrm{ref}}} \cdot \mathopen{}\left(\mathrm{Cre}_{\mathrm{plasma\_ena}} \cdot \mathrm{Kp}_{\mathrm{ena}} - \mathrm{Cre}_{\mathrm{ena}}\right) \\[1ex]
v_{\mathrm{iv\_ena}} &= \frac{\mathrm{Ki}_{\mathrm{ena}} \cdot \mathrm{IVDOSE}_{\mathrm{ena}}}{\mathrm{Mr}_{\mathrm{ena}}} \\[1ex]
v_{\mathrm{Flow\_ar\_ki\_ena}} &= \mathrm{Qki} \cdot \mathrm{Car}_{\mathrm{ena}} \\[1ex]
v_{\mathrm{Flow\_ki\_ve\_ena}} &= \mathrm{Qki} \cdot \mathrm{Cki}_{\mathrm{plasma\_ena}} \\[1ex]
v_{\mathrm{Flow\_arli\_li\_ena}} &= \mathopen{}\left(1 - f_{\mathrm{shunts}}\right) \cdot \mathrm{Qha} \cdot \mathrm{Car}_{\mathrm{ena}} \\[1ex]
v_{\mathrm{Flow\_arli\_hv\_ena}} &= f_{\mathrm{shunts}} \cdot \mathrm{Qha} \cdot \mathrm{Car}_{\mathrm{ena}} \\[1ex]
v_{\mathrm{Flow\_po\_li\_ena}} &= \mathopen{}\left(1 - f_{\mathrm{shunts}}\right) \cdot \mathrm{Qpo} \cdot \mathrm{Cpo}_{\mathrm{ena}} \\[1ex]
v_{\mathrm{Flow\_po\_hv\_ena}} &= f_{\mathrm{shunts}} \cdot \mathrm{Qpo} \cdot \mathrm{Cpo}_{\mathrm{ena}} \\[1ex]
v_{\mathrm{Flow\_li\_hv\_ena}} &= \mathopen{}\left(1 - f_{\mathrm{shunts}}\right) \cdot \mathopen{}\left(\mathrm{Qpo} + \mathrm{Qha}\right) \cdot \mathrm{Cli}_{\mathrm{plasma\_ena}} \\[1ex]
v_{\mathrm{Flow\_hv\_ve\_ena}} &= \mathrm{Qh} \cdot \mathrm{Chv}_{\mathrm{ena}} \\[1ex]
v_{\mathrm{Flow\_ve\_lu\_ena}} &= \mathrm{Qlu} \cdot \mathrm{Cve}_{\mathrm{ena}} \\[1ex]
v_{\mathrm{Flow\_lu\_ar\_ena}} &= \mathrm{Qlu} \cdot \mathrm{Clu}_{\mathrm{plasma\_ena}} \\[1ex]
v_{\mathrm{Flow\_ar\_gu\_ena}} &= \mathrm{Qgu} \cdot \mathrm{Car}_{\mathrm{ena}} \\[1ex]
v_{\mathrm{Flow\_gu\_po\_ena}} &= \mathrm{Qgu} \cdot \mathrm{Cgu}_{\mathrm{plasma\_ena}} \\[1ex]
v_{\mathrm{Flow\_ar\_re\_ena}} &= \mathrm{Qre} \cdot \mathrm{Car}_{\mathrm{ena}} \\[1ex]
v_{\mathrm{Flow\_re\_ve\_ena}} &= \mathrm{Qre} \cdot \mathrm{Cre}_{\mathrm{plasma\_ena}} \\[1ex]
v_{\mathrm{transport\_lu\_eat}} &= \frac{\mathrm{ftissue}_{\mathrm{eat}} \cdot \mathrm{BW}}{\mathrm{BW}_{\mathrm{ref}}} \cdot \mathopen{}\left(\mathrm{Clu}_{\mathrm{plasma\_eat}} \cdot \mathrm{Kp}_{\mathrm{eat}} - \mathrm{Clu}_{\mathrm{eat}}\right) \\[1ex]
v_{\mathrm{transport\_re\_eat}} &= \frac{\mathrm{ftissue}_{\mathrm{eat}} \cdot \mathrm{BW}}{\mathrm{BW}_{\mathrm{ref}}} \cdot \mathopen{}\left(\mathrm{Cre}_{\mathrm{plasma\_eat}} \cdot \mathrm{Kp}_{\mathrm{eat}} - \mathrm{Cre}_{\mathrm{eat}}\right) \\[1ex]
v_{\mathrm{iv\_eat}} &= \frac{\mathrm{Ki}_{\mathrm{eat}} \cdot \mathrm{IVDOSE}_{\mathrm{eat}}}{\mathrm{Mr}_{\mathrm{eat}}} \\[1ex]
v_{\mathrm{Flow\_ar\_ki\_eat}} &= \mathrm{Qki} \cdot \mathrm{Car}_{\mathrm{eat}} \\[1ex]
v_{\mathrm{Flow\_ki\_ve\_eat}} &= \mathrm{Qki} \cdot \mathrm{Cki}_{\mathrm{plasma\_eat}} \\[1ex]
v_{\mathrm{Flow\_arli\_li\_eat}} &= \mathopen{}\left(1 - f_{\mathrm{shunts}}\right) \cdot \mathrm{Qha} \cdot \mathrm{Car}_{\mathrm{eat}} \\[1ex]
v_{\mathrm{Flow\_arli\_hv\_eat}} &= f_{\mathrm{shunts}} \cdot \mathrm{Qha} \cdot \mathrm{Car}_{\mathrm{eat}} \\[1ex]
v_{\mathrm{Flow\_po\_li\_eat}} &= \mathopen{}\left(1 - f_{\mathrm{shunts}}\right) \cdot \mathrm{Qpo} \cdot \mathrm{Cpo}_{\mathrm{eat}} \\[1ex]
v_{\mathrm{Flow\_po\_hv\_eat}} &= f_{\mathrm{shunts}} \cdot \mathrm{Qpo} \cdot \mathrm{Cpo}_{\mathrm{eat}} \\[1ex]
v_{\mathrm{Flow\_li\_hv\_eat}} &= \mathopen{}\left(1 - f_{\mathrm{shunts}}\right) \cdot \mathopen{}\left(\mathrm{Qpo} + \mathrm{Qha}\right) \cdot \mathrm{Cli}_{\mathrm{plasma\_eat}} \\[1ex]
v_{\mathrm{Flow\_hv\_ve\_eat}} &= \mathrm{Qh} \cdot \mathrm{Chv}_{\mathrm{eat}} \\[1ex]
v_{\mathrm{Flow\_ve\_lu\_eat}} &= \mathrm{Qlu} \cdot \mathrm{Cve}_{\mathrm{eat}} \\[1ex]
v_{\mathrm{Flow\_lu\_ar\_eat}} &= \mathrm{Qlu} \cdot \mathrm{Clu}_{\mathrm{plasma\_eat}} \\[1ex]
v_{\mathrm{Flow\_ar\_gu\_eat}} &= \mathrm{Qgu} \cdot \mathrm{Car}_{\mathrm{eat}} \\[1ex]
v_{\mathrm{Flow\_gu\_po\_eat}} &= \mathrm{Qgu} \cdot \mathrm{Cgu}_{\mathrm{plasma\_eat}} \\[1ex]
v_{\mathrm{Flow\_ar\_re\_eat}} &= \mathrm{Qre} \cdot \mathrm{Car}_{\mathrm{eat}} \\[1ex]
v_{\mathrm{Flow\_re\_ve\_eat}} &= \mathrm{Qre} \cdot \mathrm{Cre}_{\mathrm{plasma\_eat}} \\[1ex]
v_{\mathrm{EATACE}} &= \mathrm{EATACE}_{\mathrm{koff}} \cdot \mathrm{Vre}_{\mathrm{tissue}} \cdot \mathopen{}\left(\frac{\mathrm{Cre}_{\mathrm{eat}} \cdot \mathopen{}\left(\mathrm{EATACE}_{\mathrm{Bmax}} - \mathrm{Cre}_{\mathrm{eat\_ace}}\right)}{\mathrm{EATACE}_{\mathrm{Kd}}} - \mathrm{Cre}_{\mathrm{eat\_ace}}\right) \\[1ex]
v_{\mathrm{KI\_\_ENAEX}} &= \mathrm{KI}_{\mathrm{\_GFR}} \cdot 0.001 \cdot \mathrm{fu}_{\mathrm{ena}} \cdot \mathrm{KI}_{\mathrm{\_ENAEX\_f}} \cdot \mathrm{Cki}_{\mathrm{plasma\_ena}} \\[1ex]
v_{\mathrm{KI\_\_EATEX}} &= \mathrm{KI}_{\mathrm{\_GFR}} \cdot 0.001 \cdot \mathrm{fu}_{\mathrm{eat}} \cdot \mathrm{KI}_{\mathrm{\_EATEX\_f}} \cdot \mathrm{Cki}_{\mathrm{plasma\_eat}} \\[1ex]
v_{\mathrm{LI\_\_ENAIM}} &= \frac{\frac{\mathrm{LI}_{\mathrm{\_ENAIM\_Vmax}}}{\mathrm{LI}_{\mathrm{\_ENAIM\_Km\_ena}}} \cdot \mathrm{Vli}_{\mathrm{tissue}} \cdot \mathopen{}\left(\mathrm{Cli}_{\mathrm{plasma\_ena}} - \mathrm{LI}_{\mathrm{\_ena}}\right)}{1 + \frac{\mathrm{Cli}_{\mathrm{plasma\_ena}}}{\mathrm{LI}_{\mathrm{\_ENAIM\_Km\_ena}}} + \frac{\mathrm{LI}_{\mathrm{\_ena}}}{\mathrm{LI}_{\mathrm{\_ENAIM\_Km\_ena}}}} \\[1ex]
v_{\mathrm{LI\_\_ENA2EAT}} &= \frac{\mathrm{LI}_{\mathrm{\_f\_ces1}} \cdot \mathrm{LI}_{\mathrm{\_ENA2EAT\_Vmax}} \cdot \mathrm{Vli}_{\mathrm{tissue}} \cdot \mathrm{LI}_{\mathrm{\_ena}}}{\mathrm{LI}_{\mathrm{\_ena}} + \mathrm{LI}_{\mathrm{\_ENA2EAT\_Km\_ena}} + \frac{\mathrm{LI}_{\mathrm{\_ena}}^{2}}{\mathrm{LI}_{\mathrm{\_ENA2EAT\_Ki\_ena}}}} \\[1ex]
v_{\mathrm{LI\_\_EATEX}} &= \frac{\frac{\mathrm{LI}_{\mathrm{\_EATEX\_Vmax}}}{\mathrm{LI}_{\mathrm{\_EATEX\_Km\_eat}}} \cdot \mathrm{Vli}_{\mathrm{tissue}} \cdot \mathopen{}\left(\mathrm{LI}_{\mathrm{\_eat}} - \mathrm{Cli}_{\mathrm{plasma\_eat}}\right)}{1 + \frac{\mathrm{Cli}_{\mathrm{plasma\_eat}}}{\mathrm{LI}_{\mathrm{\_EATEX\_Km\_eat}}} + \frac{\mathrm{LI}_{\mathrm{\_eat}}}{\mathrm{LI}_{\mathrm{\_EATEX\_Km\_eat}}}} \\[1ex]
v_{\mathrm{GU\_\_ENAABS}} &= \mathrm{GU}_{\mathrm{\_F\_ena\_abs}} \cdot \mathrm{GU}_{\mathrm{\_absorption}} \\[1ex]
v_{\mathrm{GU\_\_ENAEXC}} &= \mathopen{}\left(1 - \mathrm{GU}_{\mathrm{\_F\_ena\_abs}}\right) \cdot \mathrm{GU}_{\mathrm{\_absorption}} \\[1ex]
v_{\mathrm{GU\_\_dissolution\_ena}} &= \frac{\frac{\mathrm{GU}_{\mathrm{\_f\_dissolution}} \cdot \mathrm{Ka}_{\mathrm{dis\_ena}}}{60} \cdot \mathrm{PODOSE}_{\mathrm{ena}}}{\mathrm{Mr}_{\mathrm{ena}}}
\end{aligned}
$$

## ODE system

The states change in time with the rates of the reactions and the rate rules:

$$
\begin{aligned}
\frac{\mathrm{d} \,\mathrm{ald}}{\mathrm{d} t} &= \frac{v_{\mathrm{ALDSEC}} - v_{\mathrm{ALDDEG}}}{\mathrm{Vplasma}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{ren}}{\mathrm{d} t} &= \frac{v_{\mathrm{RENSEC}} - v_{\mathrm{RENDEG}}}{\mathrm{Vplasma}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{ang}_{1}}{\mathrm{d} t} &= \frac{v_{\mathrm{ANGGEN2ANG1}} - v_{\mathrm{ANG1ANG2}} - v_{\mathrm{ANG1DEG}}}{\mathrm{Vplasma}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{ang}_{2}}{\mathrm{d} t} &= \frac{v_{\mathrm{ANG1ANG2}} - v_{\mathrm{ANG2DEG}}}{\mathrm{Vplasma}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Cki}_{\mathrm{plasma\_ena}}}{\mathrm{d} t} &= \frac{v_{\mathrm{Flow\_ar\_ki\_ena}} - v_{\mathrm{Flow\_ki\_ve\_ena}} - v_{\mathrm{KI\_\_ENAEX}}}{\mathrm{Vki}_{\mathrm{plasma}}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Cli}_{\mathrm{plasma\_ena}}}{\mathrm{d} t} &= \frac{v_{\mathrm{Flow\_arli\_li\_ena}} + v_{\mathrm{Flow\_po\_li\_ena}} - v_{\mathrm{Flow\_li\_hv\_ena}} - v_{\mathrm{LI\_\_ENAIM}}}{\mathrm{Vli}_{\mathrm{plasma}}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Clu}_{\mathrm{plasma\_ena}}}{\mathrm{d} t} &= \frac{-v_{\mathrm{transport\_lu\_ena}} + v_{\mathrm{Flow\_ve\_lu\_ena}} - v_{\mathrm{Flow\_lu\_ar\_ena}}}{\mathrm{Vlu}_{\mathrm{plasma}}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Cgu}_{\mathrm{plasma\_ena}}}{\mathrm{d} t} &= \frac{v_{\mathrm{Flow\_ar\_gu\_ena}} - v_{\mathrm{Flow\_gu\_po\_ena}} + v_{\mathrm{GU\_\_ENAABS}}}{\mathrm{Vgu}_{\mathrm{plasma}}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Cre}_{\mathrm{plasma\_ena}}}{\mathrm{d} t} &= \frac{-v_{\mathrm{transport\_re\_ena}} + v_{\mathrm{Flow\_ar\_re\_ena}} - v_{\mathrm{Flow\_re\_ve\_ena}}}{\mathrm{Vre}_{\mathrm{plasma}}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Car}_{\mathrm{ena}}}{\mathrm{d} t} &= \frac{1}{\mathrm{Var}} \Bigl( -v_{\mathrm{Flow\_ar\_ki\_ena}} - v_{\mathrm{Flow\_arli\_li\_ena}} - v_{\mathrm{Flow\_arli\_hv\_ena}} + v_{\mathrm{Flow\_lu\_ar\_ena}} \\
&\quad {} - v_{\mathrm{Flow\_ar\_gu\_ena}} - v_{\mathrm{Flow\_ar\_re\_ena}} \Bigr) \\[1ex]
\frac{\mathrm{d} \,\mathrm{Cve}_{\mathrm{ena}}}{\mathrm{d} t} &= \frac{1}{\mathrm{Vve}} \Bigl( v_{\mathrm{iv\_ena}} + v_{\mathrm{Flow\_ki\_ve\_ena}} + v_{\mathrm{Flow\_hv\_ve\_ena}} - v_{\mathrm{Flow\_ve\_lu\_ena}} \\
&\quad {} + v_{\mathrm{Flow\_re\_ve\_ena}} \Bigr) \\[1ex]
\frac{\mathrm{d} \,\mathrm{Cpo}_{\mathrm{ena}}}{\mathrm{d} t} &= \frac{-v_{\mathrm{Flow\_po\_li\_ena}} - v_{\mathrm{Flow\_po\_hv\_ena}} + v_{\mathrm{Flow\_gu\_po\_ena}}}{\mathrm{Vpo}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Chv}_{\mathrm{ena}}}{\mathrm{d} t} &= \frac{v_{\mathrm{Flow\_arli\_hv\_ena}} + v_{\mathrm{Flow\_po\_hv\_ena}} + v_{\mathrm{Flow\_li\_hv\_ena}} - v_{\mathrm{Flow\_hv\_ve\_ena}}}{\mathrm{Vhv}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Clu}_{\mathrm{ena}}}{\mathrm{d} t} &= \frac{v_{\mathrm{transport\_lu\_ena}}}{\mathrm{Vlu}_{\mathrm{tissue}}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Cre}_{\mathrm{ena}}}{\mathrm{d} t} &= \frac{v_{\mathrm{transport\_re\_ena}}}{\mathrm{Vre}_{\mathrm{tissue}}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Aurine}_{\mathrm{ena}}}{\mathrm{d} t} &= v_{\mathrm{KI\_\_ENAEX}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Afeces}_{\mathrm{ena}}}{\mathrm{d} t} &= v_{\mathrm{GU\_\_ENAEXC}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Cgu}_{\mathrm{ena}}}{\mathrm{d} t} &= \frac{-v_{\mathrm{GU\_\_ENAABS}} - v_{\mathrm{GU\_\_ENAEXC}} + v_{\mathrm{GU\_\_dissolution\_ena}}}{\mathrm{Vgu}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Cki}_{\mathrm{plasma\_eat}}}{\mathrm{d} t} &= \frac{v_{\mathrm{Flow\_ar\_ki\_eat}} - v_{\mathrm{Flow\_ki\_ve\_eat}} - v_{\mathrm{KI\_\_EATEX}}}{\mathrm{Vki}_{\mathrm{plasma}}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Cli}_{\mathrm{plasma\_eat}}}{\mathrm{d} t} &= \frac{v_{\mathrm{Flow\_arli\_li\_eat}} + v_{\mathrm{Flow\_po\_li\_eat}} - v_{\mathrm{Flow\_li\_hv\_eat}} + v_{\mathrm{LI\_\_EATEX}}}{\mathrm{Vli}_{\mathrm{plasma}}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Clu}_{\mathrm{plasma\_eat}}}{\mathrm{d} t} &= \frac{-v_{\mathrm{transport\_lu\_eat}} + v_{\mathrm{Flow\_ve\_lu\_eat}} - v_{\mathrm{Flow\_lu\_ar\_eat}}}{\mathrm{Vlu}_{\mathrm{plasma}}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Cgu}_{\mathrm{plasma\_eat}}}{\mathrm{d} t} &= \frac{v_{\mathrm{Flow\_ar\_gu\_eat}} - v_{\mathrm{Flow\_gu\_po\_eat}}}{\mathrm{Vgu}_{\mathrm{plasma}}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Cre}_{\mathrm{plasma\_eat}}}{\mathrm{d} t} &= \frac{-v_{\mathrm{transport\_re\_eat}} + v_{\mathrm{Flow\_ar\_re\_eat}} - v_{\mathrm{Flow\_re\_ve\_eat}}}{\mathrm{Vre}_{\mathrm{plasma}}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Car}_{\mathrm{eat}}}{\mathrm{d} t} &= \frac{1}{\mathrm{Var}} \Bigl( -v_{\mathrm{Flow\_ar\_ki\_eat}} - v_{\mathrm{Flow\_arli\_li\_eat}} - v_{\mathrm{Flow\_arli\_hv\_eat}} + v_{\mathrm{Flow\_lu\_ar\_eat}} \\
&\quad {} - v_{\mathrm{Flow\_ar\_gu\_eat}} - v_{\mathrm{Flow\_ar\_re\_eat}} \Bigr) \\[1ex]
\frac{\mathrm{d} \,\mathrm{Cve}_{\mathrm{eat}}}{\mathrm{d} t} &= \frac{1}{\mathrm{Vve}} \Bigl( v_{\mathrm{iv\_eat}} + v_{\mathrm{Flow\_ki\_ve\_eat}} + v_{\mathrm{Flow\_hv\_ve\_eat}} - v_{\mathrm{Flow\_ve\_lu\_eat}} \\
&\quad {} + v_{\mathrm{Flow\_re\_ve\_eat}} \Bigr) \\[1ex]
\frac{\mathrm{d} \,\mathrm{Cpo}_{\mathrm{eat}}}{\mathrm{d} t} &= \frac{-v_{\mathrm{Flow\_po\_li\_eat}} - v_{\mathrm{Flow\_po\_hv\_eat}} + v_{\mathrm{Flow\_gu\_po\_eat}}}{\mathrm{Vpo}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Chv}_{\mathrm{eat}}}{\mathrm{d} t} &= \frac{v_{\mathrm{Flow\_arli\_hv\_eat}} + v_{\mathrm{Flow\_po\_hv\_eat}} + v_{\mathrm{Flow\_li\_hv\_eat}} - v_{\mathrm{Flow\_hv\_ve\_eat}}}{\mathrm{Vhv}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Clu}_{\mathrm{eat}}}{\mathrm{d} t} &= \frac{v_{\mathrm{transport\_lu\_eat}}}{\mathrm{Vlu}_{\mathrm{tissue}}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Cre}_{\mathrm{eat}}}{\mathrm{d} t} &= \frac{v_{\mathrm{transport\_re\_eat}} - v_{\mathrm{EATACE}}}{\mathrm{Vre}_{\mathrm{tissue}}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Aurine}_{\mathrm{eat}}}{\mathrm{d} t} &= v_{\mathrm{KI\_\_EATEX}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{Cre}_{\mathrm{eat\_ace}}}{\mathrm{d} t} &= \frac{v_{\mathrm{EATACE}}}{\mathrm{Vre}_{\mathrm{tissue}}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{LI}_{\mathrm{\_ena}}}{\mathrm{d} t} &= \frac{v_{\mathrm{LI\_\_ENAIM}} - v_{\mathrm{LI\_\_ENA2EAT}}}{\mathrm{Vli}_{\mathrm{tissue}}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{LI}_{\mathrm{\_eat}}}{\mathrm{d} t} &= \frac{v_{\mathrm{LI\_\_ENA2EAT}} - v_{\mathrm{LI\_\_EATEX}}}{\mathrm{Vli}_{\mathrm{tissue}}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{ang2}_{\mathrm{feedback}}}{\mathrm{d} t} &= \frac{\ln\mathopen{}\left(2\right)}{\mathrm{RENSEC}_{\mathrm{ang2\_t}}} \cdot \mathopen{}\left(\mathrm{ang}_{2} - \mathrm{ang2}_{\mathrm{feedback}}\right) \qquad \text{(rate rule)} \\[1ex]
\frac{\mathrm{d} \,\mathrm{PODOSE}_{\mathrm{ena}}}{\mathrm{d} t} &= -v_{\mathrm{GU\_\_dissolution\_ena}} \cdot \mathrm{Mr}_{\mathrm{ena}} \qquad \text{(rate rule)} \\[1ex]
\frac{\mathrm{d} \,\mathrm{IVDOSE}_{\mathrm{ena}}}{\mathrm{d} t} &= -v_{\mathrm{iv\_ena}} \cdot \mathrm{Mr}_{\mathrm{ena}} + \mathrm{Ri}_{\mathrm{ena}} \qquad \text{(rate rule)} \\[1ex]
\frac{\mathrm{d} \,\mathrm{cum}_{\mathrm{dose\_ena}}}{\mathrm{d} t} &= \mathrm{Ri}_{\mathrm{ena}} \qquad \text{(rate rule)} \\[1ex]
\frac{\mathrm{d} \,\mathrm{IVDOSE}_{\mathrm{eat}}}{\mathrm{d} t} &= -v_{\mathrm{iv\_eat}} \cdot \mathrm{Mr}_{\mathrm{eat}} + \mathrm{Ri}_{\mathrm{eat}} \qquad \text{(rate rule)} \\[1ex]
\frac{\mathrm{d} \,\mathrm{cum}_{\mathrm{dose\_eat}}}{\mathrm{d} t} &= \mathrm{Ri}_{\mathrm{eat}} \qquad \text{(rate rule)}
\end{aligned}
$$
