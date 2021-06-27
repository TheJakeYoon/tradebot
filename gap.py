import pandas as pd
import requests, math, asyncio, aiohttp
import profile, market_day

# asyncio method to get polyon data faster
async def get_APIdata(session, url, close_price, gap):
    async with session.get(url) as response:
        result = await response.json()
        try:
            ticker = result['results']['T']
            current_price = result['results']['p']
            pct = round(((current_price - close_price) / close_price) * 100, 2)
            gap.append({'ticker' : ticker, 'current_price' : current_price, 'close_price' : close_price, 'pct': pct})
        except Exception as e:
            #print(url)
            pass

# gets previous day's close and calls get_APIdata()
async def get_gap(prev_closes):
    gap = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for prev_close in prev_closes:
            url = "https://api.polygon.io/v2/last/trade/{}?&apiKey={}".format(prev_close['ticker'], profile.POLYGON_API_KEY)
            task = asyncio.ensure_future(get_APIdata(session, url, prev_close['close_price'], gap))
            tasks.append(task)
        await asyncio.gather(*tasks)

    return gap

def get_close():
    files = pd.read_csv('./data/tickers/smaller_polygon_list.csv')['ticker'].tolist()

    prev_closes = []

    for file in files:
        file = "./data/historical/polygon_daily/{}.csv".format(file)
        try:
            df = pd.read_csv(file)
        except Exception as e:
            #print(file)
            pass
        try:
            prev_day = market_day.prev_open()
            volume = df.loc[df['date'] == prev_day]['volume'].iloc[-1]
            # only scans for stocks with higher than daily volume of 1 million.
            if volume > 1000000:
                close_price = df.loc[df['date'] == prev_day]['close'].iloc[-1]
                ticker = file.replace('./data/historical/polygon_daily/', '')
                ticker = ticker.replace('.csv', '')
                prev_closes.append({'ticker' : ticker, 'close_price' : close_price})
        except Exception as e:
            #print(e)
            pass

    return prev_closes

# Scans for stocks
# If S&P is up, looks for gap downs
# If S&P is down, looks for gap ups
# 2-8% change and no news
def scan(api, prev_closes):
    gaps = asyncio.run(get_gap(prev_closes))

    df = pd.DataFrame(gaps)
    # print(df.info())
    # print(df)

    # checks if S&P 500 is up or down
    url = "https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/SPY?&apiKey={}".format(profile.POLYGON_API_KEY)
    response = requests.get(url).json()
    market_up = True
    try:
        # checks if S&P500 is up
        spy_open = response['ticker']['prevDay']['c']
        spy_current = response['ticker']['lastTrade']['p']
        if spy_current - spy_open > 0:
            market_up = True
        else:
            market_up = False
    except Exception as e:
        print(e)
        print("Couldn't check if SPY was up or down")
    df.sort_values(by = 'pct', inplace = True, ascending = market_up)
    if market_up:
        df = df.loc[(df['pct'] > -7) & (df['pct'] < -2)]
    else:
        df = df.loc[(df['pct'] > 2) & (df['pct'] < 7)]
    tickers = df.to_dict('records')

    gappers = []
    count = 0

    for i in range(len(tickers)):
        date = market_day.prev_open()
        # check for news
        url = "https://api.polygon.io/v2/reference/news?limit=3&order=descending&sort=published_utc&ticker={}&published_utc.gte={}&apiKey={}".format(tickers[i]['ticker'], date, profile.POLYGON_API_KEY)
        response = requests.get(url).json()
        # only pick 10 stocks
        if not response['results'] and count < 10:
            #print(response)
            if market_up:
                tickers[i]['side'] = 'buy'
            else:
                tickers[i]['side'] = 'sell'
            gappers.append(tickers[i])
            count += 1
        else:
            pass
            # print("News released {}".format(tickers[i]['ticker']))

    # print(gappers)

    return gappers

def order(api, tickers):

    account = api.get_account()
    initial_cash = float(account.buying_power)

    for ticker in tickers:

        price = float(api.get_last_trade(ticker['ticker']).price)
        limit_price = 0.0
        if ticker['side'] == 'buy':
            limit_price = price * 1.01
        elif ticker['side'] == 'sell':
            limit_price = price * 0.99
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
                            stop_loss={'stop_price': float(position.avg_entry_price) * 1.03},
                            take_profit={'limit_price': float(position.avg_entry_price) * 0.96}
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
                            stop_loss={'stop_price': float(position.avg_entry_price) * 0.97},
                            take_profit={'limit_price': float(position.avg_entry_price) * 1.04}
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