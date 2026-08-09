# RULED OUT - do not retry these

The negative-results ledger. Its whole job is to stop session 47
spending tokens on what session 3 already killed.

**A negative result is a finding.** Add to this file with the numbers
and the reason, not just the verdict. If you think something here
deserves a retry, say what changed - new data, a fixed bug, a different
formulation - and note it in the entry rather than silently redoing it.

---

## Timing overlays on 1x diversified equity

**SMA200 on VT/XEQT/VEQT.** Fair test, VT 2010+, signal live throughout:
6.4% CAGR / Sharpe 0.56 / -19% maxDD versus buy-hold 9.8% / 0.56 / -34%.
A third of the CAGR for identical Sharpe. (finding 3)

**Why it initially looked good, and the general lesson:** short
backtests flattered it because the 200-day warmup happened to cover
COVID (XEQT) and the GFC tail (VT). The strategy was flat through the
crash *by construction*, having no signal yet. **Check warmup coverage
before believing any short-history trend result.**

Retry only with: a different mandate (one that values drawdown over
terminal wealth), or leveraged underlyings, where finding 3 says timing
does earn its costs.

## Macro-statistical timing

**Payroll momentum filter.** -0.31pp CAGR against buy-and-hold (10.11%
vs 10.42%); cuts maxDD -50.79% -> -32.34%. A risk tool, not an alpha
tool - and for a no-withdrawal mandate that trade is backwards.
(finding 19)

**Macro cannot time a fast drawdown, structurally.** Publication lag,
not data quality. On 2020-03-15 the newest published payrolls described
February and the newest jobless claims read 211k, a fortnight before
they hit ~6.8M. Median lags: ICSA 5d, PAYEMS 35d, CPIAUCSL 46d, HOUST up
to 130d. (findings 19, 20)

**Payroll filter is a recession detector, not a drawdown detector.**
Caught 2 of 5 SPY drawdowns >15% since 1994. Needs BOTH slow enough to
outlast publication lag AND labour-market deterioration. 2020 failed the
first; 2022 failed the second (payrolls grew all the way down a -23.9%
decline). (finding 20)

Not ruled out: **market-price** macro (yield curve), which has no
publication lag. See H3.

## Currency hedging

**CAD-hedged US equity products, for a Canadian holder.** corr(SPY,
USD/CAD) = -0.569; unhedged gives 12.01%/yr vol and -41.82% maxDD where
the hedged/US experience is 14.48% and -50.79%. Hedging strips a free
cushion. (finding 21)

## Leveraged strategies that failed

- **TQQQ buy-and-hold**: -94% maxDD (GFC), -83% (dot-com). Uninvestable.
- **VIX-laddered TQQQ**: -95% drawdown.
- **VIX-spike leverage buying**: permutation p=0.977 - worse than random.
- **Donchian 55/20**, **GEM/VAA with EWA proxies** (proxy quality kills
  them), **low-vol at sector granularity** (it is a single-stock effect).
(findings 4, 5)

## Entry timing

**Waiting for a 10% dip before deploying**: the worst rule tested,
lowest median wealth of any entry strategy. **DCA** beats lump sum on
neither the median (at-top cohort 1.73x for lump sum) nor the tail
(worst maxDD still -50%+ once deployed). (finding 1)

## Data sources and methods

**FRED via requests/urllib**: `fred.stlouisfed.org` is Akamai-fronted
and tarpits Python's TLS fingerprint - connects, handshakes, then never
sends. Use curl subprocess, or `api.stlouisfed.org` which is unaffected.
Not a network or firewall problem; it would follow onto a CI runner.

**Naive period-label joins on macro series**: introduces lookahead that
costs -0.06pp of CAGR (invisible) but 5.55pp of maxDD (material). A
returns-only check will tell you the bias is harmless. It is not.
(finding 19)

**Daily-bar gap studies without bad-print filtering**: SPY 2000-12-18
records open and low of exactly 111.000 against a 131.45 prior close,
producing a phantom -15.56% overnight gap - which would have been the
worst in SPY history. Real value +0.87%. Use
`robust_session_edges`. (finding 18, `spikes/minute_data.md`)

**Daily-resolution fitting against thinly-traded instruments**: XEQT.TO
has 88 zero-return days; its measured daily vol (0.98%) is below VT's
(1.22%), which cannot be right for two global all-equity funds. Daily
correlation caps near 0.92 regardless of basket and the fit assigns EWC
0%. Fit at the cadence the strategy trades. (finding 17)

## Known-bad data

- **UPRO pre-2009**: series claims a 2000-03-20 start; the fund launched
  2009, and n=4,471 over 26 years is far short of the ~6,500 sessions
  implied. Full-history percentiles untrustworthy.
- **BAMLH0A0HYM2 via the keyless FRED CSV endpoint**: returns 787
  observations from 2023-08; the series starts 1996. Truncated, cause
  not yet diagnosed. Do not use until fixed.
