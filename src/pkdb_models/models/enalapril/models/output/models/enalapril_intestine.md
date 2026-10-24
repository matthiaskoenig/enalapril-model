# Model for enalapril absorption in the small intestine

Model `enalapril_intestine`, SBML Level 3 Version 2, read from enalapril\_intestine.xml, written by sbmlode 0.3.0.

Model for enalapril absorption

The oral dose of enalapril (the maleate salt, dosed as enalapril) dissolves and passes the stomach (Ka\_dis\_ena, replaced by the body model) into the lumen of the small intestine, from where the fraction F\_ena\_abs is absorbed into the portal plasma and the rest is excreted in the feces.

56 +- 6 % of an oral dose of 14C-enalapril are recovered in the urine, 39 +- 5 % in the feces, i.e. about 60 % are absorbed {Ulm1982, Ball1987}

the bioavailability of enalaprilat after enalapril is about 40 %, the absorption of enalapril about 60-64 % {Hockings1986, Dickstein1987}

food (a high fat breakfast) slows the absorption: Cmax of enalapril falls to 0.54 at an AUC of 0.86 {Moffett2014}, the exposure to enalaprilat and its urinary recovery do not change after a tablet with a meal {Swanson1984}; the fed state slows the dissolution and the gastric emptying (fed, FED\_f\_dissolution)

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
| $\mathrm{Vext}$ | `Vext` | plasma | $1$ | l | ✓ |
| $\mathrm{Vgu}$ | `Vgu` | intestine | $1.2825$ | l | ✓ |
| $\mathrm{Vlumen}$ | `Vlumen` | intestinal lumen (inner part of intestine) | $1.15425$ | l |  |
| $\mathrm{Vfeces}$ | `Vfeces` | feces | $1$ | l | ✓ |
| $\mathrm{Vstomach}$ | `Vstomach` | stomach | $1$ | l | ✓ |

## Species

| Symbol | Id | Name | Compartment | Value | Unit | Properties |
| --- | --- | --- | --- | --- | --- | --- |
| $\mathrm{ena}_{\mathrm{stomach}}$ | `ena_stomach` | enalapril (stomach) | $\mathrm{Vstomach}$ |  | mmol | amount, boundary |
| $\mathrm{ena}_{\mathrm{lumen}}$ | `ena_lumen` | enalapril (intestinal lumen) | $\mathrm{Vlumen}$ | $0$ | mmol/l | concentration |
| $\mathrm{ena}_{\mathrm{ext}}$ | `ena_ext` | enalapril (plasma) | $\mathrm{Vext}$ | $0$ | mmol/l | concentration |
| $\mathrm{ena}_{\mathrm{feces}}$ | `ena_feces` | enalapril (feces) | $\mathrm{Vfeces}$ |  | mmol | amount |

## Parameters

| Symbol | Id | Name | Value | Unit | Constant |
| --- | --- | --- | --- | --- | :---: |
| $F_{\mathrm{ena\_abs}}$ | `F_ena_abs` | fraction absorbed enalapril | $0.577261573734921$ | \- | ✓ |
| $\mathrm{ENAABS}_{\mathrm{k}}$ | `ENAABS_k` | rate of enalapril absorption | $0.02288941081702$ | 1/min | ✓ |
| $\mathrm{fed}$ | `fed` | fed state (0 fasted, 1 fed) | $0$ | \- | ✓ |
| $\mathrm{FED}_{\mathrm{f\_dissolution}}$ | `FED_f_dissolution` | fed effect on the dissolution and gastric emptying | $0.42677125646477$ | \- | ✓ |
| $f_{\mathrm{dissolution}}$ | `f_dissolution` | factor of the dissolution and gastric emptying |  | \- |  |
| $\mathrm{PODOSE}_{\mathrm{ena}}$ | `PODOSE_ena` | oral dose enalapril \[mg\] | $0$ | mg |  |
| $\mathrm{Ka}_{\mathrm{dis\_ena}}$ | `Ka_dis_ena` | Ka\_dis \[1/hr\] dissolution enalapril | $2$ | 1/hr | ✓ |
| $\mathrm{Mr}_{\mathrm{ena}}$ | `Mr_ena` | Molecular weight enalapril \[g/mole\] | $376.4467$ | g/mol | ✓ |
| $\mathrm{absorption}$ | `absorption` | transit of enalapril (absorption and fecal excretion) |  | mmol/min |  |

