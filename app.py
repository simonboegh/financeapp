import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from modules.data import (
    fetch_info_and_hist, fetch_benchmark_ret,
    sector_etf_from_info, news_flags_from_titles, hist_return_pct,
    PERIOD_MAP, BENCHMARKS
)
from modules.explain import Metrics, explain_metrics, human_explain_price_move

st.set_page_config(page_title="AI Aktiehjælper", page_icon="📈", layout="wide")
st.title("📈 AI Aktiehjælper – Bente-mode")
st.caption("Ikke investeringsrådgivning. Kun information og forklaringer.")

# ---- Inputs (top) ----
top_left, top_right = st.columns([2,1])
with top_left:
    ticker = st.text_input("Vælg ticker", value="MSFT").strip().upper()
with top_right:
    bench_key = st.selectbox(
        "Benchmark", 
        options=list(BENCHMARKS.keys()),
        format_func=lambda k: f"{k} – {BENCHMARKS[k]}"
    )

# ---- Kursgraf ----
st.subheader("Kursudvikling")
range_choice = st.radio(
    "Periode", 
    options=["1D","1U","1M","1Å","5Å","Max"], 
    horizontal=True, 
    index=3
)
period_kwargs = PERIOD_MAP[range_choice]

info, hist, news = fetch_info_and_hist(ticker, **period_kwargs)
if hist is None or hist.empty:
    st.error("Kunne ikke hente kursdata.")
    st.stop()

fig = go.Figure()
if all(col in hist.columns for col in ["Open","High","Low","Close"]):
    fig.add_trace(go.Candlestick(
        x=hist.index,
        open=hist["Open"], high=hist["High"], 
        low=hist["Low"], close=hist["Close"], 
        name="Kurs"
    ))
else:
    fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], mode="lines", name="Kurs"))

if "Volume" in hist:
    fig.add_trace(go.Bar(
        x=hist.index, y=hist["Volume"], name="Volumen", 
        yaxis="y2", opacity=0.3
    ))

fig.update_layout(
    height=520, hovermode="x unified",
    margin=dict(l=10,r=10,t=40,b=10),
    xaxis=dict(title=""),
    yaxis=dict(title="Kurs"),
    yaxis2=dict(title="Vol.", overlaying="y", side="right", showgrid=False)
)
st.plotly_chart(fig, use_container_width=True)

# ---- Call To Action buttons ----
c1, c2 = st.columns(2)
with c1:
    run_metrics = st.button("🔍 Analyser nøgletal", use_container_width=True, type="primary")
with c2:
    run_move = st.button("📉 Forklaring på kurs", use_container_width=True)

sector_etf = sector_etf_from_info(info)
sector_name = info.get("sector") or "ukendt sektor"

# ---- Peers input ----
peer_str = st.text_input(
    "Valgfrit: tilføj peers (kommasepareret, fx AAPL, GOOGL)", 
    value=""
)
peer_list = [p.strip().upper() for p in peer_str.split(",") if p.strip()]

# ---- Helper ----
def _safe(x):
    try:
        if x is None: return None
        return float(x)
    except Exception:
        return None

