import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Proje Bilgileri (Rapor Başlığı ile uyumlu)
st.set_page_config(page_title="MATH 425 Stock Analysis", layout="wide")

st.title("📈 MATH 425: Algoritmik Ticaret ve Simülasyon")
st.markdown("### Hazırlayan: [Senin Adın] - [Öğrenci Numaran]")

# Yan Panel (Sidebar)
st.sidebar.header("Parametreler")
ticker = st.sidebar.text_input("Hisse Sembolü (Örn: AAPL, TSLA)", "AAPL")
start_date = st.sidebar.date_input("Başlangıç Tarihi", pd.to_datetime("2020-01-01"))

if st.sidebar.button("Simülasyonu Çalıştır"):
    # Veri Toplama
    data = yf.download(ticker, start=start_date)
    
    # Matematiksel Model: Hareketli Ortalama (SMA)
    data['SMA20'] = data['Close'].rolling(window=20).mean()
    data['SMA100'] = data['Close'].rolling(window=100).mean()
    
    # Alım-Satım Sinyali (Crossover)
    data['Signal'] = np.where(data['SMA20'] > data['SMA100'], 1.0, 0.0)
    
    # Performans Analizi
    data['Market_Returns'] = data['Close'].pct_change()
    data['Strategy_Returns'] = data['Market_Returns'] * data['Signal'].shift(1)
    data['Market_Wealth'] = 100 * (1 + data['Market_Returns']).cumprod()
    data['Strategy_Wealth'] = 100 * (1 + data['Strategy_Returns']).cumprod()
    
    # Sonuçlar
    col1, col2 = st.columns(2)
    col1.metric("Piyasa Sonu (100$ ->)", f"${data['Market_Wealth'].iloc[-1]:.2f}")
    col2.metric("Bot Sonu (100$ ->)", f"${data['Strategy_Wealth'].iloc[-1]:.2f}")
    
    # Grafik
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(data['Strategy_Wealth'], label="Bot Stratejisi (SMA 20/100)", color='blue')
    ax.plot(data['Market_Wealth'], label="Piyasa (Buy & Hold)", color='gray', alpha=0.5)
    ax.set_title(f"{ticker} Performans Kıyaslaması")
    ax.legend()
    st.pyplot(fig)
    
    st.success("Simülasyon başarıyla tamamlandı!")