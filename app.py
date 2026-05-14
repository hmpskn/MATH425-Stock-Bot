import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Page Configuration
st.set_page_config(page_title="MATH 425 Stock Analysis Bot", layout="wide")

# Header Section
st.title("📈 MATH 425: Algorithmic Trading & Simulation")
#st.markdown("### Developed by: [Your Name] - [Your Student ID]")
st.write("This application simulates a trading bot using Mathematical Moving Averages (SMA).")

# Sidebar Configuration (Input parameters)
st.sidebar.header("Parameters")
ticker = st.sidebar.text_input("Stock Ticker (e.g., AAPL, TSLA, MSFT)", "AAPL")
start_date = st.sidebar.date_input("Start Date", pd.to_datetime("2020-01-01"))

if st.sidebar.button("Run Simulation"):
    # 1. DATA COLLECTION
    # Fetching historical data from Yahoo Finance
    data = yf.download(ticker, start=start_date)
    
    # 2. MATHEMATICAL MODELING
    # Calculating Simple Moving Averages (SMA)
    # 20-day SMA represents short-term trend
    # 100-day SMA represents long-term trend
    data['SMA20'] = data['Close'].rolling(window=20).mean()
    data['SMA100'] = data['Close'].rolling(window=100).mean()
    
    # 3. TRADING STRATEGY (Crossover Logic)
    # Buy when 20 SMA is above 100 SMA
    data['Signal'] = np.where(data['SMA20'] > data['SMA100'], 1.0, 0.0)
    
    # 4. BACKTESTING & PERFORMANCE EVALUATION
    # Calculating daily percentage returns
    data['Market_Returns'] = data['Close'].pct_change()
    # Strategy returns apply only when the bot holds a 'Buy' signal
    data['Strategy_Returns'] = data['Market_Returns'] * data['Signal'].shift(1)
    
    # Cumulative growth starting from $100
    data['Market_Wealth'] = 100 * (1 + data['Market_Returns']).cumprod()
    data['Strategy_Wealth'] = 100 * (1 + data['Strategy_Returns']).cumprod()
    
    # 5. OUTPUT DISPLAY (Metrics)
    col1, col2 = st.columns(2)
    col1.metric("Final Market Value (Buy & Hold)", f"${data['Market_Wealth'].iloc[-1]:.2f}")
    col2.metric("Final Bot Strategy Value", f"${data['Strategy_Wealth'].iloc[-1]:.2f}")
    
    # 6. VISUALIZATION
    # Comparing Market performance vs. Strategy performance
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(data['Strategy_Wealth'], label="Trading Bot Strategy (SMA 20/100)", color='blue', lw=2)
    ax.plot(data['Market_Wealth'], label="Market (Buy & Hold)", color='gray', alpha=0.5)
    ax.set_title(f"Performance Analysis: {ticker}")
    ax.set_ylabel("Portfolio Value ($)")
    ax.set_xlabel("Date")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
    
    st.success("Simulation completed successfully!")