# ---- Analyser nøgletal ----
if run_metrics:
    st.subheader(f"{ticker} – nøgletal i øjenhøjde")
    m = Metrics(
        pe = _safe(info.get('trailingPE')),
        fpe = _safe(info.get('forwardPE')),
        ps = _safe(info.get('priceToSalesTrailing12Months')),
        pb = _safe(info.get('priceToBook')),
        ev_ebitda = _safe(info.get('enterpriseToEbitda')),
        gross_margin = _safe(info.get('grossMargins')),
        op_margin = _safe(info.get('operatingMargins')),
        net_margin = _safe(info.get('profitMargins')),
        roa = _safe(info.get('returnOnAssets')),
        roe = _safe(info.get('returnOnEquity')),
        debt_to_equity = _safe(info.get('debtToEquity')),
        debt_ebitda = None,
        fcf_yield = None
    )

    # Historisk kontekst placeholder
    hist_ctx = {}
    try:
        fivey = fetch_info_and_hist(ticker, period="5y", interval="1wk")[1]
        if not fivey.empty and m.pe is not None:
            hist_ctx['pe_pct5y'] = 50.0  # placeholder, kunne udvides
    except Exception:
        pass

    for line in explain_metrics(m, hist_context=hist_ctx, sector_hint=sector_name):
        st.write("• ", line)

    # --- Sammenlign med sektor/peers ---
    st.markdown("### Sammenlign med sektor og peers")
    rows = []
    # hovedtikker
    rows.append({
        "Ticker": ticker, 
        "P/E": m.pe, "EV/EBITDA": m.ev_ebitda, "P/S": m.ps, "P/B": m.pb, 
        "ROE": m.roe, 
        "EBIT-margin": (m.op_margin*100 if m.op_margin is not None else None), 
        "Gæld/EK": m.debt_to_equity, 
        "Type": "VIRK"
    })
    # sektor-ETF
    if sector_etf:
        sinfo, _, _ = fetch_info_and_hist(sector_etf, period="1y", interval="1d")
        rows.append({
            "Ticker": sector_etf, 
            "P/E": _safe(sinfo.get('trailingPE')), 
            "EV/EBITDA": _safe(sinfo.get('enterpriseToEbitda')), 
            "P/S": _safe(sinfo.get('priceToSalesTrailing12Months')), 
            "P/B": _safe(sinfo.get('priceToBook')), 
            "ROE": _safe(sinfo.get('returnOnEquity')), 
            "EBIT-margin": _safe(sinfo.get('operatingMargins'))*100 if sinfo.get('operatingMargins') else None, 
            "Gæld/EK": _safe(sinfo.get('debtToEquity')), 
            "Type": "SEKTOR"
        })
    # peers
    for p in peer_list:
        try:
            pinfo, _, _ = fetch_info_and_hist(p, period="1y", interval="1d")
            rows.append({
                "Ticker": p, 
                "P/E": _safe(pinfo.get('trailingPE')), 
                "EV/EBITDA": _safe(pinfo.get('enterpriseToEbitda')), 
                "P/S": _safe(pinfo.get('priceToSalesTrailing12Months')), 
                "P/B": _safe(pinfo.get('priceToBook')), 
                "ROE": _safe(pinfo.get('returnOnEquity')), 
                "EBIT-margin": _safe(pinfo.get('operatingMargins'))*100 if pinfo.get('operatingMargins') else None, 
                "Gæld/EK": _safe(pinfo.get('debtToEquity')), 
                "Type": "PEER"
            })
        except Exception:
            pass

    comp_df = pd.DataFrame(rows)
    st.dataframe(comp_df, use_container_width=True)

    # Kort opsummering
    if len(comp_df) >= 2:
        med = comp_df[["P/E","EV/EBITDA","P/S","P/B","ROE","EBIT-margin","Gæld/EK"]].median(numeric_only=True)
        row0 = comp_df.iloc[0]
        bullets = []
        def rel(val, medv):
            if pd.isna(val) or pd.isna(medv): return "ukendt"
            if val > 1.2*medv: return "høj"
            if val < 0.8*medv: return "lav"
            return "omkring gennemsnit"
        bullets.append(f"P/E niveau: {rel(row0['P/E'], med['P/E'])} vs. peers/sector.")
        bullets.append(f"EV/EBITDA: {rel(row0['EV/EBITDA'], med['EV/EBITDA'])} (pris/indtjening for hele virksomheden).")
        bullets.append(f"ROE: {rel(row0['ROE'], med['ROE'])} – høj og stabil ROE er typisk kvalitet.")
        bullets.append(f"Gæld/EK: {rel(row0['Gæld/EK'], med['Gæld/EK'])}.")
        for b in bullets:
            st.write("• ", b)

    st.caption("Bemærk: ETF-multipler kan afvige fra enkeltaktier. Brug sammenligningen som pejlemærke.")

# ---- Forklaring på kurs ----
if run_move:
    st.subheader("Dynamisk forklaring")

    bench_ret = fetch_benchmark_ret(bench_key)
    sector_ret = fetch_benchmark_ret(sector_etf) if sector_etf else None

    vol_ratio = None
    if "Volume" in hist:
        v = hist["Volume"].dropna()
        if len(v) > 20:
            vol_ratio = float(v.iloc[-1] / v.iloc[-20:].mean())

    ret_pct = float(hist_return_pct(hist))

    # --- Hvis OpenAI-nøgle findes: brug AI-forklaring ---
    if "OPENAI_API_KEY" in st.secrets:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            model_name = st.secrets.get("OPENAI_MODEL", "gpt-4o-mini")

            with st.spinner("Genererer forklaring med AI..."):
                text = human_explain_price_move(
                    range_choice, ret_pct, bench_ret, sector_ret, vol_ratio, news_flags_from_titles(news)
                )  # fallback-tekst til safety
                # Lav rigtig AI-forklaring (med kilder)
                from modules.explain import ai_explain_price_move
                ai_text = ai_explain_price_move(
                    model_name=model_name,
                    client=client,
                    ticker=ticker,
                    period_label=range_choice,
                    ret_pct=ret_pct,
                    market_ret=bench_ret,
                    sector_name=info.get("sector"),
                    sector_ret=sector_ret,
                    volume_ratio=vol_ratio,
                    news_items=news or [],
                )
                st.write(ai_text)
        except Exception as e:
            st.warning("AI-forklaring fejlede, viser simplere forklaring.")
            from modules.explain import human_explain_price_move
            flags = news_flags_from_titles(news)
            for ln in human_explain_price_move(range_choice, ret_pct, bench_ret, sector_ret, vol_ratio, flags):
                st.write("• ", ln)
    else:
        # --- Fallback: simpel forklaring ---
        from modules.explain import human_explain_price_move, news_flags_from_titles
        flags = news_flags_from_titles(news)
        for ln in human_explain_price_move(range_choice, ret_pct, bench_ret, sector_ret, vol_ratio, flags):
            st.write("• ", ln)

    # Vis kilder separat også (klikbare)
    if news:
        st.caption("Kilder (seneste nyheder):")
        for n in news[:6]:
            title = n.get("title") or "Nyhed"
            link = n.get("link") or n.get("url")
            st.markdown(f"- [{title}]({link})")
