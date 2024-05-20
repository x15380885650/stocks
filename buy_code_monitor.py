import time
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime
from code_fetcher import CodeFetcher
from date_chooser import DateChooser
from ancestor import Ancestor


class BuyCodeMonitor(Ancestor):
    def __init__(self):
        super(BuyCodeMonitor, self).__init__(key_prefix='buy_code_monitor')

    def run(self):
        sleep_time = 0
        c_fetcher = CodeFetcher(ds=self.ds)
        d_chooser = DateChooser(ds=self.ds, delta_days=self.stock_days)

        while True:
            try:
                is_stop = self.persister.get_stop_status()
                if is_stop:
                    print('script stop, exit!!!')
                    return

                trade_ok = self.is_trade_2()
                # trade_ok = True
                if not trade_ok:
                    time.sleep(1)
                    continue

                start_date_str, end_date_str = d_chooser.get_start_and_end_date()
                buy_code_list = self.persister.get_buy_code_list()
                if not buy_code_list:
                    time.sleep(1)
                    continue
                code_dict = {}
                for buy_code in buy_code_list:
                    code_dict[buy_code] = 1
                all_code_list = list(code_dict.keys())
                sleep_time = self.persister.get_sleep_time_notifier()
                stock_list_kline_list = c_fetcher.get_stock_list_kline_list(all_code_list, end_date_str, end_date_str)
                sorted_stock_list_kline_list = sorted(
                    stock_list_kline_list, key=lambda k_line: k_line[-1]['pct_chg'], reverse=True)
                for stock_kline_list in sorted_stock_list_kline_list:
                    code = stock_kline_list[-1]['code']
                    name = stock_kline_list[-1]['name']
                    pct_chg = stock_kline_list[-1]['pct_chg']
                    print('code: {}, name: {}, pct_chg: {}'.format(code, name, pct_chg))
            except Exception as e:
                print(e)
            print('now: {}, sleep: {}'.format(datetime.now(), sleep_time))
            time.sleep(sleep_time)


if __name__ == '__main__':
    monitor = BuyCodeMonitor()
    monitor.run()
