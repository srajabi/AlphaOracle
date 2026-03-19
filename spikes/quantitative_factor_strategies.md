# Spike: Quantitative Factor-Based Strategies

**Status:** Proposed (Not Implemented)
**Complexity:** High
**Priority:** Medium (Consider after validating existing strategies)
**Estimated Effort:** 2-4 weeks

---

## Overview

Explore implementing quantitative factor-based strategies using linear algebra, statistical models, and portfolio optimization - moving beyond simple trend-following to multi-asset, multi-factor systematic approaches.

**Current State:** We have 4 simple rule-based strategies (TQQQ Momentum, Dual Momentum, Sector Rotation, Mean Reversion)

**Proposed State:** Add sophisticated factor-based strategy using covariance matrices, PCA, factor models, and portfolio optimization

---

## What is Quantitative Factor Investing?

### Current Strategies (Simple Rules)
```
IF price > 200 SMA:
    Buy TQQQ
ELSE:
    Go to cash
```

### Factor Strategies (Statistical Models)
```python
# 1. Score each stock on multiple factors
scores = {
    'momentum': 12_month_return,
    'value': -1 * (price / book_value),
    'quality': ROE,
    'low_vol': -1 * volatility_60d
}

# 2. Combine into composite score
composite_score = weighted_sum(normalize(scores))

# 3. Construct optimized portfolio
top_stocks = rank_top_decile(composite_score)
weights = optimize_sharpe_ratio(top_stocks, cov_matrix)

# 4. Rebalance monthly
```

---

## Key Techniques

### 1. Factor Models (Fama-French Style)

Decompose stock returns into systematic risk factors:

```python
Return_stock = α + β_market*Market + β_size*SMB + β_value*HML + β_mom*UMD + ε

Where:
- α (alpha) = Stock-specific return (skill)
- β_market = Sensitivity to market (CAPM)
- SMB = Small Minus Big (size factor)
- HML = High Minus Low (value factor)
- UMD = Up Minus Down (momentum factor)
- ε = Idiosyncratic risk (diversifiable)
```

**Common Factors:**
| Factor | Definition | Hypothesis |
|--------|------------|------------|
| **Market** | Excess return of market over risk-free rate | Market risk premium exists |
| **Size (SMB)** | Small cap returns - Large cap returns | Small caps outperform |
| **Value (HML)** | High B/P returns - Low B/P returns | Value stocks outperform growth |
| **Momentum (UMD)** | Winners - Losers (12-month) | Trends persist |
| **Quality** | High profitability - Low profitability | Quality earns premium |
| **Low Volatility** | Low vol - High vol returns | Low risk anomaly |

**Application:**
```python
import statsmodels.api as sm

# Estimate factor loadings for each stock
def estimate_betas(stock_returns, factor_returns):
    X = sm.add_constant(factor_returns)
    model = sm.OLS(stock_returns, X).fit()
    return {
        'alpha': model.params[0],
        'beta_market': model.params[1],
        'beta_smb': model.params[2],
        'beta_hml': model.params[3]
    }

# Use loadings to forecast returns
def forecast_return(betas, expected_factor_returns):
    return (betas['alpha'] +
            betas['beta_market'] * expected_factor_returns['market'] +
            betas['beta_smb'] * expected_factor_returns['smb'] +
            betas['beta_hml'] * expected_factor_returns['hml'])
```

---

### 2. Principal Component Analysis (PCA)

Find the main "drivers" of portfolio returns:

```python
from sklearn.decomposition import PCA
import numpy as np

# Input: Returns matrix (days × stocks)
returns = pd.DataFrame({
    'AAPL': aapl_returns,
    'MSFT': msft_returns,
    'GOOGL': googl_returns,
    # ... 50 more stocks
})

# Run PCA
pca = PCA(n_components=10)
principal_components = pca.fit_transform(returns)

# Interpret components
print(f"PC1 explains {pca.explained_variance_ratio_[0]:.1%} of variance")
# Typically: PC1 = 60-70% = "Market factor"
# PC2 = 10-15% = "Sector rotation" or "Growth vs Value"
# PC3-5 = 3-8% each = Industry-specific factors
# PC6+ = Noise
```

