---
title: Technical Analyst Report
date: "2026-05-08"
---

## Model: deepseek/deepseek-reasoner

Based on the price action data, here are the key technical observations and actionable setups.

### **Technical Overview**

| Condition | Tickers |
|-----------|---------|
| **Overbought (RSI > 70)** | SPY, QQQ, XLK, TQQQ, UPRO, SSO, NVDA, AAPL, AMZN, GOOGL, TSLA, AMD, INTC, MU, WDC, STX, CRWD, IWM, VTI, QUAL, AVGO (near 60 but slowing) |
| **Oversold (RSI < 45)** | PLTR (44.9), XLE (41.7), XLU (41.2), TMF (44.2), ^VIX (40.3) |
| **Mean Reversion Bounce Candidates** | PLTR, XLE, XLU, TLT (neutral, near lower BB) |
| **Trend Continuation (strong, not overbought)** | ORCL, CEG, TLN, MTZ, NBIS, TSM, SCHD, VXUS, VGK, EWC |
| **Failed Setups** | None obvious |

### **Recommended Setups**

**1. Mean Reversion Bounce – PLTR**  
- Price: $137.05 (near lower BB at $129.46)  
- RSI: 44.9 (oversold)  
- MACD: Bearish but histogram flattening  
- All SMAs below price (bearish long-term) → counter-trend bounce only  
- **Action:** Buy shares near $135 (or sell cash-secured put at $130 strike for May 22). Target: SMA20 ($140.74). Stop: below $129.

**2. Mean Reversion Bounce – XLE (Energy Sector)**  
- Price: $55.95 (near lower BB $54.31, above SMA200 $48.31)  
- RSI: 41.7 (oversold)  
- Long-term uptrend intact (price above SMA200)  
- **Action:** Buy shares near $55.50 or sell cash-secured put at $54 strike. Target: SMA50 ($57.79). Stop: below $54.30.

**3. Mean Reversion Bounce – XLU (Utilities) / TLT (Bonds)**  
- XLU: RSI 41.2, lower BB $44.95, price $45.12. Defensive play.  
- TLT: RSI 46.25, lower BB $85.03, price $85.65. Bond yields near 5% create dip-buying interest.  
- **Action:** Sell cash-secured puts on XLU ($44 strike) or TLT ($85 strike) to collect premium. Shares only if closer to lower BB.

**4. Trend Continuation – TLN, MTZ, NBIS (AI infrastructure / power)**  
- All above 20/50/200 SMAs, RSI 60-67, MACD rising.  
- **Action:** Buy on pullback to 20-day SMA (TLN ~$360, MTZ ~$386, NBIS ~$159). Not suitable for chase here.

### **What to Avoid**
- **Overbought momentum stocks** (NVDA, GOOGL, AMD, INTC, MU): risk of sharp pullback. Wait for RSI < 50.
- **Leveraged ETFs** (TQQQ, UPRO, SSO): RSI > 70, near upper BBs. Not entry points.

### **Suggested Trades (within $87k cash)**

| Trade | Entry | Stop | Target | Risk |
|-------|-------|------|--------|------|
| Buy 100 PLTR @ $137 | $137 | $129 | $141 | ~$800 |
| Buy 100 XLE @ $55.95 | $55.95 | $54.30 | $57.80 | ~$165 |
| Sell 1 CSP XLE $54 May 22 | ~$0.60 credit | if assigned $54 | keep premium | $5,400 collateral |
| Sell 1 CSP TLT $85 May 22 | ~$0.50 credit | if assigned $85 | keep premium | $8,500 collateral |

**Priority:** PLTR (highest probability of a bounce due to oversold + news-ignored technicals + high beta). XLE as second leg for portfolio diversification. Use CSPs for XLU/TLT to generate income without margin.

---

## Model: gemini/gemini-2.5-flash

Here's a technical analysis of the provided market data, focusing purely on price action and technical indicators as requested:

**Overall Market Posture (from key indices and VIX):**
The market is in a **strong bullish trend continuation**, as indicated by SPY, QQQ, VOO, and DIA all trading well above their 20, 50, and 200-day Simple Moving Averages (SMAs), with SMAs in a bullish order (`SMA20 > SMA50 > SMA200`). MACD histograms are positive, showing upward momentum. However, RSI for these major indices (SPY: 73.07, QQQ: 79.33, VOO: 73.04) are in **overbought territory**, and prices are at or near their upper Bollinger Bands, suggesting these major indices are **overextended** in the short term and potentially due for a mean reversion or pullback. The **^VIX** is in a bearish trend (low volatility), trading below all SMAs and near its lower Bollinger Band, consistent with a "Bull Quiet" regime and low market fear.

