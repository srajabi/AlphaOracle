# HANDOFF — state of the research as of 2026-08-09

**Read this before `findings.md`.** `findings.md` is the evidence
registry, in chronological order, 53 entries and 2,236 lines. This
document is the *organised* view: what was concluded, what was tried and
failed, where the data is, and which traps will cost you a day if you
rediscover them.

Owner context: 38, principal data scientist, Vancouver, ~300k CAD/yr,
frugal. Two sleeves — his own (~800k, 27–35yr horizon, 80k/yr
contributions) and his parents' (1.8M, 10–15yr, 80k/yr, low sequence
risk: house owned, OAS, family backstop). He validates everything
independently and does not want hedged advice. Do not suggest financial
advisors — he has explicitly ruled that out and taken ownership of the
decision.

---

## 1. The one-paragraph conclusion

**AlphaOracle is a risk-budgeting system, not a predictor.** Every
attempt to forecast has failed; every durable win has come from managing
risk and cost. Seven independent regime detectors have now failed to
beat a crude fixed-band trend gate, and two return-enhancers were ruled
out. The gate's *slowness is its mechanism*, not a limitation to be
engineered away — that is the single most repeatedly-confirmed result in
the repo, and the thing a new agent is most likely to try to "improve".

---

## 2. The strategy, exactly as it stands

| element | value | source |
|---|---|---|
| Trend gate | 200-day SMA, **4% band**, hysteresis | 41c |
| Gate permanence | **Permanent once levered — never remove** | 30, 37 |
| Leverage | **2x** (3x is worse on worst-case) | 30, 37, 52 |
| Geography | **Global market weight** | 46d |
| Financing assumption | **rf + 1.0%/yr** per unit borrowed | 51, 52 |
| Breadth | **INFO alert only, never an action** | 42d |
| Stop-losses | **Ruled out** | 53 |
| Check frequency | Daily. Monthly is too slow | 24, 43b |

**Expected outcome, 27y windows, 800k + 80k/yr, honest financing:**

| policy | median | worst | **worst DD** |
|---|---|---|---|
| 1x_gated | 24.95M | 12.74M | **-37.4%** |
| **2x_gated @1% spread** | **54.1M** | **24.8M** | **-70.9%** |
| 3x_gated @1% spread | 95.1M | 17.1M | **-89.2%** |

Numbers verified against `data/leverage_spread_study.json`.
**The -70.9% is the number that matters for whether this is holdable.**
An earlier draft of this file said ~-62%; it was wrong, and understating
the drawdown is the worst direction to be wrong in. 3x asks for -89.2%
to reach a WORSE worst case than 2x (17.1M vs 24.8M) - that pairing is
the whole argument against it.

2x beats 1x by **1.97–2.62x on median and 1.78–2.33x on worst case**
across the whole plausible financing range. The decision is robust; the
level is not — see §5.

**Why the gate works and everything faster fails (53c):** a stop is a
hair trigger on the LOW, the noisiest price of the day. The gate reads
the CLOSE through a band, and that band is hysteresis that deliberately
ignores exactly the moves a faster rule reacts to. It fires 0.89
times/year. That is the point.

---

## 3. Experiment ledger — everything tried, and the outcome

### 3.1 CONFIRMED — kept in the strategy

| # | result |
|---|---|
| 30 | The Depression is the case for the overlay; SPY-era data hides it |
| 35 | Trend family works out-of-sample in 5 markets — **as a RISK tool** |
| 37 | 2x + permanent gate dominates 1x at every percentile |
| 38 | Dot-com analogue: gate turned a -98.6% 2x wipeout into +165%. **Prediction not required** |
| 41c | 4% band: top p90 (43.7M), shallowest worst DD (-33.4%), least trading |
| 51 | LETF simulator beta accurate to 0.045 on 4 funds, R² 0.9937–0.9972 |
| 21 | For a CAD investor, unhedged USD is a hedge |

### 3.2 RULED OUT — seven detectors, all failed to beat the gate

| # | idea | why it failed |
|---|---|---|
| 33 | Markov regime switching | Edge was **entirely lookahead**; honest filtered version loses |
| 34 | Volatility-scaled bands | Vol rises in crashes AND chop — widened exactly when exiting mattered |
| H9 | Credit confirmation | Made things worse; no whipsaw reduction |
| 19, 20 | Macro / recession indicators | Lagging. Detects recessions, not drawdowns |
| 41b | Efficiency-ratio adaptive bands | **0 for 4** out-of-sample. Second adaptive formulation to fail |
| 42 | Breadth (49 industries) | Leads price 15/16, p≈0.0005 — but **~20 false alarms per real bear** |
| 46 | CAPE valuation | Monotonic 10.4pp spread, but n=9 independent decades; **every rule loses** |

