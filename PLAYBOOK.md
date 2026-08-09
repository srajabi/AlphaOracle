# PLAYBOOK - what to actually do

The operating manual. `claude/findings.md` is the evidence, `spikes/`
is the research, this is the "money is real, what do I do on Monday"
document.

Paper trading research. Not advice.

---

## 1. The one decision the system makes today

Everything the pipeline computes reduces to a single instruction, in
`data/family_signals.json` under `mandates`:

```
SLEEVE_INVESTED         -> the equity sleeve is in equities
SLEEVE_TO_TREASURIES    -> the equity sleeve is in short treasuries
```

The rule, from `src/family_signals.py`:

```
instruction = SLEEVE_INVESTED  if (slow_channel == risk_on
                                   AND fast_channel == clear)
              else SLEEVE_TO_TREASURIES
```

**Both conditions must hold.** Either one flipping moves you out.

**Read this carefully: only two of the four signals feed that decision.**
Credit and canary are computed and shown, but do not currently affect
the instruction at all. If you thought the canary was gating your core,
it is not - that is a change you asked about and it has not been made or
backtested yet (see §6).

---

## 2. The indicators, precisely

| Signal | Definition | Trips when |
|---|---|---|
| **Slow channel** | Month-end close of the equity ETF vs its 200-day SMA. Checked **once per month**, executed on the first trading day. | close < SMA200 -> `risk_off` |
| **Fast channel** | 5-day **median** of `^VIX / ^VIX3M`. Checked **daily**. | median > 1.0 -> `backwardation` |
| **Credit** | HYG/LQD 63-day relative momentum. **Informational only.** | < -2% -> stressed |
| **Canary** | 13612W momentum on EWA and TLT; state is the count of negatives. **Governs the satellite, not the core.** | 1 negative -> `half_defensive`, 2 -> `full_defensive` |

The two-speed design is deliberate: the slow channel catches grinding
bear markets and only trades ~41 times in 33 years (finding 5), while
the fast channel exists for COVID-shaped events the monthly check would
sleep through (finding 13).

### Live state, as of the 2026-08-07 run

| Signal | State | Detail |
|---|---|---|
| Slow channel | `risk_on` | +7.82% above SMA200, as of 2026-07-31 month-end |
| Fast channel | `clear` | VIX/VIX3M 5d median 0.858 |
| Credit | `clear` | HYG/LQD 63d +2.04% |
| Canary | `half_defensive` | TLT negative, EWA positive |
| **Mandate** | **`SLEEVE_INVESTED`** | both gates open |

You are currently invested, with a comfortable 7.82% cushion above the
trend line and no volatility stress.

---

## 3. What to do when an alert fires

Alerts arrive by Telegram (push) and email (record). Two tiers.

### ACTION - a mandate changed

| Alert | What it means | What you do |
|---|---|---|
| `SLEEVE_INVESTED -> SLEEVE_TO_TREASURIES` | A gate closed | Move the equity sleeve to short treasuries. If the **slow** channel tripped, this is a month-end signal - execute on the first trading day. If the **fast** channel tripped, it is immediate. |
| `SLEEVE_TO_TREASURIES -> SLEEVE_INVESTED` | Both gates open again | Re-enter the equity sleeve. Requires the ratio back under 1.0 **and** the monthly trend permitting. |

The entry rule is the management rule: deploy per the channels' current
state. There is no DCA logic - the channels already encode when to be
in.

### INFO - context, no trade

Credit or canary moved without changing a mandate. Nothing to do. These
exist so a later ACTION is not a surprise.

### Silence

Silence means no change - **provided** the heartbeat is alive. After 7
quiet days you get a heartbeat message; if the pipeline stops entirely,
the external dead-man's switch alerts you. If you have neither for over
a week, assume the system is down rather than the market is calm.

---

## 4. Position structure (Mandate Y - "the user pattern")

From `claude/ips_case_study.md`:

- **Core, 75-80%**: global equity ETF, governed by the two-channel
  overlay above.
