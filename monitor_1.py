import time
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime
from code_fetcher import CodeFetcher
from date_chooser import DateChooser
from strategist import Strategist
from ancestor import Ancestor

test_code_dict = {
# '002808': '2023-01-12',
# '002835': '2023-01-20',
# '002877': '2023-01-30',
# '601595': '2023-03-08',
# '605011': '2023-05-12',
# '603933': '2023-05-19',
# '002173': '2023-05-26',
# # '600280': '2023-07-14',
# '600355': '2023-09-20',
# '002682': '2023-10-20',
# '000056': '2023-11-07',
# '002584': '2023-11-08',
# '600506': '2023-11-09',
# '001300': '2023-11-10',
# '600053': '2023-11-21',
# '000017': '2024-01-09',

# '600238': '2024-02-27',
# '000797': '2024-02-28',
# '002166': '2024-02-28',
# '600616': '2024-02-29',
# '000505': '2024-02-28',
# '002713': '2024-02-28',
# '600127': '2024-02-28',
}


class FirstMonitor(Ancestor):
    def __init__(self):
        super(FirstMonitor, self).__init__(key_prefix='monitor_1')
        
    def run(self):
        sleep_time = 0
        c_fetcher = CodeFetcher(ds=self.ds)
        d_chooser = DateChooser(ds=self.ds, delta_days=self.stock_days)
        s = Strategist()
        exclude_stock_set = set()

        if test_code_dict:
            for test_stock_code, test_end_date_str in test_code_dict.items():
                test_start_date_str, test_end_date_str = d_chooser.get_start_and_end_date(test_end_date_str)
                stock_list_kline_list = c_fetcher.get_stock_list_kline_list(
                    [test_stock_code], test_start_date_str, test_end_date_str)
                for stock_kline_list in stock_list_kline_list:
                    code = stock_kline_list[-1]['code']
                    if len(stock_kline_list) < int(self.stock_days / 2):
                        continue
                    s.get_first_strategy_res(code, stock_kline_list)
        else:
            while True:
                try:
                    if self.persister.get_script_stop_status():
                        print('stop_status: 1, exited')
                        return
                    trade_ok = self.is_trade()
                    if not trade_ok:
                        time.sleep(1)
                        continue
                    start_date_str, end_date_str = d_chooser.get_start_and_end_date()
                    min_pct_chg_monitor = self.persister.get_min_pct_chg_monitor()
                    sleep_time = self.persister.get_sleep_time_monitor()
                    code_list = c_fetcher.fetch_real_time_filtered_code_list(pch_chg_min=min_pct_chg_monitor)
                    new_code_list = []
                    for c in code_list:
                        if c not in exclude_stock_set:
                            new_code_list.append(c)
                    print('code_list: {}'.format(len(new_code_list)))
                    if not new_code_list:
                        print('now: {}, sleep: {}'.format(datetime.now(), sleep_time))
                        time.sleep(sleep_time)
                        continue
                    stock_list_kline_list = c_fetcher.get_stock_list_kline_list(
                        new_code_list, start_date_str, end_date_str)
                    min_opt_macd_diff = self.persister.get_min_opt_macd_diff()
                    for stock_kline_list in stock_list_kline_list:
                        code = stock_kline_list[-1]['code']
                        if len(stock_kline_list) < int(self.stock_days/2):
                            exclude_stock_set.add(code)
                            continue
                        s_res = s.get_first_strategy_res(code, stock_kline_list, min_opt_macd_diff)
                        if not s_res:
                            exclude_stock_set.add(code)
                        else:
                            print('push to redis, code: {}'.format(code))
                            self.persister.save_code_to_monitor(end_date_str, code)
                            exclude_stock_set.add(code)
                except Exception as e:
                    print(e)
                print('now: {}, sleep: {}'.format(datetime.now(), sleep_time))
                time.sleep(sleep_time)


if __name__ == '__main__':
    monitor = FirstMonitor()
    monitor.run()