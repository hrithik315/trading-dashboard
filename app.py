import streamlit as st
import streamlit.components.v1 as components
from strategy_engine import STOCK_DIRECTORY, get_live_quote, get_stock_news

# Page Settings
st.set_page_config(
    page_title="Angel Pro Mobile Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# True Angel One App Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    * { font-family: 'Plus Jakarta Sans', sans-serif !important; }
    .stApp { background-color: #0c0f17; color: #f0f3f8; }
    
    /* Top Bar Header */
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
    
    .quote-badge {
        font-size: 24px;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    
    /* Cards */
    .angel-box {
        background: #131824;
        border: 1px solid #1e2638;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    .pill-tag {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
    }
    
    .news-item {
        background: #171d2b;
        border-left: 3px solid #387ed1;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
    }
    
    /* Buy / Sell Action Strip */
    .action-bar {
        display: flex;
        gap: 15px;
        margin-top: 15px;
    }
    .buy-btn {
        flex: 1;
        background: #00b15d;
        color: #fff;
        text-align: center;
        padding: 14px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 15px;
    }
    .sell-btn {
        flex: 1;
        background: #eb5b50;
        color: #fff;
        text-align: center;
        padding: 14px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- STOCK SELECTOR ROW -----------------
col_search, col_space = st.columns([1, 2])
with col_search:
    stock_names = list(STOCK_DIRECTORY.keys())
    selected_name = st.selectbox("🔍 Search & Select Stock", options=stock_names, index=0)
    symbol = STOCK_DIRECTORY[selected_name]

# Fetch Quotes & News
q = get_live_quote(symbol)
news_list = get_stock_news(symbol)
is_green = q['change'] >= 0
chg_color = "#00b15d" if is_green else "#eb5b50"

# ----------------- TOP ANGEL ONE QUOTE BAR -----------------
st.markdown(f"""
<div class='app-header'>
    <div>
        <div style='font-size:12px; color:#7e8b9b; font-weight:600;'>NSE • EQUITY</div>
        <div style='font-size:20px; font-weight:800; color:#ffffff;'>{selected_name}</div>
    </div>
    <div style='text-align:right;'>
        <div class='quote-badge' style='color:{chg_color};'>₹{q['ltp']:.2f}</div>
        <div style='font-size:13px; font-weight:700; color:{chg_color};'>{q['change']:+.2f} ({q['pct_change']:+.2f}%)</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------- MAIN APP TABS -----------------
tab1, tab2, tab3, tab4 = st.tabs(["📈 Pro Chart", "🧠 Smart Money & Traps", "🎯 Order Pad & SL", "📰 News"])

# TAB 1: OFFICIAL TRADINGVIEW WIDGET
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

# TAB 2: SMART MONEY CONCEPTS & TRAPS
with tab2:
    s1, s2 = st.columns(2)
    with s1:
        st.markdown(f"""
        <div class='angel-box'>
            <div class='pill-tag' style='background:#1f293d; color:#58a6ff;'>Institutional Strategy Matrix</div>
            <h4 style='margin-top:10px; color:#ffffff;'>Smart Money Bias: <span style='color:{chg_color};'>{'ACCUMULATION (BUYING)' if is_green else 'DISTRIBUTION (SELLING)'}</span></h4>
            <p style='color:#9ba8b8; font-size:13px; line-height:1.6;'>
                • <b>Institutional Score:</b> {q['score']}/100<br>
                • <b>Smart Demand Zone:</b> Near ₹{q['support']}<br>
                • <b>Smart Supply Zone:</b> Near ₹{q['resistance']}
            </p>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown(f"""
        <div class='angel-box'>
            <div class='pill-tag' style='background:#3d231f; color:#ff7b72;'>Retail Trap Alert</div>
            <h4 style='margin-top:10px; color:#ffffff;'>Fakeout & Reversal Check</h4>
            <p style='color:#9ba8b8; font-size:13px; line-height:1.6;'>
                Agar price ₹{q['resistance']} ke paas pahunch kar wick banati hai, toh breakout buy mat karein. Retailers ko trap karke profit-booking trigger ho sakti hai.
            </p>
        </div>
        """, unsafe_allow_html=True)

# TAB 3: ORDER PAD & SL TARGETS
with tab3:
    o1, o2 = st.columns(2)
    with o1:
        st.markdown(f"""
        <div class='angel-box'>
            <h4 style='color:#ffffff; margin-bottom:12px;'>🎯 Recommended Trade Plan</h4>
            <div style='font-size:14px; margin-bottom:8px;'>• <b>Optimal Entry:</b> ₹{q['ltp']}</div>
            <div style='font-size:14px; color:#eb5b50; margin-bottom:8px;'>• <b>Strict Invalidation (SL):</b> ₹{q['sl']}</div>
            <div style='font-size:14px; color:#00b15d; margin-bottom:8px;'>• <b>Target 1 (1.5R):</b> ₹{q['t1']}</div>
            <div style='font-size:14px; color:#00b15d; margin-bottom:8px;'>• <b>Target 2 (Supply Zone):</b> ₹{q['t2']}</div>
        </div>
        """, unsafe_allow_html=True)
    with o2:
        st.markdown(f"""
        <div class='angel-box'>
            <h4 style='color:#ffffff; margin-bottom:12px;'>⚡ Quick Execution Summary</h4>
            <p style='color:#9ba8b8; font-size:13px;'>Capital Risk Management ke sath position size calculate karein. Hamesha per-trade 1% se zyada risk na lein.</p>
            <div class='action-bar'>
                <div class='buy-btn'>BUY ZONE : ₹{q['ltp']}</div>
                <div class='sell-btn'>SL : ₹{q['sl']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# TAB 4: LIVE NEWS
with tab4:
    st.markdown("#### 📰 Recent Headlines & Catalyst Impact")
    for n in news_list:
        st.markdown(f"""
        <div class='news-item'>
            <div style='font-size:11px; color:#7e8b9b;'>{n['publisher']}</div>
            <div style='font-size:14px; font-weight:600; margin-top:3px;'><a href='{n['link']}' target='_blank' style='color:#f0f3f8; text-decoration:none;'>{n['title']}</a></div>
        </div>
        """, unsafe_allow_html=True)
