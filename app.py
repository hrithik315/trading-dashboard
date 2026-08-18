import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from strategy_engine import fetch_stock_data, calculate_technical_indicators, generate_trade_signal

st.set_page_config(page_title="AlphaTrade AI Scanner", page_icon="🎯", layout="wide")

st.markdown("""
<style>
    .metric-card { background-color: #1E222D; padding: 15px; border-radius: 8px; border: 1px solid #2A2E39; margin-bottom: 10px; }
    .buy-tag { background-color: #089981; color: white; padding: 5px 12px; border-radius: 5px; font-weight: bold; }
    .avoid-tag { background-color: #F23645; color: white; padding: 5px 12px; border-radius: 5px; font-weight: bold; }
    .watch-tag { background-color: #F2994A; color: white; padding: 5px 12px; border-radius: 5px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

st.title("🎯 AlphaTrade - Smart Price Action & Scenario Engine")

st.sidebar.header("⚙️ Scanner Controls")
ticker_input = st.sidebar.text_input("Enter NSE Stock Symbol", value="TATAMOTORS").upper().strip()
timeframe = st.sidebar.selectbox("Chart Timeframe", ["Daily (1D)", "Weekly (1W)", "1 Hour (1H)"], index=0)
period_map = {"Daily (1D)": ("6mo", "1d"), "Weekly (1W)": ("2y", "1wk"), "1 Hour (1H)": ("1mo", "1h")}
period, interval = period_map[timeframe]

capital = st.sidebar.number_input("Trading Capital (₹)", value=100000, step=10000)
risk_pct = st.sidebar.slider("Risk Per Trade (%)", 1.0, 5.0, 2.0, 0.5)

if ticker_input:
    raw_df = fetch_stock_data(ticker_input, period=period, interval=interval)
    if raw_df.empty:
        st.error(f"Could not load data for symbol '{ticker_input}'. Please verify.")
    else:
        df = calculate_technical_indicators(raw_df)
        data = generate_trade_signal(df)
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        chg = ((latest['Close'] - prev['Close']) / prev['Close']) * 100

        # Top Metric Ribbon
        m1, m2, m3, m4, m5, m6 = st.columns(6)
        m1.metric("LTP", f"₹{latest['Close']:.2f}", f"{chg:+.2f}%")
        m2.metric("20 EMA", f"₹{data['ema20']:.2f}")
        m3.metric("50 EMA", f"₹{data['ema50']:.2f}")
        m4.metric("RSI (14)", f"{data['rsi']:.1f}")
        m5.metric("Resistance (20D)", f"₹{data['resistance']:.2f}")
        m6.metric("Support (20D)", f"₹{data['support']:.2f}")

        st.divider()
        col_left, col_right = st.columns([1.2, 1])

        with col_left:
            st.subheader("📊 Candlestick & Indicator Verdict")
            sig = data['signal']
            if "STRONG BUY" in sig:
                st.markdown(f'<span class="buy-tag">{sig}</span> &nbsp; **Score: {data["confidence_score"]}/100**', unsafe_allow_html=True)
            elif "AVOID" in sig:
                st.markdown(f'<span class="avoid-tag">{sig}</span>', unsafe_allow_html=True)
            else:
                st.markdown(f'<span class="watch-tag">{sig}</span> &nbsp; **Score: {data["confidence_score"]}/100**', unsafe_allow_html=True)

            cd = data['candle_data']
            st.markdown(f"**Current Candle:** `{cd['pattern']}` — *{cd['note']}*")
            
            st.markdown("#### Confluence Checkpoints:")
            for r in data['reasons']:
                st.write(f"✔️ {r}")
            if not data['reasons']:
                st.write("⏳ Market is currently consolidating without high conviction.")

        with col_right:
            st.subheader("🧭 4 Key Market Action Scenarios")
            sc = data['scenarios']
            
            st.info(f"**{sc['breakout_buy']['title']} (₹{sc['breakout_buy']['price_level']})**\n\n{sc['breakout_buy']['condition']}")
            st.success(f"**{sc['dip_buy']['title']} (₹{sc['dip_buy']['price_level']})**\n\n{sc['dip_buy']['condition']}")
            st.warning(f"**{sc['profit_zone']['title']} (₹{sc['profit_zone']['price_level']})**\n\n{sc['profit_zone']['condition']}")
            st.error(f"**{sc['trap_zone']['title']} (₹{sc['trap_zone']['price_level']})**\n\n{sc['trap_zone']['condition']}")

        st.divider()
        # Chart with S/R Lines
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.6, 0.2, 0.2])
        
        # Candles & Indicators
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price OHLC"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_20'], line=dict(color='#2962FF', width=1.5), name="20 EMA"), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA_50'], line=dict(color='#FF6D00', width=1.5), name="50 EMA"), row=1, col=1)
        fig.add_hline(y=data['resistance'], line_dash="dash", line_color="#F23645", annotation_text="Key Resistance", row=1, col=1)
        fig.add_hline(y=data['support'], line_dash="dash", line_color="#089981", annotation_text="Key Support", row=1, col=1)
        
        # RSI
        fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#AB47BC', width=1.5), name="RSI"), row=2, col=1)
        fig.add_hline(y=70, line_dash="dot", line_color="gray", row=2, col=1)
        fig.add_hline(y=30, line_dash="dot", line_color="gray", row=2, col=1)
        
        # MACD
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD'], line=dict(color='#2962FF', width=1.2), name="MACD"), row=3, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], line=dict(color='#FF6D00', width=1.2), name="Signal"), row=3, col=1)
        
        fig.update_layout(height=750, xaxis_rangeslider_visible=False, template="plotly_dark", margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)