**The pattern:** 33/34/41b consume the index return series, so they
cannot be faster than price by construction. 42 and 46 use genuinely
different information and genuinely predict — and still cannot be
traded. Breadth fails on false positives; CAPE fails on persistence
(91% of months since 1995 rank "expensive"; one unbroken 16.8-year
stretch from 1991-12).

### 3.3 RULED OUT — return enhancers

| # | idea | why |
|---|---|---|
| 44 | Top-10 concentration | t=1.76, p=0.089, fragile to 2023 alone; **top-25 underperforms** (p=0.435). Dollar-volume ranking biases toward the answer |
| 43→45 | Sector momentum | Real for a century (p=1.3e-5, survives equal-weight control) but **every variant loses to equal-weighting on the 11 tradeable SPDR sectors**. Post-1999 even the 49-industry version is insignificant |
| 53 | Stop-losses | 66–95% of real triggers invisible to close-only tests |
| 32 | Volatility targeting | Loses to the trend gate |

### 3.4 CORRECTIONS to earlier findings — read these

- **26** superseded by **31**: the LETF drag problem was *overstated*,
  not understated. Rate-correct financing matters.
- **36 reversed by 37**: gating only the entry phase is wrong; the gate
  must be permanent once levered.
- **41a superseded by 41c**: 2% won the 5-market vote but **4% is right
  for a US-heavy sleeve**. Band width is second-order — gating adds ~5M
  at p90 at *every* width.
- **43 superseded in part by 45**: the century-scale effect is real, the
  tradeability claim is not.
- **51/52 correct findings 30/36/38**: they keep their ORDERING and lose
  ~25% of their LEVEL at 2x, ~42% at 3x.

### 3.5 UNTESTED / open

- **Relative cross-country CAPE** — the only live route to an
  evidence-based geography call. Needs international CAPE (Barclays,
  StarCapital); the archive has none. §46 gap.
- **Equal-weight as a core holding** — EW 11 sectors beat SPY by
  +0.42pp/yr with a shallower drawdown, no timing. Compare against RSP.
- **#4 canary-gates-core**, **#12 per-sleeve signals** (wire breadth in
  as INFO per 42d).
- **Parents' sleeve at a 10–15yr horizon** — every projection here is
  27y. The worst-case column argues for a tighter band there, but that
  is extrapolation, not a result.
- **Findings 39 and 40 do not exist** — `findings.md` jumps 38→41. Not a
  deletion; they were never written. Do not go looking.

---

## 4. Data assets

Everything lives at `E:/ColdStorage/archive/`. **`README.md` and
`MANIFEST.json` inside it are self-describing and authoritative** —
prefer them over this section if they disagree.

```
archive/
  README.md        every trap, written down
  MANIFEST.json    sizes, SHA256, coverage, per-dataset issues
  raw/             originals, renamed, SHA256-verified   64.8 GB
  derived/         minute_master/ daily_master/ reference_master/
```

| set | scale | path |
|---|---|---|
| minute_master/alpaca | **3,286,433,543 bars**, 7,610 tickers, 1999–2019 | `derived/minute_master/alpaca/<TICKER>.parquet` |
| daily_master/ohlcv1m | ~77M rows, 411 months, 22k tickers, 1992–2026 | `derived/daily_master/ohlcv1m/` |
| daily_master/alpaca | 17,822,447 rows, 7,610 tickers | `derived/daily_master/alpaca/` |
| daily_master/yfinance | 501,183 rows, 79 tickers | `derived/daily_master/yfinance/` |
| reference_master | 2,857,417 obs, **922 series**, 1870–2026 | `derived/reference_master/reference.parquet` |
| OHLCV-1m (in place) | 411 monthly parquet, 87.7 GB | `E:/ColdStorage/OHLCV-1m/data/` |

**Total 195.3 GB; 169.5 GB excluding the verified-redundant bzip2.**
Minimum irreplaceable set: **126.6 GB** — `derived/` rebuilds from
`raw/` in ~3h; `raw/` rebuilds from nothing.

Schemas: daily is `date, ticker, open, high, low, close, volume, bars,
source` (long format, one row per source — **never resolved to a
winner**, because finding 48 showed neither source is authoritative).
Reference is `series_id, date, value, source, vintage_date, unit`.

**Only 8 of 922 reference series carry a `vintage_date`** (the ALFRED
ones). Those are the ONLY ones safe for decision-time backtests. Filter
`vintage_date <= decision_date` and finding 11's lookahead trap becomes
structurally impossible.

