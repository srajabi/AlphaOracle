---
title: Risk Manager Report
date: "2026-06-24"
---

## Model: deepseek/deepseek-v4-flash

## Risk Manager Assessment – June 24, 2026

### 1. Overall Risk Posture

| Signal | State | Notes |
|---|---|---|
| **Slow Channel** | Risk-On | SPY above 200d SMA, monthly close OK |
| **Fast Channel** | Clear | VIX/VIX3M 0.84 (contango, no crash gate) |
| **Credit** | Clear | HYG/LQD relative momentum positive |
| **Canary** | Risk-On | Both EWA and TLT positive momentum |
| **Intermarket** | Cautious | Strong dollar, commodities weak, VIX rising |

**Bottom line:** Systematic mandates are invested, but the macro environment is **transitional with elevated tail risk**. The probability of a fast crash (20%) and slow bear (30%) sum to 50% within 12 months. The portfolio is currently **100% cash** – this is an opportunity to deploy defensively.

---

### 2. Key Geopolitical Catalysts

#### A. Strait of Hormuz / Iran War De-escalation (Severity: 8 → 4)
- **What happened:** Multiple headlines confirm oil pre-conflict low, more ships crossing, Brent < $74. Trump claims record oil flow.
- **Impact:** Immediate relief for inflation expectations, risk-on for equities, **bearish for energy** (XLE), gold (GLD) losing safe-haven bid, bullish for consumer discretionary, airlines, tech.
- **Hedging:** Reduce XLE longs (if any). Consider short XLE or protective puts on energy. Gold weakness (strong dollar + easing war premium) suggests GLD/IAU still vulnerable.
- **Time horizon:** Immediate days to weeks – oil could trend lower but risk of re-escalation remains (both tails live).

#### B. Fed Hawkish Pivot (Severity: 7)
- **What happened:** BofA predicts rate hikes; markets pricing July 29 live meeting. New Chair Warsh feared to “murder bull market.”
- **Impact:** Rising real yields → headwind for growth/tech (QQQ), support for banks (XLF) and short-duration bonds. Gold already down 7-month low.
- **Hedging:** Protective puts on QQQ/SPY (especially Jul 17 expiries). Favor XLF over XLK. TLT is staging a small rally (rates declining), but that could reverse if Warsh delivers.
- **Time horizon:** Weeks – key tripwire is July 29 FOMC.

#### C. China-US Trade Tensions (Severity: 5)
- **What happened:** China imposed new export controls on dozens of US firms, rare-earth restrictions.
- **Impact:** Negative for semis with China exposure (NVDA, AMD, KLAC, TSM). Bullish for US defense (but not in our focus) and gold (GLD) as risk-off asset. However, gold is currently falling due to dollar strength.
- **Hedging:** Avoid semis on any bounce. Consider short QQQ or buy puts. TSM and INTC could be dragged down by trade rhetoric.
- **Time horizon:** Weeks – watch for retaliation escalation.

#### D. AI Capex Reality Check (Severity: 8)
- **What happened:** Magnificent Seven lost $2.7T market cap in June. “Big Tech’s AI bill comes due” narrative dominating.
- **Impact:** Continued selling in mega-cap tech (MSFT, AAPL, NVDA, META, AMZN, GOOGL). ORCL, AVGO also hit. Memory players (MU, STX, WDC) still strong but high volatility.
- **Hedging:** Protective puts on QQQ or individual name puts (NVDA, MSFT, AMZN). Use the long_put on SPY/QQQ from options chain.
- **Time horizon:** Weeks to months – earnings season in July will be the next trigger.

#### E. Recession Signals (Severity: 4)
- **What happened:** Rising unemployment claims, regional economic slowdown (Virginia, Indiana). Consumer weakening.
- **Impact:** Defensive sectors (XLU, XLV, XLP) may outperform. Cyclicals (XLI, XLY) under pressure.
- **Hedging:** Rotate to utilities, healthcare, consumer staples. Reduce discretionary.
- **Time horizon:** Gradual – watch HYG/LQD credit spreads for confirmation.

---

### 3. Ticker-Level Weakness to Hedge / Reduce

