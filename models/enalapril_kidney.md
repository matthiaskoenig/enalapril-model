# Model for renal enalapril and enalaprilat excretion.

Model `enalapril_kidney`, SBML Level 3 Version 2, read from enalapril\_kidney.xml, written by sbmlode 0.3.0.

Model for the renal excretion of enalapril and enalaprilat.

Enalapril and enalaprilat are excreted unchanged in the urine (filtration and tubular secretion), no other metabolites are found. After 10 mg of enalapril maleate about 25 % of the dose are recovered as enalapril and 35 % as enalaprilat {Ishizaki1988, Ohnishi1989}, 45 % after 20 mg (3.41 mg enalapril, 3.78 mg enalaprilat) {Burckhardt2015}.

The renal clearances are given relative to the filtration of the unbound fraction, GFR \* fu, and scale with the renal function: GFR = f\_renal\_function \* GFR\_base, the healthy GFR GFR\_base (101 ml/min at 75 kg) is replaced by the body model.

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
| $\mathrm{Vext}$ | `Vext` | plasma | $1.5$ | l | ✓ |
| $\mathrm{Vki}$ | `Vki` | kidney | $0.3$ | l | ✓ |
| $\mathrm{Vurine}$ | `Vurine` | urine | $1$ | l | ✓ |

## Species

| Symbol | Id | Name | Compartment | Value | Unit | Properties |
| --- | --- | --- | --- | --- | --- | --- |
| $\mathrm{ena}_{\mathrm{ext}}$ | `ena_ext` | enalapril (plasma) | $\mathrm{Vext}$ | $0$ | mmol/l | concentration |
| $\mathrm{eat}_{\mathrm{ext}}$ | `eat_ext` | enalaprilat (plasma) | $\mathrm{Vext}$ | $0$ | mmol/l | concentration |
| $\mathrm{ena}_{\mathrm{urine}}$ | `ena_urine` | enalapril (urine) | $\mathrm{Vurine}$ |  | mmol | amount |
| $\mathrm{eat}_{\mathrm{urine}}$ | `eat_urine` | enalaprilat (urine) | $\mathrm{Vurine}$ |  | mmol | amount |

## Parameters

| Symbol | Id | Name | Value | Unit | Constant |
| --- | --- | --- | --- | --- | :---: |
| $f_{\mathrm{renal\_function}}$ | `f_renal_function` | renal function | $1$ | \- | ✓ |
| $\mathrm{GFR}_{\mathrm{base}}$ | `GFR_base` | glomerular filtration rate (healthy) | $101$ | ml/min | ✓ |
| $\mathrm{fu}_{\mathrm{ena}}$ | `fu_ena` | fraction unbound in plasma enalapril | $1$ | \- | ✓ |
| $\mathrm{fu}_{\mathrm{eat}}$ | `fu_eat` | fraction unbound in plasma enalaprilat | $0.62$ | \- | ✓ |
| $\mathrm{ENAEX}_{\mathrm{f}}$ | `ENAEX_f` | renal clearance of unbound enalapril relative to the GFR | $2.87792398538051$ | \- | ✓ |
| $\mathrm{EATEX}_{\mathrm{f}}$ | `EATEX_f` | renal clearance of unbound enalaprilat relative to the GFR | $2.56410960551508$ | \- | ✓ |
| $\mathrm{GFR}$ | `GFR` | glomerular filtration rate |  | ml/min |  |
| $\mathrm{ENA}_{\mathrm{EATEX}}$ | `ENA_EATEX` | renal excretion of enalapril and enalaprilat |  | mmol/min |  |

## Initial assignments and assignment rules

The initial assignments set the values at $t = 0$:

$$
\begin{aligned}
\mathrm{ena}_{\mathrm{urine}} &= 0 \cdot \mathrm{Vurine} \\[1ex]
\mathrm{eat}_{\mathrm{urine}} &= 0 \cdot \mathrm{Vurine}
\end{aligned}
$$

The assignment rules hold at every time $t$:

$$
\begin{aligned}
\mathrm{GFR} &= f_{\mathrm{renal\_function}} \cdot \mathrm{GFR}_{\mathrm{base}} \\[1ex]
\mathrm{ENA}_{\mathrm{EATEX}} &= v_{\mathrm{ENAEX}} + v_{\mathrm{EATEX}}
\end{aligned}
$$

## Reactions

| Rate | Id | Name | Equation |
| --- | --- | --- | --- |
| $v_{\mathrm{ENAEX}}$ | `ENAEX` | enalapril renal excretion (ENAEX) | $\mathrm{ena}_{\mathrm{ext}} \longrightarrow \mathrm{ena}_{\mathrm{urine}}$ |
| $v_{\mathrm{EATEX}}$ | `EATEX` | enalaprilat renal excretion (EATEX) | $\mathrm{eat}_{\mathrm{ext}} \longrightarrow \mathrm{eat}_{\mathrm{urine}}$ |

The rates of the reactions are:

$$
\begin{aligned}
v_{\mathrm{ENAEX}} &= \mathrm{GFR} \cdot 0.001 \cdot \mathrm{fu}_{\mathrm{ena}} \cdot \mathrm{ENAEX}_{\mathrm{f}} \cdot \mathrm{ena}_{\mathrm{ext}} \\[1ex]
v_{\mathrm{EATEX}} &= \mathrm{GFR} \cdot 0.001 \cdot \mathrm{fu}_{\mathrm{eat}} \cdot \mathrm{EATEX}_{\mathrm{f}} \cdot \mathrm{eat}_{\mathrm{ext}}
\end{aligned}
$$

## ODE system

The states change in time with the rates of the reactions:

$$
\begin{aligned}
\frac{\mathrm{d} \,\mathrm{ena}_{\mathrm{ext}}}{\mathrm{d} t} &= \frac{-v_{\mathrm{ENAEX}}}{\mathrm{Vext}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{eat}_{\mathrm{ext}}}{\mathrm{d} t} &= \frac{-v_{\mathrm{EATEX}}}{\mathrm{Vext}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{ena}_{\mathrm{urine}}}{\mathrm{d} t} &= v_{\mathrm{ENAEX}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{eat}_{\mathrm{urine}}}{\mathrm{d} t} &= v_{\mathrm{EATEX}}
\end{aligned}
$$
