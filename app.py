import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# 1. Page Config
st.set_page_config(
    page_title="SANCHETI PRO TERMINAL",
    page_icon="⚡",
    layout="wide"
)

# Dark Terminal CSS
st.markdown("""
<style>
    .stApp { background-color: #0A0E17; color: #F1F5F9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    div[data-testid="stMetricValue"] { font-size: 22px; font-weight: 700; color: #00F59B; }
    .hero-box {
        background: #111827;
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 15px;
    }
    .badge-green { background: rgba(0,245,155,0.15); color: #00F59B; border: 1px solid #00F59B; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
    .badge-red { background: rgba(255,75,75,0.15); color: #FF4B4B; border: 1px solid #FF4B4B; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 2. Stock Database
stock_baselines = {
    "WIPRO": 178.80,
    "TATAMOTORS": 985.50,
    "RELIANCE": 2980.00,
    "INFY": 1820.00,
    "HDFCBANK": 1640.00,
    "SBIN": 820.00,
    "TCS": 4250.00
}

st.sidebar.markdown("## ⚡ **SANCHETI PRO**")
selected_symbol = st.sidebar.selectbox("🎯 Select Stock Asset", list(stock_baselines.keys()), index=0)
base_val = stock_baselines[selected_symbol]

# Live Auto Tick Refresh
st.sidebar.markdown("---")
auto_tick = st.sidebar.checkbox("⚡ Live Market Movement (Active)", value=True)
tick_speed = st.sidebar.slider("Tick Speed (Seconds)", 1, 5, 2)

account_capital = st.sidebar.number_input("Account Capital (₹)", value=50000, step=5000)
risk_pct = st.sidebar.slider("Max Capital Risk (%)", 0.5, 3.0, 1.0, 0.1)

# 3. Dynamic Real-Time Micro-Tick Pipeline
# Uses current timestamp seed so price updates every cycle
current_epoch = int(time.time() // tick_speed)
np.random.seed(current_epoch + len(selected_symbol))

# Generate 30 dynamic candles
n_candles = 30
time_series = pd.date_range(end=pd.Timestamp.now(), periods=n_candles, freq="15min")
price_shocks = np.random.normal(0, base_val * 0.0012, n_candles)
close_arr = base_val + np.cumsum(price_shocks)
open_arr = np.roll(close_arr, 1)
open_arr[0] = base_val - (price_shocks[0] * 0.4)
high_arr = np.maximum(open_arr, close_arr) + np.abs(np.random.normal(0, base_val * 0.0008, n_candles))
low_arr = np.minimum(open_arr, close_arr) - np.abs(np.random.normal(0, base_val * 0.0008, n_candles))
volume_arr = np.random.randint(25000, 190000, n_candles)

df = pd.DataFrame({
    'Open': open_arr,
    'High': high_arr,
    'Low': low_arr,
    'Close': close_arr,
    'Volume': volume_arr
}, index=time_series)

# Live Metrics
df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
cmp = round(float(df['Close'].iloc[-1]), 2)
vwap = round(float(df['VWAP'].iloc[-1]), 2)
open_day = round(float(df['Open'].iloc[0]), 2)
change = round(cmp - open_day, 2)
pct_change = round((change / open_day) * 100, 2)
demand_floor = round(float(df['Low'].min()), 2)
supply_ceiling = round(float(df['High'].max()), 2)
last_vol = int(df['Volume'].iloc[-1])

# 4. Master Live Status Header
is_bull = cmp >= vwap
status_badge = '<span class="badge-green">🟢 SMART MONEY ACCUMULATION</span>' if is_bull else '<span class="badge-red">🔴 INSTITUTIONAL DISTRIBUTION</span>'

st.markdown(f"""
<div class="hero-box">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h1 style="margin: 0; font-size: 26px; color: #FFFFFF;">{selected_symbol} <span style="font-size: 14px; color: #00F59B;">● LIVE TICKING</span></h1>
            <div style="margin-top: 6px;">{status_badge}</div>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 32px; font-weight: 800; color: {'#00F59B' if change >= 0 else '#FF4B4B'};">₹{cmp:,.2f}</div>
            <div style="font-size: 15px; color: {'#00F59B' if change >= 0 else '#FF4B4B'};">
                {'+' if change >= 0 else ''}{change} ({'+' if pct_change >= 0 else ''}{pct_change}%)
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Metric Row
c1, c2, c3, c4 = st.columns(4)
c1.metric("Live Tick Price", f"₹{cmp:,.2f}")
c2.metric("Institutional VWAP", f"₹{vwap:,.2f}")
c3.metric("Demand Floor (SL)", f"₹{demand_floor:,.2f}")
c4.metric("Supply Target", f"₹{supply_ceiling:,.2f}")

# 5. Tabs
tab_chart, tab_ai, tab_hedge, tab_rescue = st.tabs([
    "📊 Live Dynamic Interactive Chart",
    "🧠 Smart Money & Traps",
    "🛡️ Hedging & Spreads",
    "⚖️ Averaging & Sizing"
])

with tab_chart:
    st.markdown(f"#### 📈 Live Candlestick & VWAP Flow: **{selected_symbol}**")
    
    fig = go.Figure()
    
    # Real-Time Dynamic Candles
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="Price Action",
        increasing_line_color='#00F59B',
        decreasing_line_color='#FF4B4B'
    ))
    
    # Live VWAP
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['VWAP'],
        mode='lines',
        name='Live VWAP',
        line=dict(color='#38BDF8', width=2)
    ))
    
    # Order Blocks / Zones
    fig.add_hline(y=demand_floor, line_dash="dash", line_color="#00F59B", annotation_text="Demand Floor")
    fig.add_hline(y=supply_ceiling, line_dash="dash", line_color="#FF4B4B", annotation_text="Supply Target")
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0A0E17",
        plot_bgcolor="#0A0E17",
        height=500,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_rangeslider_visible=False,
        yaxis=dict(gridcolor="#1E293B"),
        xaxis=dict(gridcolor="#1E293B")
    )
    
    st.plotly_chart(fig, use_container_width=True)

