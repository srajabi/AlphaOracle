# Spike: Survivorship Bias in Backtesting

**Objective:** Understand and mitigate survivorship bias when selecting tickers for long-horizon backtesting (20-30+ years).

## The Problem

> "If we pick the mega caps, it biases the test for things that are successful"

This is **survivorship bias** - the logical error of concentrating on entities that survived some selection process while overlooking those that didn't.

### Example: AAPL Over 45 Years

We have AAPL data back to 1980. If we backtest a strategy on AAPL from 1980-2026 and it performs well, what have we learned?

**What we think we learned:**
- "This strategy works on large tech stocks"

**What we actually learned:**
- "This strategy worked on ONE company that happened to survive and become the most valuable company in the world"

**What we MISSED:**
- Companies that went bankrupt: Lehman Brothers, Enron, WorldCom, Kodak, Blockbuster
- Companies that became irrelevant: Blackberry, Nokia, Yahoo, AOL, Motorola
- Companies that underperformed: IBM, Intel (for last 5 years), Cisco (peak was 2000)

### The Core Issue

**In 1980, could you have known AAPL would be the winner?**

Probably not. There were dozens of computer companies:
- Commodore
- Atari
- Wang Laboratories
- Digital Equipment Corporation
- Compaq

**Most of them are bankrupt or irrelevant now.**

If we backtest only on AAPL, MSFT, GOOGL, NVDA - the survivors - we're testing with **perfect foresight**.

## Types of Survivorship Bias

### Type 1: Company-Level Survivorship

**Problem:** Testing only on companies that exist today

**Example:**
- Testing NVDA from 1999-2026: +27,000% return
- But in 1999, you had to pick NVDA from dozens of semiconductor companies
- Most are now bankrupt or acquired: 3dfx, ATI, S3, Cyrix, etc.

**Impact:** Massively inflated returns

### Type 2: Ticker-Level Survivorship

**Problem:** Even surviving companies had rough periods that would have stopped you out

**Example:**
- AAPL nearly went bankrupt in 1997
- Would your strategy have held through -80% drawdown?
- Or would you have sold and never bought back?

**Impact:** Backtests assume you held through disasters

### Type 3: Index Inclusion Bias

**Problem:** Testing on "S&P 500 companies" using today's constituents

**Example:**
- Today's S&P 500 includes NVDA, TSLA, META
- But these were NOT in the S&P 500 for most of their existence
- TSLA added 2020, NVDA was in/out multiple times

**Impact:** Overestimates historical index performance

### Type 4: Data Availability Bias

**Problem:** We only have data for companies that were important enough to track

**Example:**
- We have 53 years of MTZ (MasTec) data
- But we don't have data for thousands of construction companies that failed
- MTZ survived BECAUSE it was successful enough to stay listed

**Impact:** Can't test on the full opportunity set

## How Our Current Approach Handles This

### ✅ Portfolio Rotation Universe: MOSTLY CLEAN

```python
CURRENT = ["QQQ", "VOO", "GLD", "TLT", "XLE", "XLU"]
```

**Why this is good:**

1. **All are ETFs/Index products** - No single-company risk
2. **Indexes rebalance automatically** - Losers get removed, winners added
3. **QQQ tracks Nasdaq 100** - Tests the methodology of "hold top 100 tech stocks", not picking specific winners
4. **VOO tracks S&P 500** - Tests the methodology of "hold top 500 US companies"
5. **Sector ETFs rebalance** - XLE holds top energy companies in each era, not just today's winners

**Remaining bias:**
- We're testing indexes that survived (QQQ, VOO, XLE did well)
- We're not testing indexes that failed or closed
- But this is MUCH less severe than individual stock bias

**Verdict:** ✅ **Acceptable for rotation strategies**

The bias is minimized because we're testing INDEX METHODOLOGIES, not stock-picking.

---

### ⚠️ Mega Cap Universe: SEVERE BIAS

```python
MEGA_CAPS = ["AAPL", "MSFT", "AMZN", "GOOGL", "NFLX", "NVDA", "AMD", "INTC", "TSM", "QQQ"]
```

