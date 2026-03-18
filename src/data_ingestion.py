import yfinance as yf
import pandas as pd
from ta.trend import SMAIndicator, MACD
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands
import json
import os
import sys
import re
from html import unescape
from datetime import datetime, timedelta
from urllib.parse import quote_plus
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from xml.etree import ElementTree
from email.utils import parsedate_to_datetime

GOOGLE_NEWS_RSS_BASE = "https://news.google.com/rss/search?q="
RSS_USER_AGENT = "AlphaOracle/1.0"
NEWS_TIMEOUT_SECONDS = 15
MAX_MACRO_NEWS_ITEMS = 8
MAX_THEME_NEWS_ITEMS = 5
MAX_TICKER_NEWS_ITEMS = 5

MACRO_NEWS_TOPICS = {
    "fed_rates": [
        "Federal Reserve OR FOMC OR interest rates OR CPI OR inflation OR Powell"
    ],
    "energy_geopolitics": [
        "Strait of Hormuz OR oil shipping OR tanker attacks OR OPEC OR Brent crude OR WTI",
        "Iran Israel OR Middle East tension OR Persian Gulf OR Red Sea shipping"
    ],
    "china_taiwan": [
        "China Taiwan OR Taiwan Strait OR semiconductor export controls OR China military"
    ],
    "trade_policy": [
        "tariffs OR sanctions OR trade war OR export controls"
    ],
    "bonds_usd": [
        "Treasury yields OR bond market OR US dollar OR dollar index"
    ],
    "recession_signals": [
        "recession OR economic slowdown OR layoffs OR unemployment rising"
    ],
}

THEME_NEWS_TOPICS = {
    "energy": [
        "energy stocks OR oil prices OR OPEC OR refiners OR exploration production"
    ],
    "gold": [
        "gold prices OR central bank gold buying OR bullion OR safe haven"
    ],
    "semiconductors": [
        "semiconductors OR AI chips OR data center spending OR foundry"
    ],
    "utilities_power": [
        "utilities stocks OR power demand OR grid capacity OR nuclear power"
    ],
    "software_ai": [
        "enterprise software OR AI software OR cloud spending OR SaaS"
    ],
    "international": [
        "Europe stocks OR Canada stocks OR China stocks OR emerging markets"
    ],
}

EVENT_RULES = [
    {
        "event_type": "geopolitical_supply_shock",
        "direction": "inflationary_risk_off",
        "keywords": ["strait of hormuz", "shipping", "tanker", "opec", "oil", "iran", "persian gulf"],
        "assets_impacted": ["XLE", "GLD", "TLT", "SPY"],
        "bullish": ["XLE", "GLD", "XLU"],
        "bearish": ["Airlines", "XLF", "Consumer Discretionary"],
        "implications": "Oil supply shock: Long energy, safe havens. Short cyclicals, transports."
    },
    {
        "event_type": "china_taiwan_tension",
        "direction": "risk_off",
        "keywords": ["china taiwan", "taiwan strait", "semiconductor", "tsm", "military exercise"],
        "assets_impacted": ["TSM", "NVDA", "AMD", "INTC", "GLD", "^VIX"],
        "bullish": ["INTC", "Defense stocks", "GLD"],
        "bearish": ["TSM", "Tech with China exposure"],
        "implications": "Semiconductor supply risk: Long domestic chips (INTC), short TSM. Safe haven bid."
    },
    {
        "event_type": "policy_rate_shift",
        "direction": "rates_sensitive",
        "keywords": ["federal reserve", "fomc", "interest rates", "cpi", "inflation", "powell"],
        "assets_impacted": ["SPY", "QQQ", "TLT", "^VIX"],
        "bullish": ["TLT if dovish", "Growth tech if dovish"],
        "bearish": ["Financials if dovish", "Tech if hawkish"],
        "implications": "Fed policy shift: Dovish = long duration/growth. Hawkish = short duration/growth."
    },
    {
        "event_type": "trade_policy_shock",
        "direction": "risk_off",
        "keywords": ["tariffs", "sanctions", "export controls", "trade war"],
        "assets_impacted": ["SPY", "GLD", "^VIX"],
        "bullish": ["GLD", "Defensive sectors"],
        "bearish": ["Multinationals", "China exposure"],
        "implications": "Trade tensions: Flight to safety, avoid companies with international revenue exposure."
    },
    {
        "event_type": "recession_signal",
        "direction": "risk_off",
        "keywords": ["recession", "layoffs", "unemployment", "economic slowdown"],
        "assets_impacted": ["SPY", "QQQ", "TLT", "GLD", "XLU"],
        "bullish": ["TLT", "GLD", "XLU", "XLP"],
        "bearish": ["Cyclicals", "Discretionary", "Small caps"],
        "implications": "Recession fears: Rotate to defensives (utilities, staples), duration (TLT), gold."
    },
]

