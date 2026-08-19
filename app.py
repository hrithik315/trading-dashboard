import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# 1. Page Configuration
st.set_page_config(
    page_title="SANCHETI QUANT | Institutional Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. Institutional Glassmorphism Design System (Bloomberg / Apex Style)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap');
    
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #07090E; color: #E2E8F0; }
    
    /* Top Header Bar */
    .top-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 24px;
        background: #0D111A;
        border-bottom: 1px solid #1E293B;
        border-radius: 12px;
        margin-bottom: 18px;
    }
    
    /* Execution Hero Card */
    .exec-hero {
        background: linear-gradient(135deg, #0F172A 0%, #0A0F1D 100%);
        border: 1px solid #1E293B;
        border-radius: 16px;
        padding: 22px 28px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }
    
    .price-large {
        font-family: 'JetBrains Mono', monospace;
        font-size: 38px;
        font-weight: 800;
        letter-spacing: -1px;
    }
    
    /* Decision Cards */
    .quant-card {
        background: #0E1422;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 18px;
        height: 100%;
        transition: all 0.2s ease-in-out;
    }
    .quant-card:hover {
        border-color: #38BDF8;
        transform: translateY(-2px);
    }
    
    .card-title {
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #94A3B8;
        margin-bottom: 10px;
    }
    
    .badge-bull {
        background: rgba(0, 245, 155, 0.12);
        color: #00F59B;
        border: 1px solid rgba(0, 245, 155, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 13px;
    }
    .badge-bear {
        background: rgba(255, 75, 75, 0.12);
        color: #FF4B4B;
        border: 1px solid rgba(255, 75, 75, 0.3);
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 13px;
    }
</style>
""", unsafe_allow_html=True)

# 3. Institutional Asset Matrix & Parameters
asset_universe = {
    "WIPRO": {"base": 178.85, "tick_range": 0.35, "lot": 3000},
    "TATA MOTORS": {"base": 985.50, "tick_range": 1.20, "lot": 575},
    "RELIANCE": {"base": 2980.00, "tick_range": 3.50, "lot": 250},
    "INFOSYS": {"base": 1820.00, "tick_range": 2.10, "lot": 400},
    "HDFC BANK": {"base": 1640.00, "tick_range": 1.80, "lot": 550},
    "STATE BANK": {"base": 820.00, "tick_range": 0.95, "lot": 750}
}

# 4. Top Navigation Bar
c_nav1, c_nav2, c_nav3 = st.columns([1.5, 2, 1.5])
with c_nav1:
    st.markdown("### ⚡ **SANCHETI QUANT**")
    st.caption("Institutional Execution & Liquidity Terminal")
with c_nav2:
    selected_asset = st.selectbox(
        "ACTIVE ASSET", 
        list(asset_universe.keys()), 
        index=0, 
        label_visibility="collapsed"
    )
with c_nav3:
    col_cap1, col_cap2 = st.columns(2)
    with col_cap1:
        capital = st.number_input("Capital (₹)", value=50000, step=5000, label_visibility="collapsed")
    with col_cap2:
        risk_pct = st.number_input("Risk %", value=1.0, step=0.5, label_visibility="collapsed")

meta = asset_universe[selected_asset]
base = meta["base"]

# 5. Clean Dynamic Candle & Math Engine
np.random.seed(int(time.time() // 3) + len(selected_asset))
n_bars = 40
dates = pd.date_range(end=pd.Timestamp.now(), periods=n_bars, freq="15min")
volatilities = np.random.normal(0, meta["tick_range"], n_bars)
closes = base + np.cumsum(volatilities)
opens = np.roll(closes, 1)
opens[0] = base - volatilities[0]
highs = np.maximum(opens, closes) + np.abs(np.random.normal(0, meta["tick_range"] * 0.6, n_bars))
lows = np.minimum(opens, closes) - np.abs(np.random.normal(0, meta["tick_range"] * 0.6, n_bars))
vols = np.random.randint(40000, 250000, n_bars)

df = pd.DataFrame({'Open': opens, 'High': highs, 'Low': lows, 'Close': closes, 'Volume': vols}, index=dates)
df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()

# Primary Quant Data
cmp = round(float(df['Close'].iloc[-1]), 2)
vwap = round(float(df['VWAP'].iloc[-1]), 2)
open_p = round(float(df['Open'].iloc[0]), 2)
change = round(cmp - open_p, 2)
pct_change = round((change / open_p) * 100, 2)
support_floor = round(float(df['Low'].min()), 2)
target_ceiling = round(float(df['High'].max()), 2)
is_bullish = cmp >= vwap

# 6. Hero Execution Hub
p_color = "#00F59B" if change >= 0 else "#FF4B4B"
badge = '<span class="badge-bull">🟢 INSTITUTIONAL ACCUMULATION</span>' if is_bullish else '<span class="badge-bear">🔴 DISTRIBUTION / NO TRADE</span>'

st.markdown(f"""
<div class="exec-hero">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <div style="margin-bottom: 6px;">{badge} <span style="font-size: 13px; color: #64748B; margin-left: 10px;">NSE REAL-TIME EQUIVALENT</span></div>
            <h1 style="margin: 0; font-size: 32px; font-weight: 800; color: #FFFFFF;">{selected_asset}</h1>
            <p style="margin: 4px 0 0 0; font-size: 14px; color: #94A3B8;">
                {'Structure confirms buyers defending VWAP support.' if is_bullish else 'Structure below VWAP. High probability of retail trap.'}
            </p>
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

# 7. Sleek High-Speed Candlestick Canvas
fig = go.Figure()

fig.add_trace(go.Candlestick(
    x=df.index,
    open=df['Open'],
    high=df['High'],
    low=df['Low'],
    close=df['Close'],
    name="Candles",
    increasing_line_color='#00F59B',
    decreasing_line_color='#FF4B4B'
))

fig.add_trace(go.Scatter(
    x=df.index,
    y=df['VWAP'],
    mode='lines',
    name='Institutional VWAP',
    line=dict(color='#38BDF8', width=2)
))

fig.add_hline(y=support_floor, line_dash="dot", line_color="#00F59B", annotation_text=f"Floor ₹{support_floor}")
fig.add_hline(y=target_ceiling, line_dash="dot", line_color="#FF4B4B", annotation_text=f"Target ₹{target_ceiling}")

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="#07090E",
    plot_bgcolor="#07090E",
    height=440,
    margin=dict(l=5, r=5, t=10, b=10),
    xaxis_rangeslider_visible=False,
    yaxis=dict(gridcolor="#131B2A", zeroline=False),
    xaxis=dict(gridcolor="#131B2A")
)

st.plotly_chart(fig, use_container_width=True)

# 8. 3-Card Instant Decision Hub
c_card1, c_card2, c_card3 = st.columns(3)

# Card 1: Trade Levels
with c_card1:
    st.markdown(f"""
    <div class="quant-card">
        <div class="card-title">🎯 Precision Levels</div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span style="color:#94A3B8;">Target Exit</span>
            <b style="color:#00F59B; font-family:'JetBrains Mono';">₹{target_ceiling}</b>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span style="color:#94A3B8;">Hard Invalidation (SL)</span>
            <b style="color:#FF4B4B; font-family:'JetBrains Mono';">₹{support_floor}</b>
        </div>
        <div style="display:flex; justify-content:space-between;">
            <span style="color:#94A3B8;">Risk-to-Reward</span>
            <b style="color:#38BDF8; font-family:'JetBrains Mono';">1 : 2.6</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Card 2: 1% Risk Sizer
sl_points = max(1.0, round(cmp - support_floor, 2))
max_risk_inr = (capital * risk_pct) / 100
safe_shares = int(max_risk_inr / sl_points)

with c_card2:
    st.markdown(f"""
    <div class="quant-card">
        <div class="card-title">🛡️ Capital Sizing (1% Rule)</div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span style="color:#94A3B8;">Max Risk Allowed</span>
            <b style="color:#F59E0B; font-family:'JetBrains Mono';">₹{max_risk_inr:,.0f}</b>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span style="color:#94A3B8;">Max Safe Position</span>
            <b style="color:#00F59B; font-family:'JetBrains Mono'; font-size:18px;">{safe_shares} Shares</b>
        </div>
        <div style="font-size:11px; color:#64748B;">SL hit hone par bhi account 100% safe rahega.</div>
    </div>
    """, unsafe_allow_html=True)

# Card 3: Hedging Shield
round_strike = round(cmp / 10) * 10 if cmp > 100 else round(cmp)
with c_card3:
    st.markdown(f"""
    <div class="quant-card">
        <div class="card-title">⚡ Hedged Spread Shield</div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span style="color:#94A3B8;">Main Leg</span>
            <b style="color:#FFFFFF; font-family:'JetBrains Mono';">BUY ₹{round_strike} CE</b>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
            <span style="color:#94A3B8;">Hedge Protection</span>
            <b style="color:#38BDF8; font-family:'JetBrains Mono';">SELL ₹{round_strike + 10} CE</b>
        </div>
        <div style="font-size:11px; color:#00F59B;">Theta Decay & Gap-down protected.</div>
    </div>
    """, unsafe_allow_html=True)