**Application:**
- **Risk decomposition**: Understand what drives portfolio risk
- **Dimensionality reduction**: 50 stocks → 5 principal factors
- **Factor construction**: Create custom factors from PCA loadings
- **Hedging**: Identify which PC to hedge (e.g., short PC1 for market neutrality)

---

### 3. Covariance Matrix & Portfolio Optimization

**Mean-Variance Optimization (Markowitz):**

```python
import numpy as np
from scipy.optimize import minimize

def optimize_sharpe_ratio(returns, risk_free_rate=0.02):
    """Find portfolio weights that maximize Sharpe ratio."""

    # Calculate statistics
    mean_returns = returns.mean() * 252  # Annualize
    cov_matrix = returns.cov() * 252

    n_assets = len(mean_returns)

    # Objective: Minimize negative Sharpe (= maximize Sharpe)
    def neg_sharpe(weights):
        portfolio_return = weights @ mean_returns
        portfolio_vol = np.sqrt(weights @ cov_matrix @ weights)
        sharpe = (portfolio_return - risk_free_rate) / portfolio_vol
        return -sharpe

    # Constraints
    constraints = [
        {'type': 'eq', 'fun': lambda w: np.sum(w) - 1}  # Fully invested
    ]

    # Bounds (long-only: 5-20% per stock)
    bounds = [(0.05, 0.20) for _ in range(n_assets)]

    # Optimize
    result = minimize(
        neg_sharpe,
        x0=np.ones(n_assets) / n_assets,  # Start equal weight
        method='SLSQP',
        bounds=bounds,
        constraints=constraints
    )

    return result.x
```

**Advanced: Risk Parity**
```python
def risk_parity_weights(cov_matrix):
    """Equal risk contribution from each asset."""
    # Each asset contributes 1/N to portfolio risk
    # More complex - requires iterative solver
```

**Advanced: Black-Litterman**
```python
def black_litterman(market_weights, views, confidence):
    """Blend market equilibrium with investor views."""
    # Bayesian approach to portfolio optimization
```

---

### 4. Long-Short Portfolio Construction

**Quantile-Based Selection:**

```python
def construct_long_short_portfolio(scores, universe):
    """Build dollar-neutral long-short portfolio."""

    # Rank stocks by composite score
    ranked = universe.copy()
    ranked['score'] = scores
    ranked = ranked.sort_values('score')

    n = len(ranked)

    # Top decile = long, bottom decile = short
    long_stocks = ranked.tail(int(n * 0.1))
    short_stocks = ranked.head(int(n * 0.1))

    # Optimize weights within each bucket
    long_weights = optimize_sharpe_ratio(long_stocks)
    short_weights = optimize_sharpe_ratio(short_stocks)

    # Dollar-neutral: 50% long, 50% short
    portfolio = {
        **{ticker: w * 0.5 for ticker, w in long_weights.items()},
        **{ticker: -w * 0.5 for ticker, w in short_weights.items()}
    }

    return portfolio
```

**Key Metrics:**
- **Market neutrality**: `sum(weights) ≈ 0`
- **Dollar neutrality**: `sum(abs(weights)) = 1.0`
- **Sector neutrality**: `sum(weights_per_sector) ≈ 0`

---

### 5. Factor Orthogonalization

Remove correlation between factors to isolate pure signals:

```python
from sklearn.linear_model import LinearRegression

def orthogonalize_factor(target_factor, control_factors):
    """Remove influence of control factors from target."""

    # Regress target on controls
    model = LinearRegression()
    model.fit(control_factors, target_factor)

    # Residual = pure target signal uncorrelated with controls
    pure_signal = target_factor - model.predict(control_factors)

    return pure_signal

# Example: Pure momentum after removing market beta
momentum_raw = calculate_momentum(stocks)
market_exposure = stocks_beta_to_spy

# Pure momentum (market-neutral)
pure_momentum = orthogonalize_factor(
    target_factor=momentum_raw,
    control_factors=market_exposure
)
```

**Application:** Separate "momentum" from "market beta" to avoid conflating skill with market timing.

---

## Implementation Phases

### Phase 1: Simple Multi-Factor Ranking (Week 1)

**Scope:** Build factor scores using only price/volume data we already have.

