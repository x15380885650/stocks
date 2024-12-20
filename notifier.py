import time
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime
from code_fetcher import CodeFetcher
from date_chooser import DateChooser
from ancestor import Ancestor


class Notifier(Ancestor):
    def __init__(self, key_prefix):
        self.key_prefix = key_prefix
        self.is_trade_time_forbidden = True
        super(Notifier, self).__init__(key_prefix=key_prefix)

    def run(self):
        print(f'is_trade_time_forbidden: {self.is_trade_time_forbidden}')
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
                # trade_ok = True
                if not trade_ok:
                    time.sleep(1)
                    continue

                start_date_str, end_date_str = d_chooser.get_start_and_end_date()
                self.persister.clear_monitor_code_list_except_date(end_date_str)
                monitor_code_list = self.persister.get_monitor_code_list(end_date_str)
                buy_code_list = self.persister.get_buy_code_list()
                if not monitor_code_list and not buy_code_list:
                    time.sleep(1)
                    continue
                code_dict = {}
                for monitor_code in monitor_code_list:
                    code_dict[monitor_code] = 0
                for buy_code in buy_code_list:
                    code_dict[buy_code] = 1
                all_code_list = list(code_dict.keys())
                min_pct_chg_notifier = self.persister.get_min_pct_chg_notifier()
                min_pct_chg_monitor = self.persister.get_min_pct_chg_monitor()
                sleep_time = self.persister.get_sleep_time_notifier()
                stock_list_kline_list = c_fetcher.get_stock_list_kline_list(all_code_list, end_date_str, end_date_str)
                sorted_stock_list_kline_list = sorted(
                    stock_list_kline_list, key=lambda k_line: k_line[-1]['pct_chg'], reverse=True)
                monitor_code_show_count = 0
                monitor_code_show_count_max = self.persister.get_max_monitor_show_count()
                print('monitor_code_list_count: {}, monitor_code_show_count_max: {}'
                      .format(len(monitor_code_list), monitor_code_show_count_max))
                for stock_kline_list in sorted_stock_list_kline_list:
                    code = stock_kline_list[-1]['code']
                    name = stock_kline_list[-1]['name']
                    pct_chg = stock_kline_list[-1]['pct_chg']
                    buy_flag = code_dict[code]
                    if code in monitor_code_list and pct_chg < min_pct_chg_monitor:
                        self.persister.remove_monitor_code(end_date_str, code)
                        print(f'code: {code} pct_chg:{pct_chg} < min_pct_chg_monitor: {min_pct_chg_monitor}, removed...')
                        continue
                    if buy_flag == 1:
                        print('code: {}, name: {}, pct_chg: {}, bought: {}'.format(code, name, pct_chg, buy_flag))
                    elif monitor_code_show_count < monitor_code_show_count_max:
                        if pct_chg > 0:
                            now_price = stock_kline_list[-1]['close']
                            prev_close = round(now_price / (1 + pct_chg/100), 2)
                            buy_price = round(prev_close * (1 + min_pct_chg_notifier/100), 2)
                            print('code: {}, name: {}, pct_chg: {}, now_price: {}, buy_price: {}, pct_chg_notifier: {}, bought: {}'
                                  .format(code, name, pct_chg, now_price, buy_price, min_pct_chg_notifier, buy_flag))
                            monitor_code_show_count += 1
                    if pct_chg < min_pct_chg_notifier or code in buy_code_list:
                        continue
                    if pct_chg >= min_pct_chg_notifier + 1:
                        continue
                    now_time_forbidden = self.is_now_time_forbidden()
                    if self.is_trade_time_forbidden and now_time_forbidden:
                        continue
                    email_dict = self.persister.get_email_dict()
                    for email, enabled in email_dict.items():
                        print(email, enabled)
                        code_from = '{}({})'.format(code, self.key_prefix)
                        if int(enabled):
                            self.notify(email=email, code=code_from)
                    self.persister.save_code_to_notifier(end_date_str, code)
            except Exception as e:
                print(e)
            print('now: {}, sleep: {}'.format(datetime.now(), sleep_time))
            time.sleep(sleep_time)
