import streamlit as st
import streamlit.components.v1 as components

# 1. Page Configuration
st.set_page_config(
    page_title="SANCHETI PRO TERMINAL",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Terminal CSS
st.markdown("""
<style>
    .stApp { background-color: #0B0E14; color: #F1F5F9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
    div[data-testid="stMetricValue"] { font-size: 20px; font-weight: 700; color: #00F59B; }
    .hero-box {
        background: #131B2A;
        border: 1px solid #1E293B;
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 15px;
    }
    .badge-green { background: rgba(0,245,155,0.15); color: #00F59B; border: 1px solid #00F59B; padding: 4px 8px; border-radius: 4px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 2. Sidebar Stock Selector (BSE Allowed Symbols)
st.sidebar.markdown("## ⚡ **SANCHETI PRO**")
st.sidebar.caption("Institutional Intelligence Engine")

stock_dict = {
    "WIPRO": "BSE:WIPRO",
    "TATA MOTORS": "BSE:TATAMOTORS",
    "RELIANCE": "BSE:RELIANCE",
    "INFOSYS": "BSE:INFY",
    "HDFC BANK": "BSE:HDFCBANK",
    "STATE BANK OF INDIA": "BSE:SBIN",
    "TCS": "BSE:TCS",
    "MAHINDRA & MAHINDRA": "BSE:M_M"
}

selected_name = st.sidebar.selectbox("🎯 Select Stock Asset", list(stock_dict.keys()), index=0)
bse_symbol = stock_dict[selected_name]

# Risk Parameters
st.sidebar.markdown("---")
account_capital = st.sidebar.number_input("Account Total Capital (₹)", value=50000, step=5000)
risk_pct = st.sidebar.slider("Max Risk per Trade (%)", 0.5, 3.0, 1.0, 0.1)

# 3. Top Status Header
st.markdown(f"""
<div class="hero-box">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <span class="badge-green">EXCHANGE CONNECTED: BSE LIVE</span>
            <h2 style="margin: 6px 0 0 0; color: #FFFFFF;">{selected_name} <span style="font-size: 15px; color: #38BDF8;">[{bse_symbol}]</span></h2>
        </div>
        <div style="text-align: right; color: #94A3B8; font-size: 13px;">
            Full Drawing Tools Active • Daily Interval Loaded
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. Tab Definitions
tab_chart, tab_ai, tab_hedge, tab_rescue = st.tabs([
    "📊 Pro TradingView Chart",
    "🧠 Smart Money & Traps",
    "🛡️ Hedging & Spreads",
    "⚖️ Position Sizing & Rescue"
])

# TAB 1: BSE TradingView Widget (Daily Interval - No Block)
with tab_chart:
    st.markdown(f"#### 📈 Live Interactive Chart: **{bse_symbol}**")
    
    tv_embed_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8" />
      <style>
        html, body {{ margin: 0; padding: 0; width: 100%; height: 100%; background-color: #0B0E14; overflow: hidden; }}
        #tv_chart_container {{ width: 100%; height: 100%; }}
      </style>
    </head>
    <body>
      <div id="tv_chart_container"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
        new TradingView.widget({{
          "autosize": true,
          "symbol": "{bse_symbol}",
          "interval": "D",
          "timezone": "Asia/Kolkata",
          "theme": "dark",
          "style": "1",
          "locale": "in",
          "toolbar_bg": "#0B0E14",
          "enable_publishing": false,
          "allow_symbol_change": true,
          "hide_side_toolbar": false,
          "withdateranges": true,
          "save_image": true,
          "container_id": "tv_chart_container"
        }});
      </script>
    </body>
    </html>
    """
    components.html(tv_embed_code, height=620)

with tab_ai:
    st.markdown("### 🤖 Institutional Order Flow Rules")
    st.markdown(f"""
    * **Active Asset:** `{bse_symbol}` (BSE Direct Exchange Data).
    * **Liquidity Sweep Rule:** Left toolbar se swing levels draw karein. Jab price major high ko sweep karke wick banaye, tab retail trap se bachein.
    * **Execution Rule:** Daily candle support floor ke upar close hone par hi multi-day accumulation start karein.
    """)

with tab_hedge:
    st.markdown("### 🛡️ Defined-Risk Spreads")
    st.write(f"• **Bullish Outlook:** {selected_name} Bull Call Spread (Buy ATM Call + Sell OTM Call)")
    st.write(f"• **Bearish Protection:** {selected_name} Bear Put Spread (Buy ATM Put + Sell OTM Put)")
    st.caption("Spreads time decay (Theta) aur gap-down risk se account ko protect karte hain.")

with tab_rescue:
    st.markdown("### ⚖️ 1% Capital Risk & Sizing")
    max_risk_amount = (account_capital * risk_pct) / 100
    st.metric("1% Max Risk Limit", f"₹{max_risk_amount:,.0f}")
    st.write("• **Capital Rule:** Stop Loss hit hone par max loss ₹" + f"{max_risk_amount:,.0f}" + " se zyada nahi hona chahiye.")
    st.write("• **Staging:** 30% initial position break/pullback par, aur 70% core demand zone par add karein.")
