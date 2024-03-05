import time
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime
from code_fetcher import CodeFetcher
from date_chooser import DateChooser
from ancestor import Ancestor


class FirstNotifier(Ancestor):
    def __init__(self):
        super(FirstNotifier, self).__init__(key_prefix='monitor_1')

    def run(self):
        sleep_time = 0
        c_fetcher = CodeFetcher(ds=self.ds)
        d_chooser = DateChooser(ds=self.ds, delta_days=self.stock_days)

        while True:
            try:
                trade_ok = self.is_trade()
                if not trade_ok:
                    time.sleep(1)
                    continue
                start_date_str, end_date_str = d_chooser.get_start_and_end_date()
                monitor_code_list = self.persister.get_monitor_code_list(end_date_str)
                if not monitor_code_list:
                    time.sleep(1)
                    continue
                min_pct_chg_notifier = self.persister.get_min_pct_chg_notifier()
                sleep_time = self.persister.get_sleep_time_notifier()
                stock_list_kline_list = c_fetcher.get_stock_list_kline_list(
                    monitor_code_list, end_date_str, end_date_str)
                for stock_kline_list in stock_list_kline_list:
                    code = stock_kline_list[-1]['code']
                    pct_chg = stock_kline_list[-1]['pct_chg']
                    print('code: {}, pct_chg: {}'.format(code, pct_chg))
                    if pct_chg < min_pct_chg_notifier:
                        continue
                    self.notify(code)
                    self.persister.save_code_to_notifier(end_date_str, code)
            except Exception as e:
                print(e)
            print('now: {}, sleep: {}'.format(datetime.now(), sleep_time))
            time.sleep(sleep_time)


if __name__ == '__main__':
    notifier = FirstNotifier()
    notifier.run()