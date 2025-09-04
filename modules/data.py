import yfinance as yf
import pandas as pd

SECTOR_ETFS = {
    'Technology': 'XLK',
    'Information Technology': 'XLK',
    'Financial Services': 'XLF',
    'Financial': 'XLF',
    'Energy': 'XLE',
    'Healthcare': 'XLV',
    'Health Care': 'XLV',
    'Consumer Defensive': 'XLP',
    'Consumer Staples': 'XLP',
    'Consumer Cyclical': 'XLY',
    'Industrials': 'XLI',
    'Utilities': 'XLU',
    'Basic Materials': 'XLB',
    'Materials': 'XLB',
    'Real Estate': 'XLRE',
    'Communication Services': 'XLC',
}

BENCHMARKS = {'SPY': 'S&P 500', 'QQQ': 'Nasdaq 100'}

PERIOD_MAP = {
    "1D": dict(period="5d", interval="30m"),
    "1U": dict(period="1mo", interval="1h"),
    "1M": dict(period="3mo", interval="1d"),
    "1Å": dict(period="1y", interval="1d"),
    "5Å": dict(period="5y", interval="1wk"),
    "Max": dict(period="max", interval="1mo"),
}

def fetch_info_and_hist(ticker: str, period="6mo", interval="1d"):
    t = yf.Ticker(ticker)
    info = t.info or {}
    hist = t.history(period=period, interval=interval, auto_adjust=False)
    news = getattr(t, "news", [])
    return info, hist, news

def today_return_from_daily(hist: pd.DataFrame) -> float | None:
    if hist is None or hist.empty or len(hist) < 2: return None
    last = hist['Close'].iloc[-1]
    prev = hist['Close'].iloc[-2]
    if prev == 0: return None
    return (last/prev - 1.0) * 100.0

def fetch_benchmark_ret(symbol='SPY') -> float | None:
    h = yf.Ticker(symbol).history(period="5d", interval="1d", auto_adjust=False)
    return today_return_from_daily(h)

def sector_etf_from_info(info: dict):
    sec = (info.get("sector") or "").strip()
    for k,v in SECTOR_ETFS.items():
        if k.lower() in sec.lower(): return v
    return None

def news_flags_from_titles(news_list):
    flags = {'earnings': False, 'upgrade': False, 'downgrade': False, 'mna': False}
    for n in news_list or []:
        title = (n.get('title') or '').lower()
        if any(k in title for k in ['earnings','guidance','results','q1','q2','q3','q4']):
            flags['earnings'] = True
        if 'downgrade' in title or 'downgraded' in title:
            flags['downgrade'] = True
        if 'upgrade' in title or 'upgraded' in title:
            flags['upgrade'] = True
        if 'acquire' in title or 'acquisition' in title or 'merger' in title:
            flags['mna'] = True
    return flags

def hist_return_pct(hist: pd.DataFrame) -> float:
    if hist is None or hist.empty: return 0.0
    start = hist['Close'].iloc[0]
    end = hist['Close'].iloc[-1]
    if start == 0: return 0.0
    return (end/start - 1.0) * 100.0
