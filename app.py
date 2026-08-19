import streamlit as st
import streamlit.components.v1 as components
import json

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

# 2. Sidebar Stock Selector
st.sidebar.markdown("## ⚡ **SANCHETI PRO**")
st.sidebar.caption("Institutional Intelligence Engine")

stock_dict = {
    "WIPRO": "NSE:WIPRO",
    "TATA MOTORS": "NSE:TATAMOTORS",
    "RELIANCE": "NSE:RELIANCE",
    "INFOSYS": "NSE:INFY",
    "HDFC BANK": "NSE:HDFCBANK",
    "STATE BANK OF INDIA": "NSE:SBIN",
    "TCS": "NSE:TCS",
    "MAHINDRA & MAHINDRA": "NSE:M_M"
}

selected_name = st.sidebar.selectbox("🎯 Select Asset to Trade", list(stock_dict.keys()), index=0)
tv_symbol = stock_dict[selected_name]
clean_name = selected_name

# Risk Controls
st.sidebar.markdown("---")
account_capital = st.sidebar.number_input("Account Capital (₹)", value=50000, step=5000)
risk_pct = st.sidebar.slider("Max Capital Risk (%)", 0.5, 3.0, 1.0, 0.1)

# 3. Top Snapshot Bar
st.markdown(f"""
<div class="hero-box">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div>
            <span class="badge-green">LIVE NSE STREAM</span>
            <h2 style="margin: 6px 0 0 0; color: #FFFFFF;">{clean_name} <span style="font-size: 14px; color: #38BDF8;">[{tv_symbol}]</span></h2>
        </div>
        <div style="text-align: right; color: #94A3B8; font-size: 13px;">
            Professional Drawing Canvas • Full Indicator Suite Active
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 4. 4 Clean Tabs
tab_chart, tab_ai, tab_hedge, tab_rescue = st.tabs([
    "📊 Pro TradingView Chart (With All Tools)",
    "🧠 Smart Money & Traps",
    "🛡️ Hedging & Spreads",
    "⚖️ Wipro Averaging Engine"
])

# TAB 1: FULL OFFICIAL TRADINGVIEW TECHNICAL CANVAS
with tab_chart:
    st.markdown(f"#### 📈 Live Real-Time Interactive Canvas: **{tv_symbol}**")
    st.caption("💡 Side toolbar se Trendlines, Fibonacci, Brush use karein; Top bar se Indicators (RSI, VWAP, MACD) lagayein.")
    
    # Official TradingView Advanced Real-Time Charting Widget
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
          "symbol": "{tv_symbol}",
          "interval": "15",
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
          "studies": [
            "VWAP@tv-basicstudies",
            "MASimple@tv-basicstudies"
          ],
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
    * **Structure Reading:** Stock symbol **{tv_symbol}** exchange real-time tick par sync hai.
    * **Smart Money Rule:** Chart par **VWAP (Blue Line)** ke upar price close hone par hi momentum buy execute karein.
    * **Trap Shield:** Previous Day High / Low ke break hote hi immediate entry lene se bachein (90% retail liquidity sweeps fake hote hain).
    """)

with tab_hedge:
    st.markdown("### 🛡️ Defined-Risk Options Hedging")
    st.write("• **Bullish Bias:** ATM Bull Call Spread (Buy ATM CE + Sell OTM CE)")
    st.write("• **Bearish Bias:** ATM Bear Put Spread (Buy ATM PE + Sell OTM PE)")
    st.caption("Never trade single-leg naked options on high volatility days.")

with tab_rescue:
    st.markdown("### ⚖️ Position Sizing & Rescue Matrix")
    max_risk = (account_capital * risk_pct) / 100
    st.metric("1% Capital Risk Limit", f"₹{max_risk:,.0f}")
    st.write("• **Rule:** Agar stock 3% girta hai, toh max holding loss ₹" + f"{max_risk:.0f}" + " se zyada nahi hona chahiye.")
    st.write("• **Averaging Rule:** Pehla 30% quantity breakout pullback par, aur baaki 70% quantity institutional demand floor par hi enter karein.")
