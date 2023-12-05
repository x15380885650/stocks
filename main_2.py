import os
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import islice
from chinese_calendar import is_holiday, is_workday
from data_source_bao import BaoDataSource
from data_source_ef import EfDataSource
from strategy import Strategy
from constants import pct_change_max_i, pct_change_max_j
from dumper_loader import load_data_append_by_json_dump, save_data_list_append_by_json_dump


test_stock_list = [
]

format_date = '%Y-%m-%d'
minus_days = 30 * 2.5
stock_value_max = 100
stock_value_min = 10


class Chooser(object):
    def __init__(self):
        self.count = 0
        self.e_count = 0
        # self.ds = BaoDataSource()
        self.ds = EfDataSource()

    def get_pct_change_max(self, code):
        if code.startswith('30') or code.startswith('sz.30'):
            return pct_change_max_j
        return pct_change_max_i

    def is_deal_date(self, t_date):
        t_holiday = is_holiday(t_date)
        if t_holiday:
            return False
        day_of_week = t_date.weekday() + 1
        if day_of_week in [6, 7]:
            return False
        return True

    def get_valid_end_date(self, _end_date=None):
        end_date = self.ds.get_end_date() if not _end_date else _end_date
        while True:
            deal_date_ok = self.is_deal_date(end_date)
            if not deal_date_ok:
                end_date = end_date - timedelta(days=1)
            else:
                break
        return end_date

    # def get_valid_k_line_list(self, code, start_date_str, end_date_str):
    #     filtered = self.ds.is_code_filtered(code)
    #     if filtered:
    #         return None
    #     k_line_list = self.ds.get_stock_kline_history(code, start_date_str, end_date_str)
    #     total_count = len(k_line_list)
    #     if total_count < int(minus_days / 2):
    #         return None
    #     last_date = k_line_list[-1]['date']
    #     if last_date != end_date_str:
    #         # print('code: {}, last_date: {} != end_date_str: {}'.format(code, last_date, end_date_str))
    #         return None
    #     return k_line_list

    def get_valid_stock_list_kline_list(self, code_list, start_date_str, end_date_str, exclude_code_list):
        stock_list_kline = self.ds.get_stock_list_kline_history(code_list, start_date_str, end_date_str)
        new_stock_list_kline = []
        for stock_k_line in stock_list_kline:
            code = stock_k_line[-1]['code']
            name = stock_k_line[-1]['name']
            total_count = len(stock_k_line)
            if total_count < int(minus_days / 2):
                exclude_code_list.append(code)
                continue
            last_date = stock_k_line[-1]['date']
            if last_date != end_date_str:
                exclude_code_list.append(code)
                continue
            if 'ST' in name:
                exclude_code_list.append(code)
                continue
            new_stock_list_kline.append(stock_k_line)
        return new_stock_list_kline

    def get_day_range_stock_list(self, end_date, min_day, max_day):
        days = 1
        stock_list = []
        valid_file_path_list = []
        while True:
            temp_date = end_date - timedelta(days=days)
            temp_date_str = temp_date.strftime(format_date)
            file_folder = 'data/{}'.format(temp_date_str[:temp_date_str.rfind('-')])
            file_path = '{}/{}_codes.json'.format(file_folder, temp_date_str)
            if not os.path.exists(file_path):
                days += 1
                continue
            valid_file_path_list.append(file_path)
            if len(valid_file_path_list) >= 30:
                break
            days += 1
        range_file_path_list = valid_file_path_list[min_day:max_day]
        for file_path in range_file_path_list:
            print(file_path)
            top_pct_chg_code_list = load_data_append_by_json_dump(file_path, ret_type=[])
            stock_list.extend(top_pct_chg_code_list)
        print('stock_list_before: {}'.format(len(stock_list)))
        stock_list = list(set(stock_list))
        print('stock_list_after: {}'.format(len(stock_list)))
        return stock_list

    def run(self):
        import time
        strategy = Strategy()
        end_date = datetime.now().date()
        # end_date = datetime.strptime('2023-11-10', '%Y-%m-%d')
        start_date = end_date - timedelta(days=minus_days)
        start_date_str = start_date.strftime(format_date)
        end_date_str = end_date.strftime(format_date)
        min_day, max_day = 5, 14
        stock_list = self.get_day_range_stock_list(end_date, min_day=min_day, max_day=14)
        sleep_time = 30
        exclude_stock_list = []
        stock_value_checked = False
        record_stock_dict = defaultdict(int)
        while True:
            filter_stock_list = []
            for code in stock_list:
                if code in exclude_stock_list:
                    continue
                filtered = self.ds.is_code_filtered(code)
                if filtered:
                    continue
                filter_stock_list.append(code)
            if not stock_value_checked:
                stocks_base_info = self.ds.get_stocks_base_info(filter_stock_list)
                for base_info in stocks_base_info.iterrows():
                    stock_value_checked = True
                    code = base_info[1][0]
                    stock_value = base_info[1][4] / 10000 / 10000
                    if stock_value > stock_value_max or stock_value < stock_value_min:
                        exclude_stock_list.append(code)
                        if code in filter_stock_list:
                            filter_stock_list.remove(code)

            stock_list_kline_list = self.get_valid_stock_list_kline_list(
                filter_stock_list, start_date_str, end_date_str, exclude_stock_list)
            for stock_kilne in stock_list_kline_list:
                code = stock_kilne[-1]['code']
                strategy_6_ok = strategy.strategy_match_6(code, stock_kilne, exclude_stock_list, m_day=min_day)
                if strategy_6_ok:
                    r_count = record_stock_dict.get(code, 0)
                    if r_count <= 10:
                        record_stock_dict[code] += 1
                        print('join strategy_6 stock, code: {}'.format(code))
            print('now: {}, sleep: {}'.format(datetime.now(), sleep_time))
            time.sleep(sleep_time)

if __name__ == '__main__':
    c = Chooser()
    c.run()
