from datetime import datetime
import alpaca_trade_api as tradeapi
import pytz, requests, json, time
import pandas as pd
import market_day, datamine, gap, profile, kakao, performance

start = datetime.now()

api = tradeapi.REST(
        profile.APCA_API_KEY_ID,
        profile.APCA_API_SECRET_KEY,
        profile.APCA_API_BASE_URL
    )

prev_closes = gap.get_close()

print(datetime.now() - start)
start = datetime.now()

tickers = gap.scan(api, prev_closes)

# get runtime
print(datetime.now() - start)