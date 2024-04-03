import pandas as pd
from ta.momentum import RSIIndicator
import matplotlib.pyplot as plt
from binance import Client

def fetch_historical_data(symbol="BTCUSDT", interval=Client.KLINE_INTERVAL_1MINUTE, start_str="1 day ago UTC", end_str="now UTC"):
    """
    Fetches historical klines for a given symbol and interval from Binance.

    Parameters:
    - symbol (str): The trading pair symbol, e.g., 'BTCUSDT'.
    - interval (str): The interval for klines, e.g., Client.KLINE_INTERVAL_1MINUTE.
    - start_str (str): The start time for data retrieval.
    - end_str (str): The end time for data retrieval.

    Returns:
    - DataFrame: A DataFrame containing the historical klines data.
    """
    client = Client()
    k_lines = client.get_historical_klines(symbol, interval, start_str, end_str)
    columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
    df = pd.DataFrame(k_lines, columns=columns)
    df[['time', 'open', 'high', 'low', 'close']] = df[['time', 'open', 'high', 'low', 'close']].apply(pd.to_numeric, errors='coerce')
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    return df

def calculate_rsi(df, periods=[14]):
    """
    Calculates the Relative Strength Index (RSI) for specified periods.

    Parameters:
    - df (DataFrame): The DataFrame containing the 'close' prices.
    - periods (list): A list of periods for which to calculate the RSI.

    Returns:
    - DataFrame: The original DataFrame with added RSI columns for each period.
    """
    for period in periods:
        df[f'RSI_{period}'] = RSIIndicator(df['close'], window=period).rsi()
    return df

def plot_data(df, periods=[14]):
    plt.figure(figsize=(14, 10))
    num_plots = 1 + len(periods)

    plt.subplot(num_plots, 1, 1)
    plt.plot(df['time'], df['close'], label='Close Price')
    plt.title('Close Price')
    plt.legend()

    for i, period in enumerate(periods, start=2):
        plt.subplot(num_plots, 1, i)
        plt.plot(df['time'], df[f'RSI_{period}'], label=f'RSI_{period}')
        plt.title(f'RSI_{period}')
        plt.legend()

    plt.tight_layout()
    plt.show()

# Main workflow
if __name__ == "__main__":
    data = fetch_historical_data()
    periods = [14, 27, 100]
    data_with_rsi = calculate_rsi(data, periods=periods)
    plot_data(data_with_rsi, periods=periods)
