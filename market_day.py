from datetime import datetime
import pytz
import trading_calendars
import pandas as pd

# gets time and date of for trading days and hours
def is_open():
    xnys = trading_calendars.get_calendar("XNYS")
    return xnys.is_session(pd.Timestamp(datetime.utcnow(), tz='UTC'))

def prev_open(date = datetime.utcnow()):
    xnys = trading_calendars.get_calendar("XNYS")
    prev_open = xnys.previous_close(pd.Timestamp(date, tz='UTC'))
    return prev_open.strftime("%Y-%m-%d") 

def next_open():
    xnys = trading_calendars.get_calendar("XNYS")
    return xnys.next_open(pd.Timestamp(datetime.utcnow(), tz='UTC'))

def today():
    today = datetime.today().strftime("%Y-%m-%d")
    return today

def now():
    est = pytz.timezone('America/New_York')
    market_time = datetime.now(est).strftime("%H:%M")
    return market_time

# converts int unix timestamp to est datetime object
def timestamp_to_est(timestamp):
    tz = pytz.timezone('America/New_York')
    time = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc).astimezone(tz)
    return time