import alpaca_trade_api as tradeapi
import time
import gap_test, profile, market_day

#TRADE BOT
if __name__ == '__main__':

    #Prevents the computer from sleeping MAC ONLY!
    #caffeine.on()

    # First, open the API connection
    api = tradeapi.REST(
        profile.APCA_API_PAPER_KEY_ID,
        profile.APCA_API_PAPER_SECRET_KEY,
        profile.APCA_API_PAPER_BASE_URL
    )

    # run forever!
    while True:
        print("Trading Bot Started!")
        print(market_day.now())

        if api.get_clock().is_open:
            print("Market Open!")
            print(market_day.now())
        else:
            print("Market Closed")
            print(market_day.now())

        prev_closes = gap_test.get_close()
        tickers = gap_test.scan(api, prev_closes)
        print(tickers)

        market_time = market_day.now()
        while market_time != "09:30":
            market_time = market_day.now()

        if api.get_clock().is_open:
            print("Scanning for stocks")
            tickers = gap_test.scan(api, prev_closes)

            print("Ordering now")
            gap_test.order(api, tickers)

            print("Order finished Done!")

            time.sleep(10)

            #Place stop limit and take profit order
            gap_test.order_v2(api)

            time.sleep(5400)

            api.cancel_all_orders()
            time.sleep(10)
            
            # place smaller profit limit order
            gap_test.order_v3(api)

            while api.list_positions() is not None and market_time != "12:01":
                time.sleep(10)
                market_time = market_day.now()
                if market_time == "12:00":
                    pass
                    #Strategy specific!!!!!!
                    gap_test.order_v4(api)

            time.sleep(1800)

            api.cancel_all_orders()
            gap_test.close(api)

            print("All positions closed now")

            #Wait until after hour closed
            print("Waiting for after hour to close")
            while market_time != "20:05":
                time.sleep(10)
                market_time = market_day.now()
