import asyncio, aiohttp, csv
import profile, market_day
import pandas as pd

async def get_APIdata(session, ticker, url):
    async with session.get(url) as response:
        with open('./data/backtest/polygon_daily/{}.csv'.format(ticker), 'a') as csvfile:
            csvwriter = csv.writer(csvfile)
            try:
                data = await response.json()
                # csvwriter.writerow(['ticker','date','open','high','low','close','volume'])
                csvwriter.writerow([data['ticker'], data['date'], data['open'], data['high'], data['low'], data['close'], data['volume']])
            except Exception as e:
                # print(ticker)
                # print(e)
                pass

async def scan(tickers, date):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for ticker in tickers:
            url = "https://api.polygon.io/v1/open-close/{}/{}?adjusted=true&apiKey={}".format(ticker, date, profile.POLYGON_API_KEY)
            task = asyncio.ensure_future(get_APIdata(session, ticker, url))
            tasks.append(task)
        #tasks = [asyncio.ensure_future(get_marketcap(session, ticker, marketcap)) for ticker in tickers]
        await asyncio.gather(*tasks)
