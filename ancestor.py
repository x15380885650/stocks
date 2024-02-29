from data_source_ef import EfDataSource

from persister import Persister


class Ancestor(object):
    def __init__(self, key_prefix):
        self.ds = EfDataSource()
        self.stock_days = 30 * 6
        self.persister = Persister(key_prefix)

    def is_trade(self):
        from datetime import datetime
        import calendar
        now = datetime.now()
        day_of_week = calendar.weekday(now.year, now.month, now.day)
        # print(day_of_week, now)
        if not 0 <= day_of_week <= 4:
            return False
        start_time = datetime(now.year, now.month, now.day, 9, 30)
        end_time = datetime(now.year, now.month, now.day, 15, 0)
        if not start_time <= now <= end_time:
            return False
        return True