**Why this is problematic:**

1. **Every single stock here is a survivor**
2. **Every single one had major success** (that's why they're mega caps today)
3. **We're ignoring all the failed tech companies** from 1980-2026
4. **Cannot generalize findings** to "tech stocks" - only to "successful tech stocks"

**Example comparison:**

| Era | Mega Caps That Would Have Been Top Holdings | Today's Status |
|-----|---------------------------------------------|----------------|
| **1980s** | IBM, DEC, Wang Labs, Commodore | Only IBM survives (underperformer) |
| **1990s** | Microsoft, Intel, Cisco, Oracle, IBM | Only MSFT, ORCL are still giants |
| **2000s** | Microsoft, Intel, Cisco, Dell, HP | MSFT only mega today |
| **2010s** | Apple, Google, Amazon, Facebook, Netflix | Most still mega (recency bias!) |
| **2020s** | Apple, Microsoft, NVDA, Tesla, Meta | We don't know yet |

**The illusion:**

If we backtest on today's mega caps over 30 years, we might conclude:
- "SMA trend following has a 2.0 Sharpe on tech stocks"

But the REAL result would be:
- "SMA trend following has a 2.0 Sharpe on tech stocks that we selected because they had 30-year trends"

**Circular logic!**

**Verdict:** ❌ **SEVERE BIAS - Results not generalizable**

---

### Semiconductor Universe: EXTREME BIAS

```python
SEMICONDUCTORS = ["NVDA", "AMD", "INTC", "MU", "KLAC", "TSM", "WDC", "STX"]
```

**Why this is the WORST:**

Semiconductors have the highest failure rate of any sector:
- 1980s: Hundreds of chip companies
- 1990s: Consolidation wave, dozens failed
- 2000s: More consolidation
- 2010s: Only giants survive
- Today: ~8 major players globally

**Companies that failed or were acquired:**

| Decade | Failed/Acquired Semiconductor Companies |
|--------|----------------------------------------|
| 1980s-90s | National Semiconductor, Zilog, Mostek, Fairchild (1st time), Cyrix, Chips & Technologies |
| 1990s-2000s | 3dfx, S3, Matrox, Trident, SiS, VIA Technologies (graphics division) |
| 2000s-2010s | ATI (acquired by AMD), Nvidia almost failed 2008, Freescale bankruptcy, Agere Systems |
| 2010s-2020s | Broadcom (acquired), Marvell struggles, GlobalFoundries exits leading edge |

**If we backtest only on survivors (NVDA, AMD, TSM):**
- These are the companies that DEFINED the winners
- Of course strategies work on them
- But could we have picked them in 1999?

**Verdict:** ❌ **EXTREME BIAS - Totally invalid for generalization**

## How to Properly Handle Long-Horizon Backtests

### Approach 1: Use Index Products (BEST for our use case)

**Strategy:** Only test on indexes and sector ETFs that rebalance automatically

**Universe:**
```python
NO_BIAS_UNIVERSE = [
    # Broad indexes
    "VOO",   # S&P 500
    "QQQ",   # Nasdaq 100
    "VTI",   # Total US Market

    # Sector ETFs (auto-rebalance)
    "XLE",   # Energy
    "XLF",   # Financials
    "XLU",   # Utilities

    # Asset classes
    "GLD",   # Gold
    "TLT",   # Treasuries
]
```

**Why this works:**
- Indexes automatically remove losers and add winners
- Tests the METHODOLOGY ("hold top 500 stocks") not stock picking
- Represents the investable universe in each era
- Minimal survivorship bias

**Limitation:**
- Can't test single-stock strategies
- But that's actually good - forces us to think in terms of indexes

**Recommendation:** ✅ **This is what we're already doing. Keep it.**

---

### Approach 2: Use Historical Constituents (COMPLEX but correct)

**Strategy:** For each year, use the constituents from THAT year, not today

