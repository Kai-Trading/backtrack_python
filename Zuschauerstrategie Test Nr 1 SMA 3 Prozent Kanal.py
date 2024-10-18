import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Name des Index oder der Aktie
ticker = "^NDX"

# Download der historischen Daten für den Zeitraum der letzten 31 Jahre
start_date = (pd.to_datetime("today") - pd.DateOffset(years=31)).strftime('%Y-%m-%d')
end_date = pd.to_datetime("today").strftime('%Y-%m-%d')
nasdaq = yf.Ticker(ticker)

# Lade Daten herunter und speichere
hist = nasdaq.history(start=start_date, end=end_date, interval='1d') 
hist.to_pickle("nasdaq.df")

# Daten aus Datei laden
hist = pd.read_pickle("nasdaq.df")

# Berechnung des SMA 200 und prozentualer Abstand vom SMA 200
sma_days = 200
derivation = 3  # Prozent
hist['SMA'] = hist['Close'].rolling(window=sma_days).mean()
hist['PctDistFromSMA'] = ((hist['Close'] - hist['SMA']) / hist['SMA']) * 100

# Hebel (Leverage)
leverage = 2

# Initiale Investition
initial_investment = 10000
initial_investment_buy_hold = 10000

# Initialize variables for the trading strategy
investment_value_strategy = initial_investment
investment_value_strategy_leveraged = initial_investment
position_opened = False
values_strategy = [initial_investment]
values_strategy_leveraged = [initial_investment]

# Trading strategy: buy the day after the signal at opening price
for i in range(1, len(hist)-1):  # We reduce the range by 1 to avoid out-of-range errors
    close_price = hist['Close'].iloc[i]
    pct_dist_from_sma = hist['PctDistFromSMA'].iloc[i]

    # Calculate daily return for the unleveraged strategy
    daily_return = (close_price / hist['Close'].iloc[i-1]) - 1

    # If position is opened, update investment value based on daily returns
    if position_opened:
        investment_value_strategy = investment_value_strategy * (1 + daily_return)
        investment_value_strategy_leveraged = investment_value_strategy_leveraged * (1 + daily_return * leverage)

    # Sell signal: if the closing price is 3% below the SMA200 and position is opened
    if pct_dist_from_sma < -derivation and position_opened:
        position_opened = False

    # Buy signal: if the closing price is 3% above the SMA200 and no position is opened
    if pct_dist_from_sma > derivation and not position_opened:
        position_opened = True
    
    # Store the investment value for the strategy
    values_strategy.append(investment_value_strategy)
    values_strategy_leveraged.append(investment_value_strategy_leveraged)

# Trim 'values_strategy' and 'values_strategy_leveraged' to match the length of the DataFrame
values_strategy = values_strategy[:len(hist)-1]
values_strategy_leveraged = values_strategy_leveraged[:len(hist)-1]

# Add the strategy values to the DataFrame
hist = hist.iloc[:-1].assign(StrategyValue=values_strategy, StrategyValueLeveraged=values_strategy_leveraged)

# Berechnung der Buy-and-Hold-Strategie mit täglichem Hebel
buy_hold_values = [initial_investment_buy_hold]
buy_hold_values_leveraged = [initial_investment_buy_hold]

for i in range(1, len(hist)):
    daily_return = (hist['Close'].iloc[i] / hist['Close'].iloc[i-1]) - 1
    new_value = buy_hold_values[-1] * (1 + daily_return)
    new_value_leveraged = buy_hold_values_leveraged[-1] * (1 + daily_return * leverage)
    buy_hold_values.append(new_value)
    buy_hold_values_leveraged.append(new_value_leveraged)

# Die Länge der Listen passt jetzt genau zur Länge des DataFrames
buy_hold_values = buy_hold_values[:len(hist)]
buy_hold_values_leveraged = buy_hold_values_leveraged[:len(hist)]

# Add Buy-and-Hold values to DataFrame
hist = hist.assign(BuyHoldValue=buy_hold_values, BuyHoldValueLeveraged=buy_hold_values_leveraged)

# Create figure
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

# SMA 200
fig.add_trace(go.Scatter(
    x=hist.index,
    y=hist['SMA'],
    marker_color='red',
    name='SMA {}'.format(sma_days),
    line=dict(width=2)
))

# Strategy performance trace
fig.add_trace(go.Scatter(
    x=hist.index,
    y=hist['StrategyValue'],
    marker_color='green',
    name='Investment Strategy Value',
    line=dict(width=2)
))

# Strategy performance with leverage trace
fig.add_trace(go.Scatter(
    x=hist.index,
    y=hist['StrategyValueLeveraged'],
    marker_color='orange',
    name='Investment Strategy Value (Leveraged)',
    line=dict(width=2)
))

# Buy-and-Hold performance trace
fig.add_trace(go.Scatter(
    x=hist.index,
    y=hist['BuyHoldValue'],
    marker_color='blue',
    name='Buy & Hold Value',
    line=dict(width=2)
))

# Buy-and-Hold performance with leverage trace
fig.add_trace(go.Scatter(
    x=hist.index,
    y=hist['BuyHoldValueLeveraged'],
    marker_color='purple',
    name='Buy & Hold Value (Leveraged)',
    line=dict(width=2)
))

# Layout
fig.update_layout(
    title={'text': 'Nasdaq 100, SMA {}, {} percent Strategy vs Buy & Hold (Last 31 Years) - Leverage 2x'.format(sma_days, derivation), 'x': 0.5},
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

# Show plot
fig.show()
