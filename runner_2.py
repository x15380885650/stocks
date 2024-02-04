import time
from datetime import datetime
from code_fetcher import CodeFetcher
from date_chooser import DateChooser
from strategist import Strategist
from dumper_loader import load_data_append_by_json_dump, save_data_append_by_json_dump
from runner import Runner

test_code_dict = {
            # '002214': '2024-01-25',
            #
            # '000070': '2024-01-22',
            # '603648': '2024-01-23',
            # '600272': '2024-01-23',
            # '600675': '2024-01-23',
            # '600639': '2024-01-23',
            # '600629': '2024-01-23',
            # '002116': '2024-01-24',
            # '603767': '2024-01-30',
        }


class SecondRunner(Runner):
    def run(self):
        m_day = 90
        sleep_time = 0
        c_fetcher = CodeFetcher(ds=self.ds)
        d_chooser = DateChooser(ds=self.ds, delta_days=self.stock_days)
        s = Strategist()
        start_date_str, end_date_str = d_chooser.get_start_and_end_date()
        code_list = c_fetcher.fetch_real_time_filtered_code_list(pch_chg_min=4)
        print('{}--->{}'.format(start_date_str, end_date_str))
        print('code_list: {}'.format(len(code_list)))
        exclude_stock_set = set()
        file_folder = 'data/{}'.format(end_date_str[:end_date_str.rfind('-')])
        notified_file_path = '{}/{}_codes_notified_2.json'.format(file_folder, end_date_str)
        notified_set = set(load_data_append_by_json_dump(notified_file_path, ret_type=[]))

        if test_code_dict:
            for test_stock_code, test_end_date_str in test_code_dict.items():
                test_start_date_str, test_end_date_str = d_chooser.get_start_and_end_date(test_end_date_str)
                stock_list_kline_list = c_fetcher.get_stock_list_kline_list(
                    [test_stock_code], test_start_date_str, test_end_date_str, stock_days=self.stock_days)
                for stock_kline_list in stock_list_kline_list:
                    code = stock_kline_list[-1]['code']
                    s.get_second_strategy_res(code, stock_kline_list, m_day=m_day)
        else:
            while True:
                try:
                    stock_list_kline_list = c_fetcher.get_stock_list_kline_list(
                        code_list, start_date_str, end_date_str, stock_days=self.stock_days)
                    for stock_kline_list in stock_list_kline_list:
                        code = stock_kline_list[-1]['code']
                        s_res = s.get_second_strategy_res(code, stock_kline_list, m_day=m_day)
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
    runner = SecondRunner()
    runner.run()