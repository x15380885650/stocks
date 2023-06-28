from datetime import datetime, timedelta
from data_source_bao import BaoDataSource
from data_source_ef import EfDataSource
from strategy import Strategy

test_stock_list = [
    # # strategy_3
    # {'code': '600629', 'end_date': datetime.strptime('2023-04-17', '%Y-%m-%d')},
    # {'code': '000736', 'end_date': datetime.strptime('2022-03-24', '%Y-%m-%d')},
    # {'code': '002866', 'end_date': datetime.strptime('2022-06-21', '%Y-%m-%d')},
    # {'code': '603322', 'end_date': datetime.strptime('2022-05-23', '%Y-%m-%d')},
    # {'code': '603767', 'end_date': datetime.strptime('2023-06-19', '%Y-%m-%d')},
    # {'code': '601900', 'end_date': datetime.strptime('2023-04-21', '%Y-%m-%d')},


    # # strategy_4
    {'code': '601595', 'end_date': datetime.strptime('2023-03-20', '%Y-%m-%d')},
    {'code': '601949', 'end_date': datetime.strptime('2023-04-20', '%Y-%m-%d')},
    {'code': '600860', 'end_date': datetime.strptime('2021-12-01', '%Y-%m-%d')},
    {'code': '002703', 'end_date': datetime.strptime('2022-06-13', '%Y-%m-%d')},
]

format_date = '%Y-%m-%d'
minus_days = 30 * 3
latest_close_price_min = 4
latest_close_price_max = 15
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
        latest_close_price = float(k_line_list[-1]['close'])
        if latest_close_price < latest_close_price_min or latest_close_price > latest_close_price_max:
            if is_test:
                print('latest_close_price: {}, latest_close_price_max: {}'
                      .format(latest_close_price, latest_close_price_max))
            return False
        self.e_count += 1
        strategy.strategy_3(code, k_line_list, m_day=5, is_test=is_test)
        strategy.strategy_4(code, k_line_list, m_day=12, is_test=is_test)

    def choose(self):
        # ds = BaoDataSource()
        ds = EfDataSource()
        strategy = Strategy()
        end_date = ds.get_end_date()
        start_date = end_date - timedelta(days=minus_days)
        start_date_str = start_date.strftime(format_date)
        end_date_str = end_date.strftime(format_date)
        # end_date_str = '2023-06-27'
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
                    print('count: {}, e_count: {}'.format(self.count, self.e_count))
                # if '000837' not in code:
                #     continue
                self.run(code, ds, strategy, start_date_str, end_date_str)
        print('count: {}, e_count: {}'.format(self.count, self.e_count))


if __name__ == '__main__':
    c = Chooser()
    c.choose()