import os
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

    def get_top_pct_chg_code_list(self, end_date_str):
        # return ['603336', '603629', '601595', '603106', '601900', '603283', '601136', '600864', '600610', '600531',
        #         '600468', '600361', '600127', '002905', '002787', '002670', '002599', '002480', '002355', '002235',
        #         '002084', '000936', '000719']
        file_folder = 'data/{}'.format(end_date_str[:end_date_str.rfind('-')])
        if not os.path.exists(file_folder):
            os.makedirs(file_folder)
        file_path = '{}/{}_codes.json'.format(file_folder, end_date_str)
        if os.path.exists(file_path):
            print('get_top_pct_chg_code_list by file_path: {}'.format(file_path))
            top_pct_chg_code_list = load_data_append_by_json_dump(file_path, ret_type=[])
            # print(top_pct_chg_code_list)
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
                kline_history_list = self.ds.get_stock_list_kline_history(batch, end_date_str, end_date_str)
                for stock_kline in kline_history_list:
                    last_date = stock_kline['date']
                    code = stock_kline['code']
                    if last_date != end_date_str:
                        print('code: {}, last_date: {} != end_date_str: {}'.format(code, last_date, end_date_str))
                        continue
                    latest_pct_chg = float(stock_kline['pct_chg'])
                    pct_change_max = self.get_pct_change_max(code)
                    if latest_pct_chg < pct_change_max:
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

    def monitor_strategy_5(self, code, strategy, start_date_str, end_date_str, is_test=False):
        k_line_list = self.get_valid_k_line_list(code, start_date_str, end_date_str)
        if not k_line_list:
            return
        name = k_line_list[0]['name']
        if 'ST' in name:
            # print(name)
            return
        strategy_5_ok = strategy.strategy_match_5(code, k_line_list, m_day=5, is_test=is_test)
        if strategy_5_ok:
            stock_value = self.ds.get_stock_value(code)
            if stock_value > stock_value_max or stock_value < stock_value_min:
                # print('stock_value: {} not in [{}, {}], code: {}'
                #       .format(stock_value, stock_value_min, stock_value_max, code))
                return
        if strategy_5_ok:
            print('join strategy_5 stock, code: {}'.format(code))

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
            self.count += 1
            if self.count % 1000 == 0:
                print('count: {}, e_count: {}'.format(self.count, strategy.e_count))
            if p_code and p_code not in code:
                continue
            # self.choose_strategy_1(code, strategy, start_date_str, end_date_str)
            self.monitor_strategy_5(code, strategy, start_date_str, end_date_str)
        print('count: {}, e_count: {}'.format(self.count, strategy.e_count))

    def monitor(self):
        strategy = Strategy()
        # end_date = self.get_valid_end_date()
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=minus_days)
        start_date_str = start_date.strftime(format_date)
        end_date_str = end_date.strftime(format_date)
        # prev_end_date = end_date - timedelta(days=1)
        prev_end_date = self.get_valid_end_date(end_date - timedelta(days=1))
        prev_end_date_str = prev_end_date.strftime(format_date)
        now_hour = datetime.now().hour
        # end_date_str = end_date_str if now_hour >= 15 else prev_end_date_str
        # code_list = self.get_top_pct_chg_code_list(prev_end_date_str)
        if now_hour >= 15:
            code_list = self.get_top_pct_chg_code_list(end_date_str)
        else:
            code_list = self.get_top_pct_chg_code_list(prev_end_date_str)
        end_date_str = end_date_str if now_hour >= 15 else prev_end_date_str
        print('monitor, {}--->{}, code_list: {}'.format(start_date_str, end_date_str, len(code_list)))
        if not code_list:
            print('code_list is empty, break!!!')
        for code in code_list:
            self.count += 1
            self.monitor_strategy_4(code, strategy, start_date_str, end_date_str)
        print('count: {}, e_count: {}'.format(self.count, strategy.e_count))

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
        while True:
            act_count, idx = 0, 0
            for idx, code in enumerate(stock_list):
                if idx % 100 == 0 and idx != 0:
                    print('idx: {}, act_count: {}'.format(idx, act_count))
                if code in exclude_stock_list:
                    continue
                stock_value = self.ds.get_stock_value(code)
                if stock_value > stock_value_max or stock_value < stock_value_min:
                    if code not in exclude_stock_list:
                        exclude_stock_list.append(code)
                    continue
                k_line_list = self.get_valid_k_line_list(code, start_date_str, end_date_str)
                if not k_line_list:
                    continue
                name = k_line_list[0]['name']
                if 'ST' in name:
                    print(name)
                    continue
                act_count += 1
                strategy_6_ok = strategy.strategy_match_6(code, k_line_list, exclude_stock_list, m_day=min_day)
                if strategy_6_ok:
                    print('join strategy_6 stock, code: {}'.format(code))
            print('idx: {}, act_count: {}, sleep {}'.format(idx, act_count, sleep_time))
            time.sleep(sleep_time)


if __name__ == '__main__':
    c = Chooser()
    c.run()
