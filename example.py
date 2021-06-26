import alpaca_trade_api as tradeapi
from alpaca_trade_api import REST
from alpaca_trade_api.rest import TimeFrame
from alpaca_trade_api import Stream
import profile, pandas
import matplotlib.pyplot as plt
from datetime import date
from datetime import timedelta


#Alpaca API

def account(api):
    # Get account info
    account = api.get_account()

    # Check if our account is restricted from trading.
    if account.trading_blocked:
        print('Account is currently restricted from trading.')

    # Check how much money we can use to open new positions.
    print('${} is available as buying power.'.format(account.buying_power))

    # Check our current balance vs. our balance at the last market close
    balance_change = float(account.equity) - float(account.last_equity)
    print(f'Today\'s portfolio balance change: ${balance_change}')

def position(api):
    # Get our position in AAPL.
    aapl_position = api.get_position('AAPL')

    # Get a list of all of our positions.
    portfolio = api.list_positions()

    # Print the quantity of shares for each position.
    if portfolio:
        for position in portfolio:
            print("{} shares of {}".format(position.qty, position.symbol))
    else:
        print("No open positions")

def historical(api):
    # Get daily price data for AAPL over the last 5 trading days.
    barset = api.get_barset('AAPL', 'day', limit=5)
    aapl_bars = barset['AAPL']

    # See how much AAPL moved in that timeframe.
    week_open = aapl_bars[0].o
    week_close = aapl_bars[-1].c
    percent_change = (week_close - week_open) / week_open * 100
    print('AAPL moved {}% over the last 5 days'.format(percent_change))

    # Get historical bar data
    data = api.get_bars('AAPL', TimeFrame.Hour, '2021-02-08', '2021-02-08', limit=100, adjustment='raw')
    print(data.df)

    # Get last bars
    barset = api.get_barset('AAPL', 'minute', limit=300)
    aapl_bar = barset['AAPL']
    print(aapl_bar.df)

def live(api):
    # Get Live Data
    async def trade_callback(t):
        print('trade', t)


    async def quote_callback(q):
        print('quote', q)


    # Initiate Class Instance
    stream = Stream(profile.APCA_API_KEY_ID,
                profile.APCA_API_SECRET_KEY,
                base_url=profile.APCA_API_BASE_URL,
                data_feed='sip')  # <- replace to SIP if you have PRO subscription

    # subscribing to event
    if api.get_clock().is_open:
        stream.subscribe_trades(trade_callback, 'AAPL')
        stream.subscribe_quotes(quote_callback, 'IBM')
        stream.run()
        print("Market is Open")
    else:
        print("Market is Closed Now")

def order(api):

    ####
    # Submit a market order to buy 1 share of Apple at market price
    api.submit_order(
        symbol='AAPL',
        qty=1,
        side='buy',
        type='market',
        time_in_force='gtc'
    )

    # Submit a limit order to attempt to sell 1 share of AMD at a
    # particular price ($20.50) when the market opens
    api.submit_order(
        symbol='AMD',
        qty=1,
        side='sell',
        type='limit',
        time_in_force='opg',
        limit_price=20.50
    )

    ####
    #Shorting
    # The security we'll be shorting
    symbol = 'TSLA'

    # Submit a market order to open a short position of one share
    order = api.submit_order(symbol, 1, 'sell', 'market', 'day')
    print("Market order submitted.")

    # Submit a limit order to attempt to grow our short position
    # First, get an up-to-date price for our symbol
    symbol_bars = api.get_barset(symbol, 'minute', 1).df.iloc[0]
    symbol_price = symbol_bars[symbol]['close']
    # Submit an order for one share at that price
    order = api.submit_order(symbol, 1, 'sell', 'limit', 'day', symbol_price)
    print("Limit order submitted.")

    # Wait a second for our orders to fill...
    print('Waiting...')
    time.sleep(1)

    # Check on our position
    position = api.get_position(symbol)
    if int(position.qty) < 0:
        print(f'Short position open for {symbol}')

    ####
    #Order ID
    # Submit a market order and assign it a Client Order ID.
    api.submit_order(
        symbol='AAPL',
        qty=1,
        side='buy',
        type='market',
        time_in_force='gtc',
        client_order_id='my_first_order'
    )

    # Get our order using its Client Order ID.
    my_order = api.get_order_by_client_order_id('my_first_order')
    print('Got order #{}'.format(my_order.id))

    ####
    #Bracket Order
    symbol = 'AAPL'
    symbol_bars = api.get_barset(symbol, 'minute', 1).df.iloc[0]
    symbol_price = symbol_bars[symbol]['close']

    # We could buy a position and add a stop-loss and a take-profit of 5 %
    api.submit_order(
        symbol=symbol,
        qty=1,
        side='buy',
        type='market',
        time_in_force='gtc',
        order_class='bracket',
        stop_loss={'stop_price': symbol_price * 0.95,
               'limit_price':  symbol_price * 0.94},
        take_profit={'limit_price': symbol_price * 1.05}
    )

    # We could buy a position and just add a stop loss of 5 % (OTO Orders)
    api.submit_order(
        symbol=symbol,
        qty=1,
        side='buy',
        type='market',
        time_in_force='gtc',
        order_class='oto',
        stop_loss={'stop_price': symbol_price * 0.95}
    )

    # We could split it to 2 orders. first buy a stock,
    # and then add the stop/profit prices (OCO Orders)
    api.submit_order(symbol, 1, 'buy', 'limit', 'day', symbol_price)

    # wait for it to buy position and then
    api.submit_order(
        symbol=symbol,
        qty=1,
        side='sell',
        type='limit',
        time_in_force='gtc',
        order_class='oco',
        stop_loss={'stop_price': symbol_price * 0.95},
        take_profit={'limit_price': symbol_price * 1.05}
    )

    ####
    #Trailing Stop
    # Submit a market order to buy 1 share of Apple at market price
    api.submit_order(
        symbol='AAPL',
        qty=1,
        side='buy',
        type='market',
        time_in_force='gtc'
    )   

    # Submit a trailing stop order to sell 1 share of Apple at a
    # trailing stop of
    api.submit_order(
        symbol='AAPL',
        qty=1,
        side='sell',
        type='trailing_stop',
        trail_price=1.00,  # stop price will be hwm - 1.00$
        time_in_force='gtc',
    )

    # Alternatively, you could use trail_percent:
    api.submit_order(
        symbol='AAPL',
        qty=1,
        side='sell',
        type='trailing_stop',
        trail_percent=1.0,  # stop price will be hwm*0.99
        time_in_force='gtc',
    )

    ####
    #Closed Orders
    # Get the last 100 of our closed orders
    closed_orders = api.list_orders(
        status='closed',
        limit=100,
        nested=True  # show nested multi-leg orders
    )

    # Get only the closed orders for a particular stock
    closed_aapl_orders = [o for o in closed_orders if o.symbol == 'AAPL']
    print(closed_aapl_orders)

    ####
    #Real Time
    conn = tradeapi.stream2.StreamConn()

    # Handle updates on an order you've given a Client Order ID.
    # The r indicates that we're listening for a regex pattern.
    client_order_id = r'my_client_order_id'
    @conn.on(client_order_id)
    async def on_msg(conn, channel, data):
        # Print the update to the console.
        print("Update for {}. Event: {}.".format(client_order_id, data['event']))

    # Start listening for updates.
    onn.run(['trade_updates'])

