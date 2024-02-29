import time
from datetime import datetime
from email_util.email_sender import EmailSender
from code_fetcher import CodeFetcher
from date_chooser import DateChooser
from ancestor import Ancestor


class ThirdMonitor(Ancestor):
    def __init__(self):
        super(ThirdMonitor, self).__init__(key_prefix='runner_3')

    def notify(self, code):
        email = EmailSender("xcg19865@126.com", "HIPJLVTIFUZQKEYB", server='smtp.126.com', port=465)
        email.set_header(code)
        email.add_text(code)
        email.add_receiver("xucg025@qq.com")
        email.send()
        
    def run(self):
        sleep_time = 0.5
        c_fetcher = CodeFetcher(ds=self.ds)
        d_chooser = DateChooser(ds=self.ds, delta_days=self.stock_days)
        start_date_str, end_date_str = d_chooser.get_start_and_end_date()
        print('{}--->{}'.format(start_date_str, end_date_str))

        while True:
            try:
                trade_ok = self.is_trade()
                if not trade_ok:
                    time.sleep(1)
                    continue
                monitor_code_list = self.persister.get_monitor_code_list(end_date_str)
                if not monitor_code_list:
                    continue
                stock_list_kline_list = c_fetcher.get_stock_list_kline_list(
                    monitor_code_list, end_date_str, end_date_str)
                for stock_kline_list in stock_list_kline_list:
                    code = stock_kline_list[-1]['code']
                    pct_chg = stock_kline_list[-1]['pct_chg']
                    monitor_pct_chg = self.persister.get_monitor_pch_chg()
                    if pct_chg < monitor_pct_chg:
                        continue
                    self.notify(code)
                    self.persister.save_code_to_notifier(end_date_str, code)
            except Exception as e:
                print(e)
            print('now: {}, sleep: {}'.format(datetime.now(), sleep_time))
            time.sleep(sleep_time)


if __name__ == '__main__':
    monitor = ThirdMonitor()
    monitor.run()