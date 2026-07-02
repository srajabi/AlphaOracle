---
title: Risk Manager Report
date: "2026-07-02"
---

## Model: deepseek/deepseek-v4-flash

## Geopolitical Risk & Downside Protection Analysis

**Date:** 2026-07-02  
**Regime:** Bull Quiet (risk-on, dollar strong, rates declining, commodities weak)  
**VIX:** 16.59 (elevated from recent lows, rising ahead of jobs data)  
**VIX/VIX3M:** 0.825 (below 1.0 – no backwardation, but compressed)  

### Key Geopolitical Catalysts & Risk Assessment

| Event | Severity (1-10) | Exposed Tickers | Impact |
|-------|----------------|----------------|--------|
| **US-Iran talks conclude, Strait of Hormuz shipping recovering** | 5 (de-escalating) | XLE (bearish oil), TLT/GLD (safe havens fade), SPY/QQQ (relief rally) | Oil falling 3rd day; shipping normalization reduces inflation risk. Bullish for equities, bearish for energy and gold. |
| **China slaps export controls on Japanese entities; EU-China trade war risks** | 7 (escalating) | TSM, NVDA, AMD, STX, WDC (supply chain risk), SPY (risk-off), GLD (safe haven) | Semiconductors exposed. Taiwan mulls AI chip export curbs aligning with US. |
| **Cooler June jobs report; Fed less likely to hike** | 6 (stagflation-lite) | TLT (bullish bonds), SPY/QQQ (mixed – lower rates support but slower growth), XLU/XLP (defensive rotation) | Unemployment dip to 4.2% but jobs miss; real rates declining. Favorable for duration, negative for cyclical earnings. |
| **AI spending boom – Mag 7 lost $2.3T in June** | 8 (sector risk) | NVDA, MSFT, AMZN, GOOGL, META, AVGO (bearish momentum), QQQ (tech-heavy), TLT (rotation) | Earnings concentration risk; any capex guidance cut could trigger 20-30% drawdown. |

### Portfolio State & Mandates

- **Current:** $87,184.98 cash (100% uninvested).  
- **Slow channel:** risk_on  
- **Fast channel:** clear  
- **Credit:** clear  
- **Canary:** half_defensive (EWA negative → signals international weakness)  

**Implication:** The system is not yet flashing emergency brakes, but the macro thesis assigns 50% probability to a “grind-with-violence” or crash scenario within 12 months. Cash is a valid position – but sitting idle in 4.2% inflation costs ~1-2% real return per year.

---

## Recommended Downside Protection & Hedges

Given the **cash heavy** state, we can deploy **low-cost tail hedges** and **defensive sector exposure** without committing to full risk-on.

### 1. Buy SPY 723 Put (July 17, 15 DTE)

| Contract | Strike | Ask | Cost per contract |
|----------|--------|-----|------------------|
| SPY260717P00723000 | $723 | $2.04 | $204 |

**Rationale:**  
- SPY trades at $745.58 (~3% above strike).  
- VIX is low (16.6) → put premiums cheap.  
- Protects against a 5-7% selloff driven by trade war escalation, AI capex deceleration, or a surprise hawkish Fed.  
- **Time horizon:** Immediate to 2 weeks (covers next jobs report and any geopolitical headline).  

### 2. Buy QQQ 696 Put (July 17, 15 DTE)

| Contract | Strike | Ask | Cost per contract |
|----------|--------|-----|------------------|
| QQQ260717P00696000 | $696 | $7.13 | $713 |

**Rationale:**  
- QQQ at $717.12, 3% above strike.  
- Tech is the most crowded and vulnerable sector: Mag 7 lost $2.3T in June, AI fear indexes spiking, and semi supply chains (TSM, China/Taiwan) are live risks.  
- A 5% tech drawdown (which happened twice in June) would be well-covered.  

### 3. Sell Cash-Secured Put on XLU (Utilities) – not in provided chain but can approximate with ETF.

**Alternative:** Buy XLU (defensive sector) outright for modest exposure.  
- XLU is now flat/neutral, with 3.2% yield.  
- If recession fears mount, utilities outperform. Fed pause benefits bond proxies.  

### 4. Avoid/Be Cautious On:

| Ticker | Reason |
|--------|--------|
| **XLE** | Oil falling on Hormuz recovery; OPEC+ raising output; momentum negative. |
| **GLD / IAU** | Precious metals in downtrend (gold -10%, silver -21%); strong dollar and falling inflation premium hurt. |
| **NVDA, AVGO, MU** | AI hardware momentum deteriorating; Morningstar warns of 30% crash; avoid until VIX term structure inverts. |
| **EWA (Australia)** | Canary half_defensive negative; RBA hiking into stagflation. |

### Summary of Near-Term Actions

| Action | Rationale | Max Risk |
|--------|-----------|----------|
| Buy 1 SPY 723 Put (Jul17) | Tail hedge at low cost | $204 |
| Buy 1 QQQ 696 Put (Jul17) | Protect tech-heavy portfolio | $713 |
| Keep $86k in cash / money market | Preserve capital for scenario C fast crash | Opportunity cost ~1-2% real |

**Total hedge cost:** ~$917 (1.05% of cash). This is an insurance premium, not an investment. If no crash occurs within 15 days, the puts expire worthless – that is the cost of protection.

### Time Critical Tripwire

**BoJ meeting (June 15-16) is already past** – no shock materialized.  
**Next live tripwire:**  
- July 29 FOMC (hike possibility).  
- Q2 earnings season (hyperscaler capex guidance).  

**If HYG/LQD 63d relative momentum turns negative** (currently +0.99%), move to full cash and add deep OTM VIX calls or TMF (3x TLT) for crash protection.

**Conclusion:** The market is in a fragile bull with multiple live geopolitical and macro risks. Use low-cost index puts as an umbrella while remaining in cash. Deploy into defensive sectors (XLU, XLP) only if credit spreads widen or unemployment rises further.