with tab_ai:
    st.markdown("### 🤖 Institutional Order Flow Rules")
    st.write(f"• **Live Footprint:** Current tick ₹{cmp} is {'ABOVE' if is_bull else 'BELOW'} VWAP (₹{vwap}).")
    st.write(f"• **Retail Trap Warning:** Stop-loss cluster at ₹{demand_floor}. Smart money absorbs volume before reverse rally.")
    st.write(f"• **15-Min Volume Surge:** {last_vol:,} shares.")

with tab_hedge:
    st.markdown("### 🛡️ Defined-Risk Spreads")
    base_strike = round(cmp / 10) * 10 if cmp > 100 else round(cmp)
    st.write(f"• **Bullish Outlook:** Buy ATM ₹{base_strike} CE & Sell OTM ₹{base_strike + 10} CE")
    st.write(f"• **Bearish Protection:** Buy ATM ₹{base_strike} PE & Sell OTM ₹{base_strike - 10} PE")

with tab_rescue:
    st.markdown("### ⚖️ Position Sizing & Averaging Matrix")
    max_risk = (account_capital * risk_pct) / 100
    st.metric("1% Max Risk Allowed", f"₹{max_risk:,.0f}")
    st.write(f"• **Stage 1 (30% Qty Entry):** ₹{cmp}")
    st.write(f"• **Stage 2 (70% Qty Base):** ₹{demand_floor}")
    st.write(f"• **Pullback Target Exit:** ₹{round(cmp + (cmp * 0.035), 1)}")

# 6. Auto-Refresh Trigger
if auto_tick:
    time.sleep(tick_speed)
    st.rerun()
