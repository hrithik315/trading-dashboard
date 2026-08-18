import streamlit as st
import streamlit.components.v1 as components
from strategy_engine import STOCK_DIRECTORY, fetch_deep_analysis, get_stock_news

st.set_page_config(page_title="Angel Pro AI Terminal", page_icon="⚡", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    * { font-family: 'Plus Jakarta Sans', sans-serif !important; }
    .stApp { background-color: #0c0f17; color: #f0f3f8; }
    
    .app-header {
        background: #131824;
        border-radius: 12px;
        padding: 14px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
        border: 1px solid #1e2638;
    }
    
    .ai-live-card {
        background: #131824;
        border-left: 4px solid #387ed1;
        border-top: 1px solid #1e2638;
        border-right: 1px solid #1e2638;
        border-bottom: 1px solid #1e2638;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    .angel-box {
        background: #131824;
        border: 1px solid #1e2638;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    .metric-badge {
        font-size: 11px;
        color: #7e8b9b;
        font-weight: 700;
        text-transform: uppercase;
    }
    .metric-num {
        font-size: 18px;
        font-weight: 800;
        color: #ffffff;
        margin-top: 2px;
    }
</style>
""", unsafe_allow_html=True)

# Top Bar Selection
col_s, col_refresh = st.columns([2, 1])
with col_s:
    stock_names = list(STOCK_DIRECTORY.keys())
    selected_name = st.selectbox("🔍 Search & Select Stock", options=stock_names, index=0)
    symbol = STOCK_DIRECTORY[selected_name]

# Fetch Data
data = fetch_deep_analysis(symbol)
news_list = get_stock_news(symbol)

if not data:
    st.error("Market data temporarily sync nahi ho pa raha hai. Kripya dusra stock chunein.")
else:
    is_green = data['change'] >= 0
    chg_color = "#00b15d" if is_green else "#eb5b50"

    # Header Strip
    st.markdown(f"""
    <div class='app-header'>
        <div>
            <div style='font-size:12px; color:#7e8b9b; font-weight:600;'>NSE • REAL-TIME CONFLUENCE</div>
            <div style='font-size:22px; font-weight:800; color:#ffffff;'>{selected_name}</div>
        </div>
        <div style='text-align:right;'>
            <div style='font-size:24px; font-weight:800; color:{chg_color};'>₹{data['ltp']:.2f}</div>
            <div style='font-size:13px; font-weight:700; color:{chg_color};'>{data['change']:+.2f} ({data['pct_change']:+.2f}%)</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 4 Pulse Metrics
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        st.markdown(f"<div class='angel-box'><div class='metric-badge'>Institutional VWAP</div><div class='metric-num'>₹{data['vwap']}</div></div>", unsafe_allow_html=True)
    with p2:
        st.markdown(f"<div class='angel-box'><div class='metric-badge'>RSI (14) Momentum</div><div class='metric-num'>{data['rsi']}</div></div>", unsafe_allow_html=True)
    with p3:
        st.markdown(f"<div class='angel-box'><div class='metric-badge'>Demand Support</div><div class='metric-num' style='color:#00b15d;'>₹{data['sup']}</div></div>", unsafe_allow_html=True)
    with p4:
        st.markdown(f"<div class='angel-box'><div class='metric-badge'>Supply Resistance</div><div class='metric-num' style='color:#eb5b50;'>₹{data['res']}</div></div>", unsafe_allow_html=True)

    # LIVE AI ASSISTANT DIRECT INSIGHT
    st.markdown(f"""
    <div class='ai-live-card'>
        <div style='display:flex; justify-content:space-between; align-items:center;'>
            <div style='font-size:15px; font-weight:800; color:{data['theme_color']};'>{data['verdict']} (Confidence: {data['score']}%)</div>
            <div style='font-size:12px; background:#1e2638; padding:4px 10px; border-radius:6px; color:#58a6ff;'>AI Live Assist 🟢 Active</div>
        </div>
        <div style='color:#d1d7e0; font-size:14px; margin-top:8px; line-height:1.5;'>
            🤖 <b>AI Analysis:</b> {data['ai_advice']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Navigation Tabs
    tab1, tab2, tab3 = st.tabs(["📈 Real-Time Chart", "🎯 Order Plan & Levels", "📰 Live News Feed"])

    with tab1:
        tv_html = f"""
        <div class="tradingview-widget-container" style="height:550px;width:100%">
          <div id="tradingview_chart" style="height:calc(100% - 32px);width:100%"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({{
            "autosize": true,
            "symbol": "NSE:{symbol}",
            "interval": "15",
            "timezone": "Asia/Kolkata",
            "theme": "dark",
            "style": "1",
            "locale": "en",
            "toolbar_bg": "#0c0f17",
            "enable_publishing": false,
            "allow_symbol_change": true,
            "container_id": "tradingview_chart"
          }});
          </script>
        </div>
        """
        components.html(tv_html, height=550)

    with tab2:
        o1, o2 = st.columns(2)
        with o1:
            st.markdown("#### 🎯 Execution Anchors")
            st.markdown(f"""
            <div class='angel-box'>
                <div style='font-size:14px; margin-bottom:8px;'>• <b>Entry Zone:</b> Near ₹{data['ltp']}</div>
                <div style='font-size:14px; color:#eb5b50; margin-bottom:8px;'>• <b>Stop Loss (Strict):</b> ₹{data['sl']}</div>
                <div style='font-size:14px; color:#00b15d; margin-bottom:8px;'>• <b>Target 1:</b> ₹{data['t1']}</div>
                <div style='font-size:14px; color:#00b15d; margin-bottom:8px;'>• <b>Target 2:</b> ₹{data['t2']}</div>
            </div>
            """, unsafe_allow_html=True)
        with o2:
            st.markdown("#### 🔍 AI Confluence Breakdown")
            st.markdown("<div class='angel-box'>", unsafe_allow_html=True)
            for r in data['bull_reasons']:
                st.markdown(f"<div style='color:#00b15d; font-size:13px; margin-bottom:4px;'>✅ {r}</div>", unsafe_allow_html=True)
            for r in data['bear_reasons']:
                st.markdown(f"<div style='color:#eb5b50; font-size:13px; margin-bottom:4px;'>⚠️ {r}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown("#### 📰 Recent Headlines")
        for n in news_list:
            st.markdown(f"""
            <div class='angel-box'>
                <div style='font-size:11px; color:#7e8b9b;'>{n['publisher']}</div>
                <div style='font-size:14px; font-weight:600; margin-top:3px;'><a href='{n['link']}' target='_blank' style='color:#f0f3f8; text-decoration:none;'>{n['title']}</a></div>
            </div>
            """, unsafe_allow_html=True)
