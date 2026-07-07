---
title: Risk Manager Report
date: "2026-07-07"
---

## Model: deepseek/deepseek-v4-flash

# Downside Protection & Geopolitical Risk Analysis
**Date:** 2026-07-07 | **Regime:** Bull Quiet | **VIX:** 15.57 (normal, falling)  
**Portfolio:** 100% Cash ($87,185) | **Risk Sentiment:** Risk-On (but fragile)

---

## 1. Geopolitical Event Assessment

### ⚠️ Strait of Hormuz / Iran — Severity: 8/10 (escalating)
**What happened:** Iran attacked commercial tankers; US revoked Iran oil waiver. Oil prices jumped. Inflationary supply shock with risk-off implications.

**Impact by sector:**
| Bullish | Bearish |
|---------|---------|
| XLE (energy stocks) | SPY, QQQ (broad equities) |
| GLD (gold safe haven) | Industrials (XLI) – fuel costs + borrowing costs |
| Oil-linked commodities | Consumer discretionary (XLY) – inflation hit |
| | Long-duration bonds (TLT) – inflation fears |

**Time horizon:** Immediate (days) – further escalation possible; resolution unlikely soon.

### ⚠️ China-Taiwan Tensions — Severity: 6/10 (latent)
CSIS report warns of NT$76.9T trade disruption in Taiwan Strait. Chip export controls escalating. Any military action would disrupt semiconductor supply chain.

**Impact:**
- **Bearish:** TSM, NVDA, AMD, INTC, AVGO (all semi stocks)
- **Bearish:** QQQ (Nasdaq 100 heavy in semi)
- **Bullish:** GLD, VIX (fear spikes)

### ⚠️ Fed Policy Corner — Severity: 7/10 (unresolved)
CPI at 4.2% (May), Fed Chair Warsh can't cut into inflation, can't hike into war. JPMorgan says every meeting is live for a hike (next July 29). Hawkish surprise would crush bonds and growth stocks.

**Time horizon:** Weeks (July 29 FOMC).

### ⚠️ Recession Signals — Severity: 5/10 (building)
Multiple recession_signal tags in macro news: rising unemployment, layoffs (Indonesia 23k), black America recession. Weak June jobs report (57k vs 115k expected). Slow-burn risk.

---

## 2. Key Ticker-Level Weakness (from news & data)

| Ticker | Reason | Action |
|--------|--------|--------|
| **MU, STX, WDC** | Samsung record profit triggers "sell the news"; memory sector drop | **Avoid / trim** |
| **NVDA, AVGO, AMD** | DeepSeek developing own AI chip; Nvidia Kyber delay; AI rotation fears | **Hedge with puts** |
| **CEG, TLN** | Nuclear/AI infrastructure – down 7-8% but secular demand intact | **Hold, but hedge** |
| **ORCL** | Broken (30 RSI, $144 vs 200D $198) – cloud capex decel fear | **Avoid** |
| **XLE** (energy) | RSI 37.5 – oversold but should bounce on oil spike | **Long biased** |

---

## 3. Recommended Hedging & Positioning (All-Cash Portfolio)

Given the **Bull Quiet regime** and your cash position, you are well-placed but missing upside. However, the geopolitical risks justify deploying **defensive hedges first** before entering long positions.

### 🛡 Primary Hedges (Tail Risk Protection)

| Ticker | Instrument | Strike | Expiry | Cost | Rationale |
|--------|------------|--------|--------|------|-----------|
| **SPY** | Long Put | 725 | Jul 24 | ~$228/contract | Broad equity tail risk – cheap (0.3% of notional) |
| **QQQ** | Long Put | 688 | Jul 24 | ~$742/contract | Tech-heavy exposure – semi risk |
| **^VIX** | Wait for backwardation trigger | – | – | – | Do not buy VIX yet (VIX/VIX3M = 0.866 < 1.0) |

### 🚀 Tactical Safe Havens & Contrarian Buys

| Ticker | Strategy | Rationale |
|--------|----------|-----------|
| **GLD** | Buy shares or call option (389 strike, Jul 24) | Geopolitical + negative real-rate drift |
| **XLE** | Buy shares (or XLE ETF) | Oil supply shock – oil majors benefit |
| **DIA** | Cash-secured put (515 strike, Jul 31) | Dow less exposed to semi/tech; earn premium |

### 🚫 Avoid / Trim / Do Not Buy

- **TLT / TMF** – Inflation and rate-hike risks make bonds toxic (2022 lesson)
- **ORCL, NBIS** – AI infrastructure names with broken charts
- **MU, STX** – Memory cycle peaking; "sell the news" momentum
- **UPRO / TQQQ** – Leveraged ETFs are dangerous into a potential gap-down (scenario C)

---

## 4. Option Ideas (From Provided Chain)

| Ticker | Strategy | Exp | Strike | Last | Why |
|--------|----------|-----|--------|------|-----|
| SPY | Long Put (hedge) | Jul 24 | 725 | $2.28 | Cheap tail protection – 3% below spot |
| QQQ | Long Put (hedge) | Jul 24 | 688 | $7.42 | Protection against semi-led drawdown |
| GLD | Long Call (upside) | Jul 24 | 389 | $4.03 | Gold should rally on war/inflation |
| DIA | Cash-Secured Put (income) | Jul 31 | 515 | $2.41 | Dow defensive; collect premium |

**Execution Priority:**
1. Buy **1 SPY 725 Put** (immediate tail hedge – $228)
2. Buy **1 GLD 389 Call** (geopolitical upside – $403)
3. Sell **1 DIA 515 CSP** (yield while waiting – collects $241)
4. Consider **QQQ 688 Put** if semi weakness deepens

---

## 5. Risk Dashboard & Tripwire Monitoring

| Tripwire | Current Value | Threshold | Alert |
|----------|---------------|-----------|-------|
| VIX/VIX3M | **0.866** | > 1.0 | Not triggered yet – watch for backwardation |
| HYG/LQD 63d rel-mom | +1.05% | < -2% | Clear – credit strong |
| SPY < 200d SMA | **751 vs 200d ~689** | Close below | Bullish – 9% above |
| XLE momentum | -8.9% (weak) | Sustained > SPY | Energy not leading yet |
| BoJ shock (USDJPY) | ~154 (est) | < 140 | Not triggered |

**Summary:** The biggest near-term danger is **Iran escalation + rate hike fears**. The all-cash portfolio should deploy **mild long exposure in energy and gold**, with **cheap equity puts** as insurance. Avoid tech (especially semi) until the Samsung/DeepSeek noise clears.

**Recommended next step:** Execute SPY put + GLD call immediately, then evaluate DIA put sell. Re-evaluate after July 29 FOMC.