import streamlit as st
from PIL import Image
import pandas as pd
import base64
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import requests
import json

# Page layout
st.set_page_config(layout="wide")

# Title
image = Image.open(r"C:\Users\pritp\Projects\6. EDA Cryptocurrency\logo.jpg")
st.image(image, width=500)
st.title('Crypto Price App')
st.markdown("This app retrieves cryptocurrency prices for the top 100 cryptocurrencies from CoinMarketCap!")

# About
expander_bar = st.expander("About")
expander_bar.markdown("""
* **Python libraries:** base64, pandas, streamlit, matplotlib, BeautifulSoup, requests, json
* **Data source:** [CoinMarketCap](http://coinmarketcap.com)
* **Credit:** Web scraper adapted from the Medium article *[Web Scraping Crypto Prices With Python](https://towardsdatascience.com/web-scraping-crypto-prices-with-python-41072ea5b5bf)* written by [Bryan Feng](https://medium.com/@bryanf)
""")

# Sidebar + Main panel
col1 = st.sidebar
col2, col3 = st.columns((2, 1))

# Sidebar - Currency price unit
currency_price_unit = col1.selectbox('Select currency for price', ('USD', 'BTC', 'ETH'))


###########################################
cmc = requests.get('https://coinmarketcap.com')
soup = BeautifulSoup(cmc.content, 'html.parser')
data = soup.find('script', id='__NEXT_DATA__', type='application/json')
coin_data = json.loads(data.contents[0])
listings = coin_data['props']['initialState']['cryptocurrency']['listingLatest']['data']
listings
##################################################




# Web scraping of CoinMarketCap data
@st.cache_resource
def load_data():
    cmc = requests.get('https://coinmarketcap.com')
    soup = BeautifulSoup(cmc.content, 'html.parser')
    data = soup.find('script', id='__NEXT_DATA__', type='application/json')
    coin_data = json.loads(data.contents[0])
    listings = coin_data['props']['initialState']['cryptocurrency']['listingLatest']['data']
    
    coin_list = []
    for i in listings:
        coin = {
            'name': i['slug'],
            'symbol': i['symbol'],
            'price': i['quote'][currency_price_unit]['price'],
            'percent_change_1h': i['quote'][currency_price_unit]['percent_change_1h'],
            'percent_change_24h': i['quote'][currency_price_unit]['percent_change_24h'],
            'percent_change_7d': i['quote'][currency_price_unit]['percent_change_7d'],
            'market_cap': i['quote'][currency_price_unit]['market_cap'],
            'volume_24h': i['quote'][currency_price_unit]['volume_24h']
        }
        coin_list.append(coin)
    
    df = pd.DataFrame(coin_list)
    return df



df = load_data()

# Sidebar - Cryptocurrency selections
sorted_coin = sorted(df['symbol'])
selected_coin = col1.multiselect('Cryptocurrency', sorted_coin, sorted_coin)

df_selected_coin = df[df['symbol'].isin(selected_coin)]  # Filtering data

# Sidebar - Number of coins to display
num_coin = col1.slider('Display Top N Coins', 1, 100, 100)
df_coins = df_selected_coin[:num_coin]

# Sidebar - Percent change timeframe
percent_timeframe = col1.selectbox('Percent change time frame', ['7d', '24h', '1h'])
selected_percent_timeframe = f'percent_change_{percent_timeframe}'

# Sidebar - Sorting values
sort_values = col1.selectbox('Sort values?', ['Yes', 'No'])

# Display selected cryptocurrency data
col2.subheader('Price Data of Selected Cryptocurrencies')
col2.write(f'Data Dimension: {df_selected_coin.shape[0]} rows and {df_selected_coin.shape[1]} columns.')
col2.dataframe(df_coins)

# Download CSV data
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="crypto.csv">Download CSV File</a>'
    return href

col2.markdown(filedownload(df_selected_coin), unsafe_allow_html=True)

# Preparing data for Bar plot of % Price change
col2.subheader('Table of % Price Change')
df_change = df_coins[['symbol', 'percent_change_1h', 'percent_change_24h', 'percent_change_7d']].set_index('symbol')
positive_columns = [col for col in df_change.columns if col.startswith('percent_change')]
df_change[positive_columns] = df_change[positive_columns] > 0
col2.dataframe(df_change)

# Conditional creation of Bar plot (time frame)
col3.subheader('Bar plot of % Price Change')

if percent_timeframe == '7d':
    column_to_plot = 'percent_change_7d'
    col3.write('*7 days period*')
elif percent_timeframe == '24h':
    column_to_plot = 'percent_change_24h'
    col3.write('*24 hour period*')
else:
    column_to_plot = 'percent_change_1h'
    col3.write('*1 hour period*')

if sort_values == 'Yes':
    df_change = df_change.sort_values(by=[column_to_plot])

plt.figure(figsize=(8, 0.4 * df_change.shape[0]))  # Adjust height based on number of coins
df_change[column_to_plot].plot(kind='barh', color=df_change[positive_columns].applymap(lambda x: 'g' if x else 'r'))
col3.pyplot(plt)
