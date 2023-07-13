from datetime import datetime, timedelta
from chinese_calendar import is_holiday, is_workday
from data_source_bao import BaoDataSource
from data_source_ef import EfDataSource
from strategy import Strategy

test_stock_list = [
    # # strategy_1
    # {'code': '601595', 'end_date': datetime.strptime('2023-03-09', '%Y-%m-%d')},
    # {'code': '600629', 'end_date': datetime.strptime('2023-04-20', '%Y-%m-%d')},
    # {'code': '601900', 'end_date': datetime.strptime('2023-04-20', '%Y-%m-%d')},
    # {'code': '605011', 'end_date': datetime.strptime('2023-05-15', '%Y-%m-%d')},
    # {'code': '002527', 'end_date': datetime.strptime('2023-06-16', '%Y-%m-%d')},
    # {'code': '603767', 'end_date': datetime.strptime('2023-06-20', '%Y-%m-%d')},  # buy的时间点不好

    # # strategy_2
    {'code': '603083', 'end_date': datetime.strptime('2023-02-27', '%Y-%m-%d')},
    {'code': '601595', 'end_date': datetime.strptime('2023-03-21', '%Y-%m-%d')},
    {'code': '600629', 'end_date': datetime.strptime('2023-04-21', '%Y-%m-%d')},
    {'code': '601900', 'end_date': datetime.strptime('2023-04-21', '%Y-%m-%d')},
    {'code': '000936', 'end_date': datetime.strptime('2023-06-13', '%Y-%m-%d')},
    {'code': '002527', 'end_date': datetime.strptime('2023-06-19', '%Y-%m-%d')},
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

    def run_strategy(self, code, ds, strategy, start_date_str, end_date_str, is_test=False):
        filtered = ds.is_code_filtered(code)
        if filtered:
            return False
        k_line_list = ds.get_stock_kline_history(code, start_date_str, end_date_str)
        total_count = len(k_line_list)
        if total_count < int(minus_days / 2):
            return False

        self.e_count += 1
        # strategy_1_ok = strategy.strategy_match(code, k_line_list, m_day=5, is_test=is_test)
        strategy_1_ok = False
        strategy_2_ok = strategy.strategy_match_2(code, k_line_list, m_day=5, is_test=is_test)
        if strategy_1_ok or strategy_2_ok:
            stock_value = ds.get_stock_value(code)
            if stock_value > stock_value_max or stock_value < stock_value_min:
                print('stock_value: {} not in [{}, {}], code: {}'
                      .format(stock_value, stock_value_min, stock_value_max, code))
                return
        if strategy_1_ok:
            print('join strategy_1 stock, code: {}'.format(code))
        if strategy_2_ok:
            print('join strategy_2 stock, code: {}'.format(code))

    def choose(self, is_test_code=False, p_end_date=None, p_code=''):
        # ds = BaoDataSource()
        ds = EfDataSource()
        strategy = Strategy()
        end_date = ds.get_end_date() if not p_end_date else p_end_date
        holiday = is_holiday(end_date)
        day_of_week = end_date.weekday()
        print('{}, 星期{}'.format(end_date, day_of_week + 1))
        # if holiday:
        #     return
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
                    self.run_strategy(code, ds, strategy, test_start_date_str, test_end_date_str, is_test=True)
            else:
                self.count += 1
                if self.count % 1000 == 0:
                    print('count: {}, e_count: {}, e_count_adv: {}'
                          .format(self.count, strategy.e_count, strategy.e_count_adv))
                if p_code and p_code not in code:
                    continue
                self.run_strategy(code, ds, strategy, start_date_str, end_date_str)
        print('count: {}, e_count: {}, e_count_adv: {}'
              .format(self.count, strategy.e_count, strategy.e_count_adv))


if __name__ == '__main__':
    p_end_date = datetime.strptime('2023-06-26', '%Y-%m-%d')
    c = Chooser()

    c.choose()  # normal

    # c.choose(is_test_code=True)  # test stock code

    # c.choose(p_end_date=p_end_date)

    # c.choose(p_end_date=p_end_date, p_code='603788')  # 2023-07-03
    # c.choose(p_end_date=p_end_date, p_code='600602')  # 2023-06-12

    # for p_day in range(1, 10):
    #     p_end_date = datetime.strptime('2023-05-09', '%Y-%m-%d') - timedelta(days=p_day)
    #     c.choose(p_end_date=p_end_date)