import alpaca_trade_api as tradeapi
from datetime import date, datetime
import time, caffeine, csv, pytz
import gap, profile, datamine, telegram_bot, market_day

#TRADE BOT
if __name__ == '__main__':

    #Prevents the computer from sleeping
    caffeine.on(display=True)

    print("Trade Bot awake")

    print("Using gap strategy")

    #kakao.send_message("I will trade using gap strategy")

    # First, open the API connection
    api = tradeapi.REST(
        profile.APCA_API_KEY_ID,
        profile.APCA_API_SECRET_KEY,
        profile.APCA_API_BASE_URL
    )

    gap.init(api)

    est = pytz.timezone('America/New_York')
    market_time = datetime.now(est).strftime("%H:%M")
    print(market_time)

    if api.get_clock().is_open:
        print("Market Open!")
        print(datetime.now(est).strftime("%H:%M"))
    else:
        print("Market Closed")
        print(datetime.now(est).strftime("%H:%M"))

    while not market_time == "09:30":
        market_time = datetime.now(est).strftime("%H:%M")
        #print(market_time)

    print("Scanning for stocks")
    tickers = gap.scan(api)

    print("Ordering now")
    gap.order(api, tickers)

    print("Order finished Done!")

    telegram_bot.send_message("Order Finished")

    time.sleep(10)

    #Place stop limit and take profit order
    gap.over_v2(api)

    while api.get_clock().is_open or api.list_positions() is not None:
        time.sleep(10)
        est = pytz.timezone('America/New_York')
        market_time = datetime.now(est).strftime("%H:%M")
        if market_time == "12:00":
            #Strategy specific!!!!!!
            gap.close(api)

    print("All positions closed now")
    telegram_bot.send_message("All positions closed now!")

    #Saves and prints daily performance        
    summary(api)

    #Including after hour trading
    market_closed = False

    #Wait until market completely closed
    print("Waiting for after hour to close")
    while not market_closed:
        time.sleep(10)
        est = pytz.timezone('America/New_York')
        market_time = datetime.now(est).strftime("%H:%M")
        if market_time == "20:05":
            market_closed = True


    #get daily open close from Polygon.io
    datamine.get_open_close()
    telegram_bot.send_message("Stored daily open/close from Polyon.io")