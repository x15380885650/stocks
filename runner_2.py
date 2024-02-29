import time, os
from datetime import datetime
from code_fetcher import CodeFetcher
from date_chooser import DateChooser
from strategist import Strategist
from dumper_loader import load_data_append_by_json_dump, save_data_append_by_json_dump
from ancestor import Runner

test_code_dict = {
# '601566': '2023-02-24',
# '603767': '2023-06-16',
# '002377': '2023-07-26',
# '600272': '2023-08-09',
# '002456': '2023-09-28',
# '603536': '2023-11-24',
# '600250': '2023-11-28',
# '600571': '2023-11-30',
# '600661': '2023-12-01',
# '600678': '2023-12-05',
# '600715': '2023-12-06',
# '603660': '2023-12-07',
# '600712': '2023-12-11',
}


class SecondRunner(Runner):
    def run(self):
        sleep_time = 0
        c_fetcher = CodeFetcher(ds=self.ds)
        d_chooser = DateChooser(ds=self.ds, delta_days=self.stock_days)
        s = Strategist()
        start_date_str, end_date_str = d_chooser.get_start_and_end_date()
        print('{}--->{}'.format(start_date_str, end_date_str))
        exclude_stock_set = set()
        file_folder = 'data/{}'.format(end_date_str[:end_date_str.rfind('-')])
        if not os.path.exists(file_folder):
            os.makedirs(file_folder)
        notified_file_path = '{}/{}_codes_notified_2.json'.format(file_folder, end_date_str)
        notified_set = set(load_data_append_by_json_dump(notified_file_path, ret_type=[]))
        exclude_stock_set.update(notified_set)

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
                    if not trade_ok:
                        time.sleep(1)
                        continue
                    code_list = c_fetcher.fetch_real_time_filtered_code_list(pch_chg_min=7.5)
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
                    for stock_kline_list in stock_list_kline_list:
                        code = stock_kline_list[-1]['code']
                        if len(stock_kline_list) < int(self.stock_days/2):
                            exclude_stock_set.add(code)
                            continue
                        s_res = s.get_second_strategy_res(code, stock_kline_list)
                        if not s_res:
                            exclude_stock_set.add(code)
                        if s_res and code not in notified_set:
                            self.notify(code)
                            print('join s_res, code: {}'.format(code))
                            save_data_append_by_json_dump(notified_file_path, code)
                            notified_set.add(code)
                            exclude_stock_set.add(code)
                except Exception as e:
                    print(e)
                print('now: {}, sleep: {}'.format(datetime.now(), sleep_time))
                time.sleep(sleep_time)


if __name__ == '__main__':
    runner = SecondRunner()
    runner.run()