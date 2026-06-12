# Data ROI Math + The Path to Managing Other People's Money (Canada)

User questions (2026-06): ROI hurdle for paid data on $100k; how to start a
hedge fund; how to prove custody-worthiness; licensing/compliance in Canada;
how to learn; what experiments to run.

NOT legal advice - educational summary; talk to a securities lawyer before
taking anyone's money.

## 1. Data ROI math ($100k account)

| Spend | Annual | Hurdle on $100k | Hurdle per month |
|---|---|---|---|
| $100/mo | $1,200 | +1.20%/yr of NET edge | ~0.10%/mo |
| $200/mo | $2,400 | +2.40%/yr of NET edge | ~0.20%/mo |

Context from our own findings: validated strategies carry +3 to +7%/yr
excess CAGR over SPY (zero-cost, gold-friendly window). So at $100k,
$100/mo eats ~1/6 to 1/3 of the excess; $200/mo eats up to 2/3. The hurdle
scales inversely with capital: at $500k, $100/mo is 0.24%/yr (noise).

**The smarter structure: data for RESEARCH is a one-time cost, not a
subscription.** Buy 1-2 months ($100-400 total), download the full history,
backtest, cancel; re-subscribe only if a strategy validates and goes live
(live signals need fresh chains). One-time $300 on $100k = 0.3% once -
trivially justified if it answers "is there a VRP sleeve worth +1-3%/yr".

"What % return can I get per month?" is the wrong frame - monthly return
targets are how retail blows up. The right frame: does the data purchase
raise the portfolio's expected ANNUAL edge by more than its annual cost,
with validation evidence. Run the experiment (sec. 6) before subscribing.

## 2. Starting a "hedge fund" in Canada - the real ladder

Regulatory reality (NI 31-103, verified 2026-06): managing other people's
money requires registration. Pooled fund = you need BOTH:
- **Portfolio Manager (PM)** registration - the firm; you as **Advising
  Representative** need **CFA charter + 12 months relevant experience**
  (within 36 months prior), or CIM designation + 48 months.
- **Investment Fund Manager (IFM)** registration - minimum capital
  **$100,000**, compliance officer, insurance, audited financials.
- Fund sold via offering memorandum under accredited-investor exemptions
  (NI 45-106): investors need ~$1M financial assets or $200k+ income.
- Realistic all-in operating cost: $50-150k+/yr (legal, audit, compliance,
  registration). Breakeven AUM at 1-2% fees: **$5-15M minimum**, sensibly
  $20M+.

**The ladder actually climbed by people who did it:**
1. Years 0-3: build an AUDITED-QUALITY personal track record (below) +
   CFA Level 1-3 in parallel.
2. Year 2-4: either join an existing PM firm as an AAR->AR (their
   compliance umbrella, their capital, your strategies), or find a
   platform/seeder. This is how most quant managers actually start - NOT
   by founding a fund at $500k AUM.
3. Year 4+: with CFA + 12mo experience + verifiable track record + $10M+
   of committed interest, THEN incorporate, register, launch. Securities
   lawyer first (Canadian fund-formation shops: BLG, McMillan, Fasken,
   AUM Law).

**What NOT to do:** informally pool friends'/family's money "to build the
track record" - that's unregistered advising/dealing, an enforcement
action, and a permanent bar from the registered route. The only money you
can run unregistered is your own.

## 3. Proving you can hold money (the track record)

What allocators/regulators accept:
- **Real capital, third-party verifiable**: broker statements (Alpaca/IBKR
  exports), ideally GIPS-composite-style monthly returns, eventually
  auditor-verified. Size matters less than length + verifiability + the
  process documentation around it.
- Paper trading does NOT count for marketing - but it's the correct
  GATE for which strategies get the real (small) capital that does count.
- 3-5 years of real returns is the currency. Start the clock as early as
  prudent, however small.
- Force multipliers we already have: the public research site (process
  transparency), the validation gauntlet (institutional-grade rigor is
  rare at retail and allocators notice), the findings registry +
  IPS-to-be (documented process = operational due diligence answers).

## 4. Learning resources

- **Regs**: NI 31-103 + Companion Policy (OSC/ASC sites); NI 45-106
  exemptions; OSC LaunchPad (innovation office - they answer questions);
  PMAC (Portfolio Management Association of Canada).
- **Credential**: CFA program is THE registration-relevant credential in
  Canada (AAR at Level 1 + 24mo; AR at charter + 12mo).
- **Books**: Ted Seides "So You Want to Start a Hedge Fund"; Carver
  "Systematic Trading" (we apply it already); Ilmanen "Expected Returns".
- **Podcasts**: Capital Allocators (Seides - the allocator's view of
  managers), Meb Faber Show, Flirting with Models (quant managers on
  process).

## 5. The experiments to run

1. **Data ROI experiment** (answers sec. 1 empirically): one month of
   Theta Data (~$40-80), download SPY/QQQ chains 2012+, backtest the VRP
   sleeve through the gauntlet with honest option spreads, measure expected
   net edge vs the $1.2k/yr hurdle. Go/no-go with numbers.
2. **Attribution backfill** (no spend): we already have months of Alpaca
   account history - reconcile every account's live curve against its
   strategy's bootstrap bands retroactively. Were we ever off-script?
3. **Track-record infrastructure** (no spend): GIPS-style monthly return
   composites per account computed in the workflow from day one - the
   evidence file for sec. 3, cheap to start now.
4. **Graduation criteria experiment**: write the IPS with predefined
   promotion rules (e.g. 6mo on-script + gauntlet survival), then let the
   paper accounts compete for promotion. Makes the fund-track question
   empirical.
5. **Meta-allocator A/B**: static lab_winners_blend vs dynamic inverse-vol
   sleeve weights - backtest first; forward-test only on user approval.
6. **Decay alarms**: monthly CI re-validation; first alarm = first real
   test of our process discipline.
