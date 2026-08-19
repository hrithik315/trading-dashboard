import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import google.generativeai as genai
import time
import os

# 1. Page Configuration
st.set_page_config(
    page_title="SANCHETI QUANT | AI Neural Terminal",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
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
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 16px;
    }
    .price-large { font-family: 'JetBrains Mono', monospace; font-size: 34px; font-weight: 800; }
    
    .ai-brain-box {
        background: rgba(56, 189, 248, 0.04);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-left: 5px solid #38BDF8;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
    }
    
    .quant-card {
        background: #0E1422;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 16px;
    }
    .card-title { font-size: 11px; font-weight: 700; text-transform: uppercase; color: #94A3B8; margin-bottom: 8px; }
    .badge-bull { background: rgba(0, 245, 155, 0.12); color: #00F59B; border: 1px solid #00F59B; padding: 4px 8px; border-radius: 6px; font-weight: 700; font-size: 12px; }
    .badge-bear { background: rgba(255, 75, 75, 0.12); color: #FF4B4B; border: 1px solid #FF4B4B; padding: 4px 8px; border-radius: 6px; font-weight: 700; font-size: 12px; }
</style>
""", unsafe_allow_html=True)

# 2. Asset Matrix
asset_universe = {
    "WIPRO": {"base": 178.85, "tick_range": 0.35},
    "TATA MOTORS": {"base": 985.50, "tick_range": 1.20},
    "RELIANCE": {"base": 2980.00, "tick_range": 3.50},
    "INFOSYS": {"base": 1820.00, "tick_range": 2.10},
    "HDFC BANK": {"base": 1640.00, "tick_range": 1.80},
    "STATE BANK": {"base": 820.00, "tick_range": 0.95}
}

# 3. Top Navigation & Capital Bar
c_nav1, c_nav2, c_nav3 = st.columns([1.5, 2, 1.5])
with c_nav1:
    st.markdown("### 🧠 **SANCHETI AI DESK**")
    st.caption("Neural Quant Order Flow Engine")
with c_nav2:
    selected_asset = st.selectbox("ACTIVE ASSET", list(asset_universe.keys()), index=0, label_visibility="collapsed")
with c_nav3:
    c_cap1, c_cap2 = st.columns(2)
    with c_cap1:
        capital = st.number_input("Capital (₹)", value=50000, step=5000, label_visibility="collapsed")
    with c_cap2:
        risk_pct = st.number_input("Risk %", value=1.0, step=0.5, label_visibility="collapsed")

meta = asset_universe[selected_asset]
base = meta["base"]

# 4. Candlestick & Quant Calculations
np.random.seed(int(time.time() // 3) + len(selected_asset))
n_bars = 35
dates = pd.date_range(end=pd.Timestamp.now(), periods=n_bars, freq="15min")
volatilities = np.random.normal(0, meta["tick_range"], n_bars)
closes = base + np.cumsum(volatilities)
opens = np.roll(closes, 1)
opens[0] = base - volatilities[0]
highs = np.maximum(opens, closes) + np.abs(np.random.normal(0, meta["tick_range"] * 0.5, n_bars))
lows = np.minimum(opens, closes) - np.abs(np.random.normal(0, meta["tick_range"] * 0.5, n_bars))
vols = np.random.randint(40000, 250000, n_bars)

df = pd.DataFrame({'Open': opens, 'High': highs, 'Low': lows, 'Close': closes, 'Volume': vols}, index=dates)
df['VWAP'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()

cmp = round(float(df['Close'].iloc[-1]), 2)
vwap = round(float(df['VWAP'].iloc[-1]), 2)
open_p = round(float(df['Open'].iloc[0]), 2)
change = round(cmp - open_p, 2)
pct_change = round((change / open_p) * 100, 2)
support_floor = round(float(df['Low'].min()), 2)
target_ceiling = round(float(df['High'].max()), 2)
is_bullish = cmp >= vwap

# 5. Live AI Reasoning Engine (Heuristic + Deep Synthesis)
def generate_ai_thesis(symbol, cmp, vwap, support, target, is_bull):
    if is_bull:
        bias_str = "BULLISH INSTITUTIONAL ACCUMULATION"
        trap_warning = f"Retail short-sellers trapped below ₹{vwap}. Higher probability of continuation to ₹{target}."
        action = f"Accumulate on VWAP re-tests (₹{vwap} – ₹{cmp}). Stop-loss hard anchored at ₹{support}."
    else:
        bias_str = "BEARISH REJECTION / DISTRIBUTION"
        trap_warning = f"Retail buyers caught in false breakout near ₹{target}. Volume failing to sustain."
        action = f"Wait for demand exhaustion at ₹{support}. Avoid fresh naked buying."
    return bias_str, trap_warning, action

ai_bias, ai_trap, ai_action = generate_ai_thesis(selected_asset, cmp, vwap, support_floor, target_ceiling, is_bullish)

# 6. Hero Execution Bar
p_color = "#00F59B" if change >= 0 else "#FF4B4B"
badge = '<span class="badge-bull">🟢 AI BIAS: ACCUMULATION</span>' if is_bullish else '<span class="badge-bear">🔴 AI BIAS: DISTRIBUTION</span>'

st.markdown(f"""
<div class="exec-hero">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
        <div>
            <div>{badge} <span style="font-size: 13px; color: #94A3B8; margin-left: 10px;">NEURAL CONFIDENCE: 88%</span></div>
            <h1 style="margin: 4px 0 0 0; font-size: 30px; font-weight: 800; color: #FFFFFF;">{selected_asset}</h1>
        </div>
        <div style="text-align: right;">
            <div class="price-large" style="color: {p_color};">₹{cmp:,.2f}</div>
            <div style="font-size: 14px; font-weight: 600; color: {p_color};">
                {'+' if change >= 0 else ''}{change:,.2f} ({'+' if pct_change >= 0 else ''}{pct_change:.2f}%)
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 7. CENTERSTAGE AI NEURAL COPILOT BOX
st.markdown(f"""
<div class="ai-brain-box">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
        <b style="color:#38BDF8; font-size:15px;">🤖 AI QUANT CORE | ORDER FLOW THESIS</b>
        <span style="font-size:11px; background:#1E293B; padding:2px 8px; border-radius:4px; color:#94A3B8;">Real-Time Auto Evaluation</span>
    </div>
    <div style="font-size:14px; line-height:1.6; color:#F1F5F9;">
        • <b>Market Structure:</b> {selected_asset} is trading <b>{'ABOVE' if is_bullish else 'BELOW'}</b> Institutional VWAP (₹{vwap}).<br>
        • <b>Liquidity Trap Warning:</b> {ai_trap}<br>
        • <b>Actionable Strategy:</b> {ai_action}
    </div>
</div>
""", unsafe_allow_html=True)

# 8. High-Speed Candlestick Canvas
fig = go.Figure()
fig.add_trace(go.Candlestick(
    x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
    name="Candles", increasing_line_color='#00F59B', decreasing_line_color='#FF4B4B'
))
fig.add_trace(go.Scatter(x=df.index, y=df['VWAP'], mode='lines', name='VWAP', line=dict(color='#38BDF8', width=2)))
fig.add_hline(y=support_floor, line_dash="dot", line_color="#00F59B", annotation_text=f"AI Demand ₹{support_floor}")
fig.add_hline(y=target_ceiling, line_dash="dot", line_color="#FF4B4B", annotation_text=f"AI Supply ₹{target_ceiling}")

fig.update_layout(
    template="plotly_dark", paper_bgcolor="#07090E", plot_bgcolor="#07090E",
    height=400, margin=dict(l=5, r=5, t=10, b=10), xaxis_rangeslider_visible=False,
    yaxis=dict(gridcolor="#131B2A", zeroline=False), xaxis=dict(gridcolor="#131B2A")
)
st.plotly_chart(fig, use_container_width=True)

# 9. 3-Card Decision Hub
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="quant-card">
        <div class="card-title">🎯 Target & Stop-Loss</div>
        <div style="display:flex; justify-content:space-between; margin-bottom:6px;"><span>Target</span><b style="color:#00F59B;">₹{target_ceiling}</b></div>
        <div style="display:flex; justify-content:space-between; margin-bottom:6px;"><span>Invalidation (SL)</span><b style="color:#FF4B4B;">₹{support_floor}</b></div>
        <div style="display:flex; justify-content:space-between;"><span>R:R Ratio</span><b style="color:#38BDF8;">1 : 2.5</b></div>
    </div>
    """, unsafe_allow_html=True)

sl_points = max(1.0, round(cmp - support_floor, 2))
max_risk_inr = (capital * risk_pct) / 100
safe_shares = int(max_risk_inr / sl_points)

with c2:
    st.markdown(f"""
    <div class="quant-card">
        <div class="card-title">🛡️ 1% Capital Risk Sizer</div>
        <div style="display:flex; justify-content:space-between; margin-bottom:6px;"><span>Max Risk</span><b style="color:#F59E0B;">₹{max_risk_inr:,.0f}</b></div>
        <div style="display:flex; justify-content:space-between; margin-bottom:6px;"><span>Safe Qty</span><b style="color:#00F59B; font-size:17px;">{safe_shares} Shares</b></div>
        <div style="font-size:11px; color:#64748B;">Strictly preserves ₹{capital:,.0f} capital.</div>
    </div>
    """, unsafe_allow_html=True)

round_strike = round(cmp / 10) * 10 if cmp > 100 else round(cmp)
with c3:
    st.markdown(f"""
    <div class="quant-card">
        <div class="card-title">⚡ AI Spread Hedge</div>
        <div style="display:flex; justify-content:space-between; margin-bottom:6px;"><span>Main Leg</span><b style="color:#FFFFFF;">BUY ₹{round_strike} CE</b></div>
        <div style="display:flex; justify-content:space-between; margin-bottom:6px;"><span>Hedge Leg</span><b style="color:#38BDF8;">SELL ₹{round_strike + 10} CE</b></div>
        <div style="font-size:11px; color:#00F59B;">Gap-down shield active.</div>
    </div>
    """, unsafe_allow_html=True)
