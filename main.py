from datetime import datetime, timedelta
from data_source_bao import BaoDataSource
from data_source_ef import EfDataSource
from strategy import Strategy

test_stock_list = [
    # {'code': '601595', 'end_date': datetime.strptime('2023-03-21', '%Y-%m-%d')},
    # {'code': '601595', 'end_date': datetime.strptime('2023-03-17', '%Y-%m-%d')},
    # {'code': '600629', 'end_date': datetime.strptime('2023-04-21', '%Y-%m-%d')},
    # {'code': '601949', 'end_date': datetime.strptime('2023-04-21', '%Y-%m-%d')},
    # {'code': '601949', 'end_date': datetime.strptime('2023-04-19', '%Y-%m-%d')},
    # {'code': '603918', 'end_date': datetime.strptime('2023-05-26', '%Y-%m-%d')},
    # {'code': '603918', 'end_date': datetime.strptime('2023-05-16', '%Y-%m-%d')},
    # {'code': '000917', 'end_date': datetime.strptime('2023-06-09', '%Y-%m-%d')},

    # # strategy_3    603918
    # {'code': '601595', 'end_date': datetime.strptime('2023-03-10', '%Y-%m-%d')},
    # {'code': '600629', 'end_date': datetime.strptime('2023-04-17', '%Y-%m-%d')},
    # # {'code': '601949', 'end_date': datetime.strptime('2023-04-14', '%Y-%m-%d')},
    # {'code': '000736', 'end_date': datetime.strptime('2022-03-24', '%Y-%m-%d')},
    # {'code': '002866', 'end_date': datetime.strptime('2022-06-21', '%Y-%m-%d')},
    # # {'code': '601138', 'end_date': datetime.strptime('2023-03-06', '%Y-%m-%d')},
    # {'code': '603322', 'end_date': datetime.strptime('2022-05-23', '%Y-%m-%d')},
    # {'code': '600860', 'end_date': datetime.strptime('2021-11-24', '%Y-%m-%d')},
    # # {'code': '601858', 'end_date': datetime.strptime('2023-03-30', '%Y-%m-%d')},
    # # {'code': '002703', 'end_date': datetime.strptime('2022-06-07', '%Y-%m-%d')},
    # {'code': '603767', 'end_date': datetime.strptime('2023-06-19', '%Y-%m-%d')},

    # {'code': '600602', 'end_date': datetime.strptime('2023-06-19', '%Y-%m-%d')},  # temp test

    # # strategy_4
    {'code': '601595', 'end_date': datetime.strptime('2023-03-20', '%Y-%m-%d')},
    #{'code': '600629', 'end_date': datetime.strptime('2023-04-20', '%Y-%m-%d')},
    {'code': '601949', 'end_date': datetime.strptime('2023-04-20', '%Y-%m-%d')},
    ##{'code': '000736', 'end_date': datetime.strptime('2022-03-25', '%Y-%m-%d')},
    #{'code': '603322', 'end_date': datetime.strptime('2022-05-26', '%Y-%m-%d')},
    {'code': '600860', 'end_date': datetime.strptime('2021-12-01', '%Y-%m-%d')},
    {'code': '601858', 'end_date': datetime.strptime('2023-04-11', '%Y-%m-%d')},
    {'code': '002703', 'end_date': datetime.strptime('2022-06-13', '%Y-%m-%d')},
    {'code': '603918', 'end_date': datetime.strptime('2023-05-17', '%Y-%m-%d')},
    {'code': '601698', 'end_date': datetime.strptime('2023-03-02', '%Y-%m-%d')},
    {'code': '002896', 'end_date': datetime.strptime('2022-07-18', '%Y-%m-%d')},
]

format_date = '%Y-%m-%d'
minus_days = 30 * 3
latest_close_price_min = 4
latest_close_price_max = 22
is_test_code = True


class Chooser(object):
    def __init__(self):
        self.count = 0
        self.e_count = 0

    def run(self, code, ds, strategy, start_date_str, end_date_str):
        filtered = ds.is_code_filtered(code)
        if filtered:
            return False
        k_line_list = ds.get_stock_kline_history(code, start_date_str, end_date_str)
        total_count = len(k_line_list)
        if total_count < int(minus_days / 2):
            return False
        latest_close_price = float(k_line_list[-1]['close'])
        if latest_close_price < latest_close_price_min or latest_close_price > latest_close_price_max:
            return False
        self.e_count += 1
        strategy.strategy_3(code, k_line_list, m_day=5)
        strategy.strategy_4(code, k_line_list, m_day=12)

    def choose(self):
        # ds = BaoDataSource()
        ds = EfDataSource()
        strategy = Strategy()
        end_date = ds.get_end_date()
        start_date = end_date - timedelta(days=minus_days)
        start_date_str = start_date.strftime(format_date)
        end_date_str = end_date.strftime(format_date)
        # end_date_str = '2023-06-15'
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
                    self.run(code, ds, strategy, test_start_date_str, test_end_date_str)
            else:
                self.count += 1
                if self.count % 1000 == 0:
                    print('count: {}, e_count: {}'.format(self.count, self.e_count))
                # if '000037' not in code:  # 605028
                #     continue
                self.run(code, ds, strategy, start_date_str, end_date_str)
        print('count: {}, e_count: {}'.format(self.count, self.e_count))


if __name__ == '__main__':
    c = Chooser()
    c.choose()