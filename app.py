import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from strategy_engine import (
    STOCK_DIRECTORY, 
    fetch_clean_market_data, 
    calculate_indicators, 
    analyze_institutional_logic, 
    fetch_live_news_sentiment
)

# App Configuration
st.set_page_config(page_title="Angel Pro Terminal | Sancheti", page_icon="📈", layout="wide", initial_sidebar_state="expanded")

# Angel One Inspired Clean Dark Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
    * { font-family: 'Plus Jakarta Sans', sans-serif; }
    
    .stApp { background-color: #0B0E14; color: #E1E7EC; }
    
    /* Top Bar & Cards */
    .angel-card {
        background: #141923;
        border: 1px solid #1E2638;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .metric-sub { font-size: 11px; color: #8F9CA9; font-weight: 600; text-transform: uppercase; }
    .metric-main { font-size: 20px; font-weight: 700; color: #FFFFFF; margin-top: 2px; }
    
    /* Pills & Status */
    .status-pill {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
    }
    
    /* News Box */
    .news-box {
        background: #141923;
        border-left: 3px solid #2962FF;
        border-top: 1px solid #1E2638;
        border-right: 1px solid #1E2638;
        border-bottom: 1px solid #1E2638;
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 10px;
    }
    
    /* Custom Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; border-bottom: 1px solid #1E2638; }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #8F9CA9;
        font-weight: 600;
        font-size: 14px;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        color: #387ED1 !important;
        border-bottom: 2px solid #387ED1 !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SESSION LOGIN PROTECTION -----------------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = True  # Default login bypass for ease (Can add PIN)

# ----------------- SIDEBAR CONTROLS -----------------
with st.sidebar:
    st.markdown("### ⚡ **Angel Pro Scanner**")
    st.caption("Clean Institutional Terminal")
    
    # Watchlist Dropdown
    stock_names = list(STOCK_DIRECTORY.keys()) + ["-- Custom Ticker --"]
    selected_name = st.selectbox("Select Asset / Watchlist:", options=stock_names, index=0)
    
    if selected_name == "-- Custom Ticker --":
        ticker = st.text_input("Enter NSE Code:", value="TATAMOTORS").upper().strip()
    else:
        ticker = STOCK_DIRECTORY[selected_name]
        
    timeframe = st.selectbox(
        "Timeframe / Interval:",
        ["15 Minute (Intraday)", "5 Minute (Scalping)", "30 Minute", "1 Hour (Swing)", "Daily (Positional)"],
        index=0
    )
    
    tf_map = {
        "5 Minute (Scalping)": ("1mo", "5m"),
        "15 Minute (Intraday)": ("1mo", "15m"),
        "30 Minute": ("1mo", "30m"),
        "1 Hour (Swing)": ("3mo", "60m"),
        "Daily (Positional)": ("1y", "1d")
    }
    range_str, interval = tf_map[timeframe]
    
    st.divider()
    st.markdown("💡 **Pro Tip:** Smart Money enters on Support retests with volume confirmation.")

# ----------------- DATA ENGINE -----------------
with st.spinner("Connecting to Live NSE Feed..."):
    raw_df, meta = fetch_clean_market_data(ticker, interval=interval, range_str=range_str)

if raw_df.empty:
    st.error(f"Could not load data for '{ticker}'. Please select another stock from the watchlist.")
else:
    df = calculate_indicators(raw_df)
    res = analyze_institutional_logic(df, ticker)
    news_feed = fetch_live_news_sentiment(ticker)
    
    prev_close = float(df.iloc[-2]['Close']) if len(df) > 1 else res['ltp']
    chg = res['ltp'] - prev_close
    chg_pct = (chg / prev_close) * 100 if prev_close else 0
    chg_color = "#089981" if chg >= 0 else "#F23645"

    # ----------------- TOP TICKER PULSE BAR -----------------
    c1, c2, c3, c4, c5 = st.columns([1.2, 1, 1, 1, 1])
    with c1:
        st.markdown(f"""
        <div class='angel-card'>
            <div class='metric-sub'>Asset | Exchange</div>
            <div class='metric-main'>NSE:{ticker} <span style='font-size:14px; color:{chg_color};'>₹{res['ltp']:.2f} ({chg_pct:+.2f}%)</span></div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class='angel-card'>
            <div class='metric-sub'>Smart Money Score</div>
            <div class='metric-main' style='color:{res['theme_color']};'>{res['score']} / 100</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class='angel-card'>
            <div class='metric-sub'>20 EMA (Momentum)</div>
            <div class='metric-main'>₹{res['ema20']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class='angel-card'>
            <div class='metric-sub'>Major Supply (Res)</div>
            <div class='metric-main' style='color:#F23645;'>₹{res['resistance']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with c5:
        st.markdown(f"""
        <div class='angel-card'>
            <div class='metric-sub'>Major Demand (Sup)</div>
            <div class='metric-main' style='color:#089981;'>₹{res['support']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)

    # ----------------- CLEAN TABS INTERFACE (ANGEL ONE STYLE) -----------------
    tab_chart, tab_smart, tab_news, tab_orders = st.tabs([
        "📊 Live Chart", 
        "🧠 Smart Money & Traps", 
        "📰 News & Sentiment", 
        "🎯 Order Levels & SL"
    ])

    # 1. TAB: PRO CHART
    with tab_chart:
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.75, 0.25]
        )
        
        # Candles
        fig.add_trace(go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
            name="Price",
            increasing_line_color='#089981', increasing_fillcolor='#089981',
            decreasing_line_color='#F23645', decreasing_fillcolor='#F23645',
            line=dict(width=1.2)
        ), row=1, col=1)
        
        # EMAs
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], line=dict(color='#2962FF', width=1.5), name="20 EMA"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_50'], line=dict(color='#FF9800', width=1.5), name="50 EMA"), row=1, col=1)
        
        # Support & Resistance Levels
        fig.add_hline(y=res['resistance'], line_dash="dash", line_color="#F23645", line_width=1.2, annotation_text=f"Supply ₹{res['resistance']:.2f}", row=1, col=1)
        fig.add_hline(y=res['support'], line_dash="dash", line_color="#089981", line_width=1.2, annotation_text=f"Demand ₹{res['support']:.2f}", row=1, col=1)
        
        # RSI
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#AB47BC', width=1.5), name="RSI (14)"), row=2, col=1)
        fig.add_hline(y=70, line_dash="dot", line_color="#F23645", row=2, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="#089981", row=2, col=1)
        
        fig.update_layout(
            height=540,
            plot_bgcolor="#0B0E14",
            paper_bgcolor="#0B0E14",
            xaxis_rangeslider_visible=False,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#8F9CA9", size=11)),
            xaxis=dict(gridcolor="#161B26", showgrid=True),
            yaxis=dict(gridcolor="#161B26", showgrid=True, side="right"),
            xaxis2=dict(gridcolor="#161B26", showgrid=True),
            yaxis2=dict(gridcolor="#161B26", showgrid=True, side="right", range=[0, 100])
        )
        st.plotly_chart(fig, use_container_width=True)

    # 2. TAB: SMART MONEY INSIGHTS & TRAPS
    with tab_smart:
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.markdown("#### 🏛️ Institutional Setup")
            st.markdown(f"""
            <div class='angel-card'>
                <div style='font-size:14px; font-weight:700; color:{res['theme_color']};'>{res['sentiment']}</div>
                <div style='color:#C5D1DE; font-size:13px; margin-top:8px;'>
                    • <b>Action Verdict:</b> {res['action']}<br>
                    • <b>RSI Momentum:</b> {res['rsi']:.1f} (Neutral 45-65, Reversal &lt;30 / &gt;70)<br>
                    • <b>Volume Footprint:</b> {'🚨 Heavy institutional volume' if res['volume_surge'] else 'Normal standard liquidity'}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_s2:
            st.markdown("#### 🪤 Retail Trap Scanner")
            st.markdown(f"""
            <div class='angel-card' style='border-left: 4px solid #FF9800;'>
                <div style='font-size:13px; font-weight:600; color:#FFFFFF;'>Trap Alert Detection:</div>
                <div style='font-size:13px; color:#C5D1DE; margin-top:6px;'>{res['trap_alert']}</div>
            </div>
            """, unsafe_allow_html=True)

    # 3. TAB: LIVE NEWS & SENTIMENT
    with tab_news:
        st.markdown("#### 📰 Taaza News & Catalyst Impact")
        for item in news_feed:
            st.markdown(f"""
            <div class='news-box'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <span style='font-size:11px; color:#8F9CA9; font-weight:600;'>{item['publisher']}</span>
                    <span style='font-size:12px; font-weight:700;'>{item['badge']}</span>
                </div>
                <div style='font-size:14px; font-weight:600; color:#FFFFFF; margin-top:5px;'>
                    <a href='{item['link']}' target='_blank' style='color:#E1E7EC; text-decoration:none;'>{item['title']}</a>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 4. TAB: ORDERS & RISK-REWARD PAD
    with tab_orders:
        o1, o2 = st.columns(2)
        with o1:
            st.markdown("#### 🛒 Execution Levels")
            st.markdown(f"""
            <div class='angel-card'>
                <div style='font-size:13px; margin-bottom:6px;'><b>Safe Pullback Entry:</b> Near ₹{max(res['ema20'], res['support']):.2f}</div>
                <div style='font-size:13px; margin-bottom:6px;'><b>Aggressive Breakout:</b> Above ₹{res['resistance'] * 1.002:.2f}</div>
                <div style='font-size:13px; color:#F23645; margin-bottom:6px;'><b>Strict Stop Loss:</b> ₹{res['sl']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        with o2:
            st.markdown("#### 🎯 Target Matrices")
            st.markdown(f"""
            <div class='angel-card'>
                <div style='font-size:13px; color:#089981; margin-bottom:6px;'><b>Target 1 (1.5R):</b> ₹{res['t1']:.2f}</div>
                <div style='font-size:13px; color:#089981; margin-bottom:6px;'><b>Target 2 (2.5R Supply):</b> ₹{res['t2']:.2f}</div>
                <div style='font-size:12px; color:#8F9CA9;'>Always trail stop-loss to cost once Target 1 is hit.</div>
            </div>
            """, unsafe_allow_html=True)
