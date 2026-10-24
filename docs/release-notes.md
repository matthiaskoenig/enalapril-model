# Release notes

## Release notes for enalapril-model 0.10.0

Made from pkdb_models 3a0b49144b with pkpdsim 0.11.0.

The changes since 0.9.5.

### Core libraries

The versions of the core libraries cannot be compared, there is no lock file in the previous release. The release uses:

- pkpdsim 0.11.0
- sbmlsim 0.13.0
- sbmlutils 0.17.0

### Libraries

The versions cannot be compared, there is no lock file in the previous release.

### Data

- Added: `enalapril/Arafat2005`, `enalapril/Baba1990`, `enalapril/Biollaz1982`, `enalapril/Burckhardt2015`, `enalapril/Dayyih2017`, `enalapril/Dickstein1987`, `enalapril/Dickstein1987a`, `enalapril/Donnelly1990`, `enalapril/ElungJensen2001`, `enalapril/Fruncillo1987`, `enalapril/Ghosh2012`, `enalapril/Gu2004`, `enalapril/He2014`, `enalapril/Her2021`, `enalapril/Hockings1986`, `enalapril/Ishizaki1988`, `enalapril/Johnston1992`, `enalapril/Kelly1986`, `enalapril/Lee2003`, `enalapril/Lees1987a`, `enalapril/Lowenthal1985`, `enalapril/Lu2009`, `enalapril/MacDonald1993`, `enalapril/Marzo2002`, `enalapril/Matalka2002`, `enalapril/Moffett2014`, `enalapril/Mujais1992`, `enalapril/Najib2003a`, `enalapril/Niopas2004`, `enalapril/Oguchi1993`, `enalapril/Ohnishi1989`, `enalapril/Portoles2004`, `enalapril/Ribeiro1996`, `enalapril/Schwartz1985`, `enalapril/Shionoiri1985`, `enalapril/Shioya1992`, `enalapril/Sica1991`, `enalapril/Stage2017`, `enalapril/Sunaga1995`, `enalapril/Swanson1984`, `enalapril/Tarkiainen2015`, `enalapril/Thongnopnua2005`, `enalapril/Till1984`, `enalapril/Tsuruoka2007`, `enalapril/VanHecken2020`, `enalapril/Wade1992`, `enalapril/Wagner2003`, `enalapril/Weisser1991`, `enalapril/Weisser1992`, `enalapril/Witte1993`, `hydrochlorothiazide/Howes1991`, `lisinopril/Ulm1982`

### Analysis

#### Models

- `enalapril_body.xml`: added 8 species, 9 reactions, 62 parameters; changed values `Ka_dis_ena` 1 → 1.2106, `Kp_eat` 0.101727 → 0.0200773, `Kp_ena` 0.304908 → 0.0217554, `ftissue_eat` 9.99544 → 2, `ftissue_ena` 9.99999 → 2
- `enalapril_body_flat.xml`: added 8 species, 9 reactions, 68 parameters; removed 3 parameters; changed values `GU__ENAABS_k` 0.1 → 0.0228894, `GU__F_ena_abs` 0.6 → 0.577262, `Ka_dis_ena` 1 → 1.2106, `Kp_eat` 0.101727 → 0.0200773, `Kp_ena` 0.304908 → 0.0217554, `LI__EATEX_Km_eat` 0.430425 → 0.43, `LI__EATEX_Vmax` 0.00148045 → 0.00145697, `LI__ENA2EAT_Vmax` 0.640305 → 0.643377, `LI__ENAIM_Vmax` 0.748447 → 0.75, `ftissue_eat` 9.99544 → 2, `ftissue_ena` 9.99999 → 2
- `enalapril_intestine.xml`: added 3 parameters; changed values `ENAABS_k` 0.1 → 0.0228894, `F_ena_abs` 0.6 → 0.577262, `Mr_ena` 416.5 → 376.447
- `enalapril_kidney.xml`: added 6 parameters; removed 2 parameters
- `enalapril_liver.xml`: changed values `EATEX_Km_eat` 0.430425 → 0.43, `EATEX_Vmax` 0.00148045 → 0.00145697, `ENA2EAT_Vmax` 0.640305 → 0.643377, `ENAIM_Vmax` 0.748447 → 0.75
- `enalapril_raas.xml`: new, 7 species, 8 reactions, 52 parameters

#### Experiments

- Added: `Arafat2005`, `Baba1990`, `Biollaz1982`, `Burckhardt2015`, `Dayyih2017`, `Dickstein1987`, `Dickstein1987a`, `Donnelly1990`, `DoseDependencyExperiment`, `EnalaprilParameterScan`, `Fruncillo1987`, `Ghosh2012`, `Gu2004`, `He2014`, `Her2021`, `Hockings1986`, `Howes1991`, `Ishizaki1988`, `Johnston1992`, `Kelly1986`, `Lee2003`, `Lees1987a`, `Lowenthal1985`, `Lu2009`, `MacDonald1993`, `Marzo2002`, `Matalka2002`, `Moffett2014`, `Mujais1992`, `Najib2003a`, `Niopas2004`, `Oguchi1993`, `Ohnishi1989`, `Portoles2004`, `RaasExperiment`, `Ribeiro1996`, `Schwartz1985`, `Shionoiri1985`, `Shioya1992`, `Stage2017`, `Sunaga1995`, `Swanson1984`, `Tarkiainen2015`, `Thongnopnua2005`, `Till1984`, `Tsuruoka2007`, `Ulm1982`, `VanHecken2020`, `Wade1992`, `Weisser1991`, `Weisser1992`, `Witte1993`

#### Fits

- `PD`: `PD_20261020_125416__5ce99`, no fit record in the previous release
- `PK`: `PK_20261020_114902__1f0f7`, no fit record in the previous release

## Release notes for enalapril-model v0.9.5

We are pleased to release a new version of the enalapril-model including the 
following changes:

- updated parameter optimization
- tissue distribution of enalapril and enalaprilat

Your enalapril-model team

## Release notes for enalapril-model v0.9.1

We are pleased to release a new version of the enalapril-model including the 
following changes:

- initial model release

Your enalapril-model team

## Release notes for enalapril-model v0.9.0

We are pleased to release a new version of the enalapril-model including the 
following changes:

- initial model release

Your enalapril-model team

