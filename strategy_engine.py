import yfinance as yf
import pandas as pd
import numpy as np

# Popular Stock Directory
STOCK_MAP = {
    "TATA MOTORS (TATAMOTORS)": "TATAMOTORS",
    "RELIANCE IND. (RELIANCE)": "RELIANCE",
    "HDFC BANK (HDFCBANK)": "HDFCBANK",
    "ICICI BANK (ICICIBANK)": "ICICIBANK",
    "INFOSYS (INFY)": "INFY",
    "STATE BANK OF INDIA (SBIN)": "SBIN",
    "TATA CONSULTANCY (TCS)": "TCS",
    "TATA STEEL (TATASTEEL)": "TATASTEEL",
    "TATA POWER (TATAPOWER)": "TATAPOWER",
    "ITC LTD (ITC)": "ITC",
    "BHARTI AIRTEL (BHARTIARTL)": "BHARTIARTL",
    "LARSEN & TOUBRO (LT)": "LT",
    "KOTAK MAHINDRA (KOTAKBANK)": "KOTAKBANK",
    "AXIS BANK (AXISBANK)": "AXISBANK",
    "HINDUSTAN UNILEVER (HINDUNILVR)": "HINDUNILVR",
    "BAJAJ FINANCE (BAJFINANCE)": "BAJFINANCE",
    "BAJAJ FINSERV (BAJAJFINSV)": "BAJAJFINSV",
    "MARUTI SUZUKI (MARUTI)": "MARUTI",
    "MAHINDRA & MAHINDRA (M&M)": "M&M",
    "SUN PHARMA (SUNPHARMA)": "SUNPHARMA",
    "ASIAN PAINTS (ASIANPAINT)": "ASIANPAINT",
    "TITAN COMPANY (TITAN)": "TITAN",
    "ADANI ENTERPRISES (ADANIENT)": "ADANIENT",
    "ADANI PORTS (ADANIPORTS)": "ADANIPORTS",
    "ADANI POWER (ADANIPOWER)": "ADANIPOWER",
    "NTPC (NTPC)": "NTPC",
    "POWER GRID (POWERGRID)": "POWERGRID",
    "COAL INDIA (COALINDIA)": "COALINDIA",
    "ONGC (ONGC)": "ONGC",
    "WIPRO (WIPRO)": "WIPRO",
    "HCL TECH (HCLTECH)": "HCLTECH",
    "TECH MAHINDRA (TECHM)": "TECHM",
    "ULTRA TECH CEMENT (ULTRACEMCO)": "ULTRACEMCO",
    "JSW STEEL (JSWSTEEL)": "JSWSTEEL",
    "VEDANTA (VEDL)": "VEDL",
    "ZOMATO (ZOMATO)": "ZOMATO",
    "JIO FINANCIAL (JIOFIN)": "JIOFIN",
    "IRCTC (IRCTC)": "IRCTC",
    "HAL (HAL)": "HAL",
    "BEL (BEL)": "BEL",
    "SUZLON ENERGY (SUZLON)": "SUZLON"
}

def fetch_stock_data(ticker_symbol: str, period: str = "1mo", interval: str = "15m") -> pd.DataFrame:
    ticker = ticker_symbol.strip().upper().replace(" ", "")
    candidates = [f"{ticker}.NS", f"{ticker}.BO", ticker]
    
    for symbol in candidates:
        try:
            t = yf.Ticker(symbol)
            df = t.history(period=period, interval=interval)
            
            # Agar intraday data fail ho toh daily par fallback karein
            if df.empty and interval not in ["1d", "1wk"]:
                df = t.history(period="6mo", interval="1d")
                
            if not df.empty and len(df) > 5:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [col[0] for col in df.columns]
                df.dropna(inplace=True)
                return df
        except Exception:
            continue
            
    # Direct yf.download fallback
    for symbol in candidates:
        try:
            df = yf.download(symbol, period=period, interval=interval, progress=False)
            if not df.empty and len(df) > 5:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [col[0] for col in df.columns]
                df.dropna(inplace=True)
                return df
        except Exception:
            continue
            
    return pd.DataFrame()

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or len(df) < 5:
        return df
    df = df.copy()
    
    # EMAs
    span_fast = min(20, len(df))
    span_slow = min(50, len(df))
    df['EMA_20'] = df['Close'].ewm(span=span_fast, adjust=False).mean()
    df['EMA_50'] = df['Close'].ewm(span=span_slow, adjust=False).mean()
    
    # RSI (14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=5).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=5).mean()
    rs = gain / loss.replace(0, np.nan)
    df['RSI'] = (100 - (100 / (1 + rs))).fillna(50)
    
    # Volatility (ATR)
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR_14'] = tr.rolling(window=14, min_periods=5).mean().fillna(df['Close'] * 0.015)

    # Dynamic Support & Resistance
    lookback = min(20, len(df))
    df['Swing_High_20'] = df['High'].rolling(window=lookback, min_periods=5).max()
    df['Swing_Low_20'] = df['Low'].rolling(window=lookback, min_periods=5).min()
    
    return df

