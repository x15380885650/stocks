import os
from datetime import datetime, timedelta
from itertools import islice
from chinese_calendar import is_holiday, is_workday
from data_source_bao import BaoDataSource
from data_source_ef import EfDataSource
from strategy import Strategy
from constants import pct_change_max_i
from dumper_loader import load_data_append_by_json_dump, save_data_list_append_by_json_dump

test_stock_list = [
    # # strategy_1
    # {'code': '601595', 'end_date': datetime.strptime('2023-03-09', '%Y-%m-%d')},
    # {'code': '600629', 'end_date': datetime.strptime('2023-04-20', '%Y-%m-%d')},
    # {'code': '601900', 'end_date': datetime.strptime('2023-04-20', '%Y-%m-%d')},
    # {'code': '605011', 'end_date': datetime.strptime('2023-05-15', '%Y-%m-%d')},
    # {'code': '002527', 'end_date': datetime.strptime('2023-06-16', '%Y-%m-%d')},
    # {'code': '603767', 'end_date': datetime.strptime('2023-06-20', '%Y-%m-%d')},  # buy的时间点不好

    # # strategy_2
    ##{'code': '603083', 'end_date': datetime.strptime('2023-02-27', '%Y-%m-%d')},

    {'code': '601595', 'end_date': datetime.strptime('2023-03-21', '%Y-%m-%d')},
    {'code': '000021', 'end_date': datetime.strptime('2023-03-31', '%Y-%m-%d')},
    {'code': '600629', 'end_date': datetime.strptime('2023-04-21', '%Y-%m-%d')},
    {'code': '601900', 'end_date': datetime.strptime('2023-04-21', '%Y-%m-%d')},
    {'code': '000936', 'end_date': datetime.strptime('2023-06-13', '%Y-%m-%d')},
    {'code': '002527', 'end_date': datetime.strptime('2023-06-19', '%Y-%m-%d')},   # 换手率太高
    {'code': '000837', 'end_date': datetime.strptime('2023-06-21', '%Y-%m-%d')},
    {'code': '002535', 'end_date': datetime.strptime('2023-06-29', '%Y-%m-%d')},

]

format_date = '%Y-%m-%d'
minus_days = 30 * 2.5
stock_value_max = 200
stock_value_min = 20