- **Satellite, 20-25%**: ONE registered champion, run exactly as
  registered. Candidates: `canary_daa_2x` (18% CAGR backtest, GFC +13%,
  monthly) or `vol_target_qqq_2x`.
- **Sizing rule**: satellite gap-risk x weight must stay above -10% of
  portfolio. See §5 - this is now measured, not assumed.

Instrument note: the live account can hold XEQT.TO, the paper account
cannot (TSX/CAD, Alpaca is US-only). Validated proxy is
**VT 77% / EWC 23%** (finding 17): TE 2.53%/yr, correlation 0.9883,
drift +0.6pp over 6.5y.

---

## 5. Confidence ledger

What is actually established, versus assumed, versus unknown. This is
the part that decides how much weight a rule can carry.

### Validated with numbers

- **Overnight gap risk** (finding 18). Measured 1993-2026 from minute
  bars. SPY worst -10.46%, QQQ -10.32% - the 15% assumption was never
  breached. 3x products: UPRO -32.08%, SOXL -31.25%, TQQQ -28.90%, all
  13-16pp inside the assumed -45% ceiling, all on 2020-03-16. Leverage
  tracked cleanly through the gap (SPY -10.46% vs UPRO -32.08% = 3.07x).
  **The sizing rule is safe.**
- **XEQT proxy** (finding 17). VT 77/EWC 23, near-zero drift.
- **SMA200 overlay truncates the left tail** (finding 1): at-top entry
  worst case 0.94x vs 0.82x, maxDD -22% vs -55%.

### Assumed, and the assumption is doing real work

- **Do NOT relax the satellite sizing rule** on finding 18. Measured
  worst x 25% weight is -8.0%, inside the -10% budget, which would
  nominally permit ~31% sizing. But every 3x tail rests on ONE event
  (2020-03-16); TQQQ and SOXL series start in 2010, so 2008 and 1987 are
  not in the sample. That headroom is a property of the sample, not the
  instrument.
- **SOXL is the fat tail**: p0.1 -17.96%, 9 breaches past -15%, versus 4
  for TQQQ and UPRO. Sector 3x is not portfolio 3x.

### Known problems, unresolved

- **The slow channel is computed on XEQT.TO, a CAD instrument, for a
  strategy you may execute in USD.** A large CAD/USD move can put the
  CAD and USD versions of the same portfolio on opposite sides of the
  200dma. CAD/USD vol is 6.12%/yr (finding 17). Not yet addressed.
- **`BAMLH0A0HYM2` is truncated** - 787 observations from 2023-08 when
  the series starts in 1996. Do not use it until diagnosed.
- **UPRO pre-2009 data is wrong** - series claims a 2000 start but the
  fund launched 2009. The 2020 tail figure is unaffected; its
  full-history percentiles are not.
- **Revised macro series are context only.** UNRATE, CPIAUCSL, INDPRO,
  PAYEMS are current-vintage. Backtesting them is lookahead bias hidden
  inside the data. Vintage (ALFRED) path needs a free API key.

---

## 6. Not decided yet - these are open questions, not settled rules

- **Canary gating the core.** You proposed 80/20 with the canary pulling
  the core out. The IPS gates the core with the two-channel overlay and
  uses the canary for the satellite. Published stats do **not** transfer
  to the inverted design. Not backtested. Do not run it live.
- **Per-sleeve signals** ("gold looks bearish", "move TQQQ to bonds").
  The system currently emits one portfolio-level instruction, not
  per-asset calls. Designing those is open work.
- **Stop losses.** Never validated on true intraday path; daily bars
  cannot tell you whether a stop hit before or after the day's high.

---

## 7. Where things live

| What | Where |
|---|---|
| Live signal state | `data/family_signals.json` |
| Alert state / history | `data/alert_state.json`, `data/alerts.json` |
| Evidence registry | `claude/findings.md` |
| Position doctrine | `claude/ips_case_study.md` |
| Minute-data caveats | `spikes/minute_data.md` |
| Open work | `TODO.md` |
