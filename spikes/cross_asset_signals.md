# Cross-Asset Signals & Intermarket Analysis

## Philosophy

No asset trades in isolation. Understanding relationships between stocks, bonds, commodities, currencies, and crypto provides early warning signals and confirmation of trend changes.

**Key principle:** When correlations break down or reverse, a regime change is happening.

---

## 1. Bitcoin as Risk Appetite Gauge

### Why It Works
- Bitcoin = "digital gold" but trades like leveraged tech
- 24/7 liquidity → reacts faster than equity markets
- Highly correlated with risk assets during risk-on
- Decouples during flight to safety

### Signals

**BTC Leading Indicator:**
- BTC rallies 10%+ on weekend → expect Monday tech rally
- BTC crashes 15%+ on weekend → expect Monday selloff
- BTC holds support while stocks weak → bullish divergence

**Correlation Regime:**
```python
if btc_corr_to_qqq > 0.7:
    regime = "risk_on"  # BTC and tech moving together
elif btc_corr_to_qqq < 0.3:
    regime = "flight_to_safety"  # BTC selling with risk assets
```

**Implementation:**
- Track BTC/USD from Coinbase, Binance, or via Yahoo (BTC-USD)
- Calculate 20-day rolling correlation with QQQ
- Flag when correlation breaks down
- Use as leading indicator for Monday gaps

**Example Rules:**
- If BTC up 5%+ over weekend AND correlation > 0.6 → Long QQQ Monday open
- If BTC down 10%+ over weekend → Reduce risk Monday, consider hedges

### Data Source
- Yahoo Finance: `BTC-USD`
- CoinGecko API (free)
- Coinbase API

---

## 2. Credit Spreads (High Yield vs Investment Grade)

### Why It Works
- High-yield bonds (junk) selloff before equity crashes
- Credit investors = "smart money", react to stress first
- Widening spreads = risk aversion, borrowing costs rising

### Signals

**HYG vs LQD Spread:**
```python
hyg = high_yield_etf  # HYG
lqd = investment_grade_etf  # LQD
spread = (hyg_yield - lqd_yield)

if spread > historical_75th_percentile:
    signal = "credit_stress"  # Bearish for equities
elif spread < historical_25th_percentile:
    signal = "risk_on"  # Credit markets healthy
```

**Leading Indicator:**
- Credit spreads widen → equity weakness follows (1-4 weeks)
- Credit spreads tighten → risk-on environment

**Practical:**
- Monitor HYG (high yield corporate bonds)
- Monitor LQD (investment grade corporate bonds)
- Monitor TLT (long treasuries)

**Signals:**
- HYG underperforming SPY by 3%+ over 2 weeks → caution
- HYG breaking below 200 SMA while SPY above → bearish divergence
- LQD rallying (flight to quality) while SPY flat → hidden stress

### Data Source
- Yahoo Finance: `HYG`, `LQD`, `TLT`

---

## 3. Commodities Divergence

### Copper (Economic Bellwether) vs Gold (Safe Haven)

**Why It Works:**
- Copper = industrial demand, economic growth
- Gold = fear, inflation, safe haven
- Divergence = stress signal

**Signals:**

```python
if copper_down and gold_up:
    signal = "stagflation_fear"  # Growth slowing, fear rising
    implications = "Bearish for cyclicals, bullish for defensives"

elif copper_up and gold_down:
    signal = "risk_on"  # Growth accelerating, no fear
    implications = "Bullish for cyclicals, commodities"

elif copper_down and gold_down:
    signal = "deflationary_crash"  # Everything selling
    implications = "Cash is king, flight to USD/Treasuries"

elif copper_up and gold_up:
    signal = "reflationary_boom"  # Inflation + growth
    implications = "Bullish commodities, real assets"
```

**Practical:**
- Copper: Track `HG=F` (copper futures) or CPER ETF
- Gold: Track `GLD` or `GC=F`

**Historical:**
- 2008: Copper crashed, gold rallied → recession signal
- 2020-21: Both rallied → reflationary boom
- 2022: Copper weak, gold up → stagflation fears

### Oil Divergence

