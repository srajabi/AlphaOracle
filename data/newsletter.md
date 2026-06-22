# AlphaOracle Daily - 2026-06-22

## Signals (rules govern; everything below is commentary)

**Mandate instruction:** SLEEVE_INVESTED

| Signal | State | Detail |
|---|---|---|
| Trend (monthly 200dma) | risk_on | 10.25% vs SMA, as of 2026-05-29 |
| VIX term structure | clear | ratio 0.84 |
| Credit (HYG/LQD 63d) | clear | 0.009 |
| Canary breadth | risk_on | negative: [] |

## Thesis Sentinel

1. **Tripwire status**

| Tripwire | Signal | Reading | Threshold | Status |
|---|---|---|---|---|
| Carry unwind | ^VIX/^VIX3M 5d median | 0.84 | > 1.0 | CLEAR |
| Credit cracks | HYG/LQD 63d rel‑mom | +0.9 % | < –2 % | CLEAR |
| Breadth break | Canary (EWA, TLT) | both +3.5 % | both negative | CLEAR |
| Trend break | SPY vs 200d SMA (monthly) | risk_on (May) | close below | CLEAR |
| Oil shock | XLE momentum vs SPY | XLE –10.1 %, SPY strong | sustained leadership | CLEAR |
| AI capex turn | hyperscaler guidance | no FY27 cuts | any cut | CLEAR |
| Carry stress | USDJPY | no data (VIX term calm) | rapid < 140 | CLEAR |

2. **Marker watch**  
- **BoJ (June 15‑16)**: No hawkish surprise apparent; VIX term structure and carry‑unwind tripwire remain calm.  
- **CPI (May‑July)**: No new print; next release upcoming.  
- **SpaceX vs $135**: Stock falling from highs but still well above issue price; $135 line not threatened.  
- **Hyperscaler capex**: Q2 earnings not yet begun; no fresh guidance.  
- **Hormuz closure**: Talks progress, oil traffic returning to normal; no week‑long closure.

3. **Delta**  
- **De‑escalation**: US‑Iran talks showing progress; oil down >3 %, energy secretary says strait traffic “back to normal.”  
- **Tech rotation**: Alphabet –6 %, Amazon –4 % on AI capex anxiety, while Dow and financials rose.  
- **Macro regime**: Bull Quiet holds; VIX 16.4, dollar strong, gold weak, rates falling.  
- **Signal states unchanged**: All mandate and tripwire signals remain risk‑on, no defensive triggers.

4. **Scenario pressure**  
Today’s evidence reinforces the **Grind‑with‑violence (A)** narrative: a narrow tech air pocket amid broad market resilience, declining oil, and no tripwire fires. Iran de‑escalation reduces the extreme‑tail probability for scenario C, but the AI‑capex anxiety highlights the vulnerability of the top‑heavy index—consistent with scenario B’s slow‑bear potential if earnings disappoint. Official weights (A 50 %, B 30 %, C 20 %) are unchanged pending monthly review.

## Portfolio Manager Synthesis

# Lead Portfolio Manager Decision — 2026-06-22

## Situation Interpretation

The signals are mechanically risk‑on across all mandates (slow/fast/credit/canary), yet the portfolio sits in 100% cash. The macro thesis and risk‑management overlay demand a defensive‑leaning, gap‑risk‑aware deployment — balancing the official “Invested” mandate with the uncomfortable reality of a 50% probability of a meaningful drawdown within 12 months. The “Bull Quiet” surface masks latent tripwires (Iran, Warsh rate‑hike risk, China trade, AI capex deceleration).

**I resolve the tension as follows:**  
- Honor the mandate signals by moving from cash to a fully invested, but **deliberately conservative**, equity allocation immediately.  
- Use the thesis’s tilts (quality, value, gold) to build a portfolio that should participate in risk‑on but suffer less in a grind or slow bear.  
- Hold a small residual cash buffer (~$1k) for gap‑down buying, and explicitly plan to escalate defense if any tripwire triggers.  
- Avoid the most extended, overbought names (semiconductors except those with reasonable RSI, leveraged ETFs) and the sectors most vulnerable to Fed hawkishness (long bonds, high‑multiple tech).

---

## Portfolio Construction Rationale

| **Allocation** | **Ticker(s)** | **Purpose** |
|---|---|---|
| **50% Core Equity** | VT (Total World Stock) | Broad global exposure; honours the P‑sleeve “Invested” mandate. The international component provides a hedge against U.S. narrow leadership, while still participating in a risk‑on tape. |
| **20% Quality** | QUAL (iShares MSCI USA Quality Factor) | Delivers exposure to high‑return‑on‑equity, low‑leverage firms — a playbook that historically holds up better in late‑cycle environments. This directly implements the thesis’s quality tilt. |
| **15% Financials** | XLF (Financial Select Sector) | Rising‑rate environment (if Warsh hikes) benefits banks; strong momentum (RSI 62) and positive relative strength support a near‑term tactical overweight. This aligns with the technician’s and strategist’s sector calls. |
| **10% Gold** | IAU (iShares Gold Trust; lower cost than GLD) | Underweight but present as an inflation/geopolitical hedge. Despite short‑term dollar headwinds, the thesis’s structural inflation floor argues for a core gold position. IAU is selected over GLD for its lower expense ratio. |
| **5% Australia** | EWA (iShares MSCI Australia) | Directly tracks the canary’s global momentum foot; positive 3‑month momentum, commodities‑leaning economy, and a potential tailwind from the July fiscal year start. Small enough to be a “signal follower” without overwhelming the portfolio. |

**Cash residual:** ~$1,000 left for opportunistic buys.  
**No leveraged positions** (no TQQQ/UPRO/SSO) until VIX term structure confirms backwardation or at least until the BoJ/rate‑hike uncertainty passes.

---

## Action Table

| Action | Ticker/Asset | Conviction | Timeframe | Justification |
|--------|--------------|------------|-----------|---------------|
| **Buy** | VT          | **High**   | Today (immediate) | Mandate P‑sleeve Invested; global diversification reduces single‑country concentration risk. |
| **Buy** | QUAL        | **High**   | Today | Mandate Y‑core Invested; thesis quality tilt; low‑volatility factor works in a “grind” environment. |
| **Buy** | XLF         | **Medium** | Today | Cyclical rotation play, rising‑rate beneficiary, strong technical momentum. |
| **Buy** | IAU         | **Medium** | Today | Structural inflation hedge; cheaper than GLD; dollar overbought so gold may rebound on any pullback. |
| **Buy** | EWA         | **Low**    | Today | Canary signal tracker; small allocation to capture international momentum without large risk. |
| **Hold**| Cash        | —          | —        | Keep ~$1,000 for gap‑buying or tripwire‑activated defense. |
| **Avoid**| NVDA, MU, WDC, STX, AVGO, MSFT, GOOGL, AMZN, etc. | — | — | Overbought or under distribution; wait for clear trend resumption or support tests. |

---

## Executable Trades (JSON)

## Paper-Account Attribution

| Account | Status |
|---|---|
| dev | insufficient_history |
| prod_1 | insufficient_history |
| prod_2 | on_script |
| prod_3 | on_script |
| prod_4 | on_script |
| prod_5 | insufficient_history |

---
Generated by AlphaOracle. Paper trading only; research, not advice.
Dashboard: https://srajabi.github.io/AlphaOracle/
