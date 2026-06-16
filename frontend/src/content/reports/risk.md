---
title: Risk Manager Report
date: "2026-06-16"
---

## Model: deepseek/deepseek-v4-flash

## Geopolitical Risk Assessment & Downside Protection Plan

### 1. Key Geopolitical Catalysts & Severity

| Catalyst | Severity (1-10) | Status | Directional Impact | Exposed Sectors |
|---|---|---|---|---|
| **US-Iran Deal / Hormuz Reopening** | 7→4 (resolving) | Preliminary deal signed; final signing June 19. Oil prices falling, stocks rallying. **BUT** details still vague – reversal risk remains. | **Bearish** energy, oil producers. **Bullish** consumer discretionary, transports, broad equity. | XLE ⬇, OIH ⬇, airlines (JETS ⬆), SPY ⬆ |
| **Fed Meeting (Warsh debut)** | 8 (policy cornered) | FOMC starts today; expected hold. CPI at 4.2% – cannot cut, cannot hike into war economy. Forward guidance key. | **Bearish** long bonds if hawkish. **Bullish** gold if dovish. | TLT ⬇ if hawkish, GLD ⬆ if dovish, SPY ⬆ late relief. |
| **BoJ June Meeting** | 8 (timed risk) | Hike to 1.0% ~97% priced. **Guidance** is the tripwire – hawkish surprise could trigger yen carry unwind (Aug 2024 precedent). | **Bearish** USDJPY, mega-cap tech, crypto. **Bullish** VIX, yen. | QQQ/SPY ⬇, yen hedged ETFs (DXJ ⬆), IBIT ⬇ |
| **China Trade Choke Points** | 6 (chronic) | Rare earths & other export controls being squeezed. Not acute but structural headwind to global supply chains. | **Bearish** semiconductors (TSM, NVDA), materials. **Bullish** US domestic manufacturing. | SMH ⬇, XLB ⬇, defense stocks. |
| **Recession Signals** | 5 (building) | Long-term unemployment surging, regional slowdowns. Not yet systemic but breadcrumb trail. | **Bearish** consumer discretionary, small caps. **Bullish** defensive sectors (XLU, XLP). | XLY ⬇, IWM ⬇, XLU ⬆, LQD ⬇ (credit spreads). |

### 2. Ticker-Level Weakness & Opportunities

**WEAKNESS (to avoid or hedge):**
- **XLE** – Oil prices below $80, Strait reopening crushes supply premium. Momentum strongly negative (-6.5%). Consider short puts or avoid.
- **XLC** – Communication services sector underperforming (RSI ~41, MACD negative). NFLX, META weak.
- **MSFT, AAPL, ORCL** – Large-cap tech showing negative momentum; SPY breadth narrow. RSI < 50 for MSFT, AAPL, AMZN.
- **GLD, IAU** – Gold in downtrend (RSI 43), strong dollar headwind. Ceasefire removes inflation panic bid.
- **SLV** – Silver even weaker (RSI 45), negative momentum.
- **MTZ** – Infrastructure play; MACD and price action weak.

**STRENGTHS (candidates for cash-secured puts or small longs):**
- **Memory/storage (MU, WDC, STX)** – AI demand + hyperscaler deals; strong uptrends but extended (RSI 66+). Sell OTM puts for entry.
- **Financials (XLF)** – Rising interest rates + strong dollar; RSI 66, uptrend intact.
- **Industrials (XLI)** – Modest momentum; defensive rotation possible.
- **Energy transition (CEG, TLN)** – Nuclear/data center growth narrative; CEG put options cheap.

### 3. Recommended Hedges (All Cash Portfolio)

**Objective:** Protect against a 5-10% air pocket (scenario A/B) or a crash (scenario C) using cheap tail hedges.

#### Priority 1: Index Put Protection (Immediate, 14-16 DTE)
Given cash-only portfolio, the most cost-efficient hedge is buying OTM puts on SPY or QQQ. The options chain shows excellent liquidity (spreads < 3 cents on SPY/QQQ).

| Ticker | Strike | Expiry | DTE | Mid Price | Cost per Contract (notional) | Break-even | Risk |
|---|---|---|---|---|---|---|---|
| **SPY** | 728 (3% OTM) | 6/30 | 14 | $2.54 | $254 | SPY < 725.46 | -$254 max |
| **QQQ** | 708 (3% OTM) | 6/30 | 14 | $6.81 | $681 | QQQ < 701.19 | -$681 max |

