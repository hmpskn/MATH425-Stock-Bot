import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Autonomous Trading Framework", layout="wide")

# Header Section
st.title("🤖 MATH 425: Autonomous Trading Simulation Framework")
st.markdown("### Advanced Decision Support & Execution System")
st.info("NOTE: This is a simulation environment. Order execution is performed in a virtual sandbox for academic demonstration.")

# Sidebar - Strategy Controls
st.sidebar.header("🕹️ Control Panel")
ticker = st.sidebar.text_input("Asset Ticker", "AAPL")
short_win = st.sidebar.slider("Fast Signal (Days)", 5, 50, 20)
long_win = st.sidebar.slider("Slow Signal (Days)", 50, 200, 100)
trade_size = st.sidebar.number_input("Simulation Trade Size ($)", 1000, 100000, 10000)

def simulate_order_execution(action, price, ticker):
    """Simulates the API call to a broker for autonomous execution"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.sidebar.warning(f"EXECUTING: {action} order for {ticker}")
    time.sleep(1) 
    st.sidebar.success(f"CONFIRMED: {action} @ ${price:.2f} at {timestamp}")
    return {"status": "Filled", "time": timestamp, "price": price}

if st.sidebar.button("Launch Autonomous Engine"):
    with st.spinner("Fetching market data..."):
        # Veriyi çekiyoruz
        data = yf.download(ticker, period="3y")
        
        if data.empty:
            st.error(f"No data found for {ticker}. Please check the ticker symbol.")
        else:
            # MultiIndex kontrolü
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            # 1. Matematiksel Göstergeler
            data['SMA_Fast'] = data['Close'].rolling(window=short_win).mean()
            data['SMA_Slow'] = data['Close'].rolling(window=long_win).mean()
            
            # 2. Sinyal Mantığı
            data['Signal'] = 0.0
            data.loc[data['SMA_Fast'] > data['SMA_Slow'], 'Signal'] = 1.0
            data['Position'] = data['Signal'].diff()

            # 3. Performans Hesaplama (Hata Payı Düşürülmüş)
            data['Market_Ret'] = data['Close'].pct_change()
            data['Strategy_Ret'] = data['Market_Ret'] * data['Signal'].shift(1)
            
            # Sermayeyi 100'den başlat ve kümülatif çarpım yap
            data['Wealth'] = (1 + data['Strategy_Ret'].fillna(0)).cumprod() * 100
            
            # Dashboard
            col1, col2, col3 = st.columns(3)
            current_price = float(data['Close'].iloc[-1])
            last_signal = "BUY" if data['Signal'].iloc[-1] == 1 else "SELL/WAIT"
            
            col1.metric("Current Market Price", f"${current_price:.2f}")
            col2.metric("Active Signal", last_signal)
            col3.metric("System Health", "Operational", delta="Online")

            # Execution Log
            st.subheader("📡 Real-Time Execution Log (Autonomous Engine)")
            latest_events = data[data['Position'].notnull() & (data['Position'] != 0)]
            
            if not latest_events.empty:
                latest_event = latest_events.iloc[-1]
                event_type = "BUY" if latest_event['Position'] > 0 else "SELL"
                exec_details = simulate_order_execution(event_type, float(latest_event['Close']), ticker)
                
                st.code(f"""
>>> INCOMING SIGNAL DETECTED: {event_type}
>>> CONNECTING TO BROKER API... [SUCCESS]
>>> SENDING MARKET ORDER FOR {ticker}...
>>> ORDER STATUS: {exec_details['status']}
>>> EXECUTION PRICE: ${exec_details['price']:.2f}
>>> TIMESTAMP: {exec_details['time']}
                """, language="python")
            else:
                st.info("System is monitoring. Currently no crossover detected for execution.")

            # Visualizations
            tab1, tab2 = st.tabs(["Equity Curve", "Technical Indicators"])
            with tab1:
                fig1, ax1 = plt.subplots(figsize=(12, 5))
                ax1.plot(data.index, data['Wealth'], color='blue', lw=2, label="Strategy Wealth")
                ax1.set_title(f"Strategy Growth Simulation for {ticker}")
                ax1.set_ylabel("Portfolio Value ($)")
                ax1.grid(True, alpha=0.3)
                st.pyplot(fig1)
                
            with tab2:
                fig2, ax2 = plt.subplots(figsize=(12, 5))
                ax2.plot(data.index, data['Close'], label="Price", alpha=0.5, color='black')
                ax2.plot(data.index, data['SMA_Fast'], label=f"{short_win} Day SMA", color='orange')
                ax2.plot(data.index, data['SMA_Slow'], label=f"{long_win} Day SMA", color='green')
                ax2.set_title("Price and Crossover Signals")
                ax2.legend()
                ax2.grid(True, alpha=0.3)
                st.pyplot(fig2)

            st.success("Analysis and simulation logic updated successfully.")