```python
# Universe: Top 30 liquid stocks
universe = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA',
    'AMD', 'INTC', 'MU', 'AVGO', 'QCOM',
    'NFLX', 'DIS', 'PYPL', 'SQ',
    'JPM', 'BAC', 'GS', 'MS',
    'XOM', 'CVX', 'COP',
    'WMT', 'TGT', 'COST',
    'UNH', 'JNJ', 'PFE', 'ABBV'
]

# Factors (price-based only)
def calculate_factors(ticker, data):
    returns = data['close'].pct_change()

    return {
        'momentum_12m': data['close'][-1] / data['close'][-252] - 1,
        'momentum_6m': data['close'][-1] / data['close'][-126] - 1,
        'momentum_3m': data['close'][-1] / data['close'][-63] - 1,
        'trend': data['close'][-1] / data['close'].rolling(200).mean()[-1] - 1,
        'relative_strength': momentum_12m - spy_momentum_12m,
        'volatility': returns[-60:].std() * np.sqrt(252),
        'sharpe': (momentum_12m / (volatility + 1e-6)),
    }

# Composite score (equal weight)
def composite_score(factors):
    # Z-score normalize each factor
    z_scores = {k: (v - mean[k]) / std[k] for k, v in factors.items()}

    # Weighted combination
    return (
        0.30 * z_scores['momentum_12m'] +
        0.20 * z_scores['relative_strength'] +
        0.20 * z_scores['trend'] +
        0.15 * z_scores['sharpe'] +
        0.15 * -z_scores['volatility']  # Negative: prefer low vol
    )

# Portfolio construction
all_scores = {ticker: composite_score(calculate_factors(ticker))
              for ticker in universe}
ranked = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)

# Hold top 10 stocks, equal weight
top_10 = ranked[:10]
weights = {ticker: 0.10 for ticker, score in top_10}
```

**Backtest comparison:**
- Factor strategy vs equal-weight 30 stocks
- Factor strategy vs SPY buy-and-hold
- Factor strategy vs TQQQ Momentum

**Metrics:**
- Total return, CAGR, Sharpe ratio, max drawdown
- Turnover (how often stocks change)
- Concentration (HHI index)

---

### Phase 2: Add Optimization (Week 2)

Replace equal weighting with mean-variance optimization:

```python
# Select top quintile by factor score
top_stocks = select_top_quintile(ranked_scores)

# Optimize weights to maximize Sharpe
historical_returns = get_returns(top_stocks, lookback=252)
optimal_weights = optimize_sharpe_ratio(historical_returns)

# Apply constraints
constraints = {
    'max_weight_per_stock': 0.20,
    'min_weight_per_stock': 0.03,
    'max_sector_weight': 0.40,
    'target_number_of_stocks': 12
}
```

**Advanced techniques:**
- **Shrinkage estimators** (Ledoit-Wolf) for stable covariance
- **Robust optimization** (worst-case scenarios)
- **Transaction cost penalties** in objective function

---

### Phase 3: Add Fundamental Factors (Week 3)

**Problem:** Price-only factors are limited. Need fundamental data.

**Solution:** Integrate fundamental data from API:

```python
import yfinance as yf

def get_fundamental_factors(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info

    return {
        'pe_ratio': info.get('forwardPE', None),
        'pb_ratio': info.get('priceToBook', None),
        'roe': info.get('returnOnEquity', None),
        'profit_margin': info.get('profitMargins', None),
        'debt_to_equity': info.get('debtToEquity', None),
        'earnings_growth': info.get('earningsGrowth', None),
        'revenue_growth': info.get('revenueGrowth', None)
    }

# Add to composite score
composite_score = (
    0.25 * momentum_score +
    0.25 * value_score +       # Based on P/E, P/B
    0.25 * quality_score +     # Based on ROE, margins
    0.25 * growth_score        # Based on earnings/revenue growth
)
```

**Data sources:**
- yfinance (free, real-time fundamentals)
- Alpha Vantage (free API, quarterly fundamentals)
- Financial Modeling Prep (paid, comprehensive)

---

### Phase 4: Long-Short Implementation (Week 4)

**Challenges:**
- Need short borrow cost data
- Margin requirements (2:1 leverage)
- Hard-to-borrow stocks