## Initial assignments and assignment rules

The initial assignments set the values at $t = 0$:

$$
\begin{aligned}
\mathrm{ena}_{\mathrm{stomach}} &= 0 \cdot \mathrm{Vstomach} \\[1ex]
\mathrm{ena}_{\mathrm{feces}} &= 0 \cdot \mathrm{Vfeces}
\end{aligned}
$$

The assignment rules hold at every time $t$:

$$
\begin{aligned}
\mathrm{absorption} &= \mathrm{ENAABS}_{\mathrm{k}} \cdot \mathrm{Vgu} \cdot \mathrm{ena}_{\mathrm{lumen}} \\[1ex]
f_{\mathrm{dissolution}} &= 1 + \mathrm{fed} \cdot \mathopen{}\left(\mathrm{FED}_{\mathrm{f\_dissolution}} - 1\right)
\end{aligned}
$$

## Reactions

| Rate | Id | Name | Equation |
| --- | --- | --- | --- |
| $v_{\mathrm{ENAABS}}$ | `ENAABS` | absorption enalapril | $\mathrm{ena}_{\mathrm{lumen}} \longrightarrow \mathrm{ena}_{\mathrm{ext}}$ |
| $v_{\mathrm{ENAEXC}}$ | `ENAEXC` | excretion enalapril (feces) | $\mathrm{ena}_{\mathrm{lumen}} \longrightarrow \mathrm{ena}_{\mathrm{feces}}$ |
| $v_{\mathrm{dissolution\_ena}}$ | `dissolution_ena` | dissolution enalapril | $\mathrm{ena}_{\mathrm{stomach}} \longrightarrow \mathrm{ena}_{\mathrm{lumen}}$ |

The rates of the reactions are:

$$
\begin{aligned}
v_{\mathrm{ENAABS}} &= F_{\mathrm{ena\_abs}} \cdot \mathrm{absorption} \\[1ex]
v_{\mathrm{ENAEXC}} &= \mathopen{}\left(1 - F_{\mathrm{ena\_abs}}\right) \cdot \mathrm{absorption} \\[1ex]
v_{\mathrm{dissolution\_ena}} &= \frac{\frac{f_{\mathrm{dissolution}} \cdot \mathrm{Ka}_{\mathrm{dis\_ena}}}{60} \cdot \mathrm{PODOSE}_{\mathrm{ena}}}{\mathrm{Mr}_{\mathrm{ena}}}
\end{aligned}
$$

## ODE system

The states change in time with the rates of the reactions and the rate rules:

$$
\begin{aligned}
\frac{\mathrm{d} \,\mathrm{ena}_{\mathrm{lumen}}}{\mathrm{d} t} &= \frac{-v_{\mathrm{ENAABS}} - v_{\mathrm{ENAEXC}} + v_{\mathrm{dissolution\_ena}}}{\mathrm{Vlumen}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{ena}_{\mathrm{ext}}}{\mathrm{d} t} &= \frac{v_{\mathrm{ENAABS}}}{\mathrm{Vext}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{ena}_{\mathrm{feces}}}{\mathrm{d} t} &= v_{\mathrm{ENAEXC}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{PODOSE}_{\mathrm{ena}}}{\mathrm{d} t} &= -v_{\mathrm{dissolution\_ena}} \cdot \mathrm{Mr}_{\mathrm{ena}} \qquad \text{(rate rule)}
\end{aligned}
$$
