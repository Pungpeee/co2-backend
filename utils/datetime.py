from datetime import datetime, timedelta

from django.conf import settings


def convert_timedelta_to_float(td):
    year = int(td.days / 365)
    month = int((td.days - (year * 365)) / 31) / 100
    return year + month


def convert_float_to_timedelta(data):
    year, month = str(float(data)).split('.')
    return timedelta(seconds=(int(year) * 365 * 24 * 60 * 60) + (int(month) * 30 * 24 * 60 * 60))


def is_valid_date(year, month, day):
    is_valid = True
    try:
        d = datetime.date(int(year), int(month), int(day))
    except ValueError as e:
        is_valid = False
    return is_valid


def convert_to_local(utc_time):
    from dateutil import tz
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz(settings.TIME_ZONE)

    try:
        utc = utc_time.replace(tzinfo=from_zone)
    except:
        return None
    return utc.astimezone(to_zone)


def duration_format(duration, is_second_included=False):
    try:
        s = duration.total_seconds()
    except:
        s = 0

    if s < 0:
        s = 0

    h, r = divmod(s, 3600)
    m, s = divmod(r, 60)

    if h > 0:
        return '%d:%02d' % (h, m) if not is_second_included else '%d:%02d:%02d' % (h, m, s)
    else:
        return '00:%02d' % m if not is_second_included else '00:%02d:%02d' % (m, s)


def get_date(str_date):
    try:
        return datetime.strptime(str_date, '%Y-%m-%d').date()
    except:
        return None
