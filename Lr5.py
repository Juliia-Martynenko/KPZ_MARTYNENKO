import pandas as pd
import ta
from matplotlib import pyplot as plt
from binance import Client
from dataclasses import dataclass

@dataclass
class Signal:
    time: pd.Timestamp
    asset: str
    quantity: float
    side: str
    entry: float
    take_profit: float
    stop_loss: float
    result: float = None  # Default value for result, making it optional

def fetch_data(client):
    k_lines = client.get_historical_klines(
        symbol="BTCUSDT",
        interval=Client.KLINE_INTERVAL_1MINUTE,
        start_str="1 week ago UTC",
        end_str="now UTC"
    )
    return pd.DataFrame(k_lines, columns=[
        'time', 'open', 'high', 'low', 'close', 'volume', 'close_time',
        'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume',
        'taker_buy_quote_asset_volume', 'ignore'
    ])

def prepare_data(df):
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].astype(float)
    return df

def calculate_indicators(df):
    df['adx'] = ta.trend.ADXIndicator(df['high'], df['low'], df['close'], window=14).adx()
    df['cci'] = ta.trend.CCIIndicator(df['high'], df['low'], df['close'], window=20).cci()

def create_signals(df):
    signals = []
    for i, row in df.iterrows():
        signal = "No signal"
        current_price = row['close']
        if row['cci'] < -100 and row['adx'] > 25:
            signal = 'sell'
        elif row['cci'] > 100 and row['adx'] > 25:
            signal = 'buy'

        stop_loss_price, take_profit_price = None, None
        if signal == "buy":
            stop_loss_price = round((1 - 0.02) * current_price, 1)
            take_profit_price = round((1 + 0.1) * current_price, 1)
        elif signal == "sell":
            stop_loss_price = round((1 + 0.02) * current_price, 1)
            take_profit_price = round((1 - 0.1) * current_price, 1)

        if signal != "No signal":
            signals.append(Signal(row['time'], 'BTCUSDT', 100, signal, current_price, take_profit_price, stop_loss_price))

    return signals

client = Client()
k_lines = fetch_data(client)
df = prepare_data(k_lines)
calculate_indicators(df)
signals = create_signals(df)

if signals:
    for sig in signals:
        print(sig)
else:
    print("No signals generated.")

plt.figure(figsize=(12, 6))
plt.plot(df['time'], df['close'], label='BTCUSDT price')

for signal in signals:
    color = 'green' if signal.side == 'buy' else 'red'
    marker = '^' if signal.side == 'buy' else 'v'
    plt.scatter(signal.time, signal.entry, color=color, label=f'{signal.side.capitalize()} Signal', marker=marker, s=100)

plt.title('BTCUSDT price and signals')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
plt.grid(True)
plt.show()
