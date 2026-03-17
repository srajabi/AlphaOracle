export type SignalStatus = "buy" | "sell" | "hold" | "n/a";

export interface MarketTickerData {
  close?: number;
  volume?: number;
  sma_20?: number;
  sma_50?: number;
  sma_200?: number;
  rsi_14?: number;
  macd?: number;
  macd_signal?: number;
  macd_hist?: number;
  bb_lower?: number;
  bb_upper?: number;
}

export interface HistoryBar {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  sma20?: number | null;
  sma50?: number | null;
  sma200?: number | null;
}

export interface TechnicalSignal {
  id: string;
  label: string;
  status: SignalStatus;
  value: string;
  reason: string;
}

function hasNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function pctDiff(a: number, b: number): string {
  return `${(((a - b) / b) * 100).toFixed(1)}%`;
}

export function getStatusClass(status: SignalStatus): string {
  if (status === "buy") return "is-buy";
  if (status === "sell") return "is-sell";
  if (status === "hold") return "is-hold";
  return "is-na";
}

export function getStatusLabel(status: SignalStatus): string {
  if (status === "buy") return "Buy";
  if (status === "sell") return "Sell";
  if (status === "hold") return "Hold";
  return "N/A";
}

export function getConsensus(signals: TechnicalSignal[]) {
  const applicable = signals.filter((signal) => signal.status !== "n/a");
  const score = applicable.reduce((sum, signal) => {
    if (signal.status === "buy") return sum + 1;
    if (signal.status === "sell") return sum - 1;
    return sum;
  }, 0);

  let status: SignalStatus = "hold";
  if (score >= 2) status = "buy";
  else if (score <= -2) status = "sell";

  return {
    status,
    score,
    buyCount: applicable.filter((signal) => signal.status === "buy").length,
    sellCount: applicable.filter((signal) => signal.status === "sell").length,
    holdCount: applicable.filter((signal) => signal.status === "hold").length,
  };
}

export function getTechnicalSignals(
  ticker: string,
  stockData: MarketTickerData,
  historyData: HistoryBar[] = [],
): TechnicalSignal[] {
  const close = stockData.close;
  const sma20 = stockData.sma_20;
  const sma50 = stockData.sma_50;
  const sma200 = stockData.sma_200;
  const rsi = stockData.rsi_14;
  const macd = stockData.macd;
  const macdSignal = stockData.macd_signal;
  const macdHist = stockData.macd_hist;
  const bbLower = stockData.bb_lower;
  const bbUpper = stockData.bb_upper;

  const signals: TechnicalSignal[] = [];

  if (hasNumber(close) && hasNumber(sma200) && sma200 !== 0) {
    const status: SignalStatus = close > sma200 ? "buy" : "sell";
    signals.push({
      id: "long_trend",
      label: "Long Trend",
      status,
      value: `${pctDiff(close, sma200)} vs 200d`,
      reason:
        status === "buy"
          ? `${ticker} is trading above its 200-day SMA, which supports a long-term uptrend bias.`
          : `${ticker} is trading below its 200-day SMA, which points to a weaker long-term trend.`,
    });
  } else {
    signals.push({
      id: "long_trend",
      label: "Long Trend",
      status: "n/a",
      value: "Insufficient data",
      reason: "Not enough data to evaluate the 200-day trend.",
    });
  }

  if (hasNumber(close) && hasNumber(sma20) && hasNumber(sma50) && sma20 !== 0 && sma50 !== 0) {
    let status: SignalStatus = "hold";
    if (close > sma20 && sma20 > sma50) status = "buy";
    else if (close < sma20 && sma20 < sma50) status = "sell";

    signals.push({
      id: "short_trend",
      label: "20/50 Trend",
      status,
      value: `${sma20.toFixed(2)} / ${sma50.toFixed(2)}`,
      reason:
        status === "buy"
          ? `Price is above the 20-day average and the 20-day average is above the 50-day average, which supports short-term trend continuation.`
          : status === "sell"
            ? `Price is below the 20-day average and the 20-day average is below the 50-day average, which signals short-term technical deterioration.`
            : `The short-term and intermediate trend signals are mixed, so there is no clean 20/50 trend setup.`,
    });
  } else {
    signals.push({
      id: "short_trend",
      label: "20/50 Trend",
      status: "n/a",
      value: "Insufficient data",
      reason: "Not enough data to evaluate the 20-day and 50-day trend relationship.",
    });
  }

  if (hasNumber(rsi)) {
    let status: SignalStatus = "hold";
    if (rsi < 35) status = "buy";
    else if (rsi > 65) status = "sell";

    signals.push({
      id: "rsi",
      label: "RSI Mean Rev",
      status,
      value: rsi.toFixed(1),
      reason:
        status === "buy"
          ? `RSI is below 35, which suggests the ticker is stretched on the downside and may be near a mean-reversion bounce.`
          : status === "sell"
            ? `RSI is above 65, which suggests momentum is overheated and vulnerable to a pullback.`
            : `RSI is in a neutral zone, so it is not giving a strong mean-reversion signal.`,
    });
  }

  if (hasNumber(macd) && hasNumber(macdSignal) && hasNumber(macdHist)) {
    let status: SignalStatus = "hold";
    if (macd > macdSignal && macdHist > 0) status = "buy";
    else if (macd < macdSignal && macdHist < 0) status = "sell";

    signals.push({
      id: "macd",
      label: "MACD Momentum",
      status,
      value: `${macd.toFixed(2)} vs ${macdSignal.toFixed(2)}`,
      reason:
        status === "buy"
          ? `MACD is above its signal line and the histogram is positive, which supports improving momentum.`
          : status === "sell"
            ? `MACD is below its signal line and the histogram is negative, which points to weakening momentum.`
            : `MACD and its signal line are close enough that momentum is inconclusive.`,
    });
  }

  if (hasNumber(close) && hasNumber(bbLower) && hasNumber(bbUpper)) {
    let status: SignalStatus = "hold";
    if (close < bbLower) status = "buy";
    else if (close > bbUpper) status = "sell";

    signals.push({
      id: "bollinger",
      label: "Bollinger",
      status,
      value: `${bbLower.toFixed(2)} - ${bbUpper.toFixed(2)}`,
      reason:
        status === "buy"
          ? `Price is below the lower Bollinger Band, which can indicate an oversold stretch.`
          : status === "sell"
            ? `Price is above the upper Bollinger Band, which can indicate an overextended move.`
            : `Price is still inside the Bollinger range, so volatility bands are not signaling an extreme.`,
    });
  }

  if (historyData.length >= 21 && hasNumber(close)) {
    const recentCloses = historyData.slice(-21, -1).map((bar) => bar.close);
    const breakoutHigh = Math.max(...recentCloses);
    const recentLow = Math.min(...historyData.slice(-11, -1).map((bar) => bar.close));
    let status: SignalStatus = "hold";
    if (close > breakoutHigh) status = "buy";
    else if (close < recentLow) status = "sell";

    signals.push({
      id: "breakout",
      label: "20D Breakout",
      status,
      value: `${breakoutHigh.toFixed(2)} / ${recentLow.toFixed(2)}`,
      reason:
        status === "buy"
          ? `Price has cleared the prior 20-day closing high, which is a breakout-style buy signal.`
          : status === "sell"
            ? `Price has fallen below the recent 10-day closing low, which is a breakdown-style sell signal.`
            : `Price is between the recent breakout and breakdown levels, so the breakout system is neutral.`,
    });
  }

  return signals;
}
