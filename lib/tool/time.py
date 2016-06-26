import datetime
import tzlocal

timezone = tzlocal.get_localzone()


def w3c_datetime_full(timestamp):
    time_obj = datetime.datetime.fromtimestamp(timestamp, timezone)
    return time_obj.isoformat()


if __name__ == '__main__':
    s = 1464512407.3335524
    print(w3c_datetime_full(s))
