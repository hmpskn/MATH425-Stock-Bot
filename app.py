import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Page Configuration
st.set_page_config(page_title="MATH 425 Final Project Bot", layout="wide")

# Header
st.title("📈 MATH 425: Algorithmic Trading Simulation")
#st.markdown("### Final Project")
st.write("An advanced simulation platform evaluating Moving Average Crossovers and Risk Metrics.")

# Sidebar
st.sidebar.header("User Input & Strategy")
ticker = st.sidebar.text_input("Stock Ticker", "AAPL")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))
short_window = st.sidebar.slider("Short-term SMA", 5, 50, 20)
long_window = st.sidebar.slider("Long-term SMA", 50, 250, 100)

if st.sidebar.button("Run Comprehensive Analysis"):
    # 1. DATA COLLECTION
    data = yf.download(ticker, start=start_date)
    
    # 2. CALCULATIONS
    data['Short_SMA'] = data['Close'].rolling(window=short_window).mean()
    data['Long_SMA'] = data['Close'].rolling(window=long_window).mean()
    
    # RSI Calculation
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # 3. STRATEGY & RETURNS
    data['Signal'] = np.where(data['Short_SMA'] > data['Long_SMA'], 1.0, 0.0)
    data['Position'] = data['Signal'].diff()
    data['Market_Returns'] = data['Close'].pct_change()
    data['Strategy_Returns'] = data['Market_Returns'] * data['Signal'].shift(1)
    
    data['Market_Wealth'] = 100 * (1 + data['Market_Returns']).cumprod()
    data['Strategy_Wealth'] = 100 * (1 + data['Strategy_Returns']).cumprod()
    
    # 4. METRICS
    col1, col2, col3, col4 = st.columns(4)
    final_bot = data['Strategy_Wealth'].iloc[-1]
    final_mkt = data['Market_Wealth'].iloc[-1]
    peak = data['Strategy_Wealth'].cummax()
    max_dd = ((data['Strategy_Wealth'] - peak) / peak).min()
    
    col1.metric("Bot Final Value", f"${final_bot:.2f}")
    col2.metric("Market Final Value", f"${final_mkt:.2f}")
    col3.metric("Bot Total Return", f"{((final_bot/100)-1)*100:.1f}%")
    col4.metric("Max Drawdown", f"{max_dd*100:.1f}%")

    # 5. CHARTS
    st.subheader("Performance & Indicators")
    tab1, tab2 = st.tabs(["Performance Graph", "RSI Analysis"])
    
    with tab1:
        fig1, ax1 = plt.subplots(figsize=(12, 5))
        ax1.plot(data['Strategy_Wealth'], label="Bot Strategy", color='#1f77b4', lw=2)
        ax1.plot(data['Market_Wealth'], label="Market (Buy & Hold)", color='#7f7f7f', alpha=0.5)
        ax1.set_title("Equity Curve Comparison")
        ax1.legend()
        st.pyplot(fig1)

    with tab2:
        fig2, ax2 = plt.subplots(figsize=(12, 3))
        ax2.plot(data['RSI'], color='purple')
        ax2.axhline(70, color='red', linestyle='--', alpha=0.5)
        ax2.axhline(30, color='green', linestyle='--', alpha=0.5)
        ax2.set_title("Momentum Indicator (RSI)")
        st.pyplot(fig2)

    # 6. TRADE LOG & DOWNLOAD
    st.subheader("Detailed Trade Log")
    trades = data[data['Position'] != 0][['Close', 'Position']]
    trades['Action'] = trades['Position'].apply(lambda x: 'BUY' if x == 1 else 'SELL')
    st.dataframe(trades[['Close', 'Action']].tail(10))
    
    csv = data.to_csv().encode('utf-8')
    st.download_button("Download Full Analysis Data (CSV)", csv, "analysis.csv", "text/csv")
    
    st.success("Full analysis completed for IEU MATH 425 Project.")
