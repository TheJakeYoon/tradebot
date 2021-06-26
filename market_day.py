from datetime import date
from datetime import timedelta
from datetime import datetime
from pytz import timezone
import trading_calendars
import pandas as pd

def is_open():
    xnys = trading_calendars.get_calendar("XNYS")
    return xnys.is_session(pd.Timestamp(datetime.utcnow(), tz='UTC'))

def prev_open(date):
    xnys = trading_calendars.get_calendar("XNYS")
    return xnys.previous_close(pd.Timestamp(date, tz='UTC'))

def prev_open2():
    xnys = trading_calendars.get_calendar("XNYS")
    prev_close = xnys.previous_close(pd.Timestamp(datetime.utcnow(), tz='UTC'))
    return prev_close.strftime("%Y-%m-%d") 

def next_open():
    xnys = trading_calendars.get_calendar("XNYS")
    return xnys.next_open(pd.Timestamp(datetime.utcnow(), tz='UTC'))