def identify_candlestick_patterns(df: pd.DataFrame) -> dict:
    if len(df) < 2:
        return {"pattern": "Neutral Base", "bias": "Neutral", "detail": "Normal price action."}
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    o, h, l, c = float(latest['Open']), float(latest['High']), float(latest['Low']), float(latest['Close'])
    po, ph, pl, pc = float(prev['Open']), float(prev['High']), float(prev['Low']), float(prev['Close'])
    
    body = abs(c - o)
    candle_range = h - l if (h - l) > 0 else 0.01
    lower_wick = min(o, c) - l
    upper_wick = h - max(o, c)
    
    if lower_wick >= (1.5 * body) and upper_wick <= (0.4 * body) and c >= o:
        return {"pattern": "Bullish Hammer 🔨", "bias": "Bullish", "detail": "Lows se strong buyer support aya hai."}
    
    if upper_wick >= (1.5 * body) and lower_wick <= (0.4 * body) and c <= o:
        return {"pattern": "Shooting Star ⚡", "bias": "Bearish", "detail": "Highs par sellers ka heavy pressure hai."}
    
    if pc < po and c > o and c >= ph and o <= pc:
        return {"pattern": "Bullish Engulfing 🟢", "bias": "Bullish", "detail": "Buyers ne previous candle ka selling pressure cover kar liya."}
    if pc > po and c < o and c <= pl and o >= pc:
        return {"pattern": "Bearish Engulfing 🔴", "bias": "Bearish", "detail": "Sellers ne pichle candle ke gains ko wipe out kar diya."}
    
    if body >= (0.70 * candle_range):
        return {"pattern": "Momentum Green Candle 🚀" if c > o else "Breakdown Red Candle ⚠️", 
                "bias": "Bullish" if c > o else "Bearish", 
                "detail": "One-sided decisive price momentum."}
            
    return {"pattern": "Normal Candle Range", "bias": "Neutral", "detail": "Sideways market, clear candle trigger ka wait karein."}

def generate_trade_signal(df: pd.DataFrame) -> dict:
    if df.empty or len(df) < 5:
        return {"status": "INSUFFICIENT_DATA"}
        
    latest = df.iloc[-1]
    close = float(latest['Close'])
    ema20 = float(latest['EMA_20']) if not np.isnan(latest['EMA_20']) else close
    ema50 = float(latest['EMA_50']) if not np.isnan(latest['EMA_50']) else ema20
    rsi = float(latest['RSI'])
    atr = float(latest['ATR_14']) if not np.isnan(latest['ATR_14']) else (close * 0.015)
    
    res_zone = float(latest['Swing_High_20']) if not np.isnan(latest['Swing_High_20']) else close * 1.02
    sup_zone = float(latest['Swing_Low_20']) if not np.isnan(latest['Swing_Low_20']) else close * 0.98
    candle_data = identify_candlestick_patterns(df)
    
    scenarios = [
        {
            "tag": "BUY",
            "title": "⚡ 1. Fresh Breakout Entry",
            "level": f"Above ₹{res_zone * 1.001:.2f}",
            "desc": f"Buy tab karein jab candle resistance ₹{res_zone:.2f} ke upar close ho.",
            "target": f"₹{res_zone + (1.8 * atr):.2f}"
        },
        {
            "tag": "DIP",
            "title": "🟢 2. Dip / Support Reversal",
            "level": f"Near ₹{max(ema20, sup_zone):.2f}",
            "desc": f"Support/EMA zone par hammer ya green candle banne par buy karein.",
            "sl": f"₹{max(ema20, sup_zone) - (1.2 * atr):.2f}"
        },
        {
            "tag": "EXIT",
            "title": "🔴 3. Resistance / Exit Zone",
            "level": f"Near ₹{res_zone:.2f}",
            "desc": f"Ye strong rejection level hai. RSI > 70 par profit book ya SL trail karein.",
            "action": "Fresh buy avoid karein"
        },
        {
            "tag": "TRAP",
            "title": "⚠️ 4. Breakdown / Danger Zone",
            "level": f"Below ₹{sup_zone:.2f}",
            "desc": f"Agar ₹{sup_zone:.2f} ke neeche breakdown hota hai toh sharp fall aa sakta hai.",
            "action": "No Long Trades"
        }
    ]
    
    score = 0
    if close >= ema20: score += 40
    if 48 <= rsi <= 68: score += 30
    if candle_data['bias'] == "Bullish": score += 30
    
    if score >= 70:
        verdict = "STRONG BUY SETUP"
        badge_color = "#00C087"
    elif close < ema20 and rsi < 45:
        verdict = "AVOID / WEAK TREND"
        badge_color = "#EB5757"
    else:
        verdict = "WATCHLIST / WAIT FOR DIP"
        badge_color = "#F2994A"

    stop_loss = round(close - (1.3 * atr), 2)
    risk = max(close - stop_loss, close * 0.015)
    
    return {
        "status": "SIGNAL_GENERATED",
        "verdict": verdict,
        "badge_color": badge_color,
        "score": score,
        "ltp": round(close, 2),
        "stop_loss": stop_loss,
        "target_1": round(close + (risk * 1.5), 2),
        "target_2": round(close + (risk * 2.8), 2),
        "candle_data": candle_data,
        "scenarios": scenarios,
        "rsi": round(rsi, 1),
        "ema20": round(ema20, 2),
        "ema50": round(ema50, 2),
        "resistance": round(res_zone, 2),
        "support": round(sup_zone, 2)
    }
