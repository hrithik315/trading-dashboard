import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from strategy_engine import fetch_stock_data, calculate_technical_indicators, generate_trade_signal, STOCK_MAP

st.set_page_config(page_title="Sancheti Trading AI", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# Ultra Clean Custom Styling (Mobile & Desktop Friendly)
st.markdown("""
<style>
    /* Dark Minimalist Theme */
    .stApp { background-color: #0E1117; color: #E0E3EB; }
    .card-box {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 14px;
        letter-spacing: 0.5px;
    }
    .scenario-card {
        background: #1B212C;
        border-left: 4px solid #388BFD;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 10px;
    }
    .scenario-card.buy { border-left-color: #00C087; }
    .scenario-card.dip { border-left-color: #388BFD; }
    .scenario-card.exit { border-left-color: #F2994A; }
    .scenario-card.trap { border-left-color: #EB5757; }
    
    .metric-title { font-size: 12px; color: #8B949E; margin-bottom: 2px; }
    .metric-val { font-size: 18px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Sancheti Trading AI")

# Sidebar - Dropdown Auto Search like Angel One
st.sidebar.markdown("### 🔍 Search Stock")
stock_options = list(STOCK_MAP.keys()) + ["-- Custom Search --"]
selected_stock = st.sidebar.selectbox("Type to Search Stock:", options=stock_options, index=0)

if selected_stock == "-- Custom Search --":
    symbol = st.sidebar.text_input("Enter NSE Ticker:", value="TATAMOTORS").upper().strip()
else:
    symbol = STOCK_MAP[selected_stock]

timeframe = st.sidebar.selectbox("Timeframe", ["Daily (1D)", "Weekly (1W)", "1 Hour (1H)"], index=0)
period_map = {"Daily (1D)": ("6mo", "1d"), "Weekly (1W)": ("2y", "1wk"), "1 Hour (1H)": ("1mo", "1h")}
period, interval = period_map[timeframe]

# Fetch Data
raw_df = fetch_stock_data(symbol, period=period, interval=interval)

if raw_df.empty:
    st.error(f"Stock '{symbol}' data not available. Please pick another stock from search.")
else:
    df = calculate_technical_indicators(raw_df)
    res = generate_trade_signal(df)
    
    # 1. Top Compact Header
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"<div class='card-box'><div class='metric-title'>STOCK / LTP</div><div class='metric-val'>₹{res['ltp']} <span style='font-size:13px; color:#58A6FF;'>({symbol})</span></div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='card-box'><div class='metric-title'>20 EMA (Trend)</div><div class='metric-val'>₹{res['ema20']}</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='card-box'><div class='metric-title'>RSI (14)</div><div class='metric-val'>{res['rsi']}</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='card-box'><div class='metric-title'>Key Resistance</div><div class='metric-val' style='color:#EB5757;'>₹{res['resistance']}</div></div>", unsafe_allow_html=True)
    with col5:
        st.markdown(f"<div class='card-box'><div class='metric-title'>Key Support</div><div class='metric-val' style='color:#00C087;'>₹{res['support']}</div></div>", unsafe_allow_html=True)

    # 2. Main Analysis Section
    left_col, right_col = st.columns([1, 1.2])
    
    with left_col:
        st.markdown("### 🎯 Signal & Candle Reading")
        st.markdown(f"<div class='badge' style='background:{res['badge_color']}; color:white;'>{res['verdict']} (Score: {res['score']}/100)</div>", unsafe_allow_html=True)
        st.write("")
        
        cd = res['candle_data']
        st.markdown(f"""
        <div class='card-box'>
            <div style='font-size: 15px; font-weight: 600; color: #58A6FF;'>Candle Pattern: {cd['pattern']}</div>
            <div style='color: #8B949E; margin-top: 5px;'>{cd['detail']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='card-box'>
            <div style='font-weight:600; margin-bottom:8px;'>🎯 Recommended Levels:</div>
            <div>• <b>Stop Loss:</b> ₹{res['stop_loss']}</div>
            <div>• <b>Target 1:</b> ₹{res['target_1']}</div>
            <div>• <b>Target 2:</b> ₹{res['target_2']}</div>
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        st.markdown("### 🧭 4 Key Action Scenarios")
        for s in res['scenarios']:
            tag_class = s['tag'].lower()
            st.markdown(f"""
            <div class='scenario-card {tag_class}'>
                <div style='font-weight:bold; font-size:14px;'>{s['title']} — <span style='color:#58A6FF;'>{s['level']}</span></div>
                <div style='font-size:13px; color:#C9D1D9; margin-top:4px;'>{s['desc']}</div>
            </div>
            """, unsafe_allow_html=True)

    # 3. Clean Interactive Chart
    st.markdown("### 📊 Interactive Technical Chart")
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.04, row_heights=[0.75, 0.25])
    
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], line=dict(color='#2962FF', width=1.5), name="20 EMA"), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA_50'], line=dict(color='#FF9800', width=1.5), name="50 EMA"), row=1, col=1)
    
    # S/R Horizontal Lines
    fig.add_hline(y=res['resistance'], line_dash="dash", line_color="#EB5757", annotation_text="Resistance", row=1, col=1)
    fig.add_hline(y=res['support'], line_dash="dash", line_color="#00C087", annotation_text="Support", row=1, col=1)
    
    # RSI Subplot
    fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#AB47BC', width=1.5), name="RSI (14)"), row=2, col=1)
    fig.add_hline(y=70, line_dash="dot", line_color="gray", row=2, col=1)
    fig.add_hline(y=30, line_dash="dot", line_color="gray", row=2, col=1)
    
    fig.update_layout(height=520, xaxis_rangeslider_visible=False, template="plotly_dark", margin=dict(l=5, r=5, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
