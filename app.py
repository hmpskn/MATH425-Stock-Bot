import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Autonomous Trading Framework", layout="wide")

# Header
st.title("🤖 MATH 425: Autonomous Trading Simulation Framework")
st.markdown("### Advanced Decision Support & Execution System")
st.info("NOTE: This is a simulation environment. Order execution is performed in a virtual sandbox for academic demonstration.")

# Sidebar - Strategy Controls
st.sidebar.header("🕹️ Control Panel")
ticker = st.sidebar.text_input("Asset Ticker", "AAPL")
short_win = st.sidebar.slider("Fast Signal (Days)", 5, 50, 20)
long_win = st.sidebar.slider("Slow Signal (Days)", 50, 200, 100)
trade_size = st.sidebar.number_input("Simulation Trade Size ($)", 1000, 100000, 10000)

# Implementation of Autonomous Logic
def simulate_order_execution(action, price, ticker):
    """Simulates the API call to a broker for autonomous execution"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.sidebar.warning(f"EXECUTING: {action} order for {ticker}")
    time.sleep(1) # Simulating network latency
    st.sidebar.success(f"CONFIRMED: {action} @ ${price:.2f} at {timestamp}")
    return {"status": "Filled", "time": timestamp, "price": price}

if st.sidebar.button("Launch Autonomous Engine"):
    # 1. LIVE DATA STREAM (Simulated)
    with st.spinner("Fetching market data and calculating signals..."):
        data = yf.download(ticker, period="2y")
        
        # 2. INDICATOR CALCULATIONS
        data['SMA_Fast'] = data['Close'].rolling(window=short_win).mean()
        data['SMA_Slow'] = data['Close'].rolling(window=long_win).mean()
        data['Signal'] = np.where(data['SMA_Fast'] > data['SMA_Slow'], 1.0, 0.0)
        data['Position'] = data['Signal'].diff()

    # 3. PERFORMANCE ANALYTICS
    data['Market_Ret'] = data['Close'].pct_change()
    data['Strategy_Ret'] = data['Market_Ret'] * data['Signal'].shift(1)
    data['Wealth'] = 100 * (1 + data['Strategy_Ret']).fillna(0).cumprod()
    
    # 4. DASHBOARD LAYOUT
    col1, col2, col3 = st.columns(3)
    current_price = data['Close'].iloc[-1]
    last_signal = "BUY" if data['Signal'].iloc[-1] == 1 else "SELL/WAIT"
    
    col1.metric("Current Market Price", f"${current_price:.2f}")
    col2.metric("Active Signal", last_signal)
    col3.metric("System Health", "Operational / Sandbox", delta="Online")

    # 5. AUTONOMOUS EXECUTION DEMONSTRATION
    st.subheader("📡 Real-Time Execution Log (Autonomous Engine)")
    latest_event = data[data['Position'] != 0].iloc[-1]
    event_type = "BUY" if latest_event['Position'] == 1 else "SELL"
    
    # Triggering the simulation of the last trade
    exec_details = simulate_order_execution(event_type, latest_event['Close'], ticker)
    
    st.code(f"""
    >>> INCOMING SIGNAL DETECTED: {event_type}
    >>> CONNECTING TO BROKER API... [SUCCESS]
    >>> SENDING MARKET ORDER FOR {ticker}...
    >>> ORDER STATUS: {exec_details['status']}
    >>> EXECUTION PRICE: ${exec_details['price']:.2f}
    >>> TIMESTAMP: {exec_details['time']}
    """, language="python")

    # 6. VISUAL ANALYTICS
    tab1, tab2 = st.tabs(["Equity Curve", "Technical Indicators"])
    with tab1:
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(data['Wealth'], color='#00ff00' if last_signal == "BUY" else '#ff0000', label="Strategy Wealth")
        ax.set_title("Autonomous Strategy Performance")
        st.pyplot(fig)
    
    with tab2:
        fig2, ax2 = plt.subplots(figsize=(12, 5))
        ax2.plot(data['Close'], label="Price", alpha=0.5)
        ax2.plot(data['SMA_Fast'], label="Fast Signal")
        ax2.plot(data['SMA_Slow'], label="Slow Signal")
        ax2.legend()
        st.pyplot(fig2)

    st.success(f"The autonomous engine has processed {ticker} and is monitoring for the next signal.")
