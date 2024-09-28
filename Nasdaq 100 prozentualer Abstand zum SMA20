import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Name des Index oder der Aktie
ticker = "^NDX"

# Download der historischen Daten für beliebige Zeiträume bis heute
start_date = (pd.to_datetime("today") - pd.DateOffset(years=10)).strftime('%Y-%m-%d')
end_date = pd.to_datetime("today").strftime('%Y-%m-%d')
nasdaq = yf.Ticker(ticker)
hist = nasdaq.history(start=start_date, end=end_date, interval='1d')

# Berechnung des SMA 20 und SMA 200
hist['SMA20'] = hist['Close'].rolling(window=20).mean()
hist['SMA200'] = hist['Close'].rolling(window=200).mean()

# Relativer Abstand von SMA 20 zu dem jeweiligen Schlusskurs
hist['PctDistFromSMA20'] = ((hist['Low'] - hist['SMA20']) / hist['SMA20']) * 100

# Mask data where Nasdaq 100 closes under SMA 200
hist['PctDistFromSMA20'] = hist['PctDistFromSMA20'].where(hist['Close'] >= hist['SMA200'])

# Create figure with secondary y-axis
fig = make_subplots(specs=[[{"secondary_y": True}]])

# Add Nasdaq 100 Index trace
fig.add_trace(go.Scatter(
    x=hist.index,
    y=hist['Close'],
    marker_color='blue',
    name='Nasdaq 100 (Close Points, Daily)',
    line=dict(width=2)
), secondary_y=False)

# Add percentage distance from SMA 20 trace
fig.add_trace(go.Scatter(
    x=hist.index,
    y=hist['PctDistFromSMA20'],
    marker_color='red',
    name='Pct Distance from SMA 20 (Low Points, Daily)',
    line=dict(width=2)
), secondary_y=True)

fig.update_layout(
    title={'text': 'Nasdaq 100 and Percentage Distance from SMA 20 (Low Points, Daily, Last 10 Years)', 'x': 0.5},
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(color='black')
)

fig.update_xaxes(
    showgrid=True,
    color='black'
)

fig.update_yaxes(
    showgrid=True,
    color='black'
)

fig.update_yaxes(
    title_text="Nasdaq 100 (Low Points, Daily)", 
    secondary_y=False,
    type='log'
)

fig.update_yaxes(
    title_text="Pct Distance from SMA 20 (Low Points, Daily)", 
    secondary_y=True
)

fig.update_xaxes(rangebreaks=[
    dict(bounds=['sat', 'mon']),
    dict(values=["2021-12-25", "2022-01-01"])
])

fig.update_xaxes(rangeslider_visible=True)

fig.show()
