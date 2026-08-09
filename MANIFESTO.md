# MANIFESTO - why this project exists

The thing every other document in this repo is downstream of. If a
finding, a strategy or a backtest does not serve what is written here,
it is a hobby, not the project.

`PLAYBOOK.md` is what to do. `claude/findings.md` is what we know. This
is what we are trying to achieve and how we will know if we failed.

---

## The situation

- 38 years old. Principal data scientist, ~300k CAD/yr. 15 years in a
  quantitative profession. Good at math.
- ~800k CAD invested. RRSP maxed.
- Canadian, spends CAD, retires in Canada.
- **Horizon 27 years.** Not retiring willingly - this capital is
  insurance against being unable to work, not a retirement date.
- Income continues and likely grows. Business, moonlighting, more
  comp - unknown but positive expectation.
- **Ongoing contributor, zero withdrawals for decades.**

That last line is the single most important fact in this document, and
most investment advice is written for people it does not describe.

## The parents - a SEPARATE mandate, not a smaller copy

- ~1.8M CAD. **10 years from retirement.** They will withdraw.
- Goal: double in 10 years (~7.2%/yr nominal).

They are the opposite case. They have sequence risk; a -40% drawdown at
year 8 is permanent damage because they sell into it. Their son does not
have that problem and must not be given their solution, nor they his.

**The same overlay is correct for them and wrong for him.** That is not
a contradiction. It follows from withdrawals.

## The actual question

> With a quantitative background, 82 GiB of minute data, point-in-time
> macro, six paper accounts and a backtesting lab - can I beat buying
> and holding a global equity index for 27 years?

And the honest sub-question underneath it:

> If the answer is no, will I accept that and hold, with peace of mind
> that I checked properly?

This project is as much about **earning the right to hold** as about
finding an edge. A rigorously-tested "just hold XEQT" is a real
deliverable, not a failure. The single largest destroyer of long-horizon
returns is selling during a drawdown, and a person who has personally
measured the thing is far more likely to sit still.

## The benchmark, stated so it can beat us

**100% XEQT, bought and held, contributions continued, never sold.**

Any strategy must beat that on **terminal wealth after tax and costs**
over the full period. Not on Sharpe. Not on drawdown. Not on a
flattering sub-window.

Rules:

1. **Drawdown reduction is not, by itself, success.** With no
   withdrawals for 27 years and contributions arriving throughout, a
   drawdown is a purchase opportunity, not a loss. Findings 1, 19 and 20
   all show the same shape: the overlays we have tested trade return for
   drawdown. That trade is **backwards for this mandate** and correct
   for the parents'.
2. **Statistical significance before adoption.** No promoting a strategy
   on a handful of forward months. n=10 has reversed on us before.
3. **After tax, after cost, after slippage.** A 0.4% MER difference over
   27 years is real money and is a *guaranteed* edge, unlike alpha.
4. **The paper accounts are evidence, not proof.** Off-script in the
   attribution monitor beats conviction, ours or anyone's.

## Two sleeves - purpose, not percentages

- **Sleeve 1 - the base.** Global equity, CAD-denominated,
  currency-UNHEDGED (finding 21: unhedged USD is a hedge for a Canadian,
  corr -0.569 with SPY, -41.82% maxDD vs -50.79%). This is the "I will
  be fine" sleeve. It should be boring and cheap.
- **Sleeve 2 - the swing.** Aggressive, leveraged, trend-gated. Sized so
  that losing most of it does not change the outcome of sleeve 1.

**Sizing follows from a question, not a round number:** how much can
sleeve 2 lose without changing whether sleeve 1 gets there? Note the
current sizing rule (finding 14) is built on *overnight gap* risk, which
is the wrong risk for this - a gap is not what threatens the plan, a
70% sleeve drawdown is.

## Named fears, so we test them instead of feeling them

- An AI capex boom that unwinds - a Gartner-cycle top in the most
  concentrated part of the index.
- Choppy, directionless, headline-driven markets: tariffs, oil, war.
  **This is the specific enemy of trend following**, and of leveraged
  trend following especially, where whipsaw costs the leverage *and*
  volatility decay from daily reset.
- Concentration risk in a US-only index at historically high valuations.

## What would make this project a success

1. A rule the user actually follows for 27 years.
2. Evidence, in this repo with numbers, that it beats or matches 100%
   XEQT after costs - or honest evidence that it does not.
3. A separate, defensible answer for the parents' 10-year withdrawal
   mandate.
4. Enough peace of mind that a -40% drawdown does not cause a sale.

## What would make it a failure

- Finding an edge in-sample and discovering it was a fitted parameter.
- Optimising drawdown for a mandate that does not care about drawdown.
- Promoting a strategy off a short forward run.
- Building elaborate machinery and not being able to answer, plainly,
  whether to hold XEQT or not.
