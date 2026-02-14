from datetime import datetime

import plotly.graph_objects as go
import streamlit as st

from finance_agent import advanced_analysis, get_stock_data

st.set_page_config(page_title="Finance Agent | Midas Tarzı Terminal", layout="wide", page_icon="📈")

st.markdown(
    """
    <style>
    .stApp { background-color: #f6f8fc; color: #0f172a; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        border-right: 1px solid rgba(148, 163, 184, 0.2);
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
    .hero-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
        margin-bottom: 12px;
    }
    .metric-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        min-height: 92px;
    }
    .metric-title { font-size: 13px; color: #64748b; margin-bottom: 4px; }
    .metric-value { font-size: 26px; font-weight: 700; color: #0f172a; }
    .signal-buy { color: #10b981; font-weight: 800; }
    .signal-sell { color: #ef4444; font-weight: 800; }
    .signal-hold { color: #f59e0b; font-weight: 800; }
    .risk-chip {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("## 🤖 Finance Agent")
    st.caption("Midas tarzı teknik görünüm")
    symbols = ["THYAO.IS", "ASELS.IS", "EREGL.IS", "BIMAS.IS", "SISE.IS", "KCHOL.IS", "BTC-USD"]
    selected_symbol = st.selectbox("Varlık", symbols)
    period = st.select_slider("Analiz Periyodu", options=["1mo", "3mo", "6mo", "1y", "2y"], value="1y")
    st.caption("Model: RSI + SMA + MACD + Volatilite")


def _signal_css(decision: str) -> str:
    if "AL" in decision:
        return "signal-buy"
    if "SAT" in decision or "ZAYIF" in decision:
        return "signal-sell"
    return "signal-hold"


df, volatility = get_stock_data(selected_symbol, period=period)

if df is None or df.empty:
    st.error("Veri alınamadı. Lütfen varlığı/periyodu değiştirip tekrar deneyin.")
    st.stop()

analysis = advanced_analysis(df, volatility)
close = float(df["Close"].iloc[-1])
prev_close = float(df["Close"].iloc[-2]) if len(df) > 1 else close
change_daily = ((close - prev_close) / prev_close * 100) if prev_close else 0.0

c1, c2 = st.columns([3, 1])
with c1:
    st.markdown(
        f"""
        <div class="hero-card">
            <h2 style="margin:0;">{selected_symbol} Teknik Terminal</h2>
            <div style="color:#64748b; margin-top:6px;">Son Güncelleme: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
with c2:
    color = "#10b981" if change_daily >= 0 else "#ef4444"
    st.markdown(
        f"""
        <div class="hero-card" style="text-align:right;">
            <div style="font-size:34px; font-weight:800;">{close:,.2f}</div>
            <div style="font-size:16px; font-weight:700; color:{color};">%{change_daily:.2f}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

fig = go.Figure()
fig.add_trace(
    go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"],
        increasing_line_color="#10b981",
        decreasing_line_color="#ef4444",
        name="Fiyat",
    )
)
fig.add_trace(go.Scatter(x=df.index, y=df["SMA20"], mode="lines", line=dict(color="#3b82f6", width=1.6), name="SMA20"))
fig.add_trace(go.Scatter(x=df.index, y=df["SMA50"], mode="lines", line=dict(color="#8b5cf6", width=1.6), name="SMA50"))
fig.update_layout(
    template="plotly_white",
    height=500,
    margin=dict(l=0, r=0, t=10, b=0),
    xaxis_rangeslider_visible=False,
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig, use_container_width=True)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(
        f"<div class='metric-box'><div class='metric-title'>RSI (14)</div><div class='metric-value'>{analysis['rsi']:.2f}</div></div>",
        unsafe_allow_html=True,
    )
with m2:
    st.markdown(
        f"<div class='metric-box'><div class='metric-title'>Yıllık Volatilite</div><div class='metric-value'>%{analysis['volatility']:.2f}</div></div>",
        unsafe_allow_html=True,
    )
with m3:
    chip_color = "#fee2e2" if analysis["risk_level"] == "Yüksek" else "#dcfce7" if analysis["risk_level"] == "Düşük" else "#fef3c7"
    chip_text = "#b91c1c" if analysis["risk_level"] == "Yüksek" else "#166534" if analysis["risk_level"] == "Düşük" else "#92400e"
    st.markdown(
        f"<div class='metric-box'><div class='metric-title'>Risk Seviyesi</div><span class='risk-chip' style='background:{chip_color}; color:{chip_text};'>{analysis['risk_level']}</span></div>",
        unsafe_allow_html=True,
    )
with m4:
    st.markdown(
        f"<div class='metric-box'><div class='metric-title'>Trend Gücü</div><div class='metric-value' style='font-size:22px'>{analysis['trend_strength']}</div></div>",
        unsafe_allow_html=True,
    )

st.markdown("### 🧠 Agent Kararı")
st.markdown(
    f"""
    <div class="hero-card">
        <div class="metric-title">Önerilen Strateji</div>
        <div class="{_signal_css(analysis['decision'])}" style="font-size:30px;">{analysis['decision']}</div>
        <p style="margin-top:8px; color:#334155;">{analysis['comment']}</p>
    </div>
    """,
    unsafe_allow_html=True,
)
