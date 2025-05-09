import streamlit as st
import pandas as pd
import numpy as np
import ta
from binance.client import Client
import datetime
Binance API keys (for public data only, no need for keys)

client = Client()

Title

st.title("Bitcoin 10-Minute Price Predictor (Free)")

Load 1-day 10-minute BTCUSDT data

@st.cache_data

def load_data(): klines = client.get_historical_klines("BTCUSDT", Client.KLINE_INTERVAL_10MINUTE, "1 day ago UTC") df = pd.DataFrame(klines, columns=[ 'time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore' ]) df = df[['time', 'open', 'high', 'low', 'close', 'volume']].astype(float) df['timestamp'] = pd.to_datetime(df['time'], unit='ms') df.set_index('timestamp', inplace=True) return df

df = load_data()

Convert columns to numeric

for col in ['open', 'high', 'low', 'close', 'volume']: df[col] = pd.to_numeric(df[col], errors='coerce')

Add indicators

df['rsi'] = ta.momentum.RSIIndicator(close=df['close']).rsi() df['ema_50'] = ta.trend.EMAIndicator(close=df['close'], window=50).ema_indicator() df['ema_200'] = ta.trend.EMAIndicator(close=df['close'], window=200).ema_indicator() df['macd_diff'] = ta.trend.MACD(close=df['close']).macd_diff()

Support/Resistance (basic pivot logic)

def get_support_resistance(data, window=5): support = data['low'].rolling(window, center=True).min() resistance = data['high'].rolling(window, center=True).max() return support, resistance

df['support'], df['resistance'] = get_support_resistance(df)

Dummy signal logic (placeholder for ML model)

def generate_signal(row): if row['close'] > row['ema_50'] and row['rsi'] > 50 and row['macd_diff'] > 0: return "YES" elif row['rsi'] < 30 or row['macd_diff'] < 0: return "NO" else: return "SKIP"

df['signal'] = df.apply(generate_signal, axis=1)

Latest signal

latest = df.iloc[-1] prediction = latest['signal']

Display prediction

st.subheader("Next 10-Minute Prediction:") st.metric(label="Signal", value=prediction) st.metric(label="Current Price", value=f"${latest['close']:.2f}")

Plot chart

st.line_chart(df[['close', 'ema_50', 'ema_200']].dropna()) st.line_chart(df[['rsi', 'macd_diff']].dropna())

Show recent data

if st.checkbox("Show Raw Data"): st.write(df.tail())