**Oil Up + Copper Down = Supply Shock (Bearish)**
- Not demand-driven (copper would rise with demand)
- Geopolitical or supply disruption
- Bearish for consumers, inflation risk

**Oil Up + Copper Up = Demand Boom (Bullish)**
- Broad-based growth
- Reflationary environment
- Bullish for energy, industrials

### Data Sources
- Yahoo Finance: `GLD`, `GC=F`, `HG=F`, `CL=F` (oil)
- ETFs: `CPER` (copper), `USO` (oil), `GLD` (gold)

---

## 4. Currency Signals

### US Dollar Strength (UUP, DXY)

**Why It Matters:**
- Strong dollar = headwind for multinationals, commodities
- Weak dollar = bullish for emerging markets, commodities, gold

**Signals:**

```python
if uup_up and spy_down:
    signal = "flight_to_safety"  # Risk-off, dollar bid

elif uup_down and spy_up:
    signal = "risk_on"  # Dollar weakness, capital flowing to risk assets

elif uup_up and spy_up:
    signal = "us_exceptionalism"  # US outperforming, capital inflows

elif uup_down and spy_down:
    signal = "broad_risk_off"  # Everything selling, possibly crisis
```

**Practical:**
- Already tracking UUP in intermarket indicators ✅
- Add interpretation: UUP strength hurts:
  - Emerging markets (EEM)
  - Commodities (GLD, oil)
  - US multinationals (high foreign revenue %)
- UUP weakness helps:
  - International stocks (EFA, EEM)
  - Commodities
  - Growth stocks

### Yen (Safe Haven Currency)

**JPY Strength:**
- Yen rallies (USD/JPY falls) → risk-off
- Carry trade unwind (investors borrow yen, buy risk assets → reverses)
- Signal of global stress

**Practical:**
- Track `USDJPY=X` on Yahoo Finance
- Yen spike (USDJPY drop) → usually precedes equity selloff

---

## 5. Emerging Market Flows

### Why It Works
- EM assets = high beta, sensitive to risk sentiment
- EM outflows = early warning of risk aversion
- EM inflows = global growth optimism

### Signals

```python
eem = emerging_markets_etf
spy = sp500

if eem_underperforming_spy:
    if duration > 2_weeks:
        signal = "capital_flight"  # Risk-off
        implications = "Raise cash, favor US over international"

elif eem_outperforming_spy:
    if duration > 2_weeks:
        signal = "risk_on"  # Global growth optimism
        implications = "Rotate to international, commodities"
```

**Practical:**
- Track `EEM` (emerging markets)
- Compare to `SPY`
- EEM strength = risk-on
- EEM weakness = risk-off

### Data Source
- Yahoo Finance: `EEM`

---

## 6. Treasury Yield Curve

### 2-Year vs 10-Year Spread

**Why It Matters:**
- Inverted curve (2Y > 10Y) = recession predictor
- Steepening curve = growth expectations
- Flattening curve = slowing growth

**Signals:**

```python
spread_2y_10y = ten_year_yield - two_year_yield

if spread < 0:
    signal = "inverted_curve"  # Recession warning (12-18 months out)

elif spread > 1.5:
    signal = "steep_curve"  # Strong growth expected

elif spread narrowing:
    signal = "flattening"  # Growth slowing
```

**Practical:**
- Track via FRED API or Yahoo Finance
- Inversion → historically precedes recession
- Steepening after inversion → often marks start of recovery

**Note:** Curve can stay inverted for months before recession hits. Not a timing tool, but a regime indicator.

### Data Source
- FRED API: `DGS2`, `DGS10` (2-year and 10-year yields)

---

## 7. VIX Structure (Contango vs Backwardation)

### Why It Works
- Contango (front month < later months) = complacency
- Backwardation (front month > later months) = fear, hedging demand
- VIX term structure flattens before crashes

### Signals

```python
vix_spot = vix_index
vix_3m = vix_3month_futures

if vix_spot > vix_3m:
    signal = "backwardation"  # Immediate fear, crashes often start here

elif vix_3m > vix_spot * 1.2:
    signal = "steep_contango"  # Extreme complacency
```

