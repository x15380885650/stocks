import time
import warnings
warnings.filterwarnings('ignore')
from datetime import datetime
from code_fetcher import CodeFetcher
from date_chooser import DateChooser
from strategist import Strategist
from ancestor import Ancestor


class Monitor(Ancestor):
    def __init__(self, key_prefix):
        super(Monitor, self).__init__(key_prefix=key_prefix)
        self.test_code_dict = {}
        self.strategist = Strategist()

    def get_strategy_res(self, code, stock_kline_list, min_opt_macd_diff=0):
        raise NotImplementedError
        
    def run(self):
        sleep_time = 0
        c_fetcher = CodeFetcher(ds=self.ds)
        d_chooser = DateChooser(ds=self.ds, delta_days=self.stock_days)
        s = Strategist()
        exclude_stock_set = set()

        if self.test_code_dict:
            for test_stock_code, test_end_date_str in self.test_code_dict.items():
                test_start_date_str, test_end_date_str = d_chooser.get_start_and_end_date(test_end_date_str)
                stock_list_kline_list = c_fetcher.get_stock_list_kline_list(
                    [test_stock_code], test_start_date_str, test_end_date_str)
                for stock_kline_list in stock_list_kline_list:
                    code = stock_kline_list[-1]['code']
                    if len(stock_kline_list) < int(self.stock_days / 2):
                        continue
                    self.get_strategy_res(code, stock_kline_list)
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
                        s_res = self.get_strategy_res(code, stock_kline_list, min_opt_macd_diff)
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