**Implementation:**
```python
def construct_market_neutral_portfolio(scores):
    # Long top quintile
    long_positions = top_20pct(scores)
    long_weights = optimize_weights(long_positions) * 1.0

    # Short bottom quintile
    short_positions = bottom_20pct(scores)
    short_weights = -optimize_weights(short_positions) * 1.0

    # Result: 100% long, 100% short = 0 net market exposure
    return {**long_weights, **short_weights}
```

**Backtest considerations:**
- **Borrow costs:** Assume 0.5% annual for liquid large caps
- **Short squeeze risk:** Avoid stocks with >20% short interest
- **Rebalancing costs:** Higher turnover on short side

---

## Practical Considerations

### Data We Have (Can Use Now)
✅ **Historical prices** (OHLCV) - 33 years for indices, 15-40 years for stocks
✅ **Sector classification** - Can add manually or via yfinance
✅ **Market cap** - Available via yfinance
✅ **Returns, volatility, momentum** - Calculated from prices

### Data We Need (Requires Additional Work)
❌ **Fundamental ratios** (P/E, ROE, debt/equity) - Need API integration
❌ **Short borrow costs** - Need Interactive Brokers data or estimates
❌ **Earnings dates** - For avoiding event risk
❌ **Analyst estimates** - For earnings surprise factors
❌ **Insider trading** - For sentiment factors

### Key Challenges

**1. Survivorship Bias**
- Our current watchlist includes only stocks that exist today
- Winners who survived vs losers who delisted
- **Solution:** Use S&P 500 constituent history (available datasets)

**2. Overfitting**
- Easy to find factors that worked historically but don't persist
- Too many parameters = curve fitting
- **Solution:** Walk-forward validation, out-of-sample testing

**3. Transaction Costs**
- Factor strategies rebalance frequently (monthly)
- Can destroy returns if not accounted for
- **Solution:** Optimize turnover, use buffer zones

**4. Estimation Error**
- Covariance matrices are noisy with limited data
- Small changes in inputs → Large changes in optimal weights
- **Solution:** Shrinkage estimators, constraints, regularization

**5. Capacity Constraints**
- Strategies work with $10M might not work with $1B
- Market impact, slippage increase with size
- **Solution:** Focus on liquid large caps (>$10B market cap)

---

## Comparison to Current Strategies

| Aspect | Current (TQQQ Momentum) | Factor Strategy |
|--------|-------------------------|-----------------|
| **Complexity** | Very simple (1 indicator) | Complex (multiple factors, optimization) |
| **Assets** | 1-3 ETFs | 10-30 stocks |
| **Rebalancing** | ~10x per year | ~12x per year (monthly) |
| **Transaction costs** | Low | Higher |
| **Diversification** | Low (single asset) | High (10-30 stocks) |
| **Max drawdown** | -38% (TQQQ) | Potentially lower (-20-25%) |
| **Backtested return** | 329% over 5 years (TQQQ) | Unknown, needs testing |
| **Implementation risk** | Low (hard to mess up) | High (many moving parts) |
| **Data requirements** | Just prices | Prices + fundamentals |
| **Explanation** | Easy ("Buy when above 200 SMA") | Complex (hard to explain) |

**Key Question:** Does the added complexity deliver enough extra return or risk reduction to justify it?

---

## Expected Performance

Based on academic literature and industry benchmarks:

### Long-Only Multi-Factor
- **CAGR:** 12-18% (vs 10% for S&P 500)
- **Sharpe:** 0.7-1.0
- **Max Drawdown:** -30 to -40%
- **Better than buy-and-hold?** Marginally (1-3% annual alpha)

### Long-Short Market Neutral
- **CAGR:** 8-12% (uncorrelated to market)
- **Sharpe:** 1.0-1.5
- **Max Drawdown:** -15 to -25%
- **Correlation to S&P:** 0.0 to 0.2 (low)

**Reality check:** Most factor strategies **underperformed** in 2018-2020 due to:
- Momentum crash (March 2020)
- Value factor failure (growth dominance)
- Quant crowding (everyone running same strategies)

**Current strategies are already excellent:**
- reddit_200sma_tqqq: +26,860% over 33 years (0.69 Sharpe)
- Dual Momentum: +65% over 5 years (0.75 Sharpe)

