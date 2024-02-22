import time
from datetime import datetime
from code_fetcher import CodeFetcher
from date_chooser import DateChooser
from strategist import Strategist
from dumper_loader import load_data_append_by_json_dump, save_data_append_by_json_dump
from runner import Runner

test_code_dict = {
# ## '000957': '2022-05-13',
# ##'002441': '2023-01-05',
# '002576': '2023-01-05',
# '002808': '2023-01-12',
# '002835': '2023-01-20',
# '002877': '2023-01-30',
# '605011': '2023-05-12',
# '603933': '2023-05-19',
# '002173': '2023-05-26',
# ## '603869': '2023-05-26',
# '002902': '2023-05-30',
# ##'603779': '2023-06-02',
# '600280': '2023-07-14',
# '600355': '2023-09-20',
# '002771': '2023-10-16',
# '002682': '2023-10-20',
# '002238': '2023-11-02',
# '603729': '2023-11-02',
# '000056': '2023-11-07',
# ##'600775': '2023-11-13',
# '001300': '2023-11-10',
# ## '002103': '2023-11-16',
# '600053': '2023-11-21',
# ## '603536': '2023-11-24',
# '000017': '2024-01-09',
# ## '603960': '2024-02-01',



#
# # '603660': '2023-12-07',
# # '600250': '2023-11-28',
# # '603196': '2023-04-25',
# # '600272': '2023-08-09',
# # '603767': '2023-06-16',

        }


class ThirdRunner(Runner):
    def run(self):
        sleep_time = 0
        c_fetcher = CodeFetcher(ds=self.ds)
        d_chooser = DateChooser(ds=self.ds, delta_days=self.stock_days)
        s = Strategist()
        start_date_str, end_date_str = d_chooser.get_start_and_end_date()
        print('{}--->{}'.format(start_date_str, end_date_str))
        exclude_stock_set = set()
        file_folder = 'data/{}'.format(end_date_str[:end_date_str.rfind('-')])
        notified_file_path = '{}/{}_codes_notified_3.json'.format(file_folder, end_date_str)
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
                    s.get_third_strategy_res(code, stock_kline_list)
        else:
            while True:
                try:
                    code_list = c_fetcher.fetch_real_time_filtered_code_list(pch_chg_min=6)
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
                        s_res = s.get_third_strategy_res(code, stock_kline_list)
                        if not s_res:
                            exclude_stock_set.add(code)
                        if s_res and code not in notified_set:
                            self.notify(code)
                            print('join s_res, code: {}'.format(code))
                            save_data_append_by_json_dump(notified_file_path, code)
                            notified_set.add(code)
                except Exception as e:
                    print(e)
                print('now: {}, sleep: {}'.format(datetime.now(), sleep_time))
                time.sleep(sleep_time)


if __name__ == '__main__':
    runner = ThirdRunner()
    runner.run()