# ROADMAP — what to do next, and what not to

**The honest framing first.** Nine strategy ideas have now been ruled
out and one risk rule validated. The expected value of *more strategy
search* is low and falling — seven detectors failed for a reason that
generalises (see `RULED_OUT.md`). The highest-value remaining work is
mostly **not** finding new edges. It is:

1. things that change the *decision* rather than the *return* (horizon,
   account structure, tax),
2. verifying claims that are currently unverified,
3. making the live system actually run.

Ordered by expected value, with what would settle each.

---

## Tier 1 — could change what the user actually does

### 1.1 Tax placement and account structure ⭐ **highest value, untouched**

**Nothing in 53 findings addresses this.** For a Canadian with ~800k
plus 80k/yr, and parents with 1.8M, the placement decision plausibly
dominates anything left in strategy space:

- RRSP vs TFSA vs taxable for the *levered* sleeve specifically. LETFs
  distribute; leverage in a taxable account has different after-tax
  behaviour than in an RRSP.
- Canadian withholding on US-listed ETFs: 15% US dividend withholding is
  recoverable in an RRSP, **not** in a TFSA. That is a real, permanent
  drag on exactly the US-heavy allocation findings 41c/46d point at.
- Contribution-room sequencing across 27 years and two sleeves.

**Why it matters more than another backtest:** a 15% withholding leak on
a 1.8% yield is ~27bp/yr, permanent, risk-free to fix, and comparable in
size to the entire band-width question that consumed two sessions.

**Settles it:** model after-tax terminal wealth for the same 27y windows
under each placement. No new data needed.

### 1.2 The parents' sleeve at its own horizon

**Every projection in this repo is 27 years.** The parents are 10–15
years out with 1.8M and low sequence risk. That is a different problem
and has never been run. Finding 41c explicitly declines to extrapolate
the band choice to a shorter horizon.

**Settles it:** re-run `backtest_band_upside_us.py` and
`backtest_leverage_with_spread.py` with `HORIZON_Y=12`, `INITIAL=1.8M`.
Both are parameterised already — this is an afternoon, not a project.

Open sub-question: **decumulation.** They will start drawing. Finding 2
covered the 4% rule generically, never for this structure with a gate
and leverage.

### 1.3 Measure the financing spread instead of bounding it

Finding 51 bounds it at 0.5–1.5%/yr and finding 52 shows that range
moves 2x median terminal wealth by ~25%. **Narrowing it is worth more
than any remaining strategy question**, because it directly sets the
expectation the user plans against.

**Blocker:** no `adj_close` anywhere in the archive, so dividend yields
are assumed. **Settles it:** fetch total-return series for SPY/QQQ
(yfinance `auto_adjust`, or the fund sponsors' published distributions),
then re-run `backtest_letf_path.py` — the drift decomposition becomes a
measurement instead of an inference.

### 1.4 Relative cross-country CAPE

The one live route to an evidence-based geography call. Finding 46 ruled
out *absolute* CAPE timing (fails on persistence) but explicitly did
**not** test relative valuation with the portfolio staying fully
invested and shifting between countries. Different bet, different
failure mode.

**Blocker:** needs international CAPE (Barclays, StarCapital, or
constructed from MSCI earnings). Archive has none.

---

## Tier 2 — verification debt

### 2.1 Re-derive findings 1–17

They predate the reproduction protocol, several came from LLM analysis
rather than code, and **one has already failed to reproduce** (finding
3's overlay claim: −34.8% against a claimed −19%). They are currently
cited by later work. Either re-derive them with a tool, or mark them
explicitly unreliable. See `REPRODUCE.md` §4.

### 2.2 Re-implement finding 42c

Its numbers came from an inline script that lives only in a session
transcript. Not reproducible as it stands.

### 2.3 Equal-weight as a core holding

The one usable residue of the sector-momentum work: EW across the 11
SPDR sectors beat SPY by +0.42pp/yr with a *shallower* drawdown, no
timing. Small, free, implementable via RSP. Test properly against
cap-weight over the full history, after fees.

---

## Tier 3 — the live system

- **#1 verify EOD strategies actually execute.** The gate bug meant
  accounts 1–5 never traded; the fix is in but has not been confirmed on
  a real run. This is the highest-value *operational* item.
- **#12 per-sleeve signal outputs**, wiring breadth in as INFO per 42d.
- **#4 canary-gates-core** portfolio variant.
- User-blocked: `MAIL_*`, `TELEGRAM_*`, provider funding,
  `HEALTHCHECK_URL`.
- **Execute the backup.** The archive is packaged and SHA256-verified
  but has not been copied off-machine. 126.6 GB is the irreplaceable
  set; skip the 25.8 GB bzip2 (finding 49).

---

## Explicitly NOT worth doing

- **Regime detector #8.** Seven failed, for a reason that generalises.
  If tempted, read `RULED_OUT.md` first and state up front what would
  make this attempt different from the previous seven.
- **Tuning the band.** 41c: gating adds ~5M at p90 at *every* width from
  2–6%. The plateau is the finding; its peak is local to whichever
  market you fitted on.
- **Buying Alpaca data at $99/mo.** Their history is ~7 years, so it
  cannot reproduce the 1999–2019 capture, and the pipeline decides EOD
  where 15-minute delayed data is adequate.
- **Minute-level research generally**, unless a specific question needs
  it. Both minute TODOs (#16, #18) are now closed, and both concluded
  that the daily-resolution answer was already right.

---

## The standing principle

The user's stated goal is **conviction** — being able to hold a position
through a −70.9% drawdown without tinkering. Conviction is not built by
finding a better rule. It is built by a documented, reproducible record
of having tried and failed to find one, so that in year three the answer
to "should I change something" is `RULED_OUT.md` rather than willpower.

**Work that strengthens that record is more valuable than work that
searches for edge.** That is the opposite of the usual instinct, and it
is the correct instinct here.