**Practical:**
- VIX spot: `^VIX`
- VIX futures: harder to get, may need paid data
- Alternative: Compare VIX to VXV (3-month VIX)

**Rule:**
- VIX term structure inverts → high risk of selloff
- VIX very low + steep contango → complacency, contrarian bearish

### Data Source
- Yahoo Finance: `^VIX`, `^VXV` (3-month VIX)

---

## Implementation Plan

### Phase 1: Data Collection (Easy)
- [x] Already have: SPY, VIX, TLT, UUP, GLD
- [ ] Add: BTC-USD, HYG, LQD, EEM, USDJPY=X, ^VXV
- [ ] Add: Copper (HG=F or CPER), Oil (CL=F or USO)

### Phase 2: Calculate Relationships
```python
# src/indicators/cross_asset.py

class CrossAssetIndicators:
    def btc_spy_correlation(self):
        """20-day rolling correlation."""
        pass

    def credit_spread_signal(self):
        """HYG vs LQD spread, vs historical percentiles."""
        pass

    def copper_gold_divergence(self):
        """Stagflation, reflationary, deflationary regimes."""
        pass

    def dollar_impact(self):
        """UUP strength/weakness, affected assets."""
        pass

    def em_relative_strength(self):
        """EEM vs SPY."""
        pass
```

### Phase 3: Visualization
- Dashboard page: "Cross-Asset Dashboard"
- Show:
  - BTC correlation to QQQ (chart + current reading)
  - Credit spread (HYG-LQD)
  - Copper vs Gold (regime indicator)
  - Dollar strength + implications
  - EM strength vs US

### Phase 4: LLM Integration
Feed cross-asset context into LLM agents:

```python
cross_asset_context = f"""
CROSS-ASSET SIGNALS:
- Bitcoin: {btc_change_pct}%, Correlation to QQQ: {btc_qqq_corr}
- Credit Spreads: {spread_signal} ({spread_percentile}th percentile)
- Copper/Gold Divergence: {copper_gold_regime}
- Dollar: {dollar_signal} (UUP: {uup_change})
- EM vs US: {em_signal} (EEM vs SPY: {em_relative_performance})

Interpret these signals in context of current market environment.
"""
```

---

## Example: Full Cross-Asset Analysis

### Scenario: Friday Evening

**Inputs:**
- SPY: $450 (flat for week)
- BTC: +8% over weekend
- HYG: -1.5% vs LQD: +0.5% (widening spread)
- Copper: -3%, Gold: +2%
- UUP: +1.2%
- EEM: -2% vs SPY

**Analysis:**

1. **BTC surge (+8%)**: Risk appetite strong in crypto
2. **Credit stress**: HYG underperforming, spreads widening → warning signal
3. **Copper/Gold**: Stagflation signal (growth slowing, fear rising)
4. **Dollar strong**: Flight to safety
5. **EM weak**: Capital flowing out of risky markets

**Synthesis:**
- **Mixed/Confusing Signals**: BTC says risk-on, but credit + copper/gold + dollar + EM say risk-off
- **Interpretation**: BTC rally may be isolated (crypto-specific news), not reflecting broader risk appetite
- **Recommendation**: Don't chase the BTC rally into equities. Credit + commodities + EM saying "be cautious"

**Action:**
- Keep positions small
- Consider hedges (buy VIX calls, buy TLT)
- Wait for credit markets to stabilize before adding risk

---

## Success Metrics

**Good cross-asset system:**
- Catches divergences early (before equity markets react)
- Provides confirmation (multiple signals agree)
- Explains "why" (mechanism linking assets)

**Track:**
- Lead time (cross-asset signal → equity reaction)
- False positive rate
- Accuracy of regime classification

---

## Next Steps

1. **Expand watchlist**: Add BTC-USD, HYG, LQD, EEM, USDJPY=X, copper
2. **Build indicator module**: `src/indicators/cross_asset.py`
3. **Create dashboard page**: `frontend/src/pages/cross-asset.astro`
4. **Integrate into LLM context**: Feed signals into macro/risk agents
5. **Backtest**: Historical cross-asset divergences → equity moves

This will give a much richer view of market dynamics beyond just stock prices and technicals.