---

**Individual Ticker Analysis:**

1.  **PLTR (Palantir Technologies): Bearish Trend Continuation.**
    *   Price is below all key SMAs (`SMA20 < SMA50 < SMA200`), indicating a clear downtrend.
    *   RSI (44.86) is in bearish territory, and MACD shows a bearish crossover (`macd < macd_signal`, negative `macd_hist`), confirming downward momentum.
    *   Price is within the lower half of Bollinger Bands, suggesting further potential downside.

2.  **XLK (Technology Select Sector SPDR Fund): Strong Bullish Trend Continuation (Highly Overextended).**
    *   Price is well above all SMAs, which are in a strong bullish order.
    *   RSI (79.80) is very overbought, and price is at the upper Bollinger Band.
    *   MACD is strongly positive. This is a very strong uptrend but highly vulnerable to a short-term pullback.

3.  **TLT (iShares 20+ Year Treasury Bond ETF): Bearish Trend Continuation / Weak Consolidation.**
    *   Price is below all SMAs, which are tightly coiled and in a slightly bearish order.
    *   RSI (46.25) is weak, and MACD shows a bearish crossover with weak negative momentum.
    *   Price is near the lower Bollinger Band, indicating short-term weakness.

4.  **AVGO (Broadcom Inc.): Bullish Trend Continuation (Momentum Fading).**
    *   Price is above all SMAs in a strong bullish order.
    *   RSI (60.06) is bullish but MACD shows a bearish crossover (`macd < macd_signal`, negative `macd_hist`), suggesting momentum is slowing despite the strong trend.
    *   Price is in the upper half of Bollinger Bands. May see short-term consolidation or a minor pullback.

5.  **ORCL (Oracle Corporation): Strong Mean Reversion Bounce / Potential Trend Reversal.**
    *   Price has aggressively rallied above its SMA20 and SMA50, though still below SMA200.
    *   RSI (68.87) is strong and approaching overbought, and MACD shows a clear bullish crossover with strong positive momentum.
    *   Price is near the upper Bollinger Band. Indicates a strong bounce with potential to challenge long-term resistance.

6.  **XLY (Consumer Discretionary Select Sector SPDR Fund): Bullish Trend Continuation.**
    *   Price is above all SMAs, which are showing a developing bullish order.
    *   RSI (62.41) is bullish, and MACD is barely positive but confirms upward momentum.
    *   Price is in the upper half of Bollinger Bands.

7.  **QUAL (iShares MSCI USA Quality Factor ETF): Bullish Trend Continuation.**
    *   Price is above all SMAs in a strong bullish order.
    *   RSI (65.69) is bullish, and MACD is positive.
    *   Price is near the upper Bollinger Band, indicating strong, sustained momentum.

8.  **XLF (Financial Select Sector SPDR Fund): Sideways Consolidation / Slight Bearish Drift.**
    *   Price is below SMA20 and SMA200 but above SMA50, indicating a mixed short-term outlook.
    *   RSI (51.68) is neutral, and MACD shows a bearish crossover with weak negative momentum.
    *   Price is within Bollinger Bands, suggesting indecision.

9.  **VT (Vanguard Total World Stock ETF): Strong Bullish Trend Continuation.**
    *   Price is above all SMAs in a strong bullish order.
    *   RSI (66.01) is bullish, and MACD is strongly positive.
    *   Price is near the upper Bollinger Band. Sustained upward momentum.

10. **TQQQ (ProShares UltraPro QQQ): Extremely Strong Bullish Trend Continuation (Highly Overextended).**
    *   Price is significantly above all SMAs in a very strong bullish order.
    *   RSI (79.67) is very overbought, and price is at the upper Bollinger Band.
    *   MACD is extremely positive. Extreme bullishness, but highly vulnerable to a sharp pullback.

11. **VTI (Vanguard Total Stock Market ETF): Strong Bullish Trend Continuation (Overextended).**
    *   Price is above all SMAs in a strong bullish order.
    *   RSI (71.30) is overbought, and price is near the upper Bollinger Band.
    *   MACD is strongly positive. Strong trend, but caution warranted due to overextension.

