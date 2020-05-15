

from datetime import datetime, date, timedelta
from ..values import ANREDE, GESCHLECHT, ARTIKEL
from .helper import reverse_lookup, gibFeiertag


def mapanrede(anredecode):
    anrede = reverse_lookup(ANREDE, anredecode)
    if(anrede == None):
        anrede = ""
    return anrede


def mapgeschlecht(geschlechtscode):
    geschlecht = reverse_lookup(GESCHLECHT, geschlechtscode)
    if(geschlecht == None):
        geschlecht = ""
    return geschlecht


def mapartikel(artikelcode):
    artikel = reverse_lookup(ARTIKEL, artikelcode)
    if(artikel == None):
        artikel = ""
    return artikel


def filter_supress_none(val):
    if not val is None:
        return val
    else:
        return ''


def filter_format_date(val):
    if not val is None:
        return val.strftime("%d.%m.%Y")
    else:
        return ''


def filter_format_datetime(val):
    if not val is None:
        return val.strftime("%d.%m.%Y, %H:%M")
    else:
        return ''


def calc_kw(now):
    dt = date(now.year, now.month, now.day)

    # Determine its Day of Week, D
    # Use that to move to the nearest Thursday (-3..+3 days)
    add = 4 - dt.weekday()
    dt += timedelta(days=add)

    # Note the year of that date, Y
    # Obtain January 1 of that year
    firstofyear = date(dt.year, 1, 1)

    # Get the Ordinal Date of that Thursday, DDD of YYYY-DDD
    ydays = (dt - firstofyear).days + 1

    # Then W is 1 + (DDD-1) div 7
    return int(1 + (ydays / 7))


def add_days(dt, days):
    return dt + timedelta(days=days)


def add_hours(dt, hours):
    return dt + timedelta(hours=hours)


def add_mins(dt, mins):
    return dt + timedelta(minutes=mins)


def gib_feiertag(now):
    return gibFeiertag(now)
