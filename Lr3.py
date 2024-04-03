import datetime
import pandas as pd
from binance.client import Client
import pandas_ta as ta

# Configuration
SYMBOL = "BTCUSDT"
INTERVAL = Client.KLINE_INTERVAL_1MINUTE
N_DAYS_AGO = 1

def fetch_historical_data(symbol, interval, start_str, end_str):
    client = Client()
    klines = client.get_historical_klines(symbol, interval, start_str, end_str)
    df = pd.DataFrame(klines, columns=['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_vol', 'trades', 'tb_base_vol', 'tb_quote_vol', 'ignore'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df = df[['time', 'open', 'high', 'low', 'close']].apply(pd.to_numeric, errors='coerce')
    return df

def calculate_indicators(df):
    df['RSI'] = ta.rsi(df['close'])
    df['CCI'] = ta.cci(df['high'], df['low'], df['close'])
    macd = ta.macd(df['close'])
    df = pd.concat([df, macd], axis=1)
    return df.dropna()

def interpret_signals(row):
    signals = {
        'RSI': "Невідомий",
        'CCI': "Невідомий",
        'MACD': "Невідомий"
    }
    if row["RSI"] > 70:
        signals['RSI'] = "Ціна буде рости"
    elif row["RSI"] > 30:
        signals['RSI'] = "Ціна впаде"

    if row["CCI"] < -100:
        signals['CCI'] = "Ціна буде рости"
    elif row["CCI"] < 100:
        signals['CCI'] = "Ціна впаде"

    if row['MACD_12_26_9'] > row['MACDs_12_26_9'] and row['MACD_12_26_9'].shift(1) < row['MACDs_12_26_9'].shift(1):
        signals['MACD'] = "Ціна буде рости"
    elif row['MACD_12_26_9'] < row['MACDs_12_26_9'] and row['MACD_12_26_9'].shift(1) > row['MACDs_12_26_9'].shift(1):
        signals['MACD'] = "Ціна впаде"

    # Final decision logic can be refined as per requirement.
    return "Невідомий" if all(value == "Невідомий" for value in signals.values()) else ', '.join([f"{key}: {value}" for key, value in signals.items() if value != "Невідомий"])

def main():
    today = datetime.datetime.now()
    start_date = today - datetime.timedelta(days=N_DAYS_AGO)
    end_date = today

    try:
        data = fetch_historical_data(SYMBOL, INTERVAL, start_date.strftime('%Y-%m-%d %H:%M'), end_date.strftime('%Y-%m-%d %H:%M'))
        data_with_indicators = calculate_indicators(data)
        data_with_indicators['Prediction'] = data_with_indicators.apply(interpret_signals, axis=1)
        data_with_indicators.to_csv('prediction.csv', columns=['time', 'RSI', 'CCI', 'MACD_12_26_9', 'MACDs_12_26_9', 'Prediction'], index=False)
        print("Saved predictions to prediction.csv")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