12. **VGK (Vanguard FTSE Europe ETF): Consolidation.**
    *   Price is around SMA20, but above SMA50 and SMA200, which are in a bullish order.
    *   RSI (53.23) is neutral, and MACD shows a bearish crossover with very weak negative momentum.
    *   Price is near the midline of Bollinger Bands. Short-term momentum has stalled within an underlying uptrend.

13. **NFLX (Netflix, Inc.): Strong Bearish Trend Continuation.**
    *   Price is well below all key SMAs (`SMA20 < SMA50 < SMA200`), indicating a strong downtrend.
    *   RSI (35.31) is bearish and approaching oversold, and MACD shows strong bearish momentum.
    *   Price is heading towards the lower Bollinger Band.

14. **UUP (Invesco DB US Dollar Index Bullish Fund): Volatility Contraction Squeeze / Slight Bearish Drift.**
    *   SMAs are tightly coiled, and Bollinger Bands are very narrow, indicating low volatility.
    *   Price is below SMA20 and SMA50 but above SMA200.
    *   RSI (46.92) is neutral, and MACD shows a very weak bearish crossover. A significant move could be imminent.

15. **QQQ (Invesco QQQ Trust): Extremely Strong Bullish Trend Continuation (Highly Overextended).**
    *   Price is significantly above all SMAs in a very strong bullish order.
    *   RSI (79.33) is very overbought, and price is at the upper Bollinger Band.
    *   MACD is extremely positive. Extreme bullishness, highly vulnerable to a sharp pullback.

16. **CEG (Constellation Energy Corporation): Mean Reversion Bounce / Potential Trend Reversal.**
    *   Price has rallied above SMA20 and SMA50, now testing SMA200.
    *   RSI (54.11) is neutral to bullish, and MACD shows a strong bullish crossover with positive momentum.
    *   Price is in the upper half of Bollinger Bands. A break above SMA200 would confirm a stronger reversal.

17. **PSTG (Pure Storage, Inc.): Strong Bullish Trend Continuation.**
    *   Price has recently broken above its SMA200 and is now well above all SMAs in a developing bullish order.
    *   RSI (69.72) is strong and approaching overbought, and MACD is strongly positive.
    *   Price is near the upper Bollinger Band. Strong upward momentum.

18. **XLU (Utilities Select Sector SPDR Fund): Bearish Trend Continuation.**
    *   Price is below SMA20 and SMA50, which are in a bearish order, though still above SMA200.
    *   RSI (41.23) is bearish, and MACD shows a bearish crossover with negative momentum.
    *   Price is at the lower Bollinger Band, suggesting potential for further downside or a short-term bounce.

19. **TMF (Direxion Daily 20+ Year Treasury Bull 3X Shares): Strong Bearish Trend Continuation.**
    *   Price is below all SMAs (`SMA20 < SMA50 < SMA200`), indicating a strong downtrend.
    *   RSI (44.16) is weak, and MACD shows a bearish crossover with negative momentum.
    *   Price is in the lower half of Bollinger Bands. Amplified bearishness due to leverage.

20. **WDC (Western Digital Corporation): Extremely Strong Bullish Trend Continuation (Highly Overextended).**
    *   Price is significantly above all SMAs in an extremely strong bullish order.
    *   RSI (73.85) is overbought, and MACD is extremely positive.
    *   Price is pushing towards the upper Bollinger Band. Extreme bullishness, but significant risk of pullback.

21. **SPY (SPDR S&P 500 ETF Trust): Strong Bullish Trend Continuation (Overextended).**
    *   Price is well above all SMAs in a strong bullish order.
    *   RSI (73.07) is overbought, and price is near the upper Bollinger Band.
    *   MACD is strongly positive. Strong trend, but caution warranted due to overextension.

22. **TLN (Talen Energy Corporation): Strong Bullish Trend Continuation.**
    *   Price is above all SMAs, which are showing a developing bullish order.
    *   RSI (61.07) is bullish, and MACD is very strongly positive.
    *   Price is in the upper half of Bollinger Bands. Strong upward momentum.

