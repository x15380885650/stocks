import time
import warnings
warnings.filterwarnings('ignore')
from collections import defaultdict
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
        exclude_stock_set = set()
        cond_dict = defaultdict(list)
        monitor_stock_count = 0

        if self.test_code_dict:
            s_count = 0
            for test_stock_code, test_end_date_str in self.test_code_dict.items():
                test_start_date_str, test_end_date_str = d_chooser.get_start_and_end_date(test_end_date_str)
                stock_list_kline_list = c_fetcher.get_stock_list_kline_list(
                    [test_stock_code], test_start_date_str, test_end_date_str)
                for stock_kline_list in stock_list_kline_list:
                    code = stock_kline_list[-1]['code']
                    if len(stock_kline_list) < int(self.stock_days / 2):
                        continue
                    res_ok, cond = self.get_strategy_res(code, stock_kline_list)
                    if res_ok:
                        s_count += 1
            print('s_count: {}, test_count: {}'.format(s_count, len(self.test_code_dict)))
        else:
            while True:
                try:
                    is_stop = self.persister.get_stop_status()
                    if is_stop:
                        print('script stop, exit!!!')
                        return

                    trade_ok = self.is_trade()
                    # trade_ok = True
                    if not trade_ok:
                        exclude_stock_set.clear()
                        monitor_stock_count = 0
                        cond_dict.clear()
                        time.sleep(1)
                        continue

                    clear_monitor_status = self.persister.get_clear_monitor_status()
                    start_date_str, end_date_str = d_chooser.get_start_and_end_date()
                    min_pct_chg_monitor = self.persister.get_min_pct_chg_monitor()
                    sleep_time = self.persister.get_sleep_time_monitor()
                    show_code = self.persister.get_show_code_status()
                    monitor_code_list = self.persister.get_monitor_code_list(end_date_str)
                    buy_code_list = self.persister.get_buy_code_list()
                    if clear_monitor_status:
                        exclude_stock_set.clear()
                        monitor_stock_count = 0
                        cond_dict.clear()
                        self.persister.clear_monitor_code_list(end_date_str)
                    code_list, pct_chg_count_ratio = c_fetcher.fetch_real_time_filtered_code_list(
                        pct_chg_min=min_pct_chg_monitor)
                    new_code_list = []
                    for c in code_list:
                        if c not in exclude_stock_set:
                            new_code_list.append(c)
                    print('code_list: {}, exclude_code_list: {}'.format(len(new_code_list), len(exclude_stock_set)))
                    if show_code:
                        cond_show_dict = {}
                        for t_cond, t_code_list in cond_dict.items():
                            if len(t_code_list) <= 10:
                                cond_show_dict[t_cond] = t_code_list
                        print('monitor_stock_count: {}, cond_show_dict: {}'.format(monitor_stock_count, cond_show_dict))
                    else:
                        cond_count_dict = {}
                        for t_cond, t_code_list in cond_dict.items():
                            cond_count_dict[t_cond] = len(t_code_list)
                        print('monitor_stock_count: {}, cond_count_dict: {}'.format(monitor_stock_count, cond_count_dict))
                    if not new_code_list:
                        print('now: {}, sleep: {}'.format(datetime.now(), sleep_time))
                        time.sleep(sleep_time)
                        continue
                    stock_list_kline_list = c_fetcher.get_stock_list_kline_list(
                        new_code_list, start_date_str, end_date_str)
                    min_opt_macd_diff = self.persister.get_min_opt_macd_diff()
                    for stock_kline_list in stock_list_kline_list:
                        code = stock_kline_list[-1]['code']
                        if code in monitor_code_list or code in buy_code_list:
                            continue
                        if len(stock_kline_list) < int(self.stock_days/2):
                            exclude_stock_set.add(code)
                            continue
                        monitor_stock_count += 1
                        res_ok, cond = self.get_strategy_res(code, stock_kline_list, min_opt_macd_diff)
                        cond_dict[cond].append(code)
                        if not res_ok:
                            exclude_stock_set.add(code)
                        else:
                            print('push to redis, code: {}'.format(code))
                            self.persister.save_code_to_monitor(end_date_str, code)
                except Exception as e:
                    print(e)
                print('now: {}, sleep: {}'.format(datetime.now(), sleep_time))
                time.sleep(sleep_time)
