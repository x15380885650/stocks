import time
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime
from code_fetcher import CodeFetcher
from date_chooser import DateChooser
from ancestor import Ancestor


class Notifier(Ancestor):
    def __init__(self, key_prefix):
        super(Notifier, self).__init__(key_prefix=key_prefix)

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

                trade_ok = self.is_trade()
                if not trade_ok:
                    time.sleep(1)
                    continue

                start_date_str, end_date_str = d_chooser.get_start_and_end_date()
                monitor_code_list = self.persister.get_monitor_code_list(end_date_str)
                buy_code_list = self.persister.get_buy_code_list()
                if not monitor_code_list and not buy_code_list:
                    time.sleep(1)
                    continue
                code_dict = {}
                for monitor_code in monitor_code_list:
                    code_dict[monitor_code] = '0'
                for buy_code in buy_code_list:
                    code_dict[buy_code] = '1'
                all_code_list = list(code_dict.keys())
                min_pct_chg_notifier = self.persister.get_min_pct_chg_notifier()
                sleep_time = self.persister.get_sleep_time_notifier()
                stock_list_kline_list = c_fetcher.get_stock_list_kline_list(all_code_list, end_date_str, end_date_str)
                for stock_kline_list in stock_list_kline_list:
                    code = stock_kline_list[-1]['code']
                    name = stock_kline_list[-1]['name']
                    pct_chg = stock_kline_list[-1]['pct_chg']
                    buy_txt = code_dict[code]
                    print('code: {}, name: {}, pct_chg: {}, {}'.format(code, name, pct_chg, buy_txt))
                    if pct_chg < min_pct_chg_notifier or code in buy_code_list:
                        continue
                    self.notify(code)
                    self.persister.save_code_to_notifier(end_date_str, code)
            except Exception as e:
                print(e)
            print('now: {}, sleep: {}'.format(datetime.now(), sleep_time))
            time.sleep(sleep_time)
