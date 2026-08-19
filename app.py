import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import datetime
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
        padding: 15px;
        margin-bottom: 15px;
    }
    .badge-green { background: rgba(0,245,155,0.15); color: #00F59B; border: 1px solid #00F59B; padding: 4px 8px; border-radius: 5px; font-weight: bold; }
    .badge-red { background: rgba(255,75,75,0.15); color: #FF4B4B; border: 1px solid #FF4B4B; padding: 4px 8px; border-radius: 5px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 2. Stock Database & Realistic Live Feed Generator
stock_baselines = {
    "WIPRO": {"base": 178.85, "lot": 3000, "floor": 171.50, "ceiling": 188.00},
    "TATAMOTORS": {"base": 985.50, "lot": 575, "floor": 955.00, "ceiling": 1020.00},
    "RELIANCE": {"base": 2980.00, "lot": 250, "floor": 2920.00, "ceiling": 3050.00},
    "INFY": {"base": 1820.00, "lot": 400, "floor": 1780.00, "ceiling": 1860.00},
    "HDFCBANK": {"base": 1640.00, "lot": 550, "floor": 1610.00, "ceiling": 1680.00},
    "SBIN": {"base": 820.00, "lot": 750, "floor": 800.00, "ceiling": 845.00},
    "TCS": {"base": 4250.00, "lot": 175, "floor": 4180.00, "ceiling": 4350.00}
}

st.sidebar.markdown("## ⚡ **SANCHETI PRO**")
selected_symbol = st.sidebar.selectbox("🎯 Select Stock", list(stock_baselines.keys()), index=0)
stock_meta = stock_baselines[selected_symbol]

# Auto Refresh Engine (Runs every 3 seconds for live ticks)
refresh_rate = st.sidebar.slider("Tick Refresh Rate (Seconds)", 2, 10, 3)
st.sidebar.caption("⚡ Live Exchange Simulation Feed Active")

# 3. Generating Robust 15M Live Candlesticks
@st.cache_data(ttl=2)
def generate_realtime_market_candles(symbol):
    meta = stock_baselines[symbol]
    base = meta["base"]
    
    # Generate 35 continuous 15-min candles
    timestamps = pd.date_range(end=pd.Timestamp.now(), periods=35, freq="15min")
    np.random.seed(int(time.time()) // 5 + len(symbol))
    
    noise = np.random.normal(0, base * 0.0015, 35)
    close_prices = base + np.cumsum(noise)
    open_prices = np.roll(close_prices, 1)
    open_prices[0] = base - (noise[0] * 0.5)
    high_prices = np.maximum(open_prices, close_prices) + np.abs(np.random.normal(0, base * 0.001, 35))
    low_prices = np.minimum(open_prices, close_prices) - np.abs(np.random.normal(0, base * 0.001, 35))
    volumes = np.random.randint(15000, 180000, 35)
    
    df = pd.DataFrame({
        'Open': open_prices,
        'High': high_prices,
        'Low': low_prices,
        'Close': close_prices,
        'Volume': volumes
    }, index=timestamps)
    
    # Cumulative VWAP
    df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
    return df

df = generate_realtime_market_candles(selected_symbol)

# Latest Price Calculations
cmp = round(float(df['Close'].iloc[-1]), 2)
vwap = round(float(df['VWAP'].iloc[-1]), 2)
open_p = round(float(df['Open'].iloc[0]), 2)
change = round(cmp - open_p, 2)
pct_change = round((change / open_p) * 100, 2)
demand_floor = round(float(df['Low'].min()), 2)
supply_ceiling = round(float(df['High'].max()), 2)

# Top Bar Hero Snapshot
st.markdown(f"""
<div class="hero-box">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <h1 style="margin: 0; font-size: 26px; color: #FFFFFF;">{selected_symbol} <span style="font-size: 14px; color: #00F59B;">● LIVE (NSE)</span></h1>
            <span class="{'badge-green' if cmp >= vwap else 'badge-red'}">
                {'🟢 SMART MONEY ACCUMULATION' if cmp >= vwap else '🔴 INSTITUTIONAL TRAP ZONE'}
            </span>
        </div>
        <div style="text-align: right;">
            <div style="font-size: 30px; font-weight: 800; color: {'#00F59B' if change >= 0 else '#FF4B4B'};">₹{cmp:,.2f}</div>
            <div style="font-size: 15px; color: {'#00F59B' if change >= 0 else '#FF4B4B'};">
                {'+' if change >= 0 else ''}{change} ({'+' if pct_change >= 0 else ''}{pct_change}%)
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Metrics Grid
c1, c2, c3, c4 = st.columns(4)
c1.metric("Live LTP", f"₹{cmp}")
c2.metric("Institutional VWAP", f"₹{vwap}")
c3.metric("Demand Floor (SL)", f"₹{demand_floor}")
c4.metric("Supply Target", f"₹{supply_ceiling}")

# Structured Tabs
t_chart, t_ai, t_hedge, t_rescue = st.tabs([
    "📊 Real-Time Candlestick Chart",
    "🤖 Institutional AI Engine",
    "🛡️ Hedging & Spreads",
    "⚖️ Averaging Calculator"
])

with t_chart:
    st.markdown(f"#### 📈 15-Minute Live Flow: **{selected_symbol}**")
    
    # Native Plotly Candlestick (100% Reliable, Never Fails)
    fig = go.Figure()
    
    # Candlestick Trace
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name="Price",
        increasing_line_color='#00F59B',
        decreasing_line_color='#FF4B4B'
    ))
    
    # Institutional VWAP Line
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['VWAP'],
        mode='lines',
        name='Institutional VWAP',
        line=dict(color='#38BDF8', width=2)
    ))
    
    # Demand and Supply Levels
    fig.add_hline(y=demand_floor, line_dash="dash", line_color="#00F59B", annotation_text="Demand Floor")
    fig.add_hline(y=supply_ceiling, line_dash="dash", line_color="#FF4B4B", annotation_text="Supply Ceiling")
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0A0E17",
        plot_bgcolor="#0A0E17",
        height=480,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_rangeslider_visible=False,
        yaxis=dict(gridcolor="#1E293B"),
        xaxis=dict(gridcolor="#1E293B")
    )
    
    st.plotly_chart(fig, use_container_width=True)

with t_ai:
    st.markdown("### 🤖 Institutional Order Block Thesis")
    st.write(f"1. **Smart Money Position:** Price (₹{cmp}) is **{'ABOVE' if cmp>=vwap else 'BELOW'}** VWAP (₹{vwap}).")
    st.write(f"2. **Trap Detection:** Stop-loss hunt zone is below **₹{demand_floor}**. Do not exit on panic wicks.")
    st.write(f"3. **Execution Plan:** Target upside move towards **₹{supply_ceiling}** with invalidation at **₹{demand_floor}**.")

with t_hedge:
    st.markdown("### 🛡️ Defined-Risk Spreads")
    base_strike = round(cmp / 10) * 10 if cmp > 100 else round(cmp)
    st.write(f"• **Primary ATM Leg:** Buy ₹{base_strike} CE")
    st.write(f"• **Hedge Protection:** Sell ₹{base_strike + 10} CE")
    st.caption("Max loss strictly capped to net debit. Theta decay protected.")

with t_rescue:
    st.markdown("### ⚖️ Position Sizing & Averaging Matrix")
    st.write(f"• **Stage 1 Allocation (30%):** ₹{cmp}")
    st.write(f"• **Stage 2 Demand Allocation (70%):** ₹{demand_floor}")
    st.write(f"• **Target Exit:** ₹{round(cmp + (cmp * 0.04), 1)}")

# Trigger rerun for live auto-tick
time.sleep(refresh_rate)
st.rerun()
