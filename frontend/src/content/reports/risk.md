---
title: Risk Manager Report
date: "2026-06-25"
---

## Model: deepseek/deepseek-v4-flash

# Downside Protection & Geopolitical Risk Analysis — 2026-06-25

## Executive Summary
**Portfolio is 100% cash ($87,185).** No existing positions to hedge, so recommendations focus on **capital deployment caution** and **opportunistic hedging** for imminent entry. The macro environment is defensive-leaning with multiple live tail risks, but none have yet triggered our automated de‑risking signals (VIX term structure, credit spreads, canary breadth). The guidance: **stay short‑duration, avoid directional war bets, and use optionality (puts) when entering volatile names.**

---

## 1. Geopolitical Catalysts (Severity & Exposures)

### 🔴 Strait of Hormuz / US‑Iran War — Severity 6/10 (De‑escalating)
- **What happened:** Attack on cargo vessel halted shipping on June 25; later reversed as tanker traffic resumed after US‑Iran agreement. Oil erased war gains.  
- **Sectors exposed:**  
  - **Bearish:** XLE (energy), airlines, shipping (near‑term volatility).  
  - **Bullish (if sustained de‑escalation):** consumer discretionary (lower fuel costs), XLI (industrials).  
- **Recommended hedges:** None now – the relief rally is already priced. Do not short oil after a 4% drop. Instead, use **long calls on TLT** (rates benefit from reduced inflation panic) or **protective puts on XLE** if re‑escalation occurs.  
- **Time horizon:** Days to weeks; both tails are live. Watch headlines from *Economies.com* and *Reuters* – we already have the `geopolitical_supply_shock` impact tag.

### 🟡 Fed / Inflation (PCE 3‑Year High) — Severity 5/10 (Cornered Policy)
- **What happened:** Core PCE hit 3‑year high (3.4% y/y). Warsh Fed expected to hike in September; July hold. Inflation expectations elevated.  
- **Sectors exposed:**  
  - **Bearish:** TLT, QQQ (tech multiples compress with rising rates).  
  - **Bullish:** XLF (banks benefit from steeper curve), GLD (negative real rates).  
- **Recommended hedges:** **Short‑duration cash** is already optimal. If deploying, bias toward **floating‑rate or inflation‑protected assets** (SCHP). For equity, use **SPY/QQQ 22‑DTE OTM puts** (see Options Chain: `SPY 260717P00712` at $4.735, $0.64% cost).  
- **Time horizon:** Weeks to months – the September hike is a known event, but guidance could shift.

### 🟡 China‑Taiwan / Trade War — Severity 4/10 (Simmering)
- **What happened:** China imposes export controls on US firms (rare earths, AI chips). Taiwan mulls curbs on AI chip sales to China.  
- **Sectors exposed:**  
  - **Bearish:** TSM, NVDA, AMD, semis (supply chain risk).  
  - **Bullish:** INTC (foundry onshoring beneficiary), GLD (safe haven).  
- **Recommended hedges:** **Avoid small‑cap semis** with high China revenue. For index‑level protection, **SPY puts** are sufficient – no need for single‑stock hedges unless holding TSMC or Nvidia directly.  
- **Time horizon:** Structural slow‑burn; revisit after Jun‑Jul export control updates.

### 🟢 Recession Signals — Severity 3/10 (Mixed)
- **What happened:** Rising unemployment (225k jobless claims), but still historically low. Long‑term unemployment surging.  
- **Sectors exposed:**  
  - **Bearish:** XLY, XLI (cyclicals).  
  - **Bullish:** XLU, XLV (defensives), TLT (flight to safety).  
- **Recommended hedges:** **Rotate into XLU/XLU** if the S&P 50‑day fails. Currently not urgent – use `canary` momentum (positive) as a check.  
- **Time horizon:** 2–3 quarters – watch payrolls trend.

---

## 2. Market Regime & Volatility Assessment

| Indicator | Value | Signal | Implication |
|-----------|-------|--------|------------|
| SPY trend | Uptrend (above 200‑day) | Risk-on | No trend break yet |
| VIX level | 18.6 (normal, rising) | Caution | Volatility rising, not panic |
| VIX/VIX3M | 0.84 < 1.0 | Clear | No backwardation – crash risk gated |
| Dollar (UUP) | Strong uptrend, 52‑week high | Headwind | Pressures commodities, EM, international |
| Real rates (TLT) | Strong uptrend (yields falling) | Favorable | Supports growth stocks but inflation negates |
| Commodities | Gold & silver downtrend | Defensive | Avoid jumping into metals near support |

