# TAB 1: BSE TRADINGVIEW (INTERVAL FIXED TO 'D')
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
