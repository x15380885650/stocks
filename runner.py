from data_source_ef import EfDataSource
from email_helper import EmailSender


class Runner(object):
    def __init__(self):
        self.ds = EfDataSource()
        self.stock_days = 30 * 6

    def notify(self, code):
        email = EmailSender("xcg19865@126.com", "HIPJLVTIFUZQKEYB", server='smtp.126.com')
        email.set_header(code)
        email.add_text(code)
        # email.add_receiver("531309575@qq.com")
        email.add_receiver("xucg025@qq.com")
        email.send()