class Chooser(object):
    def __init__(self):
        self.count = 0
        self.e_count = 0
        # self.ds = BaoDataSource()
        self.ds = EfDataSource()

    def get_valid_end_date(self):
        end_date = self.ds.get_end_date()
        while True:
            holiday = is_holiday(end_date)
            if holiday:
                end_date = end_date - timedelta(days=1)
            else:
                break
        return end_date

    def get_top_pct_chg_code_list(self):
        end_date = self.get_valid_end_date()
        day_of_week = end_date.weekday()
        print('get_top_pct_chg_code_list, {}, 星期{}'.format(end_date, day_of_week + 1))
        start_date = end_date - timedelta(days=0)
        start_date_str = start_date.strftime(format_date)
        end_date_str = end_date.strftime(format_date)
        print('get_top_pct_chg_code_list, {}--->{}'.format(start_date_str, end_date_str))
        file_path = '{}_codes.json'.format(end_date_str)
        if os.path.exists(file_path):
            print('get_top_pct_chg_code_list by file_path: {}'.format(file_path))
            top_pct_chg_code_list = load_data_append_by_json_dump(file_path, ret_type=[])
            return top_pct_chg_code_list

        code_list = self.ds.get_all_stock_code_list(end_date_str)
        top_pct_chg_code_list = []
        count = 0
        filtered_code_list = []
        for index, code in enumerate(code_list):
            filtered = self.ds.is_code_filtered(code)
            if filtered:
                continue
            filtered_code_list.append(code)
        print('all_code_list: {}, filtered_code_list: {}'.format(len(code_list), len(filtered_code_list)))
        # filtered_code_list = filtered_code_list[0: 500]
        stream = iter(filtered_code_list)
        batch_size = 1000
        while True:
            batch = list(islice(stream, 0, batch_size))
            count += len(batch)
            if count % 1000 == 0 and count != 0:
                print('count: {}, top_pct_chg_count: {}'.format(count, len(top_pct_chg_code_list)))
            if batch:
                kline_history_list = self.ds.get_stock_list_kline_history(batch, start_date_str, end_date_str)
                for stock_kline in kline_history_list:
                    last_date = stock_kline['date']
                    code = stock_kline['code']
                    if last_date != end_date_str:
                        print('code: {}, last_date: {} != end_date_str: {}'.format(code, last_date, end_date_str))
                        continue
                    latest_pct_chg = float(stock_kline['pct_chg'])
                    if latest_pct_chg < pct_change_max_i:
                        continue
                    top_pct_chg_code_list.append(code)
            else:
                break
        print('count: {}, top_pct_chg_count: {}'.format(count, len(top_pct_chg_code_list)))
        if top_pct_chg_code_list:
            save_data_list_append_by_json_dump(file_path, top_pct_chg_code_list)
        return top_pct_chg_code_list

    def get_valid_k_line_list(self, code, start_date_str, end_date_str):
        filtered = self.ds.is_code_filtered(code)
        if filtered:
            return None
        k_line_list = self.ds.get_stock_kline_history(code, start_date_str, end_date_str)
        total_count = len(k_line_list)
        if total_count < int(minus_days / 2):
            return None
        last_date = k_line_list[-1]['date']
        if last_date != end_date_str:
            # print('code: {}, last_date: {} != end_date_str: {}'.format(code, last_date, end_date_str))
            return None
        return k_line_list

    def monitor_strategy_1(self, code, strategy, start_date_str, end_date_str, is_test=False):
        k_line_list = self.get_valid_k_line_list(code, start_date_str, end_date_str)
        strategy_1_ok = strategy.strategy_match(code, k_line_list, m_day=5, is_test=is_test)
        if strategy_1_ok:
            stock_value = self.ds.get_stock_value(code)
            if stock_value > stock_value_max or stock_value < stock_value_min:
                print('stock_value: {} not in [{}, {}], code: {}'
                      .format(stock_value, stock_value_min, stock_value_max, code))
                return
        if strategy_1_ok:
            print('join strategy_1 stock, code: {}'.format(code))

    def monitor_strategy_2(self, code, strategy, start_date_str, end_date_str, is_test=False):
        k_line_list = self.get_valid_k_line_list(code, start_date_str, end_date_str)
        if not k_line_list:
            return
        strategy_2_ok = strategy.strategy_match_2(code, k_line_list, m_day=5, is_test=is_test)
        if strategy_2_ok:
            stock_value = self.ds.get_stock_value(code)
            if stock_value > stock_value_max or stock_value < stock_value_min:
                print('stock_value: {} not in [{}, {}], code: {}'
                      .format(stock_value, stock_value_min, stock_value_max, code))
                return
        if strategy_2_ok:
            print('join strategy_2 stock, code: {}'.format(code))

    def choose(self, is_test_code=False, p_end_date=None, p_code=''):
        # ds = BaoDataSource()
        ds = EfDataSource()
        strategy = Strategy()
        end_date = self.get_valid_end_date() if not p_end_date else p_end_date
        day_of_week = end_date.weekday()
        print('{}, 星期{}'.format(end_date, day_of_week + 1))
        start_date = end_date - timedelta(days=minus_days)
        start_date_str = start_date.strftime(format_date)
        end_date_str = end_date.strftime(format_date)
        print('{}--->{}'.format(start_date_str, end_date_str))
        code_list = ds.get_all_stock_code_list(end_date_str)
        for code in code_list:
            if is_test_code:
                for test_stock in test_stock_list:
                    test_code = test_stock['code']
                    if test_code not in code:
                        continue
                    test_end_date = test_stock['end_date']
                    test_start_date = test_end_date - timedelta(days=minus_days)
                    test_start_date_str = test_start_date.strftime(format_date)
                    test_end_date_str = test_end_date.strftime(format_date)
                    print('test code: {}...'.format(code))
                    # self.monitor_strategy_1(code, strategy, test_start_date_str, test_end_date_str, is_test=True)
                    self.monitor_strategy_2(code, strategy, test_start_date_str, test_end_date_str, is_test=True)
            else:
                self.count += 1
                if self.count % 1000 == 0:
                    print('count: {}, e_count: {}'.format(self.count, strategy.e_count))
                if p_code and p_code not in code:
                    continue
                # self.monitor_strategy_1(code, strategy, start_date_str, end_date_str)
                self.monitor_strategy_2(code, strategy, start_date_str, end_date_str)
        print('count: {}, e_count: {}'.format(self.count, strategy.e_count))

    def monitor(self):
        strategy = Strategy()
        end_date = self.get_valid_end_date()
        end_date = end_date + timedelta(days=1)
        start_date = end_date - timedelta(days=minus_days)
        start_date_str = start_date.strftime(format_date)
        end_date_str = end_date.strftime(format_date)
        code_list = self.get_top_pct_chg_code_list()
        print('monitor, {}--->{}, code_list: {}'.format(start_date_str, end_date_str, len(code_list)))
        if not code_list:
            print('code_list is empty, break!!!')
        for code in code_list:
            self.count += 1
            self.monitor_strategy_2(code, strategy, start_date_str, end_date_str)
        print('count: {}, e_count: {}'.format(self.count, strategy.e_count))


if __name__ == '__main__':
    p_end_date = datetime.strptime('2023-06-26', '%Y-%m-%d')
    c = Chooser()
    c.monitor()
    # c.choose()  # normal

    # c.choose(is_test_code=True)  # test stock code

    # c.choose(p_end_date=p_end_date)

    # c.choose(p_end_date=p_end_date, p_code='603788')  # 2023-07-03
    # c.choose(p_end_date=p_end_date, p_code='600602')  # 2023-06-12

    # for p_day in range(1, 10):
    #     p_end_date = datetime.strptime('2023-05-09', '%Y-%m-%d') - timedelta(days=p_day)
    #     c.choose(p_end_date=p_end_date)