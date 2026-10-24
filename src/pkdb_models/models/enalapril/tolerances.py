"""The tolerances of the integrator for the enalapril model."""

from sbmlsim.model.tolerances import AbsoluteTolerance

#: the states of the renin-angiotensin-aldosterone system. Their amounts are
#: about 1e-8 mmole (renin and ACE 5e-9 mmole, aldosterone 1e-6 mmole), six
#: orders of magnitude below the amounts of enalapril, so they get absolute
#: tolerances of their own scale; the enalaprilat which inhibits ACE in it is
#: the one of the venous plasma (an assignment, not a state). The delayed
#: angiotensin II of the renin feedback (`ang2_feedback`, a concentration of a
#: rate rule) gets the same tolerance
RAAS_STATES: tuple[str, ...] = ("ren", "ace", "ang1", "ang2", "ald", "ang2_feedback")


def absolute_tolerance(value: float, species: float, raas: float) -> AbsoluteTolerance:
    """Get the absolute tolerance of the integrator for the enalapril model.

    The species of enalapril and enalaprilat are small: the plasma
    concentrations peak at about 1e-5 (2.5 mg of enalapril maleate in renal
    impairment) to 3e-3 mM (5 mg i.v.) in the studies and fall to about 1e-6
    mM in the terminal phase, the enalaprilat bound to tissue ACE is about
    1e-7 to 1e-5 mM, the amounts in the urine and feces are about 3e-4 to 0.6
    mmole. The RAAS states are smaller still
    (`RAAS_STATES`). The other states are the doses in mg (the targets of the
    rate rules).

    Args:
        value: tolerance of the other states [mg].
        species: tolerance of the species, of their concentrations [mM] and
            amounts [mmole].
        raas: tolerance of the amounts of the RAAS states [mmole].

    Returns:
        The absolute tolerance per kind of state and of the RAAS states.
    """
    return AbsoluteTolerance(
        amount=species,
        concentration=species,
        other=value,
        ids=dict.fromkeys(RAAS_STATES, raas),
    )


#: the absolute tolerance of the simulation experiments
ABSOLUTE_TOLERANCE = absolute_tolerance(1e-10, species=1e-14, raas=1e-16)
