
AI Trade Master — Mobile-friendly Paper Trading prototype

WHAT IT DOES
- Downloads market candles via Yahoo Finance (third-party feed; may be delayed/incomplete).
- Calculates EMA20, EMA50, RSI, MACD, rolling 20-candle breakout/breakdown and volume confirmation.
- Displays a simple educational signal and illustrative risk-based paper position size.
- Supports Nifty, Bank Nifty, selected NSE stocks, Gold Futures (GC=F), Bitcoin (BTC-USD).

IMPORTANT LIMITATIONS
- Paper-analysis prototype only. It does NOT connect to Zerodha, Angel One or Groww.
- It does NOT place, modify, or exit real orders.
- Signals are simple rules, not a validated predictive AI model. No profit is guaranteed.
- Do not use screenshots or this demo alone to trade real money.
- Intraday 5-minute data from Yahoo Finance can be delayed, restricted or unavailable.
- Gold ticker GC=F is a US gold futures reference, not Indian MCX Gold.
- Crypto symbol BTC-USD is a USD reference, not necessarily the exchange/pair you trade.

RUN
1. Install Python 3.10+ on a computer/server.
2. In this folder run: pip install -r requirements.txt
3. Run: streamlit run app.py

MOBILE DEPLOYMENT (no local Python needed)
- Create a GitHub account and upload app.py and requirements.txt to a new repository.
- On Streamlit Community Cloud, create an app from that repository and select app.py.
- Open the generated app URL on your Android phone.
- Free hosting/data availability can change; the app may sleep when unused.

NEXT SAFE DEVELOPMENT STEPS
1. Add reliable broker/exchange market data.
2. Add historical backtesting with brokerage, taxes, slippage and out-of-sample tests.
3. Run paper trading for several weeks.
4. Only then consider broker API integration with explicit risk limits and manual approval.
Never share broker passwords, OTPs, API secrets or TOTP seeds in chat.
