from data_source_ef import EfDataSource
from email_util.email_sender import EmailSender


class Runner(object):
    def __init__(self):
        self.ds = EfDataSource()
        self.stock_days = 30 * 6

    def notify(self, code):
        email = EmailSender("xcg19865@126.com", "HIPJLVTIFUZQKEYB", server='smtp.126.com', port=465)
        email.set_header(code)
        email.add_text(code)
        # email.add_receiver("531309575@qq.com")
        email.add_receiver("xucg025@qq.com")
        email.send()

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
