# AlphaOracle Daily - 2026-07-21

## Signals (rules govern; everything below is commentary)

**Mandate instruction:** SLEEVE_INVESTED

| Signal | State | Detail |
|---|---|---|
| Trend (monthly 200dma) | risk_on | 10.36% vs SMA, as of 2026-06-30 |
| VIX term structure | clear | ratio 0.858 |
| Credit (HYG/LQD 63d) | clear | 0.0182 |
| Canary breadth | half_defensive | negative: ['TLT'] |

## Thesis Sentinel

1. **Tripwire status**

| Tripwire | Signal | Threshold | Today's reading | Status |
|---|---|---|---|---|
| Carry unwind | ^VIX/^VIX3M | >1.0 (backwardation) | 0.908 (contango) | CLEAR |
| Credit cracks | HYG/LQD 63d rel‑mom | < –2% | +1.82% | CLEAR |
| Breadth break | Canary (EWA, TLT) | both negative | EWA +0.34%, TLT –2.24% | CLEAR (half‑defensive) |
| Trend break | SPY vs 200d SMA (month‑end) | monthly close below | SPY 742.1 vs 200d 693.9 | CLEAR |
| Oil shock | XLE momentum vs SPY | sustained leadership | XLE strong uptrend; no numeric threshold defined | Not triggered |
| AI capex turn | Hyperscaler guidance | any FY27 capex cut | No new guidance today | CLEAR |
| Carry stress | USDJPY | rapid <140 | Not available in today’s signals | Unmonitored |

2. **Marker watch**

- BoJ guidance: no news (June hike already past; no follow‑up statements).  
- CPI: no new print; recent headlines note “cooler inflation” but no sequential data.  
- SpaceX vs $135: no price or performance news today.  
- Hyperscaler capex: no guidance changes ahead of this week’s earnings (Alphabet, Tesla).  
- Hormuz: escalation – tanker hit, Brent >$90, Goldman warns $120 possible, but no full closure.

3. **Delta**

Geopolitical risk intensified: multiple reports of tanker attacks in Strait of Hormuz, oil prices spiking, and a Reuters poll showing economists see a chance of a Fed hike. Rule‑based signals remain unchanged from yesterday’s snap: canary half‑defensive, credit clear, VIX futures contango, trend intact. The only delta is a louder inflation‑risk‑off tail from the war, but tripwires remain unfired.

4. **Scenario pressure**

Today’s evidence leans into scenario **A (Grind‑with‑violence)** – oil‑driven anxiety with no systemic cracks. Rising rates and cautious sentiment are consistent with the repeated 5–10% air pockets described in A. The war escalation adds a faint pulse toward C, but the absence of credit stress or VIX backwardation keeps the systems in risk‑on posture. Official scenario weights unchanged until monthly review.

## Portfolio Manager Synthesis

The portfolio starts from a clean cash position. The macro backdrop is dominated by the Strait of Hormuz crisis, cornered Fed policy, rising yields, a strong dollar, and mixed commodity signals. The canary is half-defensive (TLT negative), and the regime is Transitional with a strong stagflationary tilt. This argues for a defensive‑leaning deployment that overweights energy and financials, adds a small gold hedge, and keeps ample dry powder.

- **Energy (XLE)** rides the supply‑shock uptrend with strong momentum; the war and potential for further escalation keep a bid under oil.
- **Financials (XLF)** benefit from rising rates (wider net interest margins) and hold up well in the current rotation out of growth.
- **Gold (GLD)** is oversold and showing early reversal signs (positive MACD histogram); a small position serves as a geopolitical tail‑hedge and a bet that negative real rates eventually reassert themselves.
- Remaining cash (about 45%) preserves optionality for a deeper sell‑off and pays a money‑market yield of ~4.5%.

Tech and growth are under pressure from rising rates and the AI capex deceleration risk, so I avoid semis, broad tech ETFs, and leveraged instruments.

**Action Plan**

| Action | Ticker/Asset | Conviction | Timeframe | Justification |
|--------|-------------|------------|-----------|---------------|
| **Buy** | **XLE** (Energy Select Sector SPDR) | **High** | Medium‑term (4‑12 weeks) | Oil supply shock from Hormuz attacks; strong uptrend, above all SMAs, positive MACD; acts as an inflation hedge and direct beneficiary of geopolitical tail risk. |
| **Buy** | **XLF** (Financial Select Sector SPDR) | **Medium** | Medium‑term | Rising interest rates widen net interest margins; trend is strong, above all key SMAs, RSI healthy; rotation out of tech into financials is underway. |
| **Buy** | **GLD** (SPDR Gold Shares) | **Low‑Medium** | Medium‑term | Gold is oversold; MACD histogram has just turned positive, hinting at a potential reversal. A small position hedges tail risk if geopolitical deterioration triggers a flight to safety, while negative real rates provide a structural floor. |
| **Hold** | **Cash** | **High** | Indefinite | The scenario mix (50% grind‑with‑violence, 30% slow bear, 20% fast crash) plus multiple flashing tripwires (VIX/VIX3M near 1.0, canary half‑defensive) warrant preserving firepower. Money‑market yield (~4.5%) mitigates inflation cost of waiting. |

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
