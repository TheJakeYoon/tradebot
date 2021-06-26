import alpaca_trade_api as tradeapi
import pandas as pd
import asyncio, aiohttp, math
import profile, market_day

def init(api):
    print("init")

def scan(api):
    return ["AAPL", "TSM", "SPY", "JPM"]

def order(api, tickers):
    for ticker in tickers:
        #Get latest bar
        #bars = api.get_barset(ticker, 'minute', 1).df.iloc[0]
        #price = float(bars[ticker]['close'])
        price = float(api.get_last_trade(ticker).price)

        print(price)

        #price = price + (price * 0.005)

        account = api.get_account()

        initial_cash = float(account.buying_power)

        qty = math.floor((initial_cash * 0.1 ) / price)

        if qty > 0 and float(account.buying_power) > price and price < (float(account.last_equity) * 0.2):

            api.submit_order(
                symbol=ticker,
                qty=qty,
                side='buy',
                type='market',
                time_in_force='day',
                order_class='bracket',
                stop_loss={'stop_price': price * 0.98,
                    'limit_price':  price * 0.97},
                take_profit={'limit_price': price * 1.02}
            )
            try:
                print(api.get_position(ticker))
            except Exception as e:
                print(e)

def close(api):
    positions = api.close_all_positions()
    for position in positions:    
        if position.status == 200:
            print("All positions closed")
        else:
            print("Something went wrong!")