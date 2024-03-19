import time
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime
from code_fetcher import CodeFetcher
from date_chooser import DateChooser
from strategist import Strategist
from ancestor import Ancestor

test_code_dict = {
# '601566': '2023-02-24',
# '603767': '2023-06-16',
# '002377': '2023-07-26',
# '000628': '2023-09-26',
# '002456': '2023-09-28',
# '600272': '2023-08-09',
# '600571': '2023-11-30',
# '600678': '2023-12-05',
# '600715': '2023-12-06',
# '603660': '2023-12-07',
# '600712': '2023-12-11',

# '603536': '2023-11-24',
# '600250': '2023-11-28',
}


class SecondMonitor(Ancestor):
    def __init__(self):
        super(SecondMonitor, self).__init__(key_prefix='monitor_2')
        
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
                    s.get_second_strategy_res(code, stock_kline_list)
        else:
            while True:
                try:
                    trade_ok = self.is_trade()
                    # trade_ok = True
                    if not trade_ok:
                        exclude_stock_set.clear()
                        time.sleep(1)
                        continue
                    start_date_str, end_date_str = d_chooser.get_start_and_end_date()
                    min_pct_chg_monitor = self.persister.get_min_pct_chg_monitor()
                    sleep_time = self.persister.get_sleep_time_monitor()
                    code_list = c_fetcher.fetch_real_time_filtered_code_list(pct_chg_min=min_pct_chg_monitor)
                    new_code_list = []
                    for c in code_list:
                        if c not in exclude_stock_set:
                            new_code_list.append(c)
                    print('code_list: {}, exclude_code_list: {}'.format(len(new_code_list), len(exclude_stock_set)))
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
                        s_res = s.get_second_strategy_res(code, stock_kline_list, min_opt_macd_diff)
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
    monitor = SecondMonitor()
    monitor.run()