23. **IBIT (iShares Bitcoin Trust): Mean Reversion Bounce / Short-term Bullish Continuation.**
    *   Price has rallied above SMA20 and SMA50, but remains below SMA200.
    *   RSI (62.04) is bullish, and MACD shows a bullish crossover with positive momentum.
    *   Price is near the upper Bollinger Band. Continuing a bounce, but still facing long-term resistance.

24. **TSM (Taiwan Semiconductor Manufacturing Company): Strong Bullish Trend Continuation.**
    *   Price is above all SMAs in a strong bullish order.
    *   RSI (65.57) is bullish, and MACD is strongly positive.
    *   Price is near the upper Bollinger Band. Strong upward momentum.

25. **AAPL (Apple Inc.): Strong Bullish Trend Continuation (Overextended).**
    *   Price is above all SMAs in a strong bullish order.
    *   RSI (69.31) is approaching overbought, and price is at the upper Bollinger Band.
    *   MACD is strongly positive. Strong trend, but showing signs of short-term overextension.

26. **XLI (Industrial Select Sector SPDR Fund): Bullish Trend Continuation.**
    *   Price is above all SMAs in a strong bullish order.
    *   RSI (55.15) is neutral to bullish, and MACD is positive.
    *   Price is in the upper half of Bollinger Bands.

27. **INTC (Intel Corporation): Extremely Strong Bullish Trend Continuation (Highly Overextended).**
    *   Price is significantly above all SMAs in an extremely strong bullish order.
    *   RSI (80.50) is very overbought, and MACD is extremely positive.
    *   Price is pushing towards the upper Bollinger Band. Extreme bullishness, with high probability of a strong pullback.

28. **IAU (iShares Gold Trust): Consolidation / Slight Bullish Bias.**
    *   Price is around SMA20, below SMA50 but above SMA200.
    *   RSI (50.74) is neutral, and MACD shows a weak bullish crossover with minor positive momentum.
    *   Price is near the midline of Bollinger Bands. Short-term indecision within a longer-term bullish trend.

29. **TSLA (Tesla, Inc.): Strong Mean Reversion Bounce / Short-term Bullish Continuation.**
    *   Price has sharply rallied above all SMAs, which were previously in a bearish order.
    *   RSI (64.60) is bullish, and MACD shows an extremely strong bullish crossover.
    *   Price is at the upper Bollinger Band. Indicates a powerful short-term rebound that is now highly extended.

30. **SCHD (Schwab U.S. Dividend Equity ETF): Bullish Trend Continuation.**
    *   Price is above all SMAs in a strong bullish order.
    *   RSI (57.49) is neutral to bullish, and MACD is positive.
    *   Price is in the upper half of Bollinger Bands. Steady upward momentum.

31. **GLD (SPDR Gold Shares): Consolidation / Slight Bullish Bias.**
    *   Price is around SMA20, below SMA50 but above SMA200.
    *   RSI (50.70) is neutral, and MACD shows a weak bullish crossover with minor positive momentum.
    *   Price is near the midline of Bollinger Bands. Short-term indecision within a longer-term bullish trend.

32. **SSO (ProShares Ultra S&P500): Strong Bullish Trend Continuation (Overextended).**
    *   Price is well above all SMAs in a strong bullish order.
    *   RSI (72.51) is overbought, and price is near the upper Bollinger Band.
    *   MACD is strongly positive. Strong trend, but caution warranted due to overextension.

33. **^VIX (CBOE Volatility Index): Bearish Trend Continuation (Low Volatility).**
    *   Price is below all SMAs, which are in a bearish order.
    *   RSI (40.34) is bearish, and MACD is flat / weakly positive but overall negative trend.
    *   Price is near the lower Bollinger Band. Confirms a period of low market fear and volatility.

34. **STX (Seagate Technology Holdings Plc): Extremely Strong Bullish Trend Continuation (Highly Overextended).**
    *   Price is significantly above all SMAs in an extremely strong bullish order.
    *   RSI (81.06) is extremely overbought, and MACD is extremely positive.
    *   Price is pushing towards the upper Bollinger Band. Extreme bullishness, with high probability of a strong pullback.

35. **SLV (iShares Silver Trust): Bullish Trend Continuation.**
    *   Price is above all SMAs in a strong bullish order.
    *   RSI (56.09) is neutral to bullish, and MACD shows a bullish crossover with positive momentum.
    *   Price is in the upper half of Bollinger Bands. Solid upward trend.