Factor strategies might not beat this!

---

## Recommendation

### Should We Build This?

**Arguments FOR:**
- ✅ Diversification across strategy types (trend + factor)
- ✅ More institutional/professional approach
- ✅ Can run market-neutral (works in bear markets)
- ✅ Interesting learning experience
- ✅ Less concentrated risk than single-asset strategies

**Arguments AGAINST:**
- ❌ Much higher complexity (10x more code)
- ❌ Existing strategies already work extremely well
- ❌ Factor premiums may be arbitraged away
- ❌ Requires fundamental data we don't have yet
- ❌ Higher transaction costs
- ❌ Risk of overfitting

### Suggested Path Forward

**Option A: Defer (Recommended)**
1. Validate existing 4 strategies with paper trading for 6-12 months
2. Deploy live capital to proven strategies
3. Once those are running profitably, revisit factor strategies

**Option B: Proof of Concept**
1. Build Phase 1 (simple multi-factor ranking) as experiment
2. Backtest with 33 years of data
3. If Sharpe > 0.8 and outperforms SPY, continue
4. If not, abandon and stick with current strategies

**Option C: Hybrid Approach**
1. Keep Accounts 2-5 running existing strategies
2. Use Account 1 (currently LLM) for factor strategy experiment
3. Compare live performance head-to-head

---

## Next Steps (If Pursuing)

### Immediate (Week 1)
- [ ] Define universe (top 30-50 liquid stocks)
- [ ] Implement factor calculation functions
- [ ] Build composite scoring system
- [ ] Create simple equal-weight backtest
- [ ] Compare to SPY benchmark

### Short-term (Weeks 2-3)
- [ ] Add portfolio optimization
- [ ] Integrate yfinance for fundamentals
- [ ] Test multiple factor combinations
- [ ] Walk-forward validation (train 20 years, test 13 years)

### Medium-term (Month 2)
- [ ] Implement in `src/strategies/factor_strategy.py`
- [ ] Add to backtesting framework
- [ ] Create dashboard page for factor strategy
- [ ] Paper trade for 3-6 months

### Long-term (Month 3+)
- [ ] Add long-short capability
- [ ] Optimize factor weights
- [ ] Deploy to live account (small size)
- [ ] Monitor and refine

---

## References & Resources

### Academic Papers
- Fama & French (1993): "Common Risk Factors in Returns on Stocks and Bonds"
- Carhart (1997): "On Persistence in Mutual Fund Performance" (momentum factor)
- Asness et al (2013): "Value and Momentum Everywhere"
- Frazzini & Pedersen (2014): "Betting Against Beta"

### Books
- "Quantitative Momentum" by Wesley Gray
- "Factor Investing and Asset Allocation" by Andrew Ang
- "Advanced Portfolio Management" by Giuseppe Paleologo
- "Machine Learning for Asset Managers" by Marcos Lopez de Prado

### Libraries
```python
# Portfolio optimization
import cvxpy as cp  # Convex optimization
from pypfopt import EfficientFrontier, risk_models, expected_returns

# Factor analysis
import statsmodels.api as sm
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Data
import yfinance as yf  # Fundamentals
import pandas_datareader as pdr  # Fama-French factors
```

### Existing Code to Reference
- `backtesting/portfolio_strategies.py` - Portfolio construction patterns
- `src/strategies/strategy_executor.py` - Execution framework
- `backtesting/engine.py` - Backtesting infrastructure

---

## Conclusion

Quantitative factor strategies represent a sophisticated approach to systematic investing that could complement our existing trend-following strategies. However, they:

1. **Add significant complexity** without guaranteed performance improvement
2. **Require additional data** (fundamentals, borrow costs)
3. **Face empirical challenges** (factor crowding, overfitting)
4. **May not beat** our already-excellent simple strategies

**Recommendation:** Document this spike for future reference, but focus on validating and deploying the 4 existing strategies first. Revisit factor strategies in 6-12 months if:
- Existing strategies prove profitable in live trading
- We want to diversify strategy types for portfolio-level risk management
- Factor premiums show signs of recovery (post-2020 quant winter)

The knowledge documented here provides a roadmap if/when we decide to pursue this direction.
