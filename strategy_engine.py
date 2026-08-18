import yfinance as yf
import pandas as pd
import numpy as np

# Popular Stock Directory with friendly names
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
    "GRASIM IND. (GRASIM)": "GRASIM",
    "JSW STEEL (JSWSTEEL)": "JSWSTEEL",
    "HINDALCO (HINDALCO)": "HINDALCO",
    "VEDANTA (VEDL)": "VEDL",
    "ZOMATO (ZOMATO)": "ZOMATO",
    "JIO FINANCIAL (JIOFIN)": "JIOFIN",
    "PAYTM (PAYTM)": "PAYTM",
    "IRCTC (IRCTC)": "IRCTC",
    "HAL (HAL)": "HAL",
    "BEL (BEL)": "BEL",
    "BHEL (BHEL)": "BHEL",
    "REC LTD (RECLTD)": "RECLTD",
    "PFC (PFC)": "PFC",
    "DLF LTD (DLF)": "DLF",
    "TRENT (TRENT)": "TRENT",
    "VARUN BEVERAGES (VBL)": "VBL",
    "SUZLON ENERGY (SUZLON)": "SUZLON"
}

def fetch_stock_data(ticker_symbol: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    ticker = ticker_symbol.strip().upper().replace(" ", "")
    candidates = [f"{ticker}.NS", f"{ticker}.BO", ticker]
    for symbol in candidates:
        try:
            df = yf.download(symbol, period=period, interval=interval, progress=False)
            if not df.empty and len(df) > 15:
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [col[0] for col in df.columns]
                df.dropna(inplace=True)
                return df
        except Exception:
            continue
    return pd.DataFrame()

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or len(df) < 25:
        return df
    df = df.copy()
    
    # Fast / Slow Moving Averages
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    
    # RSI (14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss.replace(0, np.nan)
    df['RSI'] = (100 - (100 / (1 + rs))).fillna(50)
    
    # Volatility (ATR)
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR_14'] = tr.rolling(window=14).mean()

    # Dynamic Support & Resistance
    df['Swing_High_20'] = df['High'].rolling(window=20).max()
    df['Swing_Low_20'] = df['Low'].rolling(window=20).min()
    
    return df

def identify_candlestick_patterns(df: pd.DataFrame) -> dict:
    if len(df) < 3:
        return {"pattern": "Neutral Base", "bias": "Neutral", "detail": "Normal price movement."}
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    o, h, l, c = float(latest['Open']), float(latest['High']), float(latest['Low']), float(latest['Close'])
    po, ph, pl, pc = float(prev['Open']), float(prev['High']), float(prev['Low']), float(prev['Close'])
    
    body = abs(c - o)
    candle_range = h - l if (h - l) > 0 else 0.01
    lower_wick = min(o, c) - l
    upper_wick = h - max(o, c)
    
    # Hammer
    if lower_wick >= (1.8 * body) and upper_wick <= (0.3 * body) and c >= o:
        return {"pattern": "Bullish Hammer 🔨", "bias": "Bullish", "detail": "Rejection from lows; strong buying pressure detected."}
    
    # Shooting Star
    if upper_wick >= (1.8 * body) and lower_wick <= (0.3 * body) and c <= o:
        return {"pattern": "Shooting Star ⚡", "bias": "Bearish", "detail": "Rejection from top; heavy selling pressure at resistance."}
    
    # Engulfing
    if pc < po and c > o and c >= ph and o <= pc:
        return {"pattern": "Bullish Engulfing 🟢", "bias": "Bullish", "detail": "Buyers fully overrode the previous session selloff."}
    if pc > po and c < o and c <= pl and o >= pc:
        return {"pattern": "Bearish Engulfing 🔴", "bias": "Bearish", "detail": "Sellers completely crushed the previous session rally."}
    
    if body >= (0.75 * candle_range):
        return {"pattern": "Power Momentum Candle 🚀" if c > o else "Heavy Breakdown Candle ⚠️", 
                "bias": "Bullish" if c > o else "Bearish", 
                "detail": "Institutional volume driven one-way move."}
            
    return {"pattern": "Consolidation Range", "bias": "Neutral", "detail": "Balanced buyers & sellers. Waiting for clear direction."}

def generate_trade_signal(df: pd.DataFrame) -> dict:
    if df.empty or len(df) < 25:
        return {"status": "INSUFFICIENT_DATA"}
        
    latest = df.iloc[-1]
    close = float(latest['Close'])
    ema20 = float(latest['EMA_20'])
    ema50 = float(latest['EMA_50']) if not np.isnan(latest['EMA_50']) else ema20
    rsi = float(latest['RSI'])
    atr = float(latest['ATR_14']) if not np.isnan(latest['ATR_14']) else (close * 0.02)
    
    res_zone = float(latest['Swing_High_20'])
    sup_zone = float(latest['Swing_Low_20'])
    candle_data = identify_candlestick_patterns(df)
    
    # 4 Key Action Scenarios
    scenarios = [
        {
            "tag": "BUY",
            "title": "Fresh Breakout Entry",
            "level": f"Above ₹{res_zone * 1.002:.2f}",
            "desc": f"Buy only if candle closes above 20D Resistance (₹{res_zone:.2f}) with volume.",
            "target": f"₹{res_zone + (2.0 * atr):.2f}"
        },
        {
            "tag": "DIP",
            "title": "Dip / Support Reversal",
            "level": f"Near ₹{max(ema20, sup_zone):.2f}",
            "desc": f"Accumulate on pullback near 20 EMA / Support on bullish candle confirmation.",
            "sl": f"₹{max(ema20, sup_zone) - (1.2 * atr):.2f}"
        },
        {
            "tag": "EXIT",
            "title": "Resistance / Profit Booking",
            "level": f"Near ₹{res_zone:.2f}",
            "desc": f"Major barrier zone. If RSI > 70 and top wick forms, book profit or trail SL.",
            "action": "Avoid fresh aggressive buying"
        },
        {
            "tag": "TRAP",
            "title": "Breakdown / Danger Zone",
            "level": f"Below ₹{sup_zone:.2f}",
            "desc": f"Breakdown below swing support indicates risk of sharp fall.",
            "action": "Strict Exit / No Longs"
        }
    ]
    
    # Verdict Logic
    score = 0
    if close > ema20 and ema20 >= ema50: score += 40
    if 50 <= rsi <= 68: score += 30
    if candle_data['bias'] == "Bullish": score += 30
    
    if score >= 70:
        verdict = "STRONG BUY SETUP"
        badge_color = "#00C087"
    elif close < ema20 and rsi < 45:
        verdict = "AVOID / WEAK TREND"
        badge_color = "#EB5757"
    else:
        verdict = "SIDEWAYS / WAIT FOR DIP"
        badge_color = "#F2994A"

    stop_loss = round(min(close - (1.5 * atr), sup_zone * 0.995), 2)
    risk = max(close - stop_loss, close * 0.02)
    
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