36. **XLRE (Real Estate Select Sector SPDR Fund): Bullish Trend Continuation (Weak Momentum).**
    *   Price is above all SMAs in a strong bullish order.
    *   RSI (60.34) is bullish, but MACD shows a very weak bullish crossover, suggesting limited momentum.
    *   Price is near the upper Bollinger Band, indicating strength, but also potential for short-term pause.

37. **META (Meta Platforms, Inc.): Strong Bearish Trend Continuation.**
    *   Price is well below all key SMAs (`SMA20 < SMA50 < SMA200`), indicating a strong downtrend.
    *   RSI (44.31) is bearish, and MACD shows strong bearish momentum.
    *   Price is heading towards the lower Bollinger Band.

38. **AMD (Advanced Micro Devices, Inc.): Extremely Strong Bullish Trend Continuation (Highly Overextended).**
    *   Price is significantly above all SMAs in an extremely strong bullish order.
    *   RSI (76.14) is very overbought, and MACD is extremely positive.
    *   Price is near the upper Bollinger Band. Extreme bullishness, with high probability of a strong pullback.

39. **CRWD (CrowdStrike Holdings, Inc.): Extremely Strong Bullish Trend Continuation (Extreme Overextension).**
    *   Price is significantly above all SMAs in a strong bullish order.
    *   RSI (70.43) is overbought, and price is *above* the upper Bollinger Band.
    *   MACD is very strongly positive. Represents an extreme extension, highly likely to mean revert aggressively.

40. **AMZN (Amazon.com, Inc.): Strong Bullish Trend Continuation (Overextended).**
    *   Price is well above all SMAs in a strong bullish order.
    *   RSI (74.23) is overbought, and price is pushing towards the upper Bollinger Band.
    *   MACD is strongly positive. Strong trend, but caution warranted due to overextension.

41. **EWA (iShares MSCI Australia ETF): Consolidation / Slight Bearish Drift.**
    *   Price is below SMA20 but above SMA50 and SMA200. SMAs are mixed short-term.
    *   RSI (52.74) is neutral, and MACD shows a very weak bearish crossover.
    *   Price is near the midline of Bollinger Bands.

42. **XLC (Communication Services Select Sector SPDR Fund): Bullish Trend Continuation (Momentum Weakening).**
    *   Price is above all SMAs in a bullish order.
    *   RSI (57.74) is neutral to bullish, but MACD shows a bearish crossover with weak negative momentum.
    *   Price is in the upper half of Bollinger Bands. May see short-term consolidation or a minor pullback.

43. **GOOGL (Alphabet Inc.): Extremely Strong Bullish Trend Continuation (Highly Overextended).**
    *   Price is significantly above all SMAs in an extremely strong bullish order.
    *   RSI (83.42) is extremely overbought, and price is near the upper Bollinger Band.
    *   MACD is extremely positive. Extreme bullishness, with high probability of a strong pullback.

44. **EWC (iShares MSCI Canada ETF): Volatility Contraction Squeeze / Slight Bearish Drift.**
    *   SMAs are somewhat coiled, and Bollinger Bands show some narrowing.
    *   Price is below SMA20 but above SMA50 and SMA200.
    *   RSI (54.11) is neutral, and MACD shows a bearish crossover with weak negative momentum. Could be setting up for a move.

45. **XLP (Consumer Staples Select Sector SPDR Fund): Bullish Trend Continuation.**
    *   Price is above all SMAs in a bullish order.
    *   RSI (55.76) is neutral to bullish, and MACD shows a strong bullish crossover.
    *   Price is in the upper half of Bollinger Bands. Steady upward momentum.

46. **XLE (Energy Select Sector SPDR Fund): Bearish Short/Mid-Term Trend Continuation.**
    *   Price is below SMA20 and SMA50, which are in a bearish order, though still above SMA200.
    *   RSI (41.75) is bearish, and MACD shows a bearish crossover with weak negative momentum.
    *   Price is in the lower half of Bollinger Bands.

47. **MTZ (MasTec, Inc.): Strong Bullish Trend Continuation.**
    *   Price is well above all SMAs in an extremely strong bullish order.
    *   RSI (64.41) is bullish, and MACD is strongly positive.
    *   Price is in the upper half of Bollinger Bands. Sustained upward momentum.