def load_tickers():
    """Load tickers from watchlist and portfolio."""
    tickers = set(['SPY', '^VIX'])
    if os.path.exists('portfolio.csv'):
        df_p = pd.read_csv('portfolio.csv')
        tickers.update(df_p[df_p['Type'] == 'Equity']['Ticker'].tolist())
    if os.path.exists('watchlist.csv'):
        df_w = pd.read_csv('watchlist.csv')
        tickers.update(df_w['Ticker'].tolist())
    return list(tickers)

def get_market_regime(spy_price, spy_200sma, vix_close):
    if spy_price > spy_200sma and vix_close > 20:
        return "Bull Volatile"
    elif spy_price > spy_200sma and vix_close <= 20:
        return "Bull Quiet"
    elif spy_price <= spy_200sma and vix_close > 25:
        return "Bear Volatile"
    elif spy_price <= spy_200sma and vix_close <= 25:
        return "Bear Quiet"
    return "Unknown"


def strip_html(text):
    if not text:
        return ""
    if isinstance(text, dict):
        for key in ("name", "title", "providerName", "displayName"):
            if text.get(key):
                text = text.get(key)
                break
        else:
            text = json.dumps(text)
    elif not isinstance(text, str):
        text = str(text)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", unescape(text)).strip()


def parse_news_datetime(raw_value):
    if not raw_value:
        return None
    if isinstance(raw_value, (int, float)):
        try:
            return datetime.utcfromtimestamp(raw_value).isoformat() + "Z"
        except (OverflowError, OSError, ValueError):
            return None
    try:
        dt = parsedate_to_datetime(raw_value)
        if dt.tzinfo is None:
            return dt.isoformat() + "Z"
        return dt.astimezone().isoformat()
    except (TypeError, ValueError, IndexError):
        return None


def build_google_news_rss_url(query):
    return f"{GOOGLE_NEWS_RSS_BASE}{quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"


def fetch_rss_entries(feed_url, max_items=5):
    request = None
    try:
        request = urlopen(
            Request(feed_url, headers={"User-Agent": RSS_USER_AGENT}),
            timeout=NEWS_TIMEOUT_SECONDS,
        )
        xml_bytes = request.read()
    except (HTTPError, URLError, TimeoutError) as exc:
        print(f"Failed to fetch RSS feed {feed_url}: {exc}", file=sys.stderr)
        return []
    finally:
        if request is not None:
            request.close()

    try:
        root = ElementTree.fromstring(xml_bytes)
    except ElementTree.ParseError as exc:
        print(f"Failed to parse RSS feed {feed_url}: {exc}", file=sys.stderr)
        return []

    channel = root.find("channel")
    if channel is None:
        return []

    entries = []
    for item in channel.findall("item")[:max_items]:
        entries.append({
            "headline": strip_html(item.findtext("title")),
            "source": strip_html(item.findtext("source")) or "Unknown",
            "published_utc": parse_news_datetime(item.findtext("pubDate")),
            "summary": strip_html(item.findtext("description")),
            "link": (item.findtext("link") or "").strip(),
        })
    return entries


def dedupe_news_items(items, max_items):
    deduped = []
    seen = set()
    for item in items:
        key = (
            (item.get("headline") or "").strip().lower(),
            (item.get("source") or "").strip().lower(),
        )
        if not item.get("headline") or key in seen:
            continue
        seen.add(key)
        deduped.append(item)
        if len(deduped) >= max_items:
            break
    return deduped


def infer_event_impact(item):
    haystack = " ".join([
        item.get("headline", ""),
        item.get("summary", ""),
        item.get("topic", ""),
    ]).lower()

    tags = []
    for rule in EVENT_RULES:
        if any(keyword in haystack for keyword in rule["keywords"]):
            tags.append({
                "event_type": rule["event_type"],
                "direction": rule["direction"],
                "assets_impacted": rule["assets_impacted"],
                "confidence": "medium",
            })
    return tags


def fetch_news_topic_bucket(topic_map, max_items):
    bucketed_news = {}
    for topic, queries in topic_map.items():
        topic_items = []
        for query in queries:
            entries = fetch_rss_entries(build_google_news_rss_url(query), max_items=max_items)
            for entry in entries:
                entry["topic"] = topic
                entry["impact_tags"] = infer_event_impact(entry)
                topic_items.append(entry)
        bucketed_news[topic] = dedupe_news_items(topic_items, max_items)
    return bucketed_news


def flatten_news_buckets(bucketed_news, max_items):
    all_items = []
    for topic_items in bucketed_news.values():
        all_items.extend(topic_items)
    all_items.sort(key=lambda item: item.get("published_utc") or "", reverse=True)
    return dedupe_news_items(all_items, max_items)


def fetch_ticker_news(ticker):
    try:
        news = yf.Ticker(ticker).news or []
    except Exception as exc:
        print(f"Error fetching news for {ticker}: {exc}", file=sys.stderr)
        return [], []

    structured_items = []
    for item in news[:MAX_TICKER_NEWS_ITEMS]:
        content = item.get("content") or {}
        structured_items.append({
            "headline": strip_html(content.get("title") or item.get("title") or ""),
            "source": strip_html(content.get("provider") or item.get("publisher") or "Yahoo Finance"),
            "published_utc": parse_news_datetime(item.get("pubDate") or content.get("pubDate")),
            "summary": strip_html(content.get("summary") or ""),
            "link": (content.get("canonicalUrl", {}) or {}).get("url") or item.get("link") or "",
        })

    structured_items = dedupe_news_items(structured_items, MAX_TICKER_NEWS_ITEMS)
    headlines = [item["headline"] for item in structured_items[:3]]
    return headlines, structured_items

