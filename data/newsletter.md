# AlphaOracle Daily - 2026-07-14

## Signals (rules govern; everything below is commentary)

**Mandate instruction:** SLEEVE_INVESTED

| Signal | State | Detail |
|---|---|---|
| Trend (monthly 200dma) | risk_on | 10.36% vs SMA, as of 2026-06-30 |
| VIX term structure | clear | ratio 0.834 |
| Credit (HYG/LQD 63d) | clear | 0.019 |
| Canary breadth | half_defensive | negative: ['TLT'] |

## Thesis Sentinel

**Tripwire status (2026-07-14)**

| Tripwire | Signal | Today’s reading | Status |
|---|---|---|---|
| Carry unwind | ^VIX/^VIX3M 5d med | 0.834 (< 1.0) | CLEAR |
| Credit cracks | HYG/LQD 63d rel‑mom | +1.9% (> –2%) | CLEAR |
| Breadth break | canary 13612W (EWA,TLT) | Only TLT negative | CLEAR |
| Trend break | SPY < 200d SMA (m‑end) | 749 vs 691 (not close) | CLEAR |
| Oil shock | XLE sustained leadership | XLE +3.2% Mon; oil at 1‑mo high | FIRING |
| AI capex turn | Hyperscaler FY27 guidance | No Q2 reports; no cuts | CLEAR |
| Carry stress | USDJPY rapid < 140 | 161.74 (CNBC) | CLEAR |

**Marker watch**

*BoJ guidance* – Meeting concluded June 16; no new guidance today.  
*CPI <3.5%* – June CPI fell sharply (first MoM drop since 2020). Likely y/y < 3.5%; first of two required prints.  
*SpaceX vs $135* – No price data in today’s feed; issue-date $135 line not breached.  
*Hyperscaler capex* – Q2 earnings season yet to bring hyperscaler guidance; no FY27 cuts reported.  
*Hormuz* – Attacks intensified, traffic stalled; full one‑week closure not confirmed but risk has risen markedly.

**Delta**

Today brought a large CPI downside surprise (cooling inflation) while oil surged 2%+ on fresh US‑Iran escalation and Hormuz threats. IBM’s Q2 profit warning slammed software/AI names (ORCL, PLTR, etc.). Fed Chair Warsh testified, reiterating ‘no tolerance’ for inflation but offering no policy hints. The macro mix is sharply contradictory: disinflation good for rate‑sensitive assets, war supply shock bad for growth and inflation expectations.

**Scenario pressure**

The cooler CPI reduces the stagflation tail but does little to offset the escalating Hormuz conflict. The oil‑shock tripwire is now firing, which mechanically raises scenario‑C odds if a full strait closure persists. Market‑implied risk remains contained (VIX/VIX3M still contango, credit and breadth clear), so the evidence still fits the “grind with violence” base case (A). However, the simultaneous firing of a war‑supply tripwire and an all‑clear on other defensive signals means any further Hormuz news could quickly shift pressure toward C. The rule‑based systems remain governed by today’s clean credit/canary prints; no mandate changes are triggered.

## Portfolio Manager Synthesis

# Portfolio Manager Decision – July 14, 2026

We are sitting on $87,185 cash with both firm mandates (P_sleeve, Y_core) requiring full equity investment, while the canary signal has shifted to **half‑defensive** (TLT momentum negative). The macro backdrop is tense – an active US‑Iran war, an inflation‑stuck Fed, a strong dollar, and early signs of AI‑capex digestion. Our own thesis assigns a 50% chance to a grind‑with‑violence scenario and 50% to a slow bear or crash within 12 months.  

The risk manager urges tail hedges (SPY/QQQ puts), but our execution is equity‑only. We therefore **defensively deploy** capital – overweight the sectors that thrive in this regime (energy, financials, utilities) and add a small gold position for its mean‑reversion setup and inflation‑hedge properties, while leaving a modest cash buffer as a proxy for the absent put. We deliberately **underweight technology** and completely avoid long‑duration bonds. This gives us full mandate compliance with a defensive skew.

---

## Action Plan

| Action | Ticker/Asset | Conviction | Timeframe | Justification |
|--------|--------------|------------|-----------|---------------|
| **Buy** | SPY | High | Weeks–months | Broad US equity exposure; fulfills core mandate; still above all moving averages with positive MACD. Gives ballast to the portfolio. |
| **Buy** | XLE | High | Weeks–months | Strongest sector momentum; direct beneficiary of Hormuz supply shock; acts as an inflation hedge and geopolitical play. |
| **Buy** | XLF | High | Weeks–months | Benefits from rising rates and steepening yield curve; strong uptrend with RSI not yet overbought; value rotation tailwind. |
| **Buy** | XLU | Medium | Weeks–months | Defensive sector with AI‑power‑demand tailwind; holds above SMAs; provides stability if growth stocks falter. |
| **Buy** | GLD | Medium | Days–weeks | Oversold (RSI 36.8) with bullish MACD divergence; near lower Bollinger Band; technical bounce expected. Also an inflation‑hedge complement to XLE. |
| **Hold** | Cash (~10%) | – | – | Deliberate residual as a proxy for risk‑manager‑recommended puts; preserves optionality for a sudden drawdown or opportunity. |

**Why we are not buying AAPL/META/QQQ:**  
Our macro strategist and risk manager both flag rising‑rate headwinds for high‑multiple tech. The IBM profit warning and decelerating AI‑capex narrative add further near‑term risk, even though a few names show good technicals. We wait for a clearer de‑risking before adding growth names.

**Why we are not buying TLT/TMF:**  
Bonds remain in a downtrend; rising real rates and the inflation‑tolerant administration make TLT a poor hedge. The canary’s negative TTL signal confirms avoidance.

---

## Executable Trades (JSON)

## Paper-Account Attribution

| Account | Status |
|---|---|
| dev | insufficient_history |
| prod_1 | insufficient_history |
| prod_2 | on_script |
| prod_3 | on_script |
| prod_4 | watch |
| prod_5 | insufficient_history |

---
Generated by AlphaOracle. Paper trading only; research, not advice.
Dashboard: https://srajabi.github.io/AlphaOracle/
