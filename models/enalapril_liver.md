# Model for hepatic enalapril metabolism.

Model `enalapril_liver`, SBML Level 3 Version 2, read from enalapril\_liver.xml, written by sbmlode 0.3.0.

Model for the hepatic metabolism of enalapril.

Enalapril is taken up into the hepatocytes by OATP1B1 (ENAIM) and hydrolysed by the carboxylesterase 1 (CES1) to its active metabolite enalaprilat (ENA2EAT), which leaves the hepatocytes slowly (EATEX): the dicarboxylic acid enalaprilat permeates membranes poorly, enalaprilat in the plasma peaks 3.5-4.6 hr after an oral dose of enalapril, about 3 hr after enalapril.

The concentrations of enalapril and enalaprilat in the liver (0.1-6 µM) are far below the Michaelis constants of the transport and the conversion (0.4-1.7 mM), so all three are linear and only their ratios Vmax/Km act.

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
| $\mathrm{Vli}$ | `Vli` | liver | $1.5$ | l | ✓ |
| $\mathrm{Vmem}$ | `Vmem` | plasma membrane | $\mathrm{NaN}$ | m<sup>2</sup> | ✓ |

## Species

| Symbol | Id | Name | Compartment | Value | Unit | Properties |
| --- | --- | --- | --- | --- | --- | --- |
| $\mathrm{ena}_{\mathrm{ext}}$ | `ena_ext` | enalapril (plasma) | $\mathrm{Vext}$ | $0$ | mmol/l | concentration |
| $\mathrm{eat}_{\mathrm{ext}}$ | `eat_ext` | enalaprilat (plasma) | $\mathrm{Vext}$ | $0$ | mmol/l | concentration |
| $\mathrm{ena}$ | `ena` | enalapril (liver) | $\mathrm{Vli}$ | $0$ | mmol/l | concentration |
| $\mathrm{eat}$ | `eat` | enalaprilat (liver) | $\mathrm{Vli}$ | $0$ | mmol/l | concentration |

## Parameters

| Symbol | Id | Name | Value | Unit | Constant |
| --- | --- | --- | --- | --- | :---: |
| $\mathrm{ENAIM}_{\mathrm{Vmax}}$ | `ENAIM_Vmax` | Vmax enalapril import | $0.75$ | mmol/min/l | ✓ |
| $\mathrm{ENAIM}_{\mathrm{Km\_ena}}$ | `ENAIM_Km_ena` | Km enalapril import | $0.844$ | mmol/l | ✓ |
| $\mathrm{ENA2EAT}_{\mathrm{Vmax}}$ | `ENA2EAT_Vmax` | Vmax enalapril conversion | $0.643377167672023$ | mmol/min/l | ✓ |
| $\mathrm{ENA2EAT}_{\mathrm{Km\_ena}}$ | `ENA2EAT_Km_ena` | Km enalapril CES1 | $1.721$ | mmol/l | ✓ |
| $\mathrm{ENA2EAT}_{\mathrm{Ki\_ena}}$ | `ENA2EAT_Ki_ena` | Ki enalapril CES1 | $2.956$ | mmol/l | ✓ |
| $f_{\mathrm{ces1}}$ | `f_ces1` | scaling factor CES1 activity | $1$ | \- | ✓ |
| $\mathrm{EATEX}_{\mathrm{Vmax}}$ | `EATEX_Vmax` | Vmax enalaprilat export | $0.00145697380767393$ | mmol/min/l | ✓ |
| $\mathrm{EATEX}_{\mathrm{Km\_eat}}$ | `EATEX_Km_eat` | Km enalaprilat export | $0.43$ | mmol/l | ✓ |

## Reactions

| Rate | Id | Name | Equation |
| --- | --- | --- | --- |
| $v_{\mathrm{ENAIM}}$ | `ENAIM` | enalapril import (ENAIM) OATP1B1 | $\mathrm{ena}_{\mathrm{ext}} \rightleftharpoons \mathrm{ena}$ |
| $v_{\mathrm{ENA2EAT}}$ | `ENA2EAT` | enalapril conversion (ENA2EAT) CES1 | $\mathrm{ena} \longrightarrow \mathrm{eat}$ |
| $v_{\mathrm{EATEX}}$ | `EATEX` | enalaprilat export (EATEX) | $\mathrm{eat} \rightleftharpoons \mathrm{eat}_{\mathrm{ext}}$ |

The rates of the reactions are:

$$
\begin{aligned}
v_{\mathrm{ENAIM}} &= \frac{\frac{\mathrm{ENAIM}_{\mathrm{Vmax}}}{\mathrm{ENAIM}_{\mathrm{Km\_ena}}} \cdot \mathrm{Vli} \cdot \mathopen{}\left(\mathrm{ena}_{\mathrm{ext}} - \mathrm{ena}\right)}{1 + \frac{\mathrm{ena}_{\mathrm{ext}}}{\mathrm{ENAIM}_{\mathrm{Km\_ena}}} + \frac{\mathrm{ena}}{\mathrm{ENAIM}_{\mathrm{Km\_ena}}}} \\[1ex]
v_{\mathrm{ENA2EAT}} &= \frac{f_{\mathrm{ces1}} \cdot \mathrm{ENA2EAT}_{\mathrm{Vmax}} \cdot \mathrm{Vli} \cdot \mathrm{ena}}{\mathrm{ena} + \mathrm{ENA2EAT}_{\mathrm{Km\_ena}} + \frac{\mathrm{ena}^{2}}{\mathrm{ENA2EAT}_{\mathrm{Ki\_ena}}}} \\[1ex]
v_{\mathrm{EATEX}} &= \frac{\frac{\mathrm{EATEX}_{\mathrm{Vmax}}}{\mathrm{EATEX}_{\mathrm{Km\_eat}}} \cdot \mathrm{Vli} \cdot \mathopen{}\left(\mathrm{eat} - \mathrm{eat}_{\mathrm{ext}}\right)}{1 + \frac{\mathrm{eat}_{\mathrm{ext}}}{\mathrm{EATEX}_{\mathrm{Km\_eat}}} + \frac{\mathrm{eat}}{\mathrm{EATEX}_{\mathrm{Km\_eat}}}}
\end{aligned}
$$

## ODE system

The states change in time with the rates of the reactions:

$$
\begin{aligned}
\frac{\mathrm{d} \,\mathrm{ena}_{\mathrm{ext}}}{\mathrm{d} t} &= \frac{-v_{\mathrm{ENAIM}}}{\mathrm{Vext}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{eat}_{\mathrm{ext}}}{\mathrm{d} t} &= \frac{v_{\mathrm{EATEX}}}{\mathrm{Vext}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{ena}}{\mathrm{d} t} &= \frac{v_{\mathrm{ENAIM}} - v_{\mathrm{ENA2EAT}}}{\mathrm{Vli}} \\[1ex]
\frac{\mathrm{d} \,\mathrm{eat}}{\mathrm{d} t} &= \frac{v_{\mathrm{ENA2EAT}} - v_{\mathrm{EATEX}}}{\mathrm{Vli}}
\end{aligned}
$$
