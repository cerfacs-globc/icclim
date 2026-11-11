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
With ``run_index="last"``, a period's value can include days that fall in the
previous period, so it can exceed the length of the period itself.

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
