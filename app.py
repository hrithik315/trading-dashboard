# TAB 1: BSE REAL-TIME TRADINGVIEW EMBED (100% UNBLOCKED)
with tab_chart:
    # NSE ki jagah BSE exchange prefix lagane se data block bypass ho jata hai
    bse_symbol = f"BSE:{clean_name}"
    
    st.markdown(f"#### 📈 Live Interactive Chart: **{bse_symbol}**")
    
    tv_embed_code = f"""
    <!-- TradingView Widget BEGIN -->
    <div class="tradingview-widget-container" style="height:600px; width:100%;">
      <div id="tradingview_chart_bse" style="height:100%; width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "{bse_symbol}",
        "interval": "15",
        "timezone": "Asia/Kolkata",
        "theme": "dark",
        "style": "1",
        "locale": "in",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "hide_side_toolbar": false,
        "withdateranges": true,
        "save_image": true,
        "container_id": "tradingview_chart_bse"
      }});
      </script>
    </div>
    <!-- TradingView Widget END -->
    """
    components.html(tv_embed_code, height=620)
