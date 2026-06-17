---
title: Risk Manager Report
date: "2026-06-17"
---

## Model: deepseek/deepseek-v4-flash

# Risk Management Memo: Downside Protection & Geopolitical Risk Analysis

**Date:** 2026-06-17  
**Regime:** Bull Quiet (Transitional, with latent stagflation risks)  
**Portfolio:** 100% Cash ($87k)

---

## 1. Geopolitical & Macro Risk Dashboard

| Risk Event | Severity (1-10) | Probability | Primary Assets Impacted | Time Horizon |
|---|---|---|---|---|
| **Fed Hawkish Surprise** (one hike signaled) | 7 | Medium (50%) | SPY, QQQ, TLT (bearish); XLF (bullish as banks benefit from steeper curve) | Immediate (priced today) to weeks |
| **Iran Deal Fragility** (Hormuz restart stalled) | 5 | Medium (40%) | XLE, XLE puts (bearish if deal fails); GLD bullish on risk-off | Days to weeks |
| **China-Taiwan Chip Curbs** (export controls escalate) | 6 | Low-Medium (30%) | TSM, NVDA, AMD, INTC (bearish); GLDM, ^VIX bullish | Weeks to months |
| **Recession Signals** (rising unemployment, slower growth) | 8 | Medium (50% over 12 months) | QQQ, SPY, XLY (bearish); XLU, XLP, GLD (bullish) | Months (Q3-Q4 2026) |
| **BoJ Carry Unwind** (lagged risk from June 15-16) | 6 | Low (20%) | SPY, QQQ, crypto (bearish); USDJPY <140 trigger | Immediate to next 2 weeks |

**Composite View:** The market is pricing a benign environment (VIX 16.4, credit spreads tight), but the macro news aggregate shows multiple correlated risk drivers. The “grind-with-violence” scenario (50%) remains base case, but fast-crash tail (20%) is **live** due to Fed + BoJ + liquidity drain (SpaceX IPO).

---

## 2. Portfolio-Level Hedges & Safe Haven Deployment

Given current cash position, we recommend **immediate partial deployment into defensive assets** with embedded hedges for when equity exposure is added later.

### A. Safe Haven Accumulation

| Ticker | Direction | Rationale | Entry | Allocation |
|---|---|---|---|---|
| **GLD** (Gold) | Buy | Negative real rates (CPI 4.2% vs fed funds 4.25%), central bank buying, geopolitical risk. Current price $397.63 near 200-day SMA support. | Market order | 15–20% of cash |
| **TLT** (Long Treasuries) | Buy cautiously | Rates are declining (TLT uptrend), but inflation risk caps upside. Use as tactical bond exposure, not core defense. | Limit <$86 | 10–15% |
| **XLU** (Utilities) | Buy | Defensive sector, AI-driven power demand supports. Price $45.06, holding above SMA20. | Market order | 10% |
| **XLP** (Consumer Staples) | Buy | Classic recession hedge, low beta, steady dividends. Price $85.59, in uptrend. | Market order | 10% |

Total safe haven allocation: **45–55%** of cash.

### B. Equity Exposure with Integrated Hedges

If you wish to deploy any equity capital (e.g., for the “aggressive” sleeve), **do so only with protective puts.** The options chain snapshot provides liquid contracts.

#### Recommended Protective Put Portfolio (for a hypothetical $30k equity position):

| Underlying | Strategy | Strike & Expiry | Cost per Share | Max Downside Protection |
|---|---|---|---|---|
| **SPY** | Buy call + protective put collar? No – pure protective put is cleanest | SPY 760C / 720P? Simpler: buy 100 shares SPY + buy 1x SPY 260710P00719 ($5.07) | Put cost = $507 | Limits loss to ~$3,000 (4% below current) |
| **QQQ** (if tech exposure desired) | Buy 1x QQQ 260710P00701 ($10.47) per 100 shares | Cost = $1,047 | Limits loss to ~$2,500 (3.5%) |
| **NVDA** (if AI conviction) | 1x NVDA 260710P00190? But NVDA at 207.41 – use 190 put? Not in chain. Use SPY/QQQ for aggregate protection. | | | |

**Simplicity note:** For a cash-heavy portfolio, the most efficient hedge is **long SPY put spreads** or **VIX call spreads** to cover gap risk, rather than per-stock hedges.

### C. Gap Risk Tail Hedge (Crash Protection)

Given the 20% fast-crash scenario, buy a small **VIX call** or **SPY put spread** that pays off in a 5%+ one-day drop.

| Ticker | Strategy | Structure | Max Cost | Payout Trigger |
|---|---|---|---|---|
| **^VIX** (via VIX options?) Not in chain; use SPY options | Buy 1x SPY 260702P00719 (strike 719, 3% OTM) for $4.08 x 100 = $408. This offers ~$2,100 protection if SPY drops to 690. | Single put, 15 DTE | $408 | >2.9% drop |