| Ticker | Status | Action |
|---|---|---|
| **MSFT** | Below 20/50/200 SMA, RSI 35, MACD negative | **Hedge or avoid** – AI spending drag, no catalyst |
| **NFLX** | RSI 21, deeply oversold, below all SMAs | **Avoid** – value trap (down 32% from highs) |
| **GOOGL** | Below 20/50 SMA, RSI 37, weak | **Reduce** – AI/cloud spending concerns |
| **META** | Below 20/50/200 SMA, RSI 39 | **Reduce** – same AI cloud fears |
| **NVDA** | Just below 20 SMA, RSI 42, MACD bearish | **Tighten stops** – critical support at $200 (Bollinger lower) |
| **AMD** | RSI 56, still above 20 SMA – relatively resilient | **Hold but hedge** – if semi selloff deepens, could break |
| **AVGO** | Below 20/50 SMA, RSI 43, but OpenAI chip news positive | **Hedge with puts** – volatility is high |
| **PLTR** | RSI 32, deeply below 20/50/200 | **Avoid** – weak fundamentals, falling knife |
| **ORCL** | RSI 35, massive breakdown below 20/50/200 | **Avoid** – AI bill concerns hit legacy cloud |
| **INTC** | RSI 60, above 20/50 SMA – strong | **Hold** – Apple-Intel deal potential support |
| **TSLA** | RSI 40, below 20/50/200, weak | **Avoid** – not a safe haven |
| **GLD** | RSI 33, below 20/50/200, strong downtrend | **Reduce** – dollar strength + easing Iran = no catalyst |
| **IAU** | Same as GLD | **Reduce** – gold not a hedge here |
| **XLE** | RSI 40, below 20/50 SMA | **Reduce** – oil supply normalization |

**Defensive survivors (hold/accumulate):** XLU (utilities), XLV (healthcare), XLP (staples), IWM (small caps relative strength), TLT (rates declining bias, though Fed risk).

---

### 4. Recommended Hedges (Available Options Chain)

| Ticker | Strategy | Contract | Rationale |
|---|---|---|---|
| **SPY** | Long Put | SPY260717P00716000 (Strike $716, Jul 17) | Protect against 5%+ drawdown; cost ~$4.73 (~0.6% of notional). Good risk/reward given VIX~19. |
| **QQQ** | Long Put | QQQ260717P00694000 (Strike $694, Jul 17) | Same logic for tech-heavy exposure. Cost ~$11.11 (~1.6% of notional). |
| **NVDA** | Long Put | Use SPY/QQQ puts for broad protection; individual NVDA puts expensive | Avoid direct puts due to high IV; hedge via QQQ. |
| **Gold** | Short-term protection via UUP (Dollar) | UUP already strong | Instead of hedging gold directly, hold dollar exposure (UUP) to offset commodity losses. |

**Alternative:** Use VIX futures or VIX calls if VIX/VIX3M flips to >1.0 (backwardation). Currently not triggered.

---

### 5. Tactical Allocation Recommendations

Given **100% cash**, deploy defensively:

1. **40% cash** – maintain optionality. Waiting for the next 5-10% air pocket.
2. **20% SPY** – buy on weakness near 200d SMA ($685). Not yet.
3. **15% QQQ** – wait for VIX spike to 25+ for entry.
4. **10% XLV / XLU** – defensive sectors to earn yield while waiting.
5. **10% short-term TIPS / cash alternatives** (not available here, but conceptually).
6. **5% gold put spread** – if you want a tactical bearish hedge on gold (GLD Jul 17 355 put).

**Avoid:** Energy (XLE), discretionary (TSLA, AMZN, META), high-duration bonds (TLT long side is risky if Warsh hikes).

---

### 6. Risk Dashboard Tripwires (Updated)

| Tripwire | Current Value | Alert Threshold | Status |
|---|---|---|---|
| VIX/VIX3M | 0.84 | >1.0 | **Clear** |
| HYG 63d rel-mom | +0.57% | <-2% | **Clear** |
| SPY monthly close vs 200d | ~733 vs 685 | Close below 685 | **Clear** |
| USDJPY | Not provided | <140 | Not checked |
| XLE momentum vs SPY | Negative | Sustained leadership | **Bearish for energy** – no alarm |

None of the crash gates are triggered, so the systematic mandates are correctly invested. However, the **evolving macro risks** (Fed, trade, AI capex) justify a cautious posture.

**Bottom line:** Stay mostly cash, hedge the portfolio you would build with SPY/QQQ puts, favor defensive sectors, and wait for a volatility spike to deploy into the AI theme at better prices. The next big trigger is **July 29 FOMC** and **Q2 earnings season**.