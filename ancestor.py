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
        start_time_1 = datetime(now.year, now.month, now.day, 9, 25)
        end_time_1 = datetime(now.year, now.month, now.day, 10, 25)

        start_time_2 = datetime(now.year, now.month, now.day, 11, 28)
        end_time_2 = datetime(now.year, now.month, now.day, 13, 3)

        start_time_3 = datetime(now.year, now.month, now.day, 14, 5)
        end_time_3 = datetime(now.year, now.month, now.day, 15, 1)

        if start_time_1 <= now <= end_time_1 or start_time_2 <= now <= end_time_2 or start_time_3 <= now <= end_time_3:
        # if start_time_1 <= now <= end_time_1 or start_time_3 <= now <= end_time_3:
            return True
        return False

    def notify(self, email, code):
        sender = EmailSender("xcg19865@126.com", "HIPJLVTIFUZQKEYB", server='smtp.126.com', port=465)
        sender.set_header(code)
        sender.add_text(code)
        # sender.add_receiver("xucg025@qq.com")
        sender.add_receiver(email)
        sender.send()