Alternatively, buy a **QQQ 260702P00690** (not shown, but estimate low). Given small portfolio, a single SPY put is sufficient.

---

## 3. Specific Geopolitical Catalyst Plays

### Strait of Hormuz / Iran Deal
- **If reopening stalls:** Oil spikes, XLE rallies. **Short XLE via puts**? Actually, XLE is already weak. **Buy XLE calls** for a bounce? Counterintuitive – but we want protection. **We are long XLE via safe haven?** No – we avoid direct energy given volatility. Instead, **buy GLD** as a proxy for risk-off.
- **If deal succeeds:** Oil continues to fall, XLE drops further. **Avoid energy longs.** Our GLD position will suffer in risk-on, but TLT should gain on lower inflation.

### Fed Hawkish Pivot
- **One hike on the table:** Already priced somewhat. The risk is aggressive language. **Hedge with TLT puts**? TL TLT is up, so a put on TLT would profit if yields spike. But we own TLT as part of safe haven. Instead, **buy a TLT 260702P00084** (strike 84, ~2.6% OTM) for ~$0.30? Not in chain but low cost.
- **Best hedge:** Short duration bonds (SHY) or cash. We already have cash.

### Recession Signals (Rising Unemployment)
- **Local news (Virginia, Indiana, Seattle)** suggest layoffs are spreading. This is a leading indicator for consumer spending.
- **Sectors to avoid:** XLY (consumer discretionary), SPY/QQQ. **Favor:** XLP, XLU, GLD.
- **Action:** Increase allocation to XLP/XLU beyond initial targets.

### China-Taiwan Chip Export Controls
- **Bearish for TSM, NVDA, AMD.** These stocks are already showing weakness (AVGO -6% monthly, MSFT below 200-day). **Do not initiate longs.**
- **Hedging:** The SPY/QQQ protective puts already address this.

---

## 4. Recommended Portfolio (Risk-Managed Deployment)

| Asset Type | Ticker | Allocation % | Rationale |
|---|---|---|---|
| **Gold** | GLD | 20% | Core hedge against inflation/geopolitics |
| **Long Treasuries** | TLT | 10% | Tactical bond exposure (rates declining) |
| **Defensive Equities** | XLU + XLP | 20% | Recession resilience + low vol |
| **Equity (with hedges)** | SPY (or VOO) | 30% | Core growth, protected with puts |
| **Cash / T-Bills** | Cash | 20% | Dry powder for opportunities; earn 4.3% (^IRX 3.62%? T-bills higher) |

**Option Overlay (cost ~2% of equity sleeve):**
- Buy 1x SPY 260710P00719 ($5.07) per 100 shares of SPY – cost ~$507.
- Buy 1x QQQ 260710P00701 ($10.47) per 100 shares of QQQ – cost ~$1,047 if QQQ is held.
- Total hedge cost ≈ $1,550, protecting ~$74k of equity exposure for 23 days.

---

## 5. Sell / Trim / Avoid List

| Asset | Reason | Action |
|---|---|---|
| **XLE / Energy stocks** | Weakness from Iran deal, oversupply, falling oil. Avoid new longs. | If held, trim. |
| **High-beta tech (NVDA, AVGO, PLTR)** | Momentum fading, Fed hawkish, IPO liquidity drain. | Do not enter without hedges. |
| **Consumer Discretionary (XLY)** | Recession signals accumulating, unemployment rising. | Avoid. |
| **Long-duration bonds (TMF, ZROZ)** | Inflation risk still high; only use TLT modestly. | Reduce if held. |
| **Bitcoin (IBIT)** | Risk-off under Fed hawkishness, BoJ carry unwind still possible. | Not recommended now. |

---

## 6. Key Tripwires to Monitor (next 2 weeks)

- **^VIX/^VIX3M > 1.0** → backwardation = panic onset. If triggered, immediately buy puts on SPY/QQQ and reduce equity exposure.
- **HYG/LQD 63d momentum < -2%** → credit stress leading equity. Preemptive hedge increase.
- **USDJPY < 140** → carry unwind active. Reduce risk positions.
- **SPY weekly close below 730 (200-day SMA at 685? Actually 200d at 685.2, but close is 750)** – watch for a break of 740 for short-term support.

---

## Summary of Immediate Actions

1. **Deploy 50% of cash into safe havens:** GLD (20%), XLU (15%), XLP (15%) – market orders at open.
2. **Set limit orders for TLT at $85.50** (10% allocation) – a dip opportunity.
3. **Hold 40% cash** for tactical deployment during any 5%+ SPY dip (add QQQ puts prior).
4. **Do not initiate any long equity positions without protective puts.** If forced, use SPY 260710P00719.
5. **Ignore AI hype headlines:** The macro risks outweigh the AI growth story for the next 1–2 months.

**Bottom line:** The Bull Quiet regime is a trap. De-risking now, shifting to gold and defensives, and maintaining hedges will protect against the 50% probability of a significant drawdown within 6 months.