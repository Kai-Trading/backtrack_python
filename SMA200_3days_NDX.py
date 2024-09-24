import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Name des Index oder der Aktie
ticker = "^NDX"

# Download der historischen Daten für beliebige Zeiträume/-intervalle bis heute
start_date = (pd.to_datetime("today") - pd.DateOffset(years=31)).strftime('%Y-%m-%d')
end_date = pd.to_datetime("today").strftime('%Y-%m-%d')
nasdaq = yf.Ticker(ticker)
hist = nasdaq.history(start=start_date, end=end_date, interval='1d')

# Berechnung des SMA 200
hist['SMA200'] = hist['Close'].rolling(window=200).mean()

# Variabeln für die trading-Strategie definieren
initial_investment = 404
investment_value_strategy = initial_investment
position_opened = False
consecutive_days_above = 0
consecutive_days_below = 0
values_strategy = [initial_investment]  # Erster Trade soll mit dem definiertem Startkapital durchgeführt werden

for i in range(1, len(hist)):
    close_price = hist['Close'].iloc[i]
    sma200 = hist['SMA200'].iloc[i]
    
    # Wenn über SMA 200, zähle aufeinanderfolgende Tage
    if close_price > sma200:
        consecutive_days_above += 1
        consecutive_days_below = 0
    else:
        consecutive_days_below += 1
        consecutive_days_above = 0
    
    # Position öffnen, wenn 3 Tage über SMA 200
    if consecutive_days_above >= 3 and not position_opened:
        position_opened = True
        entry_price = close_price  # Einstiegspreis ist der close-Preis des 3. Tages
    
    # Position schließen, wenn 3 Tage unter SMA 200
    if consecutive_days_below >= 3 and position_opened:
        position_opened = False
    
    # Wenn Position eröffnet, update investment value basierend auf daily returns
    if position_opened:
        daily_return = (close_price / hist['Close'].iloc[i-1]) - 1
        investment_value_strategy = investment_value_strategy * (1 + daily_return)
    
    # Momentaner Wert der Position
    values_strategy.append(investment_value_strategy)

# Add the strategy values to the DataFrame
hist = hist.assign(StrategyValue=values_strategy)

# Figur erstellen
fig = make_subplots(specs=[[{"secondary_y": False}]])

# Nasdaq 100 Candlestick
fig.add_trace(go.Candlestick(
    x=hist.index,
    open=hist['Open'],
    high=hist['High'],
    low=hist['Low'],
    close=hist['Close'],
    name='Nasdaq 100 (Candlestick)'
))

# SMA 200 plotten
fig.add_trace(go.Scatter(
    x=hist.index,
    y=hist['SMA200'],
    marker_color='red',
    name='SMA 200',
    line=dict(width=2)
))

# Strategie-Performance plotten
fig.add_trace(go.Scatter(
    x=hist.index,
    y=hist['StrategyValue'],
    marker_color='green',
    name='Investment Strategy Value',
    line=dict(width=2)
))

# Layout
fig.update_layout(
    title={'text': 'Nasdaq 100, SMA 200, Strategy Value (Last 30 Years)', 'x': 0.5},
    plot_bgcolor='white',
    paper_bgcolor='white',
    font=dict(color='black'),
    xaxis_rangeslider_visible=True
)

# Achsen
fig.update_xaxes(
    showgrid=True,
    color='black',
    rangebreaks=[dict(bounds=["sat", "mon"])]  # Exclude weekends
)

fig.update_yaxes(
    showgrid=True,
    color='black',
    type='log',  
    title_text="Value (USD)"
)

# Zeige Plot
fig.show()
