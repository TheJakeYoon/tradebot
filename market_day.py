from datetime import datetime
from datetime import date
from datetime import timedelta
import pytz, random
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

def next_open(date = datetime.utcnow()):
    date = "{} 16:00".format(date)
    xnys = trading_calendars.get_calendar("XNYS")
    next_open = xnys.next_open(pd.Timestamp(date, tz='US/Eastern'))
    return next_open.strftime("%Y-%m-%d")

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
    return time.strftime("%Y-%m-%d %H:%M")

def next_minute(time):
    split = time.split(" ", 2)
    split_2 = split[1].split(":", 2)

    if split_2[1] == "59":
        split_2[1] = "00"
        hour = int(split_2[0])
        hour += 1
        return "{} {:02d}:{}".format(split[0], hour, split_2[1])
    else:
        minute = int(split_2[1])
        minute += 1
        return "{} {}:{:02d}".format(split[0], split_2[0], minute)

def random_date():
    start_date = date(2019, 1, 1)
    end_date = date(2021, 7, 1)

    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)

    random_date = next_open(random_date)
    return random_date