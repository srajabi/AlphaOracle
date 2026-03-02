import React, { useEffect, useRef } from 'react';
import { createChart, ColorType, CrosshairMode, LineStyle, CandlestickSeries, HistogramSeries, LineSeries } from 'lightweight-charts';

interface StockChartProps {
  data: {
    time: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
    sma20?: number | null;
    sma50?: number | null;
    sma200?: number | null;
  }[];
}

const StockChart = ({ data }: StockChartProps) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { type: ColorType.Solid, color: '#131722' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: 'rgba(197, 203, 206, 0.05)' },
        horzLines: { color: 'rgba(197, 203, 206, 0.05)' },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
      },
      rightPriceScale: {
        borderColor: 'rgba(197, 203, 206, 0.2)',
      },
      timeScale: {
        borderColor: 'rgba(197, 203, 206, 0.2)',
        timeVisible: true,
      },
      width: chartContainerRef.current.clientWidth,
      height: 600,
    });

    // 1. Candlestick Series (v5 API uses addSeries)
    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    });
    candlestickSeries.setData(data.map(d => ({
        time: d.time,
        open: d.open,
        high: d.high,
        low: d.low,
        close: d.close,
    })));

    // 2. Volume Series (Histogram)
    const volumeSeries = chart.addSeries(HistogramSeries, {
      color: '#26a69a',
      priceFormat: { type: 'volume' },
      priceScaleId: '', // Show on its own scale (bottom)
    });
    
    volumeSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });

    volumeSeries.setData(data.map(d => ({
      time: d.time,
      value: d.volume,
      color: d.close >= d.open ? 'rgba(38, 166, 154, 0.3)' : 'rgba(239, 83, 80, 0.3)',
    })));

    // 3. Technical Indicators (SMA Lines)
    const sma20Series = chart.addSeries(LineSeries, {
      color: '#2962FF',
      lineWidth: 2,
      title: 'SMA 20',
    });
    sma20Series.setData(data.filter(d => d.sma20).map(d => ({ time: d.time, value: d.sma20! })));

    const sma50Series = chart.addSeries(LineSeries, {
      color: '#FF9800',
      lineWidth: 2,
      title: 'SMA 50',
    });
    sma50Series.setData(data.filter(d => d.sma50).map(d => ({ time: d.time, value: d.sma50! })));

    const sma200Series = chart.addSeries(LineSeries, {
      color: '#F44336',
      lineWidth: 2,
      lineStyle: LineStyle.Dashed,
      title: 'SMA 200',
    });
    sma200Series.setData(data.filter(d => d.sma200).map(d => ({ time: d.time, value: d.sma200! })));

    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };
    window.addEventListener('resize', handleResize);

    chart.timeScale().fitContent();

    if (data.length > 30) {
      const lastDateStr = data[data.length - 1].time;
      const lastDate = new Date(lastDateStr);
      const sixMonthsAgo = new Date(lastDate);
      sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
      
      const fromStr = sixMonthsAgo.toISOString().split('T')[0];
      if (data[0].time <= fromStr) {
          chart.timeScale().setVisibleRange({
              from: fromStr,
              to: lastDateStr,
          });
      }
    }

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.remove();
    };
  }, [data]);

  return (
    <div style={{ position: 'relative', width: '100%', minHeight: '600px' }}>
      <div ref={chartContainerRef} />
    </div>
  );
};

export default StockChart;
