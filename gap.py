import pandas as pd
import math, asyncio, aiohttp
import profile, market_day

# asyncio methods to get polyon data faster

# gets the last traded price of a ticker
async def get_APIdata(session, url, prev_close, gap):
    async with session.get(url) as response:
        try:
            result = await response.json()
            current_price = result['results']['p']
            close_price = prev_close['close_price']
            pct = round(((current_price - close_price) / close_price) * 100, 2)
            prev_close['current_price'] = current_price
            prev_close['pct'] = pct
            gap.append(prev_close)
        except Exception as e:
            #print(url)
            pass

# gets last traded prices for all tickers
async def get_gap(prev_closes):
    gap = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for prev_close in prev_closes:
            url = "https://api.polygon.io/v2/last/trade/{}?&apiKey={}".format(prev_close['ticker'], profile.POLYGON_API_KEY)
            task = asyncio.ensure_future(get_APIdata(session, url, prev_close, gap))
            tasks.append(task)
        await asyncio.gather(*tasks)
    return gap

# gets previous market day's closing price
def get_close():
    files = pd.read_csv('./data/tickers/assets_list.csv')['ticker'].tolist()

    prev_closes = []
    prev_day = market_day.prev_open()
    print("Getting {}'s Close".format(prev_day))

    for file in files:
        file = "./data/historical/polygon_daily/{}.csv".format(file)
        try:
            df = pd.read_csv(file)
        except Exception as e:
            # print(file)
            pass
        try:
            df = df.loc[df['date'] == prev_day]
            volume = df['volume'].iloc[-1]
            close_price = df['close'].iloc[-1]
            low_price = df['low'].iloc[-1]
            high_price = df['high'].iloc[-1]
            # only scans for stocks with higher than daily volume of 1 million.
            if volume > 500000 and close_price > 10:
                ticker = file.replace('./data/historical/polygon_daily/', '')
                ticker = ticker.replace('.csv', '')
                prev_closes.append({'ticker' : ticker, 'close_price' : close_price, 'prev_low' : low_price, 'prev_high' : high_price})
        except Exception as e:
            # print(e)
            # print("Make sure to get previous open close")
            pass
    return prev_closes

# Scans for stocks
# 2-5% change
def scan(api, prev_closes):
    gaps = asyncio.run(get_gap(prev_closes))

    df = pd.DataFrame(gaps)
    # print(df.info())
    # print(df)
    df_down = df[(df['pct'] > -5) & (df['pct'] < -2)]
    df_down = df_down[df_down['prev_low'] < df_down['current_price']]
    df_down.sort_values(by = 'pct', inplace = True, ascending = True)
    # df = pd.DataFrame(gaps)
    df_up = df[(df['pct'] > 2) & (df['pct'] < 5)]
    df_up = df_up[df_up['prev_high'] > df_up['current_price']]
    df_up.sort_values(by = 'pct', inplace = True, ascending = False)
    tickers_down = df_down.to_dict('records')
    tickers_up = df_up.to_dict('records')

    gappers = []

    count = 0
    for ticker in tickers_down:
        # date = market_day.prev_open()
        # # check for news
        # url = "https://api.polygon.io/v2/reference/news?limit=3&order=descending&sort=published_utc&ticker={}&published_utc.gte={}&apiKey={}".format(ticker['ticker'], date, profile.POLYGON_API_KEY)
        # response = requests.get(url).json()
        # only pick 10 stocks
        if count < 10:
            # if not response['results']:
                # print("No news")
                ticker['side'] = 'buy'
                gappers.append(ticker)
                count += 1
            # else:
            #     pass
                # print("News released {}".format(tickers[i]['ticker']))
        else:
            break

    # print(len(tickers_up))
    count = 0
    for ticker in tickers_up:
        # date = market_day.prev_open()
        # # check for news
        # url = "https://api.polygon.io/v2/reference/news?limit=3&order=descending&sort=published_utc&ticker={}&published_utc.gte={}&apiKey={}".format(ticker['ticker'], date, profile.POLYGON_API_KEY)
        # response = requests.get(url).json()
        # only pick 10 stocks
        if count < 10:
            # if not response['results']:
                # print("No news")
                ticker['side'] = 'sell'
                gappers.append(ticker)
                count += 1
            # else:
            #     # print("News released {}".format(tickers_up[i]['ticker']))
            #     pass
        else:
            break

    # print(gappers)
    return gappers

def order(api, tickers):
    # account = api.get_account()
    # initial_cash = float(account.buying_power)
    initial_cash = 2000
    position_size = initial_cash / len(tickers)

    for ticker in tickers:
        # price = float(api.get_last_trade(ticker['ticker']).price)
        price = ticker['current_price']
        limit_price = 0.0
        if ticker['side'] == 'buy':
            limit_price = price * 1.01
        elif ticker['side'] == 'sell':
            limit_price = price * 0.99
        qty = math.floor(position_size / price)

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
def order_v2(api, tickers):
        print("Order_v2")
        df = pd.DataFrame(tickers)
        positions = api.list_positions()
        if positions is not None:
            for position in positions:
                try:
                    pct = abs(df[(df['ticker'] == position.symbol.upper())]['pct'].iloc[-1])
                    if position.side == 'long':
                            api.submit_order(
                                symbol=position.symbol,
                                qty=abs(float(position.qty)),
                                side='sell',
                                type='limit',
                                time_in_force='day',
                                order_class='oco',
                                stop_loss={'stop_price': float(position.avg_entry_price) * (1 - (pct/100))},
                                take_profit={'limit_price': float(position.avg_entry_price) * (1 + (pct/200))}
                            )
                            print("Profit/Loss Order Placed!")
                    elif position.side == 'short':
                            api.submit_order(
                                symbol=position.symbol,
                                qty=abs(float(position.qty)),
                                side='buy',
                                type='limit',
                                time_in_force='day',
                                order_class='oco',
                                stop_loss={'stop_price': float(position.avg_entry_price) * (1 + (pct/100))},
                                take_profit={'limit_price': float(position.avg_entry_price) * (1 - (pct/200))}
                            )
                            print("Profit/Loss Order Placed!")
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
                            qty=abs(float(position.qty)),
                            side='sell',
                            type='limit',
                            time_in_force='day',
                            order_class='oco',
                            stop_loss={'stop_price': float(position.avg_entry_price) * 0.98},
                            take_profit={'limit_price': float(position.avg_entry_price) * 1.02}
                        )
                        print("Profit/Loss Order Updated!")
                    except Exception as e:
                        print(e)
                elif position.side == 'short':
                    try:
                        api.submit_order(
                            symbol=position.symbol,
                            qty=abs(float(position.qty)),
                            side='buy',
                            type='limit',
                            time_in_force='day',
                            order_class='oco',
                            stop_loss={'stop_price': float(position.avg_entry_price) * 1.02},
                            take_profit={'limit_price': float(position.avg_entry_price) * 0.98}
                        )
                        print("Profit/Loss Order Updated!")
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
                            qty=abs(float(position.qty)),
                            side='sell',
                            type='limit',
                            time_in_force='day',
                            limit_price=float(position.current_price) * 0.99
                        )
                        print("Profit/Loss Order Updated Again!")
                    except Exception as e:
                        print(e)
                elif position.side == 'short':
                    try:
                        api.submit_order(
                            symbol=position.symbol,
                            qty=abs(float(position.qty)),
                            side='buy',
                            type='limit',
                            time_in_force='day',
                            limit_price=float(position.current_price) * 1.01
                        )
                        print("Profit/Loss Order Updated Again!")
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