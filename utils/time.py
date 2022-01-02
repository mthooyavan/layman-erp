from datetime import datetime, timedelta, time

import pytz
from pytz import UnknownTimeZoneError
from pytz import timezone as py_timezone

DATETIME_ISO_FORMAT = '%Y-%m-%dT%H:%M:%S.00Z'


def combine_time(time, delta, time_zone=pytz.utc):
    today = datetime.now(time_zone).today()
    return (datetime.combine(today, time) + delta).time()


def time_12_hour(date_or_time):
    return date_or_time.strftime("%-I:%M%p").replace('AM', 'am').replace('PM', 'pm')


def time_12_hour_only(date_or_time):
    return date_or_time.strftime("%-I%p").replace('AM', 'am').replace('PM', 'pm')


def is_usa_dst():
    """
    Determine whether or not Daylight Savings Time (DST)
    is currently in effect for the US - EST is alright as all states are in or out
    """

    first = datetime(datetime.now().year, 1, 1, 0, 0, 0,
                     tzinfo=pytz.timezone('US/Eastern'))  # Jan 1 of this year
    now = datetime.now(pytz.timezone('US/Eastern'))

    # if DST is in effect, their offsets will be different
    return first.utcoffset() != now.utcoffset()


def convert_timezone(date_time: datetime, from_: pytz.tzinfo, to_: pytz.tzinfo) -> datetime:
    """
    converts date_time from `from_` timezone to `to_` timezone
    """
    date_time = date_time.replace(tzinfo=None)
    return from_.localize(date_time, is_dst=is_usa_dst()).astimezone(to_)


def convert_to_utc(date_time: datetime, from_: pytz.tzinfo) -> datetime:
    """
    converts date_time from `from_` timezone to UTC
    """
    return convert_timezone(date_time, from_, pytz.utc)


def convert_from_utc(date_time: datetime, to_: pytz.tzinfo) -> datetime:
    """
    converts date_time from UTC timezone to `to_` timezone
    """
    return convert_timezone(date_time, pytz.utc, to_)


def convert_to_utc_iso_string(date_time):
    """
    # converts a datetime to utc and then formats ISO8601 (RFC 3339):
    # example 2012-01-14T13:00:00.00Z
    """
    return pytz.utc.normalize(date_time).strftime(DATETIME_ISO_FORMAT)


def convert_to_milliseconds(date_time: datetime) -> int:
    """takes datetime and returns milliseconds"""
    return round(date_time.timestamp() * 1000)


def convert_from_milliseconds(milliseconds: int) -> datetime:
    """takes milliseconds and returns datetime"""
    return datetime.utcfromtimestamp(milliseconds//1000).replace(
        microsecond=milliseconds%1000*1000).astimezone(pytz.utc)


def subtract_month_from_date(cutoff):
    """get the first day of the previous month"""
    return cutoff.replace(
        year=cutoff.year if cutoff.month > 1 else cutoff.year - 1,
        month=cutoff.month - 1 if cutoff.month > 1 else 12,
        day=1
    )


def get_week_start_date(reference_date: datetime) -> datetime:
    """
    Gets the date for monday of the week the reference date falls in
    """
    date_shift = timedelta(
        days=reference_date.weekday()
    )
    week_start = datetime.combine(
        date=reference_date.date(),
        time=time.min,
        tzinfo=pytz.utc
    )
    return week_start - date_shift
