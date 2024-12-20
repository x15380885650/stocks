import time
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime
from code_fetcher import CodeFetcher
from date_chooser import DateChooser
from ancestor import Ancestor


class LargeScreenMonitor(Ancestor):
    def __init__(self, key_prefix):
        self.key_prefix = key_prefix
        super(LargeScreenMonitor, self).__init__(key_prefix=key_prefix)

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
                # trade_ok = True
                if not trade_ok:
                    time.sleep(1)
                    continue

                start_date_str, end_date_str = d_chooser.get_start_and_end_date()
                monitor_code_info = self.persister.get_all_monitor_code_info(end_date_str)
                buy_code_info = self.persister.get_all_buy_code_info()
                if not monitor_code_info and not buy_code_info:
                    time.sleep(1)
                    continue
                code_dict = {}
                for monitor_code, from_monitor_list in monitor_code_info.items():
                    code_dict[monitor_code] = 0
                for buy_code, from_monitor_list in buy_code_info.items():
                    code_dict[buy_code] = 1
                all_code_list = list(code_dict.keys())
                sleep_time = self.persister.get_sleep_time_notifier()
                stock_list_kline_list = c_fetcher.get_stock_list_kline_list(all_code_list, end_date_str, end_date_str)
                sorted_stock_list_kline_list = sorted(
                    stock_list_kline_list, key=lambda k_line: k_line[-1]['pct_chg'], reverse=True)
                monitor_code_show_count = 0
                monitor_code_show_count_max = self.persister.get_max_monitor_show_count()
                for stock_kline_list in sorted_stock_list_kline_list:
                    code = stock_kline_list[-1]['code']
                    name = stock_kline_list[-1]['name']
                    pct_chg = stock_kline_list[-1]['pct_chg']
                    buy_flag = code_dict[code]
                    if buy_flag == 1:
                        from_monitor_list = buy_code_info[code]
                        print('code: {}, name: {}, pct_chg: {}, bought: {}, from: {}'
                              .format(code, name, pct_chg, buy_flag, ','.join(from_monitor_list)))
                    elif monitor_code_show_count < monitor_code_show_count_max:
                        if pct_chg > 0:
                            now_price = stock_kline_list[-1]['close']
                            prev_close = round(now_price / (1 + pct_chg/100), 2)
                            from_monitor_list = monitor_code_info[code]
                            for monitor_source in from_monitor_list:
                                min_pct_chg_notifier = self.persister.get_min_pct_chg_notifier(key_prefix=monitor_source)
                                buy_price = round(prev_close * (1 + min_pct_chg_notifier / 100), 2)
                                print('code: {}, name: {}, pct_chg: {}, now_price: {}, buy_price: {}, bought: {}, from: {}, pct_chg_notifier: {}'
                                      .format(code, name, pct_chg, now_price, buy_price, buy_flag, monitor_source, min_pct_chg_notifier))
                            monitor_code_show_count += 1
            except Exception as e:
                print(e)
            print('now: {}, sleep: {}'.format(datetime.now(), sleep_time))
            time.sleep(sleep_time)


if __name__ == '__main__':
    monitor = LargeScreenMonitor(key_prefix='large_screen_monitor')
    monitor.run()

