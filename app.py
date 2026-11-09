
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta

st.set_page_config(page_title="AI Trade Master", page_icon="📈", layout="wide")
st.title("📈 AI Trade Master — Paper Trading")
st.caption("NSE stocks • Nifty • Gold • Bitcoin | Educational analysis only — no live orders")

st.warning("यह शुरुआती Paper Trading संस्करण है। यह आपके broker account में ऑर्डर नहीं लगाता। डेटा provider में देरी/गड़बड़ी हो सकती है; असली पैसे लगाने से पहले अलग से सत्यापन करें।")

DEFAULTS = {
    "Nifty 50": "^NSEI",
    "Bank Nifty": "^NSEBANK",
    "Reliance": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "Gold Futures": "GC=F",
    "Bitcoin": "BTC-USD",
}
with st.sidebar:
    st.header("सेटिंग")
    market = st.selectbox("Market", ["Swing (Daily)", "Intraday (5-minute)"])
    period = st.selectbox("इतिहास", ["1mo", "3mo", "6mo", "1y"], index=1)
    interval = "5m" if market.startswith("Intraday") else "1d"
    if interval == "5m":
        period = "5d"
    symbol_name = st.selectbox("Symbol", list(DEFAULTS.keys()) + ["अपना Symbol"])
    ticker = st.text_input("Yahoo Finance Symbol", value="") if symbol_name == "अपना Symbol" else DEFAULTS[symbol_name]
    capital = st.number_input("Paper capital (₹)", min_value=1000, value=100000, step=5000)
    risk_pct = st.slider("हर ट्रेड में जोखिम (%)", 0.25, 2.0, 1.0, 0.25)
    run = st.button("चार्ट का विश्लेषण करें", type="primary", use_container_width=True)

def get_data(sym, per, inter):
    df = yf.download(sym, period=per, interval=inter, auto_adjust=True, progress=False)
    if df is None or df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns=str.title)
    needed = ["Open", "High", "Low", "Close", "Volume"]
    if not all(c in df.columns for c in needed):
        return pd.DataFrame()
    return df[needed].dropna()

def analyze(df):
    x = df.copy()
    x["EMA20"] = x.Close.ewm(span=20, adjust=False).mean()
    x["EMA50"] = x.Close.ewm(span=50, adjust=False).mean()
    delta = x.Close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1/14, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    x["RSI"] = 100 - (100 / (1 + rs))
    x["VolAvg20"] = x.Volume.rolling(20).mean()
    x["High20"] = x.High.shift(1).rolling(20).max()
    x["Low20"] = x.Low.shift(1).rolling(20).min()
    x["MACD"] = x.Close.ewm(span=12, adjust=False).mean() - x.Close.ewm(span=26, adjust=False).mean()
    x["Signal"] = x.MACD.ewm(span=9, adjust=False).mean()
    last = x.iloc[-1]
    prev = x.iloc[-2] if len(x) > 1 else last
    bullish = last.Close > last.EMA20 > last.EMA50
    bearish = last.Close < last.EMA20 < last.EMA50
    breakout = pd.notna(last.High20) and last.Close > last.High20
    breakdown = pd.notna(last.Low20) and last.Close < last.Low20
    vol_ok = pd.notna(last.VolAvg20) and last.Volume > last.VolAvg20 * 1.5
    if breakout and vol_ok and last.RSI < 75:
        signal = "BUY SETUP (paper)"
        reason = "20-period high के ऊपर close और volume औसत से 1.5x से अधिक।"
    elif breakdown and vol_ok and last.RSI > 25:
        signal = "SELL / EXIT SETUP (paper)"
        reason = "20-period low के नीचे close और volume औसत से 1.5x से अधिक।"
    elif bullish and last.MACD > last.Signal:
        signal = "BULLISH — WAIT FOR ENTRY"
        reason = "Close EMA20/EMA50 के ऊपर और MACD bullish है; breakout confirmation नहीं।"
    elif bearish and last.MACD < last.Signal:
        signal = "BEARISH — AVOID LONG"
        reason = "Close EMA20/EMA50 के नीचे और MACD bearish है।"
    else:
        signal = "WAIT / NO CLEAR SETUP"
        reason = "मौजूदा नियमों के अनुसार स्पष्ट setup नहीं मिला।"
    return x, signal, reason

if run:
    with st.spinner("Market data लोड हो रहा है..."):
        data = get_data(ticker.strip(), period, interval)
    if data.empty or len(data) < 30:
        st.error("पर्याप्त डेटा नहीं मिला। Symbol जांचें या Daily timeframe चुनें। Yahoo Finance symbols में भारतीय शेयर के अंत में .NS लगाएं।")
    else:
        out, signal, reason = analyze(data)
        last = out.iloc[-1]
        a,b,c,d = st.columns(4)
        a.metric("Latest close", f"{last.Close:,.2f}")
        b.metric("RSI (14)", f"{last.RSI:.1f}" if pd.notna(last.RSI) else "N/A")
        c.metric("EMA 20", f"{last.EMA20:,.2f}")
        d.metric("EMA 50", f"{last.EMA50:,.2f}")
        st.subheader(f"Signal: {signal}")
        st.write(reason)
        st.caption(f"Data timestamp: {out.index[-1]} | Source: Yahoo Finance (third-party; may be delayed)")
        st.line_chart(out[["Close", "EMA20", "EMA50"]].tail(150))
        st.bar_chart(out["Volume"].tail(60))
        st.subheader("Recent candles")
        st.dataframe(out[["Open","High","Low","Close","Volume","RSI","MACD","Signal"]].tail(15), use_container_width=True)
        # Conservative illustrative paper position sizing only
        if "BUY SETUP" in signal:
            stop = min(last.Low, last.Close * 0.98)
            risk_per_unit = max(last.Close - stop, 0.01)
            risk_cash = capital * risk_pct / 100
            qty = int(risk_cash / risk_per_unit)
            target = last.Close + 2 * risk_per_unit
            st.info(f"Illustrative paper plan only — Entry reference: {last.Close:.2f} | Stop reference: {stop:.2f} | 2R target: {target:.2f} | Quantity by risk: {qty}")
        st.caption("यह सरल rule-based demo है, प्रशिक्षित/validated prediction model नहीं। Slippage, brokerage, taxes और liquidity शामिल नहीं हैं।")
else:
    st.info("बाईं तरफ Symbol और timeframe चुनें, फिर 'चार्ट का विश्लेषण करें' दबाएं।")
    st.markdown("""
    **शुरुआती symbols**
    - Nifty 50: `^NSEI`
    - Bank Nifty: `^NSEBANK`
    - Reliance: `RELIANCE.NS`
    - Gold Futures: `GC=F`
    - Bitcoin: `BTC-USD`

    **ध्यान दें:** Intraday 5-minute data सीमित/देरी से मिल सकता है। इस demo को live execution या guaranteed buy/sell signal न मानें।
    """)
