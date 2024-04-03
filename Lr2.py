import pandas as pd
from binance.client import Client

def get_historical_data(symbol, start_str, end_str, intervals='1m'):
    client = Client()
    klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1MINUTE if intervals == '1m' else intervals, start_str, end_str)
    columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 
               'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 
               'taker_buy_quote_asset_volume', 'ignore']
    
    data = pd.DataFrame(klines, columns=columns)
    data = data[['time', 'open', 'high', 'low', 'close', 'volume']].apply(pd.to_numeric, errors='coerce')
    data['time'] = pd.to_datetime(data['time'], unit='ms')
    
    return data

def calculate_RSI(df, periods=[14]):
    
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    rsi_df = pd.DataFrame({'time': df['time']})
    for period in periods:
        avg_gain = gain.rolling(window=period, min_periods=1).mean()
        avg_loss = loss.rolling(window=period, min_periods=1).mean()
        rs = avg_gain / avg_loss
        rsi_df[f'RSI {period}'] = 100 - (100 / (1 + rs))
    
    return rsi_df

# Example usage
symbol = 'BTCUSDT'
yesterday = pd.Timestamp.now() - pd.Timedelta(days=1)
start_str = yesterday.strftime('%Y-%m-%d %H:%M')
end_str = yesterday.strftime('%Y-%m-%d %H:%M')

data = get_historical_data(symbol, start_str, end_str)
rsi_data = calculate_RSI(data)

print(rsi_data.tail())
