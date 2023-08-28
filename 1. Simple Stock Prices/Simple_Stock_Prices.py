import yfinance as yf
import streamlit as st
import pandas as pd

st.write("""
# Simple Stock Price App

Shown are the Stock **Closing Price** and **Volume** of Google!         

""")

#define ticker symbol
tickersymbol = 'GOOGL'

#get data on this ticker
tickerData = yf.Ticker(tickersymbol)


#get the historical prices for this ticker
tickerDf = tickerData.history(period = 'id', start = '2010-5-31', end = '2023-5-31')

#open high low close volume Dividends stock splits
st.write("""
## Closing Price
""")

st.line_chart(tickerDf.Close)


st.write("""
## Volume
""")


st.line_chart(tickerDf.Volume)