**Regime verdict:** Transitional, low confidence. The central conflict is between a still‑rising equity trend (slow channel risk‑on) and multiple macro headwinds (dollar, inflation, geopolitics). **This is precisely the environment where cash and short‑dated puts add value.**

---

## 3. Recommended Actions (No Positions Held)

### ✅ Keep Cash as a Hedge
- **Rationale:** $87k cash earns ~4.1% short‑term (3m T‑bill). In a 50% probability of A‑grind, waiting for volatility bursts is optimal.  
- **Action:** Do not deploy more than 30% of cash until VIX > 22 or a clear tripwire triggers (e.g., SPY monthly close < 200‑day).

### ✅ Buy Protective Puts on SPY / QQQ (for future entry)
- **Why:** If you plan to enter equities in the next 3 weeks, buying a 22‑DTE put costs ~0.6% of notional and caps drawdown.  
- **Recommended contracts (from Options Chain):**
  - `SPY 260717P00712` – last $4.735, 22 DTE, cost = $473.50 per 100 shares equivalent.  
  - `QQQ 260717P00695000` – last $11.405, cost = $1,140.50 per 100 shares.  
- **Time horizon:** Expires before July 29 FOMC – perfect for covering through next rate decision.

### ✅ Avoid These Sectors Now
- **Sell/Trip:**
  - **XLE** – oil volatility likely to compress after the 4% drop; no clear edge.  
  - **IBIT / crypto** – Bitcoin near 2‑year low, still in downtrend.  
  - **TQQQ / UPRO** – 3x leverage + rising VIX = decay risk. The 200‑SMA strategy works on daily resets but gap events destroy it.  
- **Trim (if you owned):**
  - **NVDA** – below $200, 50‑day rolling. Semis face capex deceleration risk (see thesis).  
  - **PLTR** – down 36% YTD, momentum bearish.  
  - **GOLD / SLV** – commodities weak on strong dollar; wait for a stabilization signal.

### ✅ Preferred Safe Havens (if deploying)
- **TLT** – real rates falling, bonds offer a rare positive carry vs. historical volatility.  
- **XLU** – AI‑power demand narrative intact, but don’t chase; dip buy below $45.  
- **Cash** – still the best “position” until a clear regime emerges.

---

## 4. Specific Ticker‑Level Weakness (from Data)

| Ticker | RSI | MACD Hist | Trend | Risk |
|-------|-----|-----------|-------|------|
| GLD | 28.7 | -1.61 | Strong downtrend | Oversold but momentum negative |
| NFLX | 20.2 | -0.77 | Below all SMAs | Severe weakness, avoid |
| IBIT | 32.1 | -0.02 | Near yearly low | Momentum still bearish |
| ORCL | 32.5 | -6.38 | Massive break below 20‑d | Post‑gap risk |
| MSFT | 32.5 | -5.03 | Below 200‑d | Trend broken |
| AAPL | 45.8 | -1.74 | Just above 50‑d | Price hike shock |

> **Takeaway:** No reason to buy these outliers on weakness – wait for a higher‑low pattern or VIX spike to enter.

---

## 5. Summary of Hedging Strategy

- **For existing (none):** Stay in cash, but buy a **small SPY put** as a “portfolio insurance” that can be rolled if you plan to enter soon.  
- **For new entries:** Only deploy into **defensive sectors (XLU, XLP, TLT)** using **limit orders 2–3% below current.** No rushed buys.  
- **For day‑traders:** Avoid leverage (TQQQ/UPRO) until VIX drops below 16.  
- **Tripwire watch:** Monitor the six signals in the thesis – especially USDJPY < 140 (carry unwind) and HYG/LQD relmom. If two fire concurrently, reduce even cash deployments.

**Final risk assessment:** Probability of sharp 5–10% drawdown within 4 weeks = **35%** (Mideast flare‑up + FOMC hawkish surprise). Probability of continued grind higher = **40%**. The 25% remainder is dovish pivot or escalation. In this asymmetry, **premium selling (cash‑secured puts) is preferred to outright long bias.** Consider selling the `SPY 260717P00712` put if you are comfortable buying the S&P at 712 (3% below) – it yields $473 per contract and aligns with the thesis.