**Example:**
- 1990 backtest: Use 1990 S&P 500 constituents
- 2000 backtest: Use 2000 S&P 500 constituents
- 2010 backtest: Use 2010 S&P 500 constituents

**Why this works:**
- No hindsight bias
- Tests strategy on the stocks that WERE available at the time
- Includes companies that later failed

**Limitations:**
- Requires historical constituent data (hard to get)
- Requires rebalancing logic for additions/removals
- Much more complex to implement

**Recommendation:** ⚠️ **Only if we need single-stock strategy validation**

---

### Approach 3: Survivorship-Adjusted Datasets (IDEAL but expensive)

**Strategy:** Use commercial datasets that include delisted companies

**Providers:**
- CRSP (Center for Research in Security Prices)
- Compustat
- QuantConnect (includes delisted stocks)

**Why this works:**
- Includes companies that went bankrupt
- Includes companies that were acquired
- True historical opportunity set

**Limitations:**
- Expensive ($10k-$100k+ per year)
- Complex data management
- Overkill for our use case

**Recommendation:** ❌ **Not needed for portfolio rotation strategies**

---

### Approach 4: Limit Lookback to Recent Eras (COMPROMISE)

**Strategy:** Only backtest 10-15 years, not 30+

**Rationale:**
- Last 15 years: Most mega caps still existed and were already successful
- Reduces (but doesn't eliminate) survivorship bias
- Still captures GFC, COVID, 2022 bear

**Example:**
```python
# Instead of 30-year AAPL backtest
# Do 15-year QQQ backtest (which INCLUDES Apple)
```

**Recommendation:** ⚠️ **Reasonable compromise if you must test individual stocks**

But better to just use indexes.

## What This Means for Our Backtesting

### ✅ Current Rotation Strategy: VALID

```python
["QQQ", "VOO", "GLD", "TLT", "XLE", "XLU"]
```

**Why it's valid:**
- All index products that rebalance
- We're testing "rotate between asset classes" not "pick winning stocks"
- Minimal survivorship bias
- Results ARE generalizable

**27-year backtest of dual_momentum_rotation:** ✅ **Trustworthy**

---

### ❌ Proposed Mega Cap Testing: INVALID

```python
["AAPL", "MSFT", "NVDA", "AMD", "GOOGL", "AMZN"]
```

**Why it's invalid:**
- All survivors selected with hindsight
- Results NOT generalizable to "tech stocks"
- Would give false confidence

**Backtest results would be meaningless** for forward deployment

---

### ⚠️ Semiconductor Testing: USE WITH CAUTION

```python
["NVDA", "AMD", "INTC", "MU", "KLAC", "TSM"]
```

**If we must test:**
- Use **SMH** (semiconductor ETF) instead of individual stocks
- Or use **SOXX** (iShares semiconductor ETF)
- These include the sector winners automatically

**Better approach:**
```python
["SMH", "SOXX"]  # Semiconductor ETFs (if we add to watchlist)
```

This tests "hold semiconductor sector" not "pick NVDA"

## Rules for Avoiding Survivorship Bias

### Rule 1: Prefer Indexes Over Individual Stocks

❌ **Wrong:** "Test trend following on AAPL"
✅ **Right:** "Test trend following on QQQ" (which includes Apple + 99 others)

### Rule 2: If Testing Stocks, Use Short Lookbacks

❌ **Wrong:** "NVDA trend following over 27 years"
✅ **Right:** "NVDA trend following over last 5 years" (still biased but less so)

### Rule 3: Never Optimize on Survivor Universe

❌ **Wrong:** "Test 20 strategies on AAPL/MSFT/NVDA and pick the best one"
✅ **Right:** "Test one strategy on QQQ/VOO and accept the results"

### Rule 4: Test on Rebalancing Products

❌ **Wrong:** "Test on today's S&P 500 stocks over 30 years"
✅ **Right:** "Test on VOO (which rebalances) over 30 years"

### Rule 5: Be Skeptical of Amazing Results

If a strategy has:
- Sharpe > 3.0 over 20+ years on individual stocks
- Max drawdown < 10%
- Win rate > 70%

**It's probably survivorship bias.**

Real strategies on real opportunity sets don't perform that well.

## Recommendations for Each Testing Phase

### ✅ Phase 1: Core Rotation (Current)

**Universe:** `QQQ, VOO, GLD, TLT, XLE, XLU`

**Survivorship bias:** Minimal (all are indexes)

**Action:** ✅ **Proceed with confidence**

Results from this testing ARE generalizable to forward deployment.

---

### ⚠️ Phase 2: Extended Rotation

**Universe:** `VOO, QQQ, VTI, XLE, XLF, GLD, IAU, TLT, XLU, VGK, EWA`

**Survivorship bias:** Minimal (all are ETFs/indexes)

**Action:** ⚠️ **OK to test, but don't overfit**

If we test 5 universe variations and pick the best one, that's data mining.

---

### ❌ Phase 3: Mega Cap Single-Asset

**Universe:** `AAPL, MSFT, AMZN, GOOGL, NVDA, AMD, INTC, TSM, QQQ`

**Survivorship bias:** SEVERE

**Action:** ❌ **Skip individual stocks, use QQQ instead**

Or if we must test individual stocks:
- Limit to last 10 years
- Don't generalize findings
- Label results as "survivor-biased"

---

### ❌ Phase 4: Semiconductor Testing

**Universe:** `NVDA, AMD, INTC, MU, KLAC, TSM, WDC, STX`

**Survivorship bias:** EXTREME

**Action:** ❌ **Replace with semiconductor ETF**

**Better alternative:**
```python
# Add to watchlist.csv:
SMH,Semiconductors,VanEck Semiconductor ETF
SOXX,Semiconductors,iShares Semiconductor ETF

# Then test:
python3 backtesting/run_backtests.py --tickers SMH,SOXX,QQQ
```

This tests "hold semiconductor sector" without survivor bias.

---

### ⚠️ Phase 5: High-Vol Swing Trading

**Universe:** `TSLA, PLTR, CRWD`

**Survivorship bias:** SEVERE + short history

**Action:** ⚠️ **Use only for recent-period research (5 years max)**

These are the companies that survived the growth/startup gauntlet. Thousands didn't.

## Bottom Line

### What We're Doing Right ✅

1. **Using ETFs/indexes for rotation strategies** - Correct approach
2. **27-year QQQ backtest** - Valid because QQQ rebalances
3. **Testing on 6 tickers** - Good, avoids overfitting

### What We Should Avoid ❌

1. **Backtesting individual stocks over 20+ years** - Survivor bias
2. **Testing on "today's mega caps"** - Selected with hindsight
3. **Semiconductor survivor universe** - Extreme bias

### Adjusted Recommendation

**For any strategy requiring 20+ year validation:**
- ✅ Use index ETFs only
- ✅ Current 6-ticker universe is perfect
- ❌ Don't add individual stocks to long-horizon tests

**For single-asset strategies:**
- Use 5-10 year horizons maximum
- Or test on QQQ instead of individual stocks
- Clearly label results as "survivor-biased" if using mega caps

**For sector strategies:**
- Add sector ETFs (SMH, SOXX, etc.) not individual stocks
- These ETFs rebalance automatically

## Action Items

1. ✅ **Keep current 6-ticker universe for production**
2. ❌ **Remove individual stocks from 20+ year testing**
3. ⚠️ **If testing single stocks, limit to 5-10 years and label as biased**
4. ✅ **Add sector ETFs to watchlist if we want sector testing**
5. ✅ **Document that our rotation results are NOT survivor-biased**

## Final Verdict

**Our current approach with QQQ, VOO, GLD, TLT, XLE, XLU is methodologically sound.**

The results from `dual_momentum_rotation` over 27 years ARE valid for forward deployment because:
- We're testing index rebalancing methodologies
- Not cherry-picking individual stock winners
- The universe represents the investable opportunity set

**This is actually a strength of our approach, not a weakness.**

Most retail backtests fail because they test on survivor-only universes. We're doing it right.