---

## 5. Traps that will cost you a day

### 5.1 Data traps — four of six are SILENT

| trap | symptom | fix |
|---|---|---|
| **Naive-Eastern timestamps** (Alpaca) | AAPL "opens" 09:30 UTC = 04:30 ET | Use `millis`, never `timestamp` |
| **`millis` holds SECONDS** | Read as ms → January 1970 | `unit="s"` |
| **Split-adjusted vs unadjusted** | Alpaca adjusted, OHLCV-1m NOT | Compare **returns**, never levels |
| **Duplicate minute timestamps** | >391 bars/day (AAPL 2026-03-31 = 394) | Dedup on (ticker, timestamp) before summing volume |
| **Multi-stream bzip2** (loud) | `EOFError: End of stream already reached` — looks like truncation, **is not** | `tarfile.open(fileobj=bz2.open(p,"rb"), mode="r|")` |
| **Windows reserved names** (loud) | `PRN.parquet` → `FileNotFoundError` | PRN/CON/AUX/NUL/COM0-9/LPT0-9 need suffixing |
| **TICKER REUSE** | UPRO gave beta **-12.6**, 427x wealth ratio | **Gate every ETF at its inception date.** OHLCV-1m holds a different security under UPRO in 2000–01 ($6.50) before real UPRO launched 2009-06-25 ($128) |
| **SPY absent from Alpaca** | Both captures, never downloaded | Source SPY from OHLCV-1m |
| Symbol changes | QQQ traded as **QQQQ** 2004–2011 | Stitch both |

### 5.2 Methodology traps

- **Overlapping windows inflate every forward-return p-value** (29).
  CAPE: naive t=27.67 → Newey-West 6.33 → non-overlapping n=9, p=0.233.
- **Causality.** `signal[T]` with `returns[T]` once produced sma200 at
  +271%. Also hit this session via `.resample("ME").last()` applied to
  the same month's return. **Heuristic: a familiar strategy printing an
  unfamiliar number is a bug until proven otherwise.**
- **Always run the control that shares the structure.** Equal-weight for
  a concentrated portfolio; same-period for a different-universe claim.
  Three promising results died on the control, not the headline (35, 44,
  45).
- **A bad rule can masquerade as a finding.** The first stop-loss run
  showed -100% drawdowns — that was a re-entry rule buying back above
  the sale price, not intraday triggering. Separate the *measurement*
  from the *strategy*.
- **Tolerance must exceed one tick.** A 1bp comparison tolerance on a
  $20 stock reported 72.3% "disagreement" that was pure rounding.
- **findings.md is not evidence until a test re-derives it** (25).

---

## 6. Live system state

- 6 Alpaca paper accounts; daily LLM analysis; Astro dashboard on Pages.
- **EOD gate fixed** — it used wall-clock `date -u +%H` which never
  returned "20", so accounts 1–5 never traded. Now keys off
  `github.event.schedule`.
- **LLM fallback chain** — `PM_MODELS` comma-separated, drains in order.
  `sys.exit(1)` on total PM failure is deliberate (stale-trades guard).
- **Alerting built** — state-diff, ACTION vs INFO split, email +
  Telegram. First run establishes a baseline silently.
- 385 tests pass. `python -m pytest tests/ -q` before any commit
  touching `backtesting/`.

**Blocked on the user:** `MAIL_*` secrets, `TELEGRAM_*` secrets, funding
an LLM provider (DeepSeek confirmed at zero), `HEALTHCHECK_URL`.

**Do not pay Alpaca $99/mo.** Their history is ~7 years, so it cannot
reproduce the 1999–2019 tar; and the pipeline decides EOD, for which
15-minute delayed data is adequate.

---

## 7. How to work here

1. Read `claude/agents.md` (the 8-step loop), `context.md`, this file,
   then `findings.md` for detail and `claude/REPRODUCE.md` to re-run
   anything. **REPRODUCE.md also lists what is NOT reproducible** -
   findings 1-17 predate the protocol and are unverified.
2. **Failures are findings.** Write them up with numbers, not
   adjectives.
3. Every experiment gets a tool in `tools/` with a docstring stating
   *what would falsify it* before the code.
4. Conventional commits. Never change the live forward test unless asked.
5. Record results in `findings.md`, narrative in `current.md`.

**The highest-value thing you can do is kill an idea cheaply.** This
project's value to date is 9 ruled-out strategies and a validated risk
rule, not a discovered edge. The user's stated goal is *conviction* —
which is built from documented, reproducible failures to improve on the
rule, so that in year three the answer to "should I tinker" is
`findings.md` rather than willpower.
