from datetime import datetime, timedelta


class DateChooser(object):
    def __init__(self, ds, delta_days):
        self.ds = ds
        self.delta_days = delta_days
        self.format_date = '%Y-%m-%d'

    def is_deal_date(self, t_date):
        # return True
        # t_holiday = is_holiday(t_date)
        # if t_holiday:
        #     return False
        day_of_week = t_date.weekday() + 1
        if day_of_week in [6, 7]:
            return False
        return True

    def get_start_and_end_date(self, _end_date=None, is_str=True):
        end_date = self.ds.get_end_date() if not _end_date else _end_date
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, self.format_date)
        while True:
            deal_date_ok = self.is_deal_date(end_date)
            if not deal_date_ok:
                end_date = end_date - timedelta(days=1)
            else:
                break
        start_date = end_date - timedelta(days=self.delta_days)
        if is_str:
            return start_date.strftime(self.format_date), end_date.strftime(self.format_date)
        else:
            return start_date, end_date
