import yfinance as yf
from datetime import datetime 
import pandas as pd
import numpy
import matplotlib.pyplot as plt


ticker = yf.download('SPY', start='2020-01-01', end=datetime.now().date())

close = ticker['Close'].squeeze()

ma_50 = close.rolling(50).mean()
ma_200 = close.rolling(200).mean()


ticker_buy = (ma_50.shift(1) <= ma_200.shift(1)) & (ma_50 > ma_200)
ticker_sell = (ma_50.shift(1) >= ma_200.shift(1)) & (ma_50< ma_200)

# Moving Average Crossover Decision

position = 0 
positions = []

for i in range(len(ticker)):
    if ticker_buy.iloc[i]:
        position = 1
    elif ticker_sell.iloc[i]:
        position = 0
    positions.append(position)


# Moving Average Crossover Decision

position = 0 
positions = []

for i in range(len(ticker)):
    if ticker_buy.iloc[i]:
        position = 1
    elif ticker_sell.iloc[i]:
        position = 0
    positions.append(position)


ticker = yf.download('SPY', start='2020-01-01', end=datetime.now().date())

close = ticker['Close'].squeeze()

ma_50 = close.rolling(50).mean()
ma_200 = close.rolling(200).mean()


ticker_buy = (ma_50.shift(1) <= ma_200.shift(1)) & (ma_50 > ma_200)
ticker_sell = (ma_50.shift(1) >= ma_200.shift(1)) & (ma_50< ma_200)

# Moving Average Crossover Decision

position = 0 
positions = []

for i in range(len(ticker)):
    if ticker_buy.iloc[i]:
        position = 1
    elif ticker_sell.iloc[i]:
        position = 0
    positions.append(position)


ticker = yf.download('SPY', start='2020-01-01', end=datetime.now().date())

close = ticker['Close'].squeeze()

ma_50 = close.rolling(50).mean()
ma_200 = close.rolling(200).mean()


ticker_buy = (ma_50.shift(1) <= ma_200.shift(1)) & (ma_50 > ma_200)
ticker_sell = (ma_50.shift(1) >= ma_200.shift(1)) & (ma_50< ma_200)

# Moving Average Crossover Decision

position = 0 
positions = []

for i in range(len(ticker)):
    if ticker_buy.iloc[i]:
        position = 1
    elif ticker_sell.iloc[i]:
        position = 0
    positions.append(position)



#  Plot price 
plt.figure(figsize=(14,7))

# Price and moving averages
plt.plot(ticker.index, close, label='Price', color='blue')
plt.plot(ticker.index, ma_50, label='MA50', color='orange')
plt.plot(ticker.index, ma_200, label='MA200', color='green')

plt.title('SPY Price with 50/200 MA Crossover Strategy')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()  