#TA_Lib

def moving_average(api):
    data = api.get_bars('AAPL', TimeFrame.Day, '2020-01-01', '2020-02-01', limit=50, adjustment='raw')
    data = data.df.close
    print(talib.SMA(data, timeperiod=9))
    data = data.tolist()
    print(data)

#Data Science

def plot(api):
    # Calculate mean (20 day moving average)
    data = api.get_bars('AAPL', TimeFrame.Day, '2020-01-01', '2020-02-01', limit=50, adjustment='raw')
    print(data.df.close.rolling(20).mean())
    data.df.plot()
    plt.show()

def plot_pair(api):

    data = api.get_bars('MA', TimeFrame.Day, '2020-01-01', '2020-06-01', limit=100, adjustment='raw').df
    data = data.drop(columns = ['open', 'high', 'low', 'volume'])
    data.columns = ['MA_close']
    data['V_close'] = api.get_bars('V', TimeFrame.Day, '2020-01-01', '2020-06-01', limit=100, adjustment='raw').df['close']

    #Rebasing
    for col in data:
        data[col+'_rebased'] = (data[-100:][col].pct_change() + 1).cumprod()

    #Relative Strength
    data['relative_strength'] = data['MA_close']/data['V_close']

    #Correlation
    ret1 = data['MA_close'].pct_change()
    print(ret1)
    ret2 = data['V_close'].pct_change()
    print(ret2)
    corr = ret1.rolling(10).corr(ret2)
    data['corr'] = corr

    print(data.info())
    print(data)

    fig = plt.figure(figsize=(12,8))

    ax = fig.add_subplot(411)
    ax.set_title("MA and V Comparison")
    ax.semilogy(data['V_close'], linestyle='-', label='V', linewidth=3)
    ax.semilogy(data['MA_close'], linestyle='--', label='MA', linewidth=3)
    ax.legend()

    ax = fig.add_subplot(412)
    ax.semilogy(data['V_close_rebased'], linestyle='-', label='V', linewidth=3)
    ax.semilogy(data['MA_close_rebased'], linestyle='--', label='MA', linewidth=3)
    ax.legend()

    ax = fig.add_subplot(413)
    ax.semilogy(data['relative_strength'], linestyle=':', label='Relative Strength', linewidth=3)
    ax.legend()

    ax = fig.add_subplot(414)
    ax.semilogy(data['corr'], linestyle='-.', label='Correlation', linewidth=3)

    ax.legend()
    ax.grid(False)

    plt.show()


if __name__ == '__main__':

    # First, open the API connection
    api = tradeapi.REST(
        profile.APCA_API_KEY_ID,
        profile.APCA_API_SECRET_KEY,
        profile.APCA_API_BASE_URL
    )
    date = date.today() - timedelta(days = 4)
    date = date.strftime("%Y-%m-%d")
    data = api.get_bars("AAPL", TimeFrame.Hour, date, date, limit = 10000, adjustment='raw')
    print(data.df)