import yfinance as yf
import pandas as pd
import numpy as np

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
    
    # EMAs
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    df['EMA_50'] = df['Close'].ewm(span=50, adjust=False).mean()
    df['EMA_200'] = df['Close'].ewm(span=200, adjust=False).mean()
    
    # RSI (14)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss.replace(0, np.nan)
    df['RSI'] = (100 - (100 / (1 + rs))).fillna(50)
    
    # MACD (12, 26, 9)
    exp12 = df['Close'].ewm(span=12, adjust=False).mean()
    exp26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = exp12 - exp26
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

    # Volume & Volatility (ATR)
    df['Vol_SMA_20'] = df['Volume'].rolling(window=20).mean()
    high_low = df['High'] - df['Low']
    high_close = (df['High'] - df['Close'].shift()).abs()
    low_close = (df['Low'] - df['Close'].shift()).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR_14'] = tr.rolling(window=14).mean()

    # Dynamic Support & Resistance (Swing Pivots)
    df['Swing_High_20'] = df['High'].rolling(window=20).max()
    df['Swing_Low_20'] = df['Low'].rolling(window=20).min()
    
    return df

def identify_candlestick_patterns(df: pd.DataFrame) -> dict:
    if len(df) < 3:
        return {"pattern": "Standard Candle", "bias": "Neutral"}
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    o, h, l, c = float(latest['Open']), float(latest['High']), float(latest['Low']), float(latest['Close'])
    po, ph, pl, pc = float(prev['Open']), float(prev['High']), float(prev['Low']), float(prev['Close'])
    
    body = abs(c - o)
    candle_range = h - l if (h - l) > 0 else 0.01
    lower_wick = min(o, c) - l
    upper_wick = h - max(o, c)
    
    # Hammer / Pinbar
    if lower_wick >= (1.8 * body) and upper_wick <= (0.3 * body) and c >= o:
        return {"pattern": "Bullish Hammer / Pin Bar", "bias": "Strong Bullish Reversal", "note": "Rejection from lows with heavy buyer support."}
    
    # Shooting Star / Inverted Pinbar
    if upper_wick >= (1.8 * body) and lower_wick <= (0.3 * body) and c <= o:
        return {"pattern": "Bearish Shooting Star", "bias": "Bearish Rejection", "note": "Failed to sustain highs; seller rejection at peak."}
    
    # Bullish Engulfing
    if pc < po and c > o and c >= ph and o <= pc:
        return {"pattern": "Bullish Engulfing", "bias": "Strong Bullish", "note": "Buyers fully overpower sellers from previous session."}
    
    # Bearish Engulfing
    if pc > po and c < o and c <= pl and o >= pc:
        return {"pattern": "Bearish Engulfing", "bias": "Strong Bearish", "note": "Sellers wiped out previous candle gains completely."}
    
    # Strong Momentum Marubozu Candle
    if body >= (0.75 * candle_range):
        if c > o:
            return {"pattern": "Bullish Marubozu (Power Candle)", "bias": "Bullish Continuation", "note": "Pure buying power with minimal wicks."}
        else:
            return {"pattern": "Bearish Marubozu (Heavy Selling)", "bias": "Bearish Continuation", "note": "Aggressive institutional selloff."}
            
    return {"pattern": "Consolidation Candle", "bias": "Rangebound", "note": "Balanced buying & selling; wait for range break."}

def generate_trade_signal(df: pd.DataFrame) -> dict:
    if df.empty or len(df) < 25:
        return {"status": "INSUFFICIENT_DATA"}
        
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    close = float(latest['Close'])
    ema20 = float(latest['EMA_20'])
    ema50 = float(latest['EMA_50']) if not np.isnan(latest['EMA_50']) else ema20
    rsi = float(latest['RSI'])
    volume = float(latest['Volume'])
    vol_avg = float(latest['Vol_SMA_20']) if not np.isnan(latest['Vol_SMA_20']) else volume
    atr = float(latest['ATR_14']) if not np.isnan(latest['ATR_14']) else (close * 0.02)
    
    res_zone = float(latest['Swing_High_20'])
    sup_zone = float(latest['Swing_Low_20'])
    candle_data = identify_candlestick_patterns(df)
    
    # Key 4 Trading Action Zones
    scenarios = {
        "breakout_buy": {
            "title": "⚡ 1. Fresh Breakout Buy Entry",
            "price_level": round(res_zone * 1.002, 2),
            "condition": f"Enter only if daily/1H candle closes decisively above resistance ₹{res_zone:.2f} with volume > 1.2x avg.",
            "target": round(res_zone + (2.0 * atr), 2)
        },
        "dip_buy": {
            "title": "🟢 2. Dip Accumulation (Reversal Entry)",
            "price_level": round(max(ema20, sup_zone), 2),
            "condition": f"Buy on pullback near 20 EMA / Support (₹{max(ema20, sup_zone):.2f}) if a Bullish Hammer or Green candle forms.",
            "stop_loss": round(max(ema20, sup_zone) - (1.2 * atr), 2)
        },
        "profit_zone": {
            "title": "🔴 3. Reversal / Profit Booking Zone",
            "price_level": round(res_zone, 2),
            "condition": f"Strong Resistance at ₹{res_zone:.2f}. If RSI reaches 70+ and wick rejection appears, trail stop-loss or book profits.",
            "action": "Avoid fresh buy here / Exit longs"
        },
        "trap_zone": {
            "title": "⚠️ 4. Danger / Breakdown Trap Zone",
            "price_level": round(sup_zone, 2),
            "condition": f"If price breaks below ₹{sup_zone:.2f} and 50 EMA, trend flips bearish. Strict no-entry zone for longs.",
            "action": "High risk of deep correction down to lower demand"
        }
    }
    
    # Scoring Matrix
    score = 0
    reasons = []
    if close > ema20 and ema20 >= ema50:
        score += 30
        reasons.append("Bullish Trend Structure: Price is holding above 20 & 50 EMA")
    if 50 <= rsi <= 68:
        score += 25
        reasons.append(f"Clean Momentum: RSI at {rsi:.1f} (Balanced, not overbought)")
    if volume >= (1.1 * vol_avg):
        score += 20
        reasons.append(f"Volume Confluence: Activity is {(volume/vol_avg):.2f}x of 20-day average")
    if "Bullish" in candle_data['bias']:
        score += 25
        reasons.append(f"Candlestick Trigger: {candle_data['pattern']} detected")

    signal_status = "STRONG BUY SETUP" if score >= 60 else ("AVOID / BEARISH" if close < ema20 and rsi < 45 else "WATCHLIST / DIP WAITING")
    
    stop_loss = round(min(close - (1.5 * atr), sup_zone * 0.995), 2)
    risk = max(close - stop_loss, close * 0.02)
    
    return {
        "status": "SIGNAL_GENERATED",
        "signal": signal_status,
        "confidence_score": score,
        "entry_price": round(close, 2),
        "stop_loss": stop_loss,
        "target_1": round(close + (risk * 1.5), 2),
        "target_2": round(close + (risk * 2.8), 2),
        "risk_per_share": round(risk, 2),
        "reasons": reasons,
        "candle_data": candle_data,
        "scenarios": scenarios,
        "rsi": round(rsi, 2),
        "ema20": round(ema20, 2),
        "ema50": round(ema50, 2),
        "resistance": round(res_zone, 2),
        "support": round(sup_zone, 2),
        "volume_ratio": round(volume / vol_avg, 2) if vol_avg > 0 else 1.0
    }