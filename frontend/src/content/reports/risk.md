---
title: Risk Manager Report
date: "2026-06-19"
---

## Model: deepseek/deepseek-v4-flash

## Risk Assessment: Downside Protection & Geopolitical Hedges

### Macro Risk Snapshot (2026-06-19)

| Catalyst | Severity (1–10) | Status | Exposed Sectors | Recommended Action |
|----------|----------------|--------|-----------------|-------------------|
| US-Iran Ceasefire / Hormuz Reopen | 5 (de-escalating) | Agreed, but fragile | Oil (XLE) – bearish; Consumer cyclicals – bullish | Avoid XLE; trim any energy longs |
| China-Taiwan Chip Curbs | 4 (simmering) | Taiwan/Nvidia export controls; ASML probe | Semis (TSM, NVDA, AMD) – bearish | Hedge semis with put spreads |
| Fed Hawkish Tilt (rate hike hints) | 6 (active) | 9/19 FOMC members see future hikes; dollar at 13-mo high | Growth tech, bonds – bearish; Dollar – bullish | Short-dated bond exposure risky; favor cash |
| Recession Signals (layoffs, rising claims) | 4 (emerging) | Paper industry layoffs; unemployment uptick | Consumer disc (XLY), industrials – bearish; Defensives (XLU, XLP) – bullish | Rotate to defensives via puts or direct buys |
| AI Capex Deceleration Risk | 5 (latent) | Hyperscaler guidance in Q2 earnings – tripwire | NVDA, broad tech | Protective puts on QQQ/SPY |

**Current Regime:** Bull Quiet → risk-on, but with hidden tail risks.  
**Portfolio:** 100% cash ($87,185). No position to trim, but we can pre-deploy hedges before entering equity exposure.

---

### What to **Avoid / Sell / Trim** (if holding)

- **Energy (XLE):** Oil down 8% on ceasefire; Hormuz reopening may push Brent to $70–80. XLE below 200d SMA, RSI ~34. Avoid or hedge with puts.
- **High-Beta Tech (NVDA, AMD, QQQ):** Narrow leadership, rich valuations, Fed hawkishness, and BoJ carry risk make them vulnerable. If holding, trim 20–30%.
- **Gold (GLD, IAU):** Strong dollar + hawkish Fed have broken the uptrend. Gold is in downtrend (RSI 38). Hedge any existing long, or wait for a better entry near $375 support.

---

### Recommended Hedges (from Options Chain)

All hedges should be **tactical (21–28 DTE)** to cover the near-term risk window (BoJ decision, Q2 guidance season, ceasefire verification).

#### 1. SPY Protective Put – Index Tail Hedge
- **Why:** SPY at 746. A 10% drawdown to 671 would be plausible in a slow-bear scenario. The 724 strike (3% OTM) offers cheap tail protection.
- **Trade:** Buy 1 SPY 724 Put exp. July 10 (DTE 21) @ $3.27 mid. **Cost: $327**.  
  *Alternative:* July 17 (DTE 28) @ $4.54. Cost: $454.  
- **Payoff:** Breakeven below 720.76. Covers gap risk down to 724.

#### 2. QQQ Protective Put – Tech Tail Hedge
- **Why:** QQQ is 741; semis are extended. A 5–8% tech selloff would hit QQQ hard.
- **Trade:** Buy 1 QQQ 718 Put exp. July 17 @ $11.25 mid. **Cost: $1,125**.  
  (July 10 put is cheaper at $8.96 but less time).  
- **Payoff:** Protects below 706.75. Gives 3% buffer.

#### 3. VIX Call Spread – Volatility Spike Insurance
- **Why:** VIX at 16.4 (near BB lower). Any geopolitical shock (Hormuz re-escalation, BoJ guidance) could push VIX to 25+.  
- **Trade (not in chain but standard):** Buy VIX 20 Call exp. July 17, sell VIX 30 Call to cap cost. Cost ~$0.50–0.80.  
- Alternatively, use **^VIX futures options** if available.

#### 4. Long GLD Put – Commodity Weakness Hedge
- **Why:** Gold trend is down. If dollar continues to rally, GLD could test $375 (BB lower).  
- **Trade:** Buy 1 GLD 375 Put exp. July 17 @ $5.45. **Cost: $545**.  
- **Payoff:** Breakeven below 369.55. Protects against further gold weakness.

**Total hedge cost** (if using SPY + GLD puts): ~$872 (1% of cash). This is a small premium for tail insurance.

---

### Safe-Haven & Rotation Ideas

| Asset | Why | Entry Strategy |
|-------|-----|----------------|
| **Cash** | Highest safe haven in scenario B/C. Already 100% – keep 30–50% cash at all times. | N/A |
| **Defensives (XLU, XLP)** | Recession signals + falling rates benefit utilities & staples. | Cash-secured put: Sell XLU 44 Put exp. July 17 (OTM ~2%) for $0.40–0.50 credit. |
| **Long-Duration Bonds (TLT)** | Rates falling now, but Fed hawkishness is a risk. Short-term momentum is bullish. | Buy TLT 87 Call exp. July 17 (slightly OTM) for $0.85 mid. Small speculative hedge. |
| **USD (UUP)** | Dollar breakout; no direct option chain, but long dollar is a hedge against risk-off. | Already strong; can hold via UUP (ETF) but not needed. |

---

### Time Horizon & Tripwires to Watch

| Tripwire | Signal to Monitor | Action if Triggered |
|----------|-------------------|---------------------|
| VIX/VIX3M > 1.0 | Backwardation signal for crash scenario | Immediately buy VIX calls / sell SPY |
| HYG/LQD 63d rel-mom < -2% | Credit cracks precede equity selloff | Increase put hedge duration |
| SPY < 200d SMA (monthly close) | Trend break → scenario B | Go to 100% cash, rotate to TLT/GLD |
| BoJ guidance (June 15–16) | Hawkish surprise → USDJPY < 140 | Sell risk assets, buy USD puts |
| Q2 hyperscaler capex cuts | Any FY27 guidance reduction | Trim NVDA, buy QQQ puts |

**Immediate (next 48 hours):** Place the SPY 724 put (July 10) and GLD 375 put (July 17) as core tail hedges.  
**Days to weeks:** Monitor BoJ aftermath. If no shock, hold hedges until expiry; if shock, scale up.

---

### Final Action Summary

1. **Do NOT enter long equity positions** without the suggested puts in place.
2. **Buy SPY 724 Put (Jul 10) – 1 contract** @ $3.27. Cost: $327.
3. **Buy GLD 375 Put (Jul 17) – 1 contract** @ $5.45. Cost: $545.
4. **Consider selling XLU 44 Put (Jul 17)** to generate premium while expressing a defensive tilt.
5. **Avoid XLE, high-beta tech, and gold** until trends improve or tail risks are reduced.

Your cash position is a powerful asset. Use it to wait for a better entry (scenarios B or C) while paying a small premium for insurance against the 50% chance of a slow bear or fast crash.