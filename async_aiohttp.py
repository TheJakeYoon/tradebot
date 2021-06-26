import asyncio, aiohttp
import pandas as pd

async def get_APIdata(session, url, datas):
    async with session.get(url) as response:
        result = await response.json()
        ticker = result['ticker']
        try:
            datas[ticker] = result['marketcap']
        except Exception as e:
            print(ticker)

async def scan():
    df = pd.read_csv('./data/tickers/polygon_list.csv')

    tickers = df['ticker'].tolist()

    datas = {}

    async with aiohttp.ClientSession() as session:
        tasks = []
        for ticker in tickers:
            url = ""
            task = asyncio.ensure_future(get_APIdata(session, url, datas))
            tasks.append(task)
        #tasks = [asyncio.ensure_future(get_marketcap(session, ticker, marketcap)) for ticker in tickers]
        await asyncio.gather(*tasks)

    return datas
