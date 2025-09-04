import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, timezone

SECTOR_ETFS = {
    'XLK': 'Technology',
    'XLF': 'Financials',
    'XLE': 'Energy',
    'XLV': 'Health Care',
    'XLY': 'Consumer Discretionary',
    'XLP': 'Consumer Staples',
    'XLI': 'Industrials',
    'XLU': 'Utilities',
    'XLRE': 'Real Estate',
    'XLB': 'Materials',
    'IYR': 'Real Estate (alt)',
}

BENCHMARKS = {
    'SPY': 'S&P 500',
    'QQQ': 'Nasdaq 100',
    'IWM': 'Russell 2000',
    'EFA': 'MSCI EAFE',
}

def fetch_info(ticker: str):
    t = yf.Ticker(ticker)
    info = t.info or {}
    # price history past few days (to compute today's change robustly)
    hist = t.history(period="5d", interval="1d", auto_adjust=False)
    # intraday for volume baseline
    intraday = t.history(period="1mo", interval="1d", auto_adjust=False)
    avg_vol = intraday['Volume'].tail(20).mean() if not intraday.empty else None
    news = t.news if hasattr(t, 'news') else []
    return info, hist, avg_vol, news

def ret_today_from_history(hist: pd.DataFrame) -> float | None:
    if hist is None or hist.empty or len(hist) < 2:
        return None
    # Use last row vs prior close
    last = hist['Close'].iloc[-1]
    prev = hist['Close'].iloc[-2]
    if prev == 0: 
        return None
    return (last/prev - 1.0) * 100.0

def fetch_benchmark_ret(symbol='SPY') -> float | None:
    h = yf.Ticker(symbol).history(period="5d", interval="1d", auto_adjust=False)
    return ret_today_from_history(h)

def fetch_sector_ret_from_map(sector_hint: str | None) -> tuple[str|None, float|None]:
    # Try to pick an ETF based on sector_hint
    if not sector_hint:
        return None, None
    sector_hint = sector_hint.lower()
    etf = None
    if 'technology' in sector_hint or 'it' == sector_hint:
        etf = 'XLK'
    elif 'financial' in sector_hint:
        etf = 'XLF'
    elif 'energy' in sector_hint:
        etf = 'XLE'
    elif 'health' in sector_hint:
        etf = 'XLV'
    elif 'consumer defensive' in sector_hint or 'staples' in sector_hint:
        etf = 'XLP'
    elif 'consumer cyclical' in sector_hint or 'discretionary' in sector_hint:
        etf = 'XLY'
    elif 'industrial' in sector_hint:
        etf = 'XLI'
    elif 'utilities' in sector_hint:
        etf = 'XLU'
    elif 'materials' in sector_hint:
        etf = 'XLB'
    elif 'real estate' in sector_hint:
        etf = 'XLRE'
    if etf:
        return etf, fetch_benchmark_ret(etf)
    return None, None

def news_flags_from_titles(news_list):
    flags = {'earnings': False, 'upgrade': False, 'downgrade': False, 'mna': False}
    for n in news_list or []:
        title = (n.get('title') or '').lower()
        if any(k in title for k in ['earnings', 'guidance', 'q1', 'q2', 'q3', 'q4']):
            flags['earnings'] = True
        if 'downgrade' in title or 'downgraded' in title:
            flags['downgrade'] = True
        if 'upgrade' in title or 'upgraded' in title:
            flags['upgrade'] = True
        if 'acquire' in title or 'acquisition' in title or 'merger' in title:
            flags['mna'] = True
    return flags
