.. _run_attribution:

#################################
 Attribute or split longest runs
#################################

``CDD``, ``CWD``, ``CFD``, ``CSU``, ``PXCDD`` and ``PXCWD`` (the Météo-France DCSC maximum
consecutive dry-day and wet-day indices), and the generic
``max_consecutive_occurrence`` can contain a run that crosses an output-period
boundary. Since icclim 7.4.0, their default is ``run_index="last"``: the whole
run is attributed to the period in which it ends. This is a behaviour change;
the same call can produce different values from earlier releases. The same
applies to monthly and seasonal output: a run crossing a month boundary is
attributed to the month in which it ends. For monthly output, a 12-day run from
January 25 through February 5 is ``[12, 0]`` with ``run_index="first"``,
``[0, 12]`` with the new default, and ``[7, 5]`` when split at the boundary.
With ``run_index="first"`` or ``"last"``, a period's value counts the whole run,
including the days that fall in other periods, so it can exceed the length of the
period itself.

For example, the ECA&D ATBD describes a dry spell beginning in December 2000
and ending in January 2001. It counts toward 2001. For a longer dry spell from
2001-10-01 through 2002-04-30 with yearly output, the alternatives are:

===============================================  ============
Setting                                          Result
===============================================  ============
Default since 7.4.0 (``run_index="last"``)       ``[0, 212]``
Pre-7.4.0 behavior (``run_index="first"``)       ``[212, 0]``
``split_runs_at_period_boundary=True``           ``[92, 120]``
===============================================  ============

Pass ``run_index="first"`` explicitly to reproduce the old attribution. Pass
``split_runs_at_period_boundary=True`` to cut every run at each period boundary;
the pieces then contribute independently to their respective periods.

Periods wholly traversed by a run
=================================

Only the period where a run starts (``run_index="first"``) or ends
(``run_index="last"``) receives its length. The result of the other periods depends on
what they contain:

- a period without any event, or that contains at least one day outside a run, gets
  ``0``;
- a period that is wholly traversed by one continuous run attributed to another period
  is **not reported**: its value is ``NaN``. ``NaN`` here means "not reported because
  every day of this period belongs to a run that is attributed to another period", not
  a missing input.

With ``split_runs_at_period_boundary=True`` the runs are cut at the boundaries, so every
period gets a value.

For example, with a continuous run of 1095 days from 2001-01-01 to 2003-12-31 (three
years of consecutive dry days) and yearly output:

===============================================  ============================
Setting                                          Result
===============================================  ============================
``run_index="first"``                            ``[1095, NaN, NaN]``
``run_index="last"`` (default)                   ``[NaN, NaN, 1095]``
``split_runs_at_period_boundary=True``           ``[365, 365, 365]``
===============================================  ============================

The same holds for monthly output: with ``run_index="last"`` the 35 first months are
``NaN`` and the last one is ``1095``, which is far more than the length of a month.
A period without any event, on the other hand, is ``0`` in the three modes.

This is the convention of ETCCDI and ``climdex`` for a spell that spans a whole year
(the year is not reported and the run is carried to the period where it ends), and
the one of the ECA&D ATBD for ``CDD`` and ``CWD``. It is applied to ``CFD``, ``CSU``,
``PXCDD``, ``PXCWD`` and the generic function for consistency (issue #580).

Default-change notice
=====================

When ``run_index`` is not given, icclim prints the default-change notice on stdout,
once per process for each index: the second call of ``CDD`` prints nothing, and
``CFD`` prints its own notice the first time it is called. Passing ``run_index``
explicitly, as either ``"first"`` or ``"last"``, prints no notice. For ``CDD``, the
exact text is::

   Since icclim 7.4.0, CDD defaults to run_index="last", so a run crossing a period boundary is counted where it ends. Use run_index="first" for the pre-7.4.0 result, or split_runs_at_period_boundary=True to cut the run at each boundary.

The end-period rule for CDD and CWD follows the *ECA&D Algorithm Theoretical
Basis Document*, version 11, pp. 20--21, which says that a crossing spell is
"counted against the year in which the spell ends". The RClimDex user manual,
Appendix C, and the ``climdex.pcic`` implementation use the same end-period
convention for CDD and CWD.

The ATBD defines CFD and CSU per period ("day i of period j") and does not state
the same crossing-spell rule for them. icclim applies end-period attribution to
CFD, CSU, PXCDD, PXCWD and the generic function for consistency with CDD and CWD,
not because the ATBD requires it. ``WSDI`` and ``CSDI`` are different spell
indices and are unchanged.