def fetch_data():
    tickers = load_tickers()
    market_data = {}
    macro_news_by_topic = fetch_news_topic_bucket(MACRO_NEWS_TOPICS, MAX_MACRO_NEWS_ITEMS)
    theme_news_by_topic = fetch_news_topic_bucket(THEME_NEWS_TOPICS, MAX_THEME_NEWS_ITEMS)
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365) # 1 year data for 200 SMA

    for ticker in tickers:
        print(f"Fetching data for {ticker}...")
        try:
            df = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), progress=False)
            
            if df.empty:
                continue
                
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Calculate Technicals using ta
            df['SMA_20'] = SMAIndicator(close=df['Close'], window=20).sma_indicator()
            df['SMA_50'] = SMAIndicator(close=df['Close'], window=50).sma_indicator()
            df['SMA_200'] = SMAIndicator(close=df['Close'], window=200).sma_indicator()
            df['RSI_14'] = RSIIndicator(close=df['Close'], window=14).rsi()
            
            macd = MACD(close=df['Close'], window_slow=26, window_fast=12, window_sign=9)
            df['MACD_12_26_9'] = macd.macd()
            df['MACDs_12_26_9'] = macd.macd_signal()
            df['MACDh_12_26_9'] = macd.macd_diff()
            
            bb = BollingerBands(close=df['Close'], window=20, window_dev=2)
            df['BBL_20_2.0'] = bb.bollinger_lband()
            df['BBU_20_2.0'] = bb.bollinger_hband()
            
            # Drop NaN rows which are at the beginning due to MAs
            df = df.dropna()
            if df.empty:
                continue

            # Save history for charts
            history_data = []
            for date, row in df.iterrows():
                history_data.append({
                    'time': date.strftime('%Y-%m-%d'),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': float(row['Volume']),
                    'sma20': float(row['SMA_20']) if not pd.isna(row['SMA_20']) else None,
                    'sma50': float(row['SMA_50']) if not pd.isna(row['SMA_50']) else None,
                    'sma200': float(row['SMA_200']) if not pd.isna(row['SMA_200']) else None,
                })
            
            # Save to both locations
            for base_dir in ['data/history', 'frontend/public/data/history']:
                os.makedirs(base_dir, exist_ok=True)
                with open(f'{base_dir}/{ticker}.json', 'w') as f:
                    json.dump(history_data, f, indent=4)

            latest = df.iloc[-1]
            
            def get_val(col_name):
                val = latest.get(col_name, 0)
                if isinstance(val, pd.Series):
                    return float(val.iloc[0])
                return float(val)

            ticker_data = {
                'close': get_val('Close'),
                'volume': get_val('Volume'),
                'sma_20': get_val('SMA_20'),
                'sma_50': get_val('SMA_50'),
                'sma_200': get_val('SMA_200'),
                'rsi_14': get_val('RSI_14'),
                'macd': get_val('MACD_12_26_9'),
                'macd_signal': get_val('MACDs_12_26_9'),
                'macd_hist': get_val('MACDh_12_26_9'),
                'bb_lower': get_val('BBL_20_2.0'),
                'bb_upper': get_val('BBU_20_2.0'),
            }
            
            # Fetch ticker-specific news
            ticker_news_headlines, ticker_news_items = fetch_ticker_news(ticker)
            ticker_data['news'] = ticker_news_headlines
            ticker_data['news_items'] = ticker_news_items
            
            market_data[ticker] = ticker_data
            
        except Exception as e:
            print(f"Error fetching {ticker}: {e}", file=sys.stderr)

    # Determine Regime
    regime = "Unknown"
    if 'SPY' in market_data and '^VIX' in market_data:
        spy_close = market_data['SPY']['close']
        spy_200 = market_data['SPY']['sma_200']
        vix_close = market_data['^VIX']['close']
        regime = get_market_regime(spy_close, spy_200, vix_close)
        
    output = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'regime': regime,
        'macro_news': flatten_news_buckets(macro_news_by_topic, MAX_MACRO_NEWS_ITEMS),
        'macro_news_by_topic': macro_news_by_topic,
        'theme_news': theme_news_by_topic,
        'data': market_data
    }
    
    # Save to both locations
    for base_path in ['data/market_context.json', 'frontend/public/data/market_context.json']:
        os.makedirs(os.path.dirname(base_path), exist_ok=True)
        with open(base_path, 'w') as f:
            json.dump(output, f, indent=4)
        
    print(f"Market data fetched and saved to {len(market_data)} tickers.")

if __name__ == "__main__":
    fetch_data()
