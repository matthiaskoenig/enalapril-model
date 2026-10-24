# Model for RAAS system of blood pressure regulation.

Model `enalapril_raas`, SBML Level 3 Version 2, read from enalapril\_raas.xml, written by sbmlode 0.3.0.

Model for RAAS system of blood pressure regulation. Enalaprilat is an inhibitor of ACE, so it inhibits conversion of angiotensin I to angiotensin II.

components: renin, angiotensinogen, angiotensin I, angiotensin II, ACE, aldosterone, systolic and diastolic blood pressure

angiotensin II raises the blood pressure (vasoconstriction) and the aldosterone secretion

negative feedback loop: angiotensin II inhibits the secretion of renin

angiotensin I is converted by ACE or cleared by other peptidases

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

## Species

| Symbol | Id | Name | Compartment | Value | Unit | Properties |
| --- | --- | --- | --- | --- | --- | --- |
| $\mathrm{ald}$ | `ald` | aldosterone | $\mathrm{Vplasma}$ | $2.5 \times 10^{-7}$ | mmol/l | concentration |
| $\mathrm{ren}$ | `ren` | renin | $\mathrm{Vplasma}$ | $10^{-9}$ | mmol/l | concentration |
| $\mathrm{anggen}$ | `anggen` | angiotensinogen | $\mathrm{Vplasma}$ | $10^{-8}$ | mmol/l | concentration, boundary |
| $\mathrm{ang}_{1}$ | `ang1` | angiotensin I | $\mathrm{Vplasma}$ | $10^{-8}$ | mmol/l | concentration |
| $\mathrm{ang}_{2}$ | `ang2` | angiotensin II | $\mathrm{Vplasma}$ | $8 \times 10^{-9}$ | mmol/l | concentration |
| $\mathrm{ace}$ | `ace` | ACE | $\mathrm{Vplasma}$ | $10^{-9}$ | mmol/l | concentration |
| $\mathrm{eat}$ | `eat` | enalaprilat | $\mathrm{Vplasma}$ | $0$ | mmol/l | concentration |

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
| $\mathrm{MAP}_{\mathrm{ref}}$ | `MAP_ref` |  |  | (133.322 N)/m<sup>2</sup> |  |

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
\mathrm{ace}_{\mathrm{inhibition}} &= \frac{\mathrm{ANG1ANG2}_{\mathrm{Emax\_eat}} \cdot \mathrm{eat}}{\mathrm{eat} + \mathrm{ANG1ANG2}_{\mathrm{EC50\_eat}}} \\[1ex]
\mathrm{ace}_{\mathrm{activity}} &= 1 - \mathrm{ace}_{\mathrm{inhibition}} \\[1ex]
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
\mathrm{MAP}_{\mathrm{change\_relative}} &= \frac{\mathrm{MAP}_{\mathrm{change}}}{\mathrm{MAP}_{\mathrm{ref}}}
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
v_{\mathrm{ANG2DEG}} &= \mathrm{ANG2DEG}_{\mathrm{k}} \cdot \mathrm{ang}_{2}
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
\frac{\mathrm{d} \,\mathrm{ang2}_{\mathrm{feedback}}}{\mathrm{d} t} &= \frac{\ln\mathopen{}\left(2\right)}{\mathrm{RENSEC}_{\mathrm{ang2\_t}}} \cdot \mathopen{}\left(\mathrm{ang}_{2} - \mathrm{ang2}_{\mathrm{feedback}}\right) \qquad \text{(rate rule)}
\end{aligned}
$$