48. **NBIS (Nebius Group N.V.): Strong Bullish Trend Continuation (Approaching Overextended).**
    *   Price is well above all SMAs in an extremely strong bullish order.
    *   RSI (67.18) is strong and approaching overbought, and MACD is strongly positive.
    *   Price is pushing towards the upper Bollinger Band. Strong trend, but becoming extended.

49. **NVDA (NVIDIA Corporation): Bullish Trend Continuation (Momentum Weakening).**
    *   Price is above all SMAs in a strong bullish order.
    *   RSI (63.40) is bullish but MACD shows a bearish crossover (`macd < macd_signal`, negative `macd_hist`), suggesting momentum is slowing despite the strong trend.
    *   Price is in the upper half of Bollinger Bands. May see short-term consolidation or a minor pullback.

50. **MSFT (Microsoft Corporation): Consolidation / Pullback within Mixed Trend.**
    *   Price is above SMA20 and SMA50 but below SMA200, which acts as long-term resistance.
    *   RSI (57.82) is neutral to bullish, but MACD shows a bearish crossover with negative momentum.
    *   Price is in the upper half of Bollinger Bands, but with falling momentum.

51. **XLV (Health Care Select Sector SPDR Fund): Bearish Trend Continuation / Weak Mean Reversion Bounce.**
    *   Price is below all SMAs (`SMA20 < SMA50 < SMA200`), indicating a downtrend.
    *   RSI (44.30) is bearish. MACD shows a weak bullish crossover, but it might be a temporary bounce within a bearish trend, especially with price near the lower Bollinger Band.

52. **KLAC (KLA Corporation): Pullback within Bullish Trend.**
    *   Price is below SMA20 but remains above SMA50 and SMA200, which are in a bullish order.
    *   RSI (53.66) is neutral, but MACD shows a strong bearish crossover with significant negative momentum.
    *   Price is in the middle to lower half of Bollinger Bands. Indicates a notable loss of short-term upward momentum.

53. **XLB (Materials Select Sector SPDR Fund): Volatility Contraction Squeeze / Slight Bearish Drift.**
    *   Bollinger Bands are somewhat narrow, and price is below SMA20 but above SMA50 and SMA200.
    *   RSI (51.21) is neutral, and MACD shows a weak bearish crossover. Could be setting up for a move.

54. **MU (Micron Technology, Inc.): Extremely Strong Bullish Trend Continuation (Highly Overextended).**
    *   Price is significantly above all SMAs in an extremely strong bullish order.
    *   RSI (77.50) is very overbought, and price is near the upper Bollinger Band.
    *   MACD is extremely positive. Extreme bullishness, with high probability of a strong pullback.

55. **VXUS (Vanguard Total International Stock Index Fund ETF Shares): Bullish Trend Continuation.**
    *   Price is above all SMAs in a strong bullish order.
    *   RSI (59.82) is bullish, and MACD is positive.
    *   Price is near the upper Bollinger Band, indicating strong upward momentum.

56. **UPRO (ProShares UltraPro S&P500): Strong Bullish Trend Continuation (Overextended).**
    *   Price is well above all SMAs in a very strong bullish order.
    *   RSI (72.33) is overbought, and price is in the upper half of Bollinger Bands.
    *   MACD is strongly positive. Strong trend, but caution warranted due to overextension.

57. **DIA (SPDR Dow Jones Industrial Average ETF Trust): Bullish Trend Continuation (Weak Momentum).**
    *   Price is above all SMAs in a strong bullish order.
    *   RSI (59.77) is bullish, but MACD shows very weak positive momentum, barely above its signal line.
    *   Price is in the upper half of Bollinger Bands. Suggests waning momentum and potential for consolidation.

58. **IWM (iShares Russell 2000 ETF): Strong Bullish Trend Continuation.**
    *   Price is above all SMAs in a strong bullish order.
    *   RSI (64.43) is bullish, and MACD is positive.
    *   Price is in the upper half of Bollinger Bands. Strong upward momentum.

59. **VOO (Vanguard S&P 500 ETF): Strong Bullish Trend Continuation (Overextended).**
    *   Price is well above all SMAs in a strong bullish order.
    *   RSI (73.04) is overbought, and price is near the upper Bollinger Band.
    *   MACD is strongly positive. Strong trend, but caution warranted due to overextension.