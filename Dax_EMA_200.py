import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import numpy as np
import mplfinance as mpf
import os
import time
# Laden der Daten
ticker = "^GDAXI"  # Ticker-Symbol für den Index
# onyl download if not already downloaded or data is older than 1 day
filename = "dax.df"
redownload = True
if not os.path.exists(filename) or (os.path.getmtime(filename) < (time.time() - 86400)) or redownload:
    print("Downloading data")
    data = yf.download(ticker, period="40y", interval="1d",multi_level_index = False)  # 6 Monate Tagesdaten
    data.to_pickle(filename)

data = pd.read_pickle(filename)
# Berechnung der SMA-20
# data['SMA_20'] = data['Close'].rolling(window=20).mean()

# Berechnung des prozentualen Abstands (nur für nicht-NaN-Werte)

n = 200
# calculate EMA and SMA for n days
data['SMA'] = data['Close'].rolling(window=n).mean()
data['EMA'] = data['Close'].ewm(span=n).mean()

# def moving_average(x, n):
#     result = np.zeros_like(x)
#     result[n-1:] = np.convolve(x, np.ones(n), 'valid') / n
#     for i in range(n-1):
#         result[i] = np.nan
#     return result 

low = data['Close'].to_numpy()
sma = data['SMA'].to_numpy()
ema = data['EMA'].to_numpy()

# n-1 days are NaN because of the moving average. we remove them and add them back later 
# to the correct positions at the start of the arrays to have the same length as the original data
pct_dist_sma = ((low[n-1:]-sma[n-1:])/sma[n-1:]) * 100
pct_dist_ema = ((low[n-1:]-ema[n-1:])/ema[n-1:]) * 100

pct_dist_sma = np.append(np.ones(n-1)*np.nan,pct_dist_sma)
pct_dist_ema = np.append(np.ones(n-1)*np.nan,pct_dist_ema)

ema = np.append(np.ones(n-1)*np.nan,ema[n-1:])
sma = np.append(np.ones(n-1)*np.nan,sma[n-1:])

# data = data.dropna()

# Visualisierung mit Plotly
# print(data['Close'].head())
fig = go.Figure()

# Plot des Schlusskurses
fig.add_trace(go.Scatter(x=data.index, y=low, mode='lines', name='Schlusskurs'))

# Plot der SMA-20
fig.add_trace(go.Scatter(x=data.index, y=ema, mode='lines', name='EMA-{}'.format(n)))

# Plot des prozentualen Abstands
fig.add_trace(go.Scatter(x=data.index, y=pct_dist_ema, mode='lines', name='% Abstand EMA-{}'.format(n), yaxis='y2'))

# Layout anpassen
fig.update_layout(
    title="DAX Schlusskurs, EMA-{} und Prozentualer Abstand".format(n),
    xaxis_title="Datum",
    yaxis=dict(title="Preis"),
    yaxis2=dict(title="Prozentualer Abstand", overlaying="y", side="right"),
    legend=dict(orientation="h", x=0, y=-0.2),
)

# Plot anzeigen
fig.show()


# mpf.plot(data,type='line',warn_too_much_data=int(1e10))#,figratio=(16.9))
# # mpf.plot(df,type='candle',addplot=[apdict,ap_open,ap_close_win,ap_close_loss,sma_plot],mav=200,style=s,yscale='linear')#,figratio=(16.9))
# mpf.show()