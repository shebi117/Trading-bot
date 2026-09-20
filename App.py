import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="Trading Signal Dashboard", layout="wide")
st.title("📈 Real-Time Trading Signal Dashboard")


def get_market_data(symbol="EURUSD=X"):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    data = response.json()
    prices = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
    return [p for p in prices if p is not None]


def calculate_rsi(prices, window=14):
    df = pd.DataFrame(prices, columns=["close"])
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=window - 1, adjust=False).mean()
    avg_loss = loss.ewm(com=window - 1, adjust=False).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    df["RSI"] = rsi.fillna(50)
    return df


symbol = st.selectbox(
    "Select Trading Pair", ["EURUSD=X", "GBPUSD=X", "USDJPY=X"]
)

if st.button("Refresh Live Signal"):
    prices = get_market_data(symbol)
    if prices:
        df = calculate_rsi(prices)
        latest_price = df["close"].iloc[-1]
        latest_rsi = df["RSI"].iloc[-1]

        col1, col2 = st.columns(2)
        col1.metric("Live Price", f"{latest_price:.5f}")
        col2.metric("RSI (14)", f"{latest_rsi:.2f}")

        if latest_rsi >= 70:
            st.error("🚨 Signal: OVERBOUGHT (SELL / PUT)")
        elif latest_rsi <= 30:
            st.success("🟢 Signal: OVERSOLD (BUY / CALL)")
        else:
            st.info("⚪ Signal: NEUTRAL (WAIT)")

        st.line_chart(df["RSI"].tail(30))
