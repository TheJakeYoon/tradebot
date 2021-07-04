import pandas as pd
import requests, math, asyncio, aiohttp
import profile, market_day

# asyncio method to get polyon data faster
async def get_APIdata(session, url, close_price, gap):
    async with session.get(url) as response:
        result = await response.json()
        try:
            ticker = result['symbol']
            current_price = result['open']
            pct = round(((current_price - close_price) / close_price) * 100, 2)
            gap.append({'ticker' : ticker, 'current_price' : current_price, 'close_price' : close_price, 'pct': pct})
        except Exception as e:
            # print(e)
            #print(url)
            pass

# gets today's close and calls get_APIdata()
async def get_gap(prev_closes, date):
    gap = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for prev_close in prev_closes:
            url = "https://api.polygon.io/v1/open-close/{}/{}?adjusted=true&apiKey={}".format(prev_close['ticker'], date, profile.POLYGON_API_KEY)
            task = asyncio.ensure_future(get_APIdata(session, url, prev_close['close_price'], gap))
            tasks.append(task)
        await asyncio.gather(*tasks)

    return gap

def get_close(tickers):
    
    prev_closes = []

    for ticker in tickers:
        file = "./data/backtest/polygon_daily/{}.csv".format(ticker)
        try:
            df = pd.read_csv(file)
        except Exception as e:
            # print(file)
            pass
        try:
            volume = df['volume'].iloc[-1]
            close_price = df['close'].iloc[-1]
            # only scans for stocks with higher than daily volume of 1 million and price $10 or higher.
            if volume > 1000000 and close_price > 10:
                prev_closes.append({'ticker' : ticker, 'close_price' : close_price})
        except Exception as e:
            # print(e)
            # print("Make sure to get previous open close")
            pass

    return prev_closes

# Scans for stocks
# If S&P is up, looks for gap downs
# If S&P is down, looks for gap ups
# 2-8% change and no news
def scan(api, prev_closes, date):
    gaps = asyncio.run(get_gap(prev_closes, date))

    df = pd.DataFrame(gaps)
    # print(df.info())
    # print(df)

    # checks if S&P 500 is up or down
    url = "https://api.polygon.io/v1/open-close/SPY/{}?adjusted=true&apiKey={}".format(date, profile.POLYGON_API_KEY)
    response = requests.get(url).json()
    try:
        # checks if S&P500 is up
        spy_open = response['open']
        spy_pre = response['preMarket']
        market_up = True
        if spy_open - spy_pre > 0:
            print("SPY up today")
            df.sort_values(by = 'pct', inplace = True, ascending = True)
            df = df.loc[(df['pct'] > -5) & (df['pct'] < -3)]
        else:
            print("SPY down today")
            market_up = False
            df.sort_values(by = 'pct', inplace = True, ascending = False)
            df = df.loc[(df['pct'] > 3) & (df['pct'] < 5)]
    except Exception as e:
        print(e)
        print("Couldn't check if SPY was up or down")

    tickers = df.to_dict('records')

    gappers = []
    count = 0

    for i in range(len(tickers)):
        date = market_day.prev_open()
        # check for news
        url = "https://api.polygon.io/v2/reference/news?limit=3&order=descending&sort=published_utc&ticker={}&published_utc.gte={}&apiKey={}".format(tickers[i]['ticker'], date, profile.POLYGON_API_KEY)
        response = requests.get(url).json()
        # only pick 10 stocks
        if count < 10:
            if not response['results']:
                # print("No news")
                if market_up:
                    tickers[i]['side'] = 'buy'
                else:
                    tickers[i]['side'] = 'sell'
                gappers.append(tickers[i])
                count += 1
            else:
                pass
                # print("News released {}".format(tickers[i]['ticker']))
        else:
            break

    # print(gappers)

    return gappers

def order(api, tickers):

    account = api.get_account()
    initial_cash = float(account.buying_power)
    initial_cash = 30000

    for ticker in tickers:

        price = float(api.get_last_trade(ticker['ticker']).price)
        limit_price = 0.0
        if ticker['side'] == 'buy':
            limit_price = price * 1.005
        elif ticker['side'] == 'sell':
            limit_price = price * 0.995
        qty = math.floor((initial_cash * 0.1 ) / price)

        if qty > 0:
            try:
                api.submit_order(
                symbol=ticker['ticker'],
                qty=qty,
                side=ticker['side'],
                type='limit',
                limit_price=limit_price,
                time_in_force='day',
                )
                print("Order Placed!")
            except Exception as e:
                print(e)

# oco (One Cancels Other) stop limit and profit limit order after market order
def order_v2(api):
        positions = api.list_positions()
        if positions is not None:
            for position in positions:
                if position.side == 'long':
                    try:
                        api.submit_order(
                            symbol=position.symbol,
                            qty=float(position.qty),
                            side='sell',
                            type='limit',
                            time_in_force='day',
                            order_class='oco',
                            stop_loss={'stop_price': float(position.avg_entry_price) * 0.97},
                            take_profit={'limit_price': float(position.avg_entry_price) * 1.04}
                        )
                    except Exception as e:
                        print(e)
                elif position.side == 'short':
                    try:
                        api.submit_order(
                            symbol=position.symbol,
                            qty=float(position.qty),
                            side='buy',
                            type='limit',
                            time_in_force='day',
                            order_class='oco',
                            stop_loss={'stop_price': float(position.avg_entry_price) * 1.03},
                            take_profit={'limit_price': float(position.avg_entry_price) * 0.96}
                        )
                    except Exception as e:
                        print(e)
        else:
            print("Orders not filled yet!")

# oco (One Cancels Other) stop limit and profit limit order after profit target not reached
def order_v3(api):
        positions = api.list_positions()
        if positions is not None:
            for position in positions:
                if position.side == 'long':
                    try:
                        api.submit_order(
                            symbol=position.symbol,
                            qty=float(position.qty),
                            side='sell',
                            type='limit',
                            time_in_force='day',
                            order_class='oco',
                            stop_loss={'stop_price': float(position.avg_entry_price) * 0.98},
                            take_profit={'limit_price': float(position.avg_entry_price) * 1.02}
                        )
                    except Exception as e:
                        print(e)
                elif position.side == 'short':
                    try:
                        api.submit_order(
                            symbol=position.symbol,
                            qty=float(position.qty),
                            side='buy',
                            type='limit',
                            time_in_force='day',
                            order_class='oco',
                            stop_loss={'stop_price': float(position.avg_entry_price) * 1.02},
                            take_profit={'limit_price': float(position.avg_entry_price) * 0.98}
                        )
                    except Exception as e:
                        print(e)
        else:
            print("Orders not filled yet!")

# oco (One Cancels Other) stop limit and profit limit order after market order
def order_v4(api):
        positions = api.list_positions()
        if positions is not None:
            for position in positions:
                if position.side == 'long':
                    try:
                        api.submit_order(
                            symbol=position.symbol,
                            qty=float(position.qty),
                            side='sell',
                            type='limit',
                            time_in_force='day',
                            limit_price=float(position.current_price) * 0.99
                        )
                    except Exception as e:
                        print(e)
                elif position.side == 'short':
                    try:
                        api.submit_order(
                            symbol=position.symbol,
                            qty=float(position.qty),
                            side='buy',
                            type='limit',
                            time_in_force='day',
                            limit_price=float(position.current_price) * 1.01
                        )
                    except Exception as e:
                        print(e)
        else:
            print("Orders not filled yet!")

# close all positions
def close(api):
    positions = api.close_all_positions()
    for position in positions:    
        if position.status == 200:
            print("All positions closed")
        else:
            print("Something went wrong!")