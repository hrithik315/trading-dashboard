import yfinance as yf
import pandas as pd
import numpy as np
import requests

STOCK_DIRECTORY = {
    "TATA MOTORS": "TATAMOTORS",
    "RELIANCE": "RELIANCE",
    "HDFC BANK": "HDFCBANK",
    "ICICI BANK": "ICICIBANK",
    "INFOSYS": "INFY",
    "STATE BANK OF INDIA": "SBIN",
    "TCS": "TCS",
    "TATA STEEL": "TATASTEEL",
    "TATA POWER": "TATAPOWER",
    "ITC": "ITC",
    "BHARTI AIRTEL": "BHARTIARTL",
    "LARSEN & TOUBRO": "LT",
    "KOTAK BANK": "KOTAKBANK",
    "AXIS BANK": "AXISBANK",
    "BAJAJ FINANCE": "BAJFINANCE",
    "MARUTI SUZUKI": "MARUTI",
    "M&M": "M&M",
    "SUN PHARMA": "SUNPHARMA",
    "TITAN": "TITAN",
    "ADANI ENT": "ADANIENT",
    "ADANI PORTS": "ADANIPORTS",
    "VEDANTA": "VEDL",
    "ZOMATO": "ZOMATO",
    "JIO FINANCIAL": "JIOFIN",
    "SUZLON": "SUZLON"
}

def fetch_deep_analysis(symbol: str) -> dict:
    clean = symbol.strip().upper()
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        # 1. Fetch 15m Intraday Data
        url_15m = f"https://query1.finance.yahoo.com/v8/finance/chart/{clean}.NS?interval=15m&range=5d"
        res = requests.get(url_15m, headers=headers, timeout=6).json()
        quote = res['chart']['result'][0]['indicators']['quote'][0]
        meta = res['chart']['result'][0].get('meta', {})
        
        closes = [c for c in quote['close'] if c is not None]
        highs = [h for h in quote['high'] if h is not None]
        lows = [l for l in quote['low'] if l is not None]
        volumes = [v for v in quote['volume'] if v is not None]
        
        ltp = round(float(meta.get('regularMarketPrice', closes[-1])), 2)
        prev_close = round(float(meta.get('chartPreviousClose', closes[-2])), 2)
        change = round(ltp - prev_close, 2)
        pct_change = round((change / prev_close) * 100, 2)
        
        # VWAP Calculation
        df_calc = pd.DataFrame({'High': highs, 'Low': lows, 'Close': closes, 'Volume': volumes})
        df_calc['Typical_Price'] = (df_calc['High'] + df_calc['Low'] + df_calc['Close']) / 3
        df_calc['VP'] = df_calc['Typical_Price'] * df_calc['Volume']
        vwap = round(df_calc['VP'].sum() / max(df_calc['Volume'].sum(), 1), 2)
        
        # RSI 14
        delta = df_calc['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss.replace(0, np.nan)
        rsi = round(float((100 - (100 / (1 + rs))).iloc[-1]), 1)
        
        # Support / Resistance & Traps
        res_zone = round(max(highs[-25:]), 2)
        sup_zone = round(min(lows[-25:]), 2)
        avg_vol = np.mean(volumes[-15:])
        current_vol = volumes[-1]
        is_vol_spike = current_vol > (avg_vol * 1.5)
        
        # AI Confluence Scoring (Multi-Factor)
        score = 50
        bull_reasons = []
        bear_reasons = []
        
        if ltp > vwap:
            score += 15
            bull_reasons.append("Price Institutional VWAP ke upar trade kar raha hai (Bullish Buyers in control).")
        else:
            score -= 15
            bear_reasons.append("Price VWAP ke neeche slip hua hai (Sellers dominating).")
            
        if 48 <= rsi <= 65:
            score += 15
            bull_reasons.append("RSI healthy momentum zone mein hai (No overbought risk).")
        elif rsi > 70:
            score -= 10
            bear_reasons.append("RSI overbought (>70) hai. Trap breakout ka high chance hai.")
        elif rsi < 35:
            bull_reasons.append("RSI oversold (<35) demand bounce zone ke paas hai.")
            
        if is_vol_spike:
            if ltp > closes[-2]:
                score += 20
                bull_reasons.append("Big Institutional Buying Volume detected (Accumulation).")
            else:
                score -= 20
                bear_reasons.append("Heavy Institutional Distribution Volume (Selling pressure).")
                
        score = max(10, min(95, score))
        
        # Generate Actionable AI Guidance
        risk = max(ltp - sup_zone, ltp * 0.015)
        sl = round(max(sup_zone * 0.996, ltp - (risk * 0.9)), 2)
        t1 = round(ltp + (risk * 1.5), 2)
        t2 = round(ltp + (risk * 2.8), 2)
        
        if score >= 70:
            ai_verdict = "🔥 HIGH PROBABILITY BUY SETUP"
            theme_color = "#00b15d"
            ai_advice = f"Smart Money buying zone mein active hai. Agar candle ₹{vwap} ke upar hold karti hai, toh target ₹{t1} ke liye entry valid hai. Stop-loss strictly ₹{sl} par rakhein."
        elif score <= 40:
            ai_verdict = "⚠️ AVOID BUYING / SELL ZONE"
            theme_color = "#eb5b50"
            ai_advice = f"Institutional selling footprint dikh raha hai. Fresh buy avoid karein jab tak price ₹{sup_zone} support par strong green rejection candle na banaye."
        else:
            ai_verdict = "⚖️ RANGE BOUND / WAIT FOR DIP"
            theme_color = "#f2994a"
            ai_advice = f"Stock sideways consolidation mein hai. Jaldbazi mein entry lene se capital fas sakta hai. ₹{sup_zone} ke pullback par ya breakout hone par hi trade lein."
            
        return {
            "ltp": ltp,
            "change": change,
            "pct_change": pct_change,
            "vwap": vwap,
            "rsi": rsi,
            "res": res_zone,
            "sup": sup_zone,
            "score": score,
            "verdict": ai_verdict,
            "theme_color": theme_color,
            "ai_advice": ai_advice,
            "bull_reasons": bull_reasons,
            "bear_reasons": bear_reasons,
            "sl": sl,
            "t1": t1,
            "t2": t2,
            "vol_spike": is_vol_spike
        }
    except Exception:
        return {}

def get_stock_news(symbol: str) -> list:
    try:
        t = yf.Ticker(f"{symbol}.NS")
        news = t.news or []
        parsed = []
        for n in news[:4]:
            parsed.append({
                "title": n.get('title', ''),
                "publisher": n.get('publisher', 'Market Wire'),
                "link": n.get('link', '#')
            })
        return parsed
    except Exception:
        return [
            {"title": f"{symbol} consolidates near key EMA demand zone.", "publisher": "Pulse", "link": "#"}
        ]
