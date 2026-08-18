import streamlit as st
import streamlit.components.v1 as components
from strategy_engine import STOCK_DIRECTORY, fetch_institutional_deep_data

# Terminal Settings
st.set_page_config(
    page_title="Institutional Trading Terminal",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dark Sleek Institutional Terminal Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    * { font-family: 'Plus Jakarta Sans', sans-serif !important; }
    .stApp { background-color: #080B11; color: #E1E7EC; }
    
    .top-header {
        background: #101520;
        border: 1px solid #1C2436;
        border-radius: 12px;
        padding: 16px 22px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }
    
    .inst-card {
        background: #101520;
        border: 1px solid #1C2436;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
    }
    
    .metric-title { font-size: 11px; color: #7E8B9B; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-value { font-size: 19px; font-weight: 800; color: #FFFFFF; margin-top: 3px; }
    
    .ai-verdict-box {
        background: #101520;
        border-left: 4px solid #387ED1;
        border-top: 1px solid #1C2436;
        border-right: 1px solid #1C2436;
        border-bottom: 1px solid #1C2436;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 14px;
    }
    
    .news-card {
        background: #131926;
        border-left: 3px solid #387ED1;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Top Bar Selection
col1, col2 = st.columns([1.5, 1])
with col1:
    stock_names = list(STOCK_DIRECTORY.keys())
    selected_name = st.selectbox("🔍 Select Stock for Deep Institutional Scan:", options=stock_names, index=0)
    symbol = STOCK_DIRECTORY[selected_name]

# Fetch Real Deep Institutional Metrics
data = fetch_institutional_deep_data(symbol)
is_pos = data['change'] >= 0
chg_color = "#00B15D" if is_pos else "#EB5B50"

# ----------------- 1. LIVE TOP HEADER -----------------
st.markdown(f"""
<div class='top-header'>
    <div>
        <div style='font-size:11px; color:#7E8B9B; font-weight:700;'>NSE • INSTITUTIONAL FLOW TRACKER</div>
        <div style='font-size:24px; font-weight:800; color:#FFFFFF;'>{selected_name} <span style='font-size:14px; color:#7E8B9B;'>({symbol})</span></div>
    </div>
    <div style='text-align:right;'>
        <div style='font-size:26px; font-weight:800; color:{chg_color};'>₹{data['ltp']:.2f}</div>
        <div style='font-size:13px; font-weight:700; color:{chg_color};'>{data['change']:+.2f} ({data['pct_change']:+.2f}%)</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------- 2. FOUR REAL INSTITUTIONAL PULSE CARDS -----------------
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.markdown(f"<div class='inst-card'><div class='metric-title'>Smart Money Score</div><div class='metric-value' style='color:{data['theme_color']};'>{data['score']} / 100</div></div>", unsafe_allow_html=True)
with m2:
    st.markdown(f"<div class='inst-card'><div class='metric-title'>Institutional VWAP</div><div class='metric-value'>₹{data['vwap']}</div></div>", unsafe_allow_html=True)
with m3:
    st.markdown(f"<div class='inst-card'><div class='metric-title'>Derivatives PCR</div><div class='metric-value' style='color:#387ED1;'>{data['pcr']}</div></div>", unsafe_allow_html=True)
with m4:
    st.markdown(f"<div class='inst-card'><div class='metric-title'>Max Pain Strike</div><div class='metric-value'>₹{data['max_pain']}</div></div>", unsafe_allow_html=True)
with m5:
    st.markdown(f"<div class='inst-card'><div class='metric-title'>Inst. Holding</div><div class='metric-value' style='color:#00B15D;'>{data['inst_holding']}%</div></div>", unsafe_allow_html=True)

# ----------------- 3. INSTITUTIONAL REASONING & VERDICT -----------------
st.markdown(f"""
<div class='ai-verdict-box' style='border-left-color: {data['theme_color']};'>
    <div style='display:flex; justify-content:space-between; align-items:center;'>
        <div style='font-size:16px; font-weight:800; color:{data['theme_color']};'>{data['verdict']}</div>
        <div style='font-size:12px; background:#1C2436; padding:4px 10px; border-radius:6px; color:#58A6FF;'>Institutional AI Engine</div>
    </div>
    <div style='color:#DCE4EC; font-size:14px; margin-top:8px; line-height:1.5;'>
        🏛️ <b>Institutional Master Thesis:</b> {data['master_action']}
    </div>
</div>
""", unsafe_allow_html=True)

# ----------------- 4. DEEP INSTITUTIONAL TABS -----------------
tab_chart, tab_logic, tab_derivatives, tab_fund, tab_news = st.tabs([
    "📈 Pro Live Chart",
    "🧠 Institutional Thesis & Traps",
    "📊 Option Chain & Derivatives",
    "🏢 Valuation & FII Stake",
    "📰 Live News Catalysts"
])

with tab_chart:
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
        "toolbar_bg": "#080B11",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "container_id": "tradingview_chart"
      }});
      </script>
    </div>
    """
    components.html(tv_html, height=550)

with tab_logic:
    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown("#### 🟢 Big Money Confluence (Why Institutions are Interested)")
        st.markdown("<div class='inst-card'>", unsafe_allow_html=True)
        if data['thesis']:
            for t in data['thesis']:
                st.markdown(f"<div style='color:#00B15D; font-size:13px; margin-bottom:6px;'>• {t}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#7E8B9B; font-size:13px;'>No strong institutional accumulation detected currently.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with c_right:
        st.markdown("#### 🔴 Retail Traps & Caution Points")
        st.markdown("<div class='inst-card'>", unsafe_allow_html=True)
        if data['warnings']:
            for w in data['warnings']:
                st.markdown(f"<div style='color:#EB5B50; font-size:13px; margin-bottom:6px;'>⚠️ {w}</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#00B15D; font-size:13px;'>No major distribution or trap detected. Clear runway.</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("#### 🎯 Smart Money Trade Plan")
    st.markdown(f"""
    <div class='inst-card'>
        <div style='display:flex; justify-content:space-around; text-align:center;'>
            <div><div class='metric-title'>Optimal Entry Zone</div><div style='font-size:16px; font-weight:700; color:#387ED1;'>₹{data['vwap']} - ₹{data['ltp']}</div></div>
            <div><div class='metric-title'>Strict Invalidation (SL)</div><div style='font-size:16px; font-weight:700; color:#EB5B50;'>₹{data['sl']}</div></div>
            <div><div class='metric-title'>Target 1 (Liquidity Pool)</div><div style='font-size:16px; font-weight:700; color:#00B15D;'>₹{data['t1']}</div></div>
            <div><div class='metric-title'>Target 2 (Major Supply)</div><div style='font-size:16px; font-weight:700; color:#00B15D;'>₹{data['t2']}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab_derivatives:
    st.markdown("#### ⚡ Option Chain & Open Interest Breakdown")
    d1, d2, d3 = st.columns(3)
    with d1:
        st.markdown(f"""
        <div class='inst-card'>
            <div class='metric-title'>Major Call OI (Ceiling)</div>
            <div class='metric-value' style='color:#EB5B50;'>₹{data['call_oi']} Strike</div>
            <div style='font-size:12px; color:#7E8B9B; margin-top:4px;'>Highest Call Writer resistance zone.</div>
        </div>
        """, unsafe_allow_html=True)
    with d2:
        st.markdown(f"""
        <div class='inst-card'>
            <div class='metric-title'>Major Put OI (Floor)</div>
            <div class='metric-value' style='color:#00B15D;'>₹{data['put_oi']} Strike</div>
            <div style='font-size:12px; color:#7E8B9B; margin-top:4px;'>Highest Put Writer demand support floor.</div>
        </div>
        """, unsafe_allow_html=True)
    with d3:
        st.markdown(f"""
        <div class='inst-card'>
            <div class='metric-title'>Max Pain Level</div>
            <div class='metric-value' style='color:#387ED1;'>₹{data['max_pain']}</div>
            <div style='font-size:12px; color:#7E8B9B; margin-top:4px;'>Strike where option writers face minimum loss.</div>
        </div>
        """, unsafe_allow_html=True)

with tab_fund:
    st.markdown("#### 🏢 Fundamentals & FII/DII Stake Safety")
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        st.markdown(f"<div class='inst-card'><div class='metric-title'>Trailing P/E</div><div class='metric-value'>{data['pe']}x</div></div>", unsafe_allow_html=True)
    with f2:
        st.markdown(f"<div class='inst-card'><div class='metric-title'>Price to Book (P/B)</div><div class='metric-value'>{data['pb']}</div></div>", unsafe_allow_html=True)
    with f3:
        st.markdown(f"<div class='inst-card'><div class='metric-title'>Return on Equity (ROE)</div><div class='metric-value' style='color:#00B15D;'>{data['roe']}%</div></div>", unsafe_allow_html=True)
    with f4:
        st.markdown(f"<div class='inst-card'><div class='metric-title'>52W High / Low</div><div class='metric-value' style='font-size:15px;'>₹{data['high_52w']} / ₹{data['low_52w']}</div></div>", unsafe_allow_html=True)

with tab_news:
    st.markdown("#### 📰 Institutional News Catalysts")
    for n in data['news']:
        st.markdown(f"""
        <div class='news-card'>
            <div style='font-size:11px; color:#7E8B9B;'>{n['publisher']}</div>
            <div style='font-size:14px; font-weight:600; margin-top:3px;'><a href='{n['link']}' target='_blank' style='color:#E1E7EC; text-decoration:none;'>{n['title']}</a></div>
        </div>
        """, unsafe_allow_html=True)
