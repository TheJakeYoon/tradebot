import alpaca_trade_api as tradeapi
import time
import gap, profile, market_day, datamine, telegram_bot, performance

#TRADE BOT
if __name__ == '__main__':

    #Prevents the computer from sleeping MAC ONLY!
    #caffeine.on()

    # First, open the API connection
    api = tradeapi.REST(
        profile.APCA_API_KEY_ID,
        profile.APCA_API_SECRET_KEY,
        profile.APCA_API_BASE_URL
    )

    # run forever!
    while True:
        print("Trading Bot Started!")
        print(market_day.now())
        prev_closes = gap.get_close()

        if api.get_clock().is_open:
            print("Market Open!")
            print(market_day.now())
        else:
            print("Market Closed")
            print(market_day.now())

        market_time = market_day.now()
        while not market_time == "09:30":
            market_time = market_day.now()
            #print(market_time)

        if api.get_clock().is_open:
            print("Closing all positions")
            gap.close(api)

            print("Scanning for stocks")
            tickers = gap.scan(api, prev_closes)

            print("Ordering now")
            gap.order(api, tickers)

            print("Order finished Done!")

            telegram_bot.send_message("Order Finished!")

            time.sleep(10)

            #Place stop limit and take profit order
            # gap.over_v2(api)

            while api.list_positions() is not None and market_time is not "12:01":
                time.sleep(10)
                market_time = market_day.now()
                if market_time == "12:00":
                    pass
                    #Strategy specific!!!!!!
                    # gap.close(api)

            # print("All positions closed now")
            # telegram_bot.send_message("All positions closed now!")

            #Wait until market completely closed
            print("Waiting for after hour to close")
            while market_time is not "20:05":
                time.sleep(10)
                market_time = market_day.now()

            #get daily open close from Polygon.io
            datamine.get_open_close()
            telegram_bot.send_message("Stored daily open/close from Polyon.io")

            #Saves daily performance        
            performance.summary(api)
            performance.today(api)