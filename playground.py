from datetime import datetime
import alpaca_trade_api as tradeapi
import pytz, requests, json
import pandas as pd
import market_day, datamine, gap, profile, kakao, performance

# est = pytz.timezone('America/New_York')
# market_time = datetime.now(est).strftime("%H:%m")
# print(market_time)
# start = datetime.now()
api = tradeapi.REST(
        profile.APCA_API_KEY_ID,
        profile.APCA_API_SECRET_KEY,
        profile.APCA_API_BASE_URL
    )

# gap.close(api)
# gap.init(api)

#print(gap.scan(api))


# # get runtime
# print(datetime.now() - start)

# kakao.send_message("hi")

performance.summary(api)
