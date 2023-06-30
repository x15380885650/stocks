from datetime import datetime, timedelta
from chinese_calendar import is_holiday, is_workday
from data_source_bao import BaoDataSource
from data_source_ef import EfDataSource
from strategy import Strategy

test_stock_list = [
    # # strategy_5    # ## {'code': '601858', 'end_date': datetime.strptime('2023-04-12', '%Y-%m-%d')},
    {'code': '601595', 'end_date': datetime.strptime('2023-03-09', '%Y-%m-%d')},
    {'code': '600629', 'end_date': datetime.strptime('2023-04-20', '%Y-%m-%d')},
    {'code': '601900', 'end_date': datetime.strptime('2023-04-20', '%Y-%m-%d')},
    {'code': '601949', 'end_date': datetime.strptime('2023-04-21', '%Y-%m-%d')},  # buy 时间点不好
    {'code': '605011', 'end_date': datetime.strptime('2023-05-15', '%Y-%m-%d')},
    {'code': '002527', 'end_date': datetime.strptime('2023-06-16', '%Y-%m-%d')},
    {'code': '603767', 'end_date': datetime.strptime('2023-06-20', '%Y-%m-%d')},  # buy的时间点不好
]

format_date = '%Y-%m-%d'
minus_days = 30 * 3
is_test_code = False


class Chooser(object):
    def __init__(self):
        self.count = 0
        self.e_count = 0

    def run(self, code, ds, strategy, start_date_str, end_date_str, is_test=False):
        filtered = ds.is_code_filtered(code)
        if filtered:
            return False
        k_line_list = ds.get_stock_kline_history(code, start_date_str, end_date_str)
        total_count = len(k_line_list)
        if total_count < int(minus_days / 2):
            return False

        self.e_count += 1
        strategy.strategy(code, k_line_list, m_day=5, is_test=is_test)

    def choose(self):
        # ds = BaoDataSource()
        ds = EfDataSource()
        strategy = Strategy()
        end_date = ds.get_end_date()
        # end_date = datetime.strptime('2023-05-09', '%Y-%m-%d')
        # workday = is_workday(end_date)
        holiday = is_holiday(end_date)
        day_of_week = end_date.weekday()
        print('{}, 星期{}'.format(end_date, day_of_week + 1))
        if holiday:
            return
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
                    self.run(code, ds, strategy, test_start_date_str, test_end_date_str, is_test=True)
            else:
                self.count += 1
                if self.count % 1000 == 0:
                    print('count: {}, e_count: {}'.format(self.count, strategy.e_count))
                # if '002553' not in code:
                #     continue
                self.run(code, ds, strategy, start_date_str, end_date_str)
        print('count: {}, e_count: {}'.format(self.count, strategy.e_count))


if __name__ == '__main__':
    c = Chooser()
    c.choose()