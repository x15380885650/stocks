from data_source_ef import EfDataSource
from email_util.email_sender import EmailSender
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
        start_time_1 = datetime(now.year, now.month, now.day, 9, 30)
        end_time_1 = datetime(now.year, now.month, now.day, 11, 30)

        start_time_2 = datetime(now.year, now.month, now.day, 13, 00)
        end_time_2 = datetime(now.year, now.month, now.day, 15, 00)

        if start_time_1 <= now <= end_time_1 or start_time_2 <= now <= end_time_2:
            return True
        return False

    def notify(self, code):
        email = EmailSender("xcg19865@126.com", "HIPJLVTIFUZQKEYB", server='smtp.126.com', port=465)
        email.set_header(code)
        email.add_text(code)
        email.add_receiver("xucg025@qq.com")
        email.send()
