from datetime import date
from datetime import timedelta
from datetime import datetime
from pytz import timezone
import trading_calendars
import pandas as pd

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