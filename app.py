import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. Page Configuration
st.set_page_config(
    page_title="SANCHETI QUANT | Live NSE Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Terminal CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #07090E; color: #E2E8F0; }
    .exec-hero {
        background: linear-gradient(135deg, #0F172A 0%, #0A0F1D 100%);
        border: 1px solid #1E293B;
        border-radius: 14px;
        padding: 16px 20px;
        margin-bottom: 14px;
    }
    .price-large { font-family: 'JetBrains Mono', monospace; font-size: 34px; font-weight: 800; }
    .ai-brain-box {
        background: rgba(56, 189, 248, 0.04);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-left: 5px solid #38BDF8;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 14px;
    }
    .badge-bull { background: rgba(0, 245, 155, 0.12); color: #00F59B; border: 1px solid #00F59B; padding: 4px 8px; border-radius: 6px; font-weight: 700; font-size: 12px; }
    .badge-bear { background: rgba(255, 75, 75, 0.12); color: #FF4B4B; border: 1px solid #FF4B4B; padding: 4px 8px; border-radius: 6px; font-weight: 700; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# 2. Real NSE Tickers
asset_universe = {
    "WIPRO": "WIPRO.NS",
    "TATA MOTORS": "TATAMOTORS.NS",
    "RELIANCE": "RELIANCE.NS",
    "INFOSYS": "INFY.NS",
    "HDFC BANK": "HDFCBANK.NS",
    "STATE BANK": "SBIN.NS"
}

# 3. Sidebar Controls
st.sidebar.markdown("## ⚡ **AI QUANT TOOLKIT**")
selected_name = st.sidebar.selectbox("🎯 Select Stock", list(asset_universe.keys()), index=0)
ticker_symbol = asset_universe[selected_name]

if st.sidebar.button("🔄 Refresh Real-Time Data"):
    st.cache_data.clear()

with st.sidebar.expander("📐 Fibonacci & SMC Tools", expanded=True):
    show_fib = st.checkbox("Auto Fibonacci Retracement", value=True)
    show_vwap = st.checkbox("Institutional VWAP", value=True)
    show_ema9 = st.checkbox("9 EMA Momentum", value=True)
    show_ema21 = st.checkbox("21 EMA Trend", value=True)
    show_rsi = st.checkbox("RSI (14) Momentum", value=True)

# 4. Fetch Real Live Market Data Directly from Exchange
@st.cache_data(ttl=15)
def get_live_market_data(ticker):
    stock = yf.Ticker(ticker)
    df = stock.history(period="5d", interval="15m")
    if df.empty or len(df) < 5:
        df = stock.history(period="1mo", interval="1d")
    return df

df = get_live_market_data(ticker_symbol)

if df.empty:
    st.error("Live market feed connect nahi ho paya. Refresh dabayein.")
    st.stop()

# Indicators Calculation on Real Data
df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
df['EMA21'] = df['Close'].ewm(span=21, adjust=False).mean()

delta = df['Close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / (loss + 1e-9)
df['RSI'] = 100 - (100 / (1 + rs))

# Exact Live Numbers
cmp = round(float(df['Close'].iloc[-1]), 2)
vwap = round(float(df['VWAP'].iloc[-1]), 2)
prev_close = round(float(df['Close'].iloc[-2]), 2)
change = round(cmp - prev_close, 2)
pct_change = round((change / prev_close) * 100, 2)

high_swing = round(float(df['High'].max()), 2)
low_swing = round(float(df['Low'].min()), 2)
diff = high_swing - low_swing

fib_382 = round(high_swing - 0.382 * diff, 2)
fib_500 = round(high_swing - 0.500 * diff, 2)
fib_618 = round(high_swing - 0.618 * diff, 2)

is_bullish = cmp >= vwap

# 5. Live Price Header
p_color = "#00F59B" if change >= 0 else "#FF4B4B"
badge = '<span class="badge-bull">🟢 ACCUMULATION (ABOVE VWAP)</span>' if is_bullish else '<span class="badge-bear">🔴 DISTRIBUTION (BELOW VWAP)</span>'

st.markdown(f"""
<div class="exec-hero">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <div>{badge} <span style="font-size: 13px; color: #94A3B8; margin-left: 10px;">EXACT NSE LIVE TICK</span></div>
            <h1 style="margin: 4px 0 0 0; font-size: 30px; font-weight: 800; color: #FFFFFF;">{selected_name} <span style="font-size: 16px; color: #38BDF8;">[{ticker_symbol}]</span></h1>
        </div>
        <div style="text-align: right;">
            <div class="price-large" style="color: {p_color};">₹{cmp:,.2f}</div>
            <div style="font-size: 15px; font-weight: 600; color: {p_color};">
                {'+' if change >= 0 else ''}{change:,.2f} ({'+' if pct_change >= 0 else ''}{pct_change:.2f}%)
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 6. Real AI Synthesis Box
st.markdown(f"""
<div class="ai-brain-box">
    <b style="color:#38BDF8; font-size:15px;">🤖 AI QUANT SYNTHESIS (REAL LIVE DATA)</b><br>
    <div style="font-size:13.5px; line-height:1.6; color:#E2E8F0; margin-top:6px;">
        • <b>Current Actual Price:</b> ₹{cmp:,.2f} | <b>VWAP:</b> ₹{vwap:,.2f}<br>
        • <b>Fibonacci Golden Zone:</b> ₹{fib_618} – ₹{fib_500} (Smart Money Reversal Floor)<br>
        • <b>Order Blocks:</b> Major Floor at ₹{low_swing} | Resistance at ₹{high_swing}
    </div>
</div>
""", unsafe_allow_html=True)

# 7. Real Candlestick Chart
fig = make_subplots(rows=2 if show_rsi else 1, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.75, 0.25] if show_rsi else [1.0])

fig.add_trace(go.Candlestick(
    x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
    name="Real Candles", increasing_line_color='#00F59B', decreasing_line_color='#FF4B4B'
), row=1, col=1)

if show_vwap:
    fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], mode='lines', name='VWAP', line=dict(color='#38BDF8', width=2)), row=1, col=1)
if show_ema9:
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA9'], mode='lines', name='9 EMA', line=dict(color='#F59E0B', width=1.5)), row=1, col=1)
if show_ema21:
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA21'], mode='lines', name='21 EMA', line=dict(color='#EC4899', width=1.5)), row=1, col=1)

if show_fib:
    fig.add_hline(y=high_swing, line_dash="solid", line_color="#94A3B8", annotation_text=f"High ₹{high_swing}", row=1, col=1)
    fig.add_hline(y=fib_500, line_dash="dash", line_color="#F59E0B", annotation_text=f"Fib 0.5 ₹{fib_500}", row=1, col=1)
    fig.add_hline(y=fib_618, line_dash="solid", line_color="#00F59B", annotation_text=f"Fib 0.618 ₹{fib_618}", row=1, col=1)
    fig.add_hline(y=low_swing, line_dash="solid", line_color="#FF4B4B", annotation_text=f"Low ₹{low_swing}", row=1, col=1)

if show_rsi:
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], name="RSI (14)", line=dict(color='#F43F5E', width=1.5)), row=2, col=1)
    fig.add_hline(y=70, line_dash="dash", line_color="rgba(255,75,75,0.4)", row=2, col=1)
    fig.add_hline(y=30, line_dash="dash", line_color="rgba(0,245,155,0.4)", row=2, col=1)

fig.update_layout(
    template="plotly_dark", paper_bgcolor="#07090E", plot_bgcolor="#07090E",
    height=540, margin=dict(l=5, r=5, t=10, b=10), xaxis_rangeslider_visible=False,
    yaxis=dict(gridcolor="#131B2A", zeroline=False), xaxis=dict(gridcolor="#131B2A")
)

st.plotly_chart(fig, use_container_width=True)

# 8. Real Metrics Row
t1, t2, t3, t4 = st.columns(4)
t1.metric("Real LTP", f"₹{cmp:,.2f}")
t2.metric("Real VWAP", f"₹{vwap:,.2f}")
t3.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.1f}")
t4.metric("Day Range", f"₹{low_swing} - ₹{high_swing}")