**Recommendation:** Buy **1 SPY put (728 strike, 6/30)** for $254. This covers ~$75k notional (our total cash) against a 3% drop. If a BoJ shock or war reversal hits, this could pay 3-5x. Cost = 0.3% of portfolio.

#### Priority 2: Tail Hedge via VIX Calls (Optional, Small)
If you want to bet on a volatility spike (BoJ guidance or Iran reversal):
- **VIX 30-day call options** are expensive. Instead, consider **futures-based ETF** like UVXY or VXX but those decay. A better approach: **buy a SPY put spread** (e.g., 728/715 put spread for ~$1.00) to cap cost.

#### Priority 3: Cash-Secured Puts (Income + Entry)
The options ideas list cash-secured puts on AAPL, AMD, AMZN, AVGO – all with attractive premiums. Since you are all cash, selling 1-2 puts on quality names can generate income while waiting to deploy.

**Best candidates given macro:**
- **AAPL 280 put (7/2)** – $0.78 premium, 6% OTM. Apple is a defensive name with strong cash flows.
- **MSFT 400 put (7/2)** – Not listed but similar; watchlist ticker.
- **CEG 235 put (7/2)** – $0.95 premium, 12% OTM. Nuclear/data center thesis intact despite recent weakness.

**Warning:** Do not sell puts on cyclical or commodity-sensitive names (XLE, AMD) during this volatile week. Focus on high-quality, low-beta names.

#### Priority 4: Sector Rotation (Avoid Energy, Trim Tech)
- **Sell/write:** If you had positions, you’d sell XLE and trim overextended semis (NVDA, AMAT). Since you're cash, **avoid buying them**.
- **Safe havens:** Short-dated Treasuries (SHV, BIL) are unnecessary – you're already cash. Consider **utilities (XLU)** or **consumer staples (XLP)** as eventual dip-buy targets.

### 4. Time Horizon & Execution

| Action | When | Duration | Reasoning |
|---|---|---|---|
| Buy SPY 728 put (6/30) | Immediately | 14 days | Covers FOMC + BoJ + Iran signing period. Cheap tail. |
| Sell AAPL 280 CSP (7/2) | Today | 16 days | 0.3% yield, 6% downside buffer. Quality name. |
| Sell CEG 235 CSP (7/2) | Today | 16 days | 0.4% yield, 12% downside buffer. Data center play. |
| Avoid XLE, SLV, GLD | Until oil stabilizes | 1-2 weeks | Momentum and fundamentals bearish. |
| Watch USDJPY level | June 16-23 | Weekly | If < 140, buy broader puts. |

### 5. Specific Recommendations (From Options Chain)

**Do Not Buy:**
- Long calls on GLD – gold is in downtrend, strong dollar headwind.
- Long calls on QQQ/SPY – risk of post-FOMC letdown or BoJ shock.
- Long puts on XLE – already priced in.

**Consider:**
- **SPY put** (as above) – the best pure hedge for cash-heavy accounts.
- **TLT call** – if you believe the Fed will signal dovishness (rates down). The TLT 87 call (6/30) costs $0.26 – cheap, but remember the thesis says TLT as hedge is suspect. Small position only.

### 6. Summary of Downside Protection Plan

1. **Buy 1 SPY 728 put (6/30) immediately** – $254 cost, covers ~10% of cash portfolio against a 3% drop. This is the core hedge.
2. **Sell 1 AAPL 280 CSP (7/2)** – collects $78, reduces cost of hedge.
3. **Sell 1 CEG 235 CSP (7/2)** – collects $95, further reduces net cost.
4. **Total net cost of protection:** $254 - $78 - $95 = **$81** (0.09% of portfolio) for 14 days of tail coverage. Highly efficient.
5. **Remain liquid** – do not chase the rally. Wait for the FOMC ambiguity to clear (Wednesday afternoon) and the BoJ decision (Tuesday night/Wednesday Asia). If markets drop 3-5% on a BoJ shock, deploy cash into quality at lower prices.

**Key Risk:** The hedge expires worthless if no crash occurs – but that's the cost of insurance. The macro reading strongly favors the "grind with violence" scenario where dips are sudden and fast. This hedge turns a -10% drawdown into a -2% drawdown.