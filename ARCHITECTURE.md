# ARCHITECTURE - what this system actually is

Written after 31 findings, because the project sprawled and the goal
needs restating in light of what the evidence says rather than what we
hoped.

`MANIFESTO.md` is why. `PLAYBOOK.md` is what to do today. This is the
shape of the machine.

---

## The reframe

Every win in `claude/findings.md` is risk or cost management. Not one is
prediction.

| Result | Kind | Verdict |
|---|---|---|
| Depression: 3x overlay 1.44x vs buy-hold 0.0225x (30) | risk | **won** |
| Fee reduction worth ~1.19M over 10y (22) | cost | **won** |
| Unhedged CAD cushions drawdown 9pp (21) | structure | **won** |
| Leverage survives high rates (31) | risk | **won** |
| Macro timing (19, 20) | prediction | failed |
| 1x trend overlay alpha (3, 24, 27) | prediction | failed |
| "Overdue for a crash" (28) | prediction | failed |
| VIX level predicts returns (29) | prediction | failed |

**So: this is not an alpha-hunting system. It is a risk-budgeting system
with a human executor.**

That is a demotion in ambition and an upgrade in honesty. Controlling
risk is what turned a 97.75% permanent loss into a 44% gain in 1929-1935
- a bigger effect than any predictive edge we have found or are likely
to find.

### The goal, restated

> Decide **how much risk to hold**, per sleeve, and tell a human when
> that answer changes.

Not "predict the market". Everything downstream follows from that.

---

## ONE control, not two - corrected by finding 32

**The section below proposed two controls. Testing killed the second.**

Finding 32 built vol targeting and compared it to the trend gate at
EQUAL AVERAGE LEVERAGE, which is the only fair comparison. The gate won
on return and drawdown at every comparable leverage (16.01% vs 14.03% at
~1.4x; 20.89% vs 15.51% at ~2.2x), and gate+vol always beat vol alone -
meaning the gate was doing the work. Vol targeting also cost 2-6x the
turnover.

**The design is therefore ONE control - the trend gate - plus a fixed
leverage ceiling chosen as a judgement about tail tolerance, not fitted.**

Finding 4's vol-targeting claim tested QQQ from 1999 and should not be
generalised beyond that. The rest of this section stands as the record
of what was proposed and why it was wrong.

## Two controls, not a policy matrix (SUPERSEDED - see above)

The tempting design is a regime matrix: in regime A do X with the safe
sleeve and Y with the aggressive. Resist it. Four regimes x two sleeves
x three leverage levels is ~24 fitted decisions against **~32
independent observations** (finding 29), on a scoreboard already at
**PBO 0.36**. That produces a beautiful backtest and no edge.

Two mechanism-level controls, both already evidenced here:

**1. Trend gate - decides IN or OUT.**
Daily check, 200-day SMA, **+/-4% bands** (finding 41c supersedes the
5% written here originally; 4% has the top p90, the shallowest worst
drawdown and the least trading on US data). Finding 24: bands invert the
frequency answer and cut trading to 0.7 round trips/yr, fewer than a
monthly check. Plateau 2-6%, cliff at 8%.

**2. Volatility target - decides HOW MUCH.**

> **RULED OUT BY FINDING 32.** Volatility targeting LOSES to the trend
> gate. This section describes an architecture that was subsequently
> tested and rejected - it is kept for the reasoning, not as a
> specification. The system has ONE control, the gate. Leverage is a
> fixed 2x with a permanent gate (findings 30, 37, 52), not a
> vol-scaled quantity.

Leverage scales inversely with realised volatility. Finding 4 already
identified this as the only leverage scheme that survived the dot-com
test (vol_target_qqq_2x Sharpe 0.67 vs SMA-rule 0.36, -57% vs -90%).
Finding 31 ranked volatility drag as the top threat to a leveraged
sleeve, rate-independent. This is the mechanism-level answer to that
threat, and it is ONE continuous parameter rather than a regime
classifier.

Together: the gate says whether to be exposed, the vol target says how
much. Both are functions of price, so neither carries publication lag
(findings 19, 20).

---

## Sleeve design

### Sleeve 1 - base. "I will be fine."

- Global equity, CAD-denominated, currency-UNHEDGED (finding 21).
- **1x. No overlay.** Findings 3, 24 and 27 all agree the overlay costs
  return at 1x, and with 80k/yr of contributions and no withdrawals a
  drawdown is a discount, not a loss (finding 23).
- Policy: always invested. The only decision is contribution size.

### Sleeve 2 - aggressive. "Compound hard, survive the tail."

- Leveraged equity, gated and vol-targeted.
- **Never leveraged buy-and-hold.** Finding 30 is categorical: 3x
  buy-and-hold through 1929-1935 is a 97.75% permanent loss.
- Leverage ceiling is a judgement, not a fit. 3x has the higher mean
  (22.41% vs 16.68% over the century) and the worse tail; 2x ended
  BETTER than 3x through the Depression (1.69x vs 1.44x) with far less
  drawdown.
- Sized so that losing most of it does not change sleeve 1's outcome.
  Note the current sizing rule (finding 14) is built on OVERNIGHT GAP
  risk, which is the wrong risk - a gap is not what threatens the plan,
  a 70% sleeve drawdown is.

---

## What the machine does, in order

```
prices, macro, vintage macro
   -> indicators           deterministic, price-based, no API dependency
   -> regime state         discrete, few states, mechanism-defined
   -> risk budget          per sleeve: in/out, and how much leverage
   -> alert on CHANGE      Telegram for ACTION, email for the record
   -> human executes       manually, in the real account
   -> attribution monitor  did live match the model? off_script beats
                           conviction
```

The paper accounts are the forward test of the model, not of the
returns. `off_script` is the signal that matters; P&L over months cannot
distinguish skill from luck (finding 29's power problem again).

---

## What this system is NOT

- **Not a predictor.** Four separate attempts failed. Stop rebuilding
  them under new names.
- **Not high frequency.** Monthly-to-daily decisions. The minute archive
  is for execution, gap and path-dependency questions (findings 18, 24),
  not for signal generation.
- **Not automated trading.** The human executes. The system's output is
  an instruction and a reason.
- **Not a fee-free lunch.** The largest certain edge found so far is
  cost reduction (finding 22), and it needed no model at all.

---

## Open architectural questions

1. **Vol targeting is not yet implemented or tested here.** Finding 4
   cites it from an earlier session; it has not been re-derived under
   the current standards (live warmup, rate-correct financing,
   multi-regime reporting). That is the highest-value open build.
2. **How do the two controls interact?** Gate and vol target could be
   redundant - both de-risk in a crash. The test is whether vol
   targeting alone matches gate+vol, in which case drop the gate.
3. **What triggers a leverage change in practice?** A continuously
   varying target means continuous rebalancing. Needs a deadband, or
   turnover eats the edge.
