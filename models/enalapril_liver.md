# model: enalapril_liver
Autogenerated ODE System from SBML file with sbmlutils.
```
time: [min]
substance: [mmol]
extent: [mmol]
volume: [l]
area: [m^2]
length: [m]
```

## Parameters `p`
```
EATEX_Km_eat = 0.1  # [mmol/l] 
EATEX_Vmax = 100.0  # [mmol/min/l] 
ENA2EAT_Ki_ena = 2.956  # [mmol/l] 
ENA2EAT_Km_ena = 1.721  # [mmol/l] 
ENA2EAT_Vmax = 1.0  # [mmol/min/l] 
ENAIM_Km_ena = 0.262  # [mmol/l] 
ENAIM_Vmax = 100.0  # [mmol/min/l] 
Vext = 1.5  # [l] 
Vli = 1.5  # [l] 
Vmem = nan  # [m^2] 
f_ces1 = 1.0  # [-] 
```

## Initial conditions `x0`
```
eat = 0.0  # [mmol/l] Vli
eat_ext = 0.0  # [mmol/l] Vext
ena = 0.0  # [mmol/l] Vli
ena_ext = 0.0  # [mmol/l] Vext
```

## ODE system
```
# y
EATEX = (EATEX_Vmax / EATEX_Km_eat) * Vli * (eat - eat_ext) / (1 + eat_ext / EATEX_Km_eat + eat / EATEX_Km_eat)  # [mmol/min]
ENA2EAT = f_ces1 * ENA2EAT_Vmax * Vli * ena / (ena + ENA2EAT_Km_ena + ena**2 / ENA2EAT_Ki_ena)  # [mmol/min]
ENAIM = (ENAIM_Vmax / ENAIM_Km_ena) * Vli * (ena_ext - ena) / (1 + ena_ext / ENAIM_Km_ena + ena / ENAIM_Km_ena)  # [mmol/min]

# odes
d eat/dt = ENA2EAT / Vli - EATEX / Vli  # [mmol/l/min]
d eat_ext/dt = EATEX / Vext  # [mmol/l/min]
d ena/dt = ENAIM / Vli - ENA2EAT / Vli  # [mmol/l/min]
d ena_ext/dt = -ENAIM / Vext  # [mmol/l/min]
```