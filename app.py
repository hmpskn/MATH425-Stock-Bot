import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Page Configuration
st.set_page_config(page_title="Advanced Stock Analysis Bot", layout="wide")

# Header Section
st.title("📈 MATH 425: Advanced Algorithmic Trading & Simulation")
#st.markdown("### Developed by: [Your Name] - [Your Student ID]")
st.write("An interactive simulation platform using Moving Average Crossovers and RSI indicators.")

# Sidebar Configuration
st.sidebar.header("Strategy Parameters")
ticker = st.sidebar.text_input("Stock Ticker", "AAPL")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))

# Dynamic Sliders for Interactive Analysis
short_window = st.sidebar.slider("Short-term SMA (Days)", 5, 50, 20)
long_window = st.sidebar.slider("Long-term SMA (Days)", 50, 250, 100)

if st.sidebar.button("Run Advanced Simulation"):
    # 1. DATA COLLECTION
    data = yf.download(ticker, start=start_date)
    
    # 2. MATHEMATICAL MODELING: SMAs
    data['Short_SMA'] = data['Close'].rolling(window=short_window).mean()
    data['Long_SMA'] = data['Close'].rolling(window=long_window).mean()
    
    # 3. RSI CALCULATION (Relative Strength Index)
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    
    # 4. TRADING STRATEGY
    data['Signal'] = np.where(data['Short_SMA'] > data['Long_SMA'], 1.0, 0.0)
    
    # 5. PERFORMANCE & RISK ANALYSIS
    data['Market_Returns'] = data['Close'].pct_change()
    data['Strategy_Returns'] = data['Market_Returns'] * data['Signal'].shift(1)
    
    data['Market_Wealth'] = 100 * (1 + data['Market_Returns']).cumprod()
    data['Strategy_Wealth'] = 100 * (1 + data['Strategy_Returns']).cumprod()
    
    # Risk Metric: Maximum Drawdown
    peak = data['Strategy_Wealth'].cummax()
    drawdown = (data['Strategy_Wealth'] - peak) / peak
    max_drawdown = drawdown.min()
    
    # 6. OUTPUT DISPLAY
    col1, col2, col3 = st.columns(3)
    col1.metric("Final Bot Value", f"${data['Strategy_Wealth'].iloc[-1]:.2f}")
    col2.metric("Market Performance", f"{((data['Market_Wealth'].iloc[-1]/100)-1)*100:.1f}%")
    col3.metric("Max Drawdown (Risk)", f"{max_drawdown*100:.1f}%")
    
    # 7. VISUALIZATION
    # Main Performance Chart
    st.subheader("Performance Comparison")
    fig1, ax1 = plt.subplots(figsize=(12, 5))
    ax1.plot(data['Strategy_Wealth'], label="Bot Strategy", color='blue', lw=2)
    ax1.plot(data['Market_Wealth'], label="Market (Buy & Hold)", color='gray', alpha=0.5)
    ax1.legend()
    st.pyplot(fig1)
    
    # RSI Chart
    st.subheader("RSI Indicator (Momentum)")
    fig2, ax2 = plt.subplots(figsize=(12, 3))
    ax2.plot(data['RSI'], color='purple')
    ax2.axhline(70, linestyle='--', color='red', alpha=0.5) # Overbought
    ax2.axhline(30, linestyle='--', color='green', alpha=0.5) # Oversold
    ax2.set_ylim(0, 100)
    st.pyplot(fig2)
    
    st.success("Analysis Complete!")
