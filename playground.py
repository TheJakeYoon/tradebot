from datetime import datetime
import alpaca_trade_api as tradeapi
import pytz, requests, json, time
import pandas as pd
import market_day, gap, profile, kakao, performance, telegram_bot

start = datetime.now()

api = tradeapi.REST(
        profile.APCA_API_KEY_ID,
        profile.APCA_API_SECRET_KEY,
        profile.APCA_API_BASE_URL
    )

# prev_closes = gap.get_close()

print(datetime.now() - start)
start = datetime.now()

# tickers = gap.scan(api, prev_closes)
# print(tickers)
# print(datetime.now() - start)
# start = datetime.now()

gap.order_v3(api)
# telegram_bot.send_message("Order Finished")

# get runtime
print(datetime.now() - start)

# df = pd.read_csv("./data/backtest/results/backtest_2.csv")
# avg_pct = df['pct'].sum() / len(df.index)
# print(avg_pct)