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
    {'code': '600895', 'end_date': datetime.strptime('2023-03-16', '%Y-%m-%d')},
    {'code': '601595', 'end_date': datetime.strptime('2023-03-21', '%Y-%m-%d')},
    {'code': '000021', 'end_date': datetime.strptime('2023-03-31', '%Y-%m-%d')},
    {'code': '600629', 'end_date': datetime.strptime('2023-04-21', '%Y-%m-%d')},
    {'code': '603779', 'end_date': datetime.strptime('2023-06-05', '%Y-%m-%d')},
    {'code': '000936', 'end_date': datetime.strptime('2023-06-13', '%Y-%m-%d')},
    {'code': '603767', 'end_date': datetime.strptime('2023-06-19', '%Y-%m-%d')},
    {'code': '002535', 'end_date': datetime.strptime('2023-06-29', '%Y-%m-%d')},
    {'code': '600266', 'end_date': datetime.strptime('2023-07-26', '%Y-%m-%d')},
    {'code': '600272', 'end_date': datetime.strptime('2023-08-10', '%Y-%m-%d')},
    {'code': '601188', 'end_date': datetime.strptime('2023-09-13', '%Y-%m-%d')},



    # {'code': '002174', 'end_date': datetime.strptime('2023-04-25', '%Y-%m-%d')},
    # {'code': '600713', 'end_date': datetime.strptime('2023-04-28', '%Y-%m-%d')},
    # {'code': '601068', 'end_date': datetime.strptime('2023-04-28', '%Y-%m-%d')},
    # {'code': '600880', 'end_date': datetime.strptime('2023-05-04', '%Y-%m-%d')},
    # {'code': '600425', 'end_date': datetime.strptime('2023-05-05', '%Y-%m-%d')},
    # {'code': '603999', 'end_date': datetime.strptime('2023-05-05', '%Y-%m-%d')},
    # {'code': '000561', 'end_date': datetime.strptime('2023-06-29', '%Y-%m-%d')},
    # {'code': '000795', 'end_date': datetime.strptime('2023-06-30', '%Y-%m-%d')},
    # {'code': '002117', 'end_date': datetime.strptime('2023-07-04', '%Y-%m-%d')},
    # {'code': '002771', 'end_date': datetime.strptime('2023-07-04', '%Y-%m-%d')},
    # {'code': '002790', 'end_date': datetime.strptime('2023-07-04', '%Y-%m-%d')},
    # {'code': '601567', 'end_date': datetime.strptime('2023-07-17', '%Y-%m-%d')},
    # {'code': '600153', 'end_date': datetime.strptime('2023-08-01', '%Y-%m-%d')},

]

format_date = '%Y-%m-%d'
minus_days = 30 * 2.5
stock_value_max = 200
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
                    if not stock_kline:
                        continue
                    last_date = stock_kline[-1]['date']
                    code = stock_kline[-1]['code']
                    if last_date != end_date_str:
                        print('code: {}, last_date: {} != end_date_str: {}'.format(code, last_date, end_date_str))
                        continue
                    latest_pct_chg = float(stock_kline[-1]['pct_chg'])
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

    def monitor_strategy_3(self, code, strategy, start_date_str, end_date_str, is_test=False):
        k_line_list = self.get_valid_k_line_list(code, start_date_str, end_date_str)
        if not k_line_list:
            return
        strategy_3_ok = strategy.strategy_match_3(code, k_line_list, m_day=3, is_test=is_test)
        if strategy_3_ok:
            stock_value = self.ds.get_stock_value(code)
            if stock_value > stock_value_max or stock_value < stock_value_min:
                print('stock_value: {} not in [{}, {}], code: {}'
                      .format(stock_value, stock_value_min, stock_value_max, code))
                return
        if strategy_3_ok:
            print('join strategy_3 stock, code: {}'.format(code))

    def choose(self, is_test_code=False, p_end_date=None, p_code='', partial_code_list=False):
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
        if not partial_code_list:
            code_list = ds.get_all_stock_code_list(end_date_str)
        else:
            t_end_date = self.get_valid_end_date(end_date - timedelta(days=1))
            deal_date_ok = self.is_deal_date(t_end_date)
            if not deal_date_ok:
                return
            t_end_date_str = t_end_date.strftime(format_date)
            code_list = self.get_top_pct_chg_code_list(t_end_date_str)
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
                    self.monitor_strategy_3(code, strategy, test_start_date_str, test_end_date_str, is_test=True)
            else:
                self.count += 1
                if self.count % 1000 == 0:
                    print('count: {}, e_count: {}'.format(self.count, strategy.e_count))
                if p_code and p_code not in code:
                    continue
                # self.choose_strategy_1(code, strategy, start_date_str, end_date_str)
                self.monitor_strategy_3(code, strategy, start_date_str, end_date_str)
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
        print('monitor, {}--->{}, code_list: {}'.format(start_date_str, end_date_str, len(code_list)))
        if not code_list:
            print('code_list is empty, break!!!')
        for code in code_list:
            self.count += 1
            self.monitor_strategy_3(code, strategy, start_date_str, end_date_str)
        print('count: {}, e_count: {}'.format(self.count, strategy.e_count))


if __name__ == '__main__':
    p_end_date = datetime.strptime('2023-10-18', '%Y-%m-%d')
    c = Chooser()
    c.monitor()

    # c.choose()  # normal

    # c.choose(is_test_code=True)  # test stock code

    # c.choose(p_end_date=p_end_date, partial_code_list=True)

    # c.choose(p_end_date=p_end_date, p_code='603229')

    # for p_day in range(0, 300):
    #     p_end_date = datetime.strptime('2023-09-14', '%Y-%m-%d') - timedelta(days=p_day)
    #     # p_end_date = datetime.strptime('2023-07-31', '%Y-%m-%d')
    #     deal_date_ok = c.is_deal_date(p_end_date)
    #     if not deal_date_ok:
    #         continue
    #     c.count = 0
    #     c.choose(p_end_date=p_end_date, partial_code_list=True)