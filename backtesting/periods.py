"""Canonical test windows.

MARKET_PERIODS are single regimes - useful for asking "how did this
behave in a crash" but useless for judging a strategy, because a regime
is chosen knowing what happened in it.

MULTI_REGIME_WINDOWS are the ones that decide things. A trend overlay is
crash insurance: it necessarily wins any window containing a crash and
necessarily loses any window without one. Quoting either in isolation is
window-selection bias, and it is how finding 26 nearly drew the wrong
conclusion from real LETF data that happens to start in 2010.

RULE: report a strategy across ALL multi-regime windows, never one.
"""

MARKET_PERIODS = {
    "dotcom_bear": ("2000-03-24", "2002-10-09"),
    "post_dotcom_bull": ("2002-10-10", "2007-10-09"),
    "gfc_bear": ("2007-10-10", "2009-03-09"),
    "post_gfc_bull": ("2009-03-10", "2020-02-19"),
    "covid_crash": ("2020-02-20", "2020-03-23"),
    "covid_rebound": ("2020-03-24", "2021-12-31"),
    "inflation_bear_2022": ("2022-01-03", "2022-10-12"),
    "ai_bull_2023_2024": ("2023-01-03", "2024-12-31"),
    "chop_2015_2016": ("2015-05-01", "2016-02-11"),
    "chop_2018": ("2018-01-26", "2018-12-24"),
}

# Each entry: (start, end, what this window is FOR).
MULTI_REGIME_WINDOWS = {
    "full_sample": (
        "1994-01-03", "2026-03-31",
        "Everything SPY covers. Two major crashes, two shocks, three "
        "bulls. The default; anything not reported here is cherry-picked."),
    "two_crashes": (
        "1998-01-02", "2010-12-31",
        "Dot-com AND the GFC. The window most favourable to trend "
        "overlays - quote it only alongside no_crash_era."),
    "no_crash_era": (
        "2010-01-04", "2020-02-19",
        "ZIRP bull, no bear worse than -20%. The window most hostile to "
        "trend overlays, and the one real LETF history mostly covers."),
    "lost_decade": (
        "2000-01-03", "2009-12-31",
        "SPY roughly flat across ten years. Tests whether a strategy can "
        "earn anything when beta pays nothing."),
    "letf_era": (
        "2010-06-01", "2026-03-31",
        "Where real TQQQ/UPRO prices exist. Any claim about actual funds "
        "is confined to this window - and it contains no major crash."),
    "modern_shocks": (
        "2018-01-02", "2026-03-31",
        "COVID, the 2022 rate shock and the AI boom. Fast crashes and "
        "sharp reversals rather than grinding bears."),
    "post_gfc_full": (
        "2009-03-10", "2026-03-31",
        "The whole post-GFC era including COVID and 2022. A softer "
        "version of no_crash_era."),
}

