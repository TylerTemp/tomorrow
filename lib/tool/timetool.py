import datetime
import tzlocal
import datetime
timezone = tzlocal.get_localzone()


def w3c_datetime_full(timestamp):
    time_obj = datetime.datetime.fromtimestamp(timestamp, timezone)
    return time_obj.isoformat()


def timestamp_readable(timestamp):
    return datetime.datetime.fromtimestamp(
        timestamp, 
        timezone
    ).strftime('%Y-%m-%d %H:%M:%S')


if __name__ == '__main__':
    s = 1464512407.3335524
    print(w3c_datetime_full(s))
