import yfinance as yf
import pandas as pd
import numpy as np

def calculate_smc_levels(df):
    """
    Computes Institutional SMC metrics: Order Blocks, Liquidity Sweeps, VWAP, Delivery Footprints
    """
    if df is None or len(df) < 15:
        return {}
    
    # VWAP Calculation
    cum_vol = df['Volume'].cumsum()
    cum_vol_price = (df['Close'] * df['Volume']).cumsum()
    vwap = cum_vol_price / cum_vol
    current_vwap = round(vwap.iloc[-1], 2)
    
    # Demand & Supply Clusters
    high_cluster = round(df['High'].max(), 2)
    low_cluster = round(df['Low'].min(), 2)
    current_close = round(df['Close'].iloc[-1], 2)
    
    # Order Block detection (Institutional Demand floor & Supply ceiling)
    recent_swings_low = df['Low'].rolling(window=10).min().iloc[-1]
    recent_swings_high = df['High'].rolling(window=10).max().iloc[-1]
    
    # Volume Spread Analysis (VSA)
    avg_vol = df['Volume'].tail(20).mean()
    last_vol = df['Volume'].iloc[-1]
    vol_surge_ratio = round(last_vol / avg_vol, 2) if avg_vol > 0 else 1.0
    
    # Trap / Sweep detection
    prev_high = df['High'].iloc[-2]
    prev_low = df['Low'].iloc[-2]
    is_liquidity_sweep = False
    sweep_type = "None"
    
    if df['High'].iloc[-1] > prev_high and df['Close'].iloc[-1] < prev_high:
        is_liquidity_sweep = True
        sweep_type = "🔴 Bearish Liquidity Sweep (Retail Buy Trap detected at Highs)"
    elif df['Low'].iloc[-1] < prev_low and df['Close'].iloc[-1] > prev_low:
        is_liquidity_sweep = True
        sweep_type = "🟢 Bullish Liquidity Sweep (Retail Stop-Hunt at Lows -> Reversal Setup)"
        
    return {
        "current_price": current_close,
        "vwap": current_vwap,
        "demand_zone": round(recent_swings_low, 2),
        "supply_zone": round(recent_swings_high, 2),
        "range_52w_high": high_cluster,
        "range_52w_low": low_cluster,
        "vol_surge_ratio": vol_surge_ratio,
        "is_liquidity_sweep": is_liquidity_sweep,
        "sweep_type": sweep_type
    }

def generate_hedging_strategies(cmp, bias="BULLISH"):
    """
    Generates Multi-leg options hedging parameters with strike selection and defined payoff
    """
    base_strike = round(cmp / 10) * 10 if cmp > 100 else round(cmp)
    
    if bias == "BULLISH":
        return {
            "strategy": "Bull Call Spread (Defined Risk)",
            "bias_badge": "🟢 MODERATELY BULLISH",
            "leg1": f"Buy ATM Call Strike: ₹{base_strike} CE",
            "leg2": f"Sell OTM Call Strike (Hedge): ₹{base_strike + 10} CE",
            "max_risk": "Strictly limited to Net Premium Paid (~1.5% - 2%)",
            "max_reward": "Capped at Strike Width - Net Premium (~1:2.4 R:R)",
            "theta_impact": "Protected (Sold Call reduces time decay burn)",
            "advice": "Ideal for swing upside without overnight gap-down risk."
        }
    elif bias == "BEARISH":
        return {
            "strategy": "Bear Put Spread (Downside Shield)",
            "bias_badge": "🔴 MODERATELY BEARISH",
            "leg1": f"Buy ATM Put Strike: ₹{base_strike} PE",
            "leg2": f"Sell OTM Put Strike (Hedge): ₹{base_strike - 10} PE",
            "max_risk": "Strictly limited to Net Debit",
            "max_reward": "Capped at Difference between strikes",
            "theta_impact": "Shielded against IV crush",
            "advice": "Best for high volatility breakdown protection."
        }
    else:
        return {
            "strategy": "Short Iron Condor / Range Bound Play",
            "bias_badge": "🟡 SIDEWAYS / CONSOLIDATION",
            "leg1": f"Sell ₹{base_strike + 10} CE & Buy ₹{base_strike + 20} CE",
            "leg2": f"Sell ₹{base_strike - 10} PE & Buy ₹{base_strike - 20} PE",
            "max_risk": "Defined wing spread difference",
            "max_reward": "100% Net Credit collected on range retention",
            "theta_impact": "Max Positive Theta (Time decay works for you)",
            "advice": "High probability win rate when stock is in consolidation."
        }
