import streamlit as st
import pandas as pd
import numpy as np
from modules.explain import Metrics, explain_metrics, explain_move
from modules.data import fetch_info, ret_today_from_history, fetch_benchmark_ret, fetch_sector_ret_from_map, news_flags_from_titles, BENCHMARKS

st.set_page_config(page_title="AI Aktiehjælper (MVP)", page_icon="📈", layout="centered")
st.title("📈 AI Aktiehjælper – MVP")
st.caption("Ikke investeringsrådgivning. Kun information og forklaringer.")

ticker = st.text_input("Vælg ticker (f.eks. AAPL, MSFT, NVDA, NOVO-B.CO)", value="AAPL")
bente = st.toggle("Bente‑mode (forklaringer i helt almindeligt sprog)", value=True)

bench_key = st.selectbox("Markeds-benchmark", options=list(BENCHMARKS.keys()), format_func=lambda k: f"{k} – {BENCHMARKS[k]}")

if st.button("Hent og forklar"):
    with st.spinner("Henter data..."):
        info, hist, avg_vol, news = fetch_info(ticker)

    if not info:
        st.error("Kunne ikke hente info for den ticker.")
        st.stop()

    # Basic metrics
    pe = info.get('trailingPE') or info.get('forwardPE')
    ev_ebitda = info.get('enterpriseToEbitda')
    # Placeholders (not available directly via yfinance info)
    m = Metrics(
        pe = float(pe) if pe else None,
        ev_ebitda = float(ev_ebitda) if ev_ebitda else None,
        roic = None,
        wacc = None,
        fcf_yield = None,
        debt_ebitda = None
    )

    # Today's return and volume signal
    stock_ret = ret_today_from_history(hist) or 0.0
    bench_ret = fetch_benchmark_ret(bench_key) or 0.0
    sector_etf, sector_ret = fetch_sector_ret_from_map(info.get('sector'))
    volume_ratio = None
    if avg_vol and not hist.empty:
        today_vol = hist['Volume'].iloc[-1] if 'Volume' in hist.columns else None
        if today_vol and avg_vol > 0:
            volume_ratio = today_vol / avg_vol

    # News flags
    flags = news_flags_from_titles(news)

    st.subheader(f"{ticker} – nøgletal i øjenhøjde")
    for line in explain_metrics(m, bente_mode=bente):
        st.write("• ", line)

    st.subheader("Dagens bevægelse – sandsynlig forklaring")
    reasons = explain_move(stock_ret, bench_ret, sector_ret, volume_ratio, flags)
    st.metric("Dagens afkast", f"{stock_ret:.2f}%")
    st.metric(f"Benchmark ({bench_key})", f"{bench_ret:.2f}%")
    if sector_etf:
        st.metric(f"Sektor ({sector_etf})", f"{sector_ret:.2f}%" if sector_ret is not None else "ukendt")
    if volume_ratio is not None:
        st.metric("Volumen vs. 20‑d. snit", f"{volume_ratio:.2f}x")

    for r in reasons:
        st.write("• ", r)

    if news:
        st.subheader("Seneste nyheder (kilder)")
        for n in news[:5]:
            title = n.get('title') or 'Nyhed'
            link = n.get('link') or n.get('url')
            st.markdown(f"- [{title}]({link})")

    st.caption("Tip: Skift Bente‑mode til/fra for at ændre detaljeringsgrad.")
