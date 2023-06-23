from datetime import datetime, timedelta
from data_source_bao import BaoDataSource
from data_source_ef import EfDataSource
from strategy import Strategy

test_stock_dict = [
    # {'code': '601595', 'end_date': datetime.strptime('2023-03-21', '%Y-%m-%d')},
    # {'code': '601595', 'end_date': datetime.strptime('2023-03-17', '%Y-%m-%d')},
    # {'code': '600629', 'end_date': datetime.strptime('2023-04-21', '%Y-%m-%d')},
    # {'code': '601949', 'end_date': datetime.strptime('2023-04-21', '%Y-%m-%d')},
    # {'code': '601949', 'end_date': datetime.strptime('2023-04-19', '%Y-%m-%d')},
    # {'code': '603918', 'end_date': datetime.strptime('2023-05-26', '%Y-%m-%d')},
    # {'code': '603918', 'end_date': datetime.strptime('2023-05-16', '%Y-%m-%d')},
    # {'code': '000917', 'end_date': datetime.strptime('2023-06-09', '%Y-%m-%d')},

    # strategy_3
    # {'code': '002866', 'end_date': datetime.strptime('2022-06-21', '%Y-%m-%d')},
    # {'code': '000736', 'end_date': datetime.strptime('2022-03-24', '%Y-%m-%d')},
    # {'code': '600629', 'end_date': datetime.strptime('2023-04-17', '%Y-%m-%d')},
    # {'code': '601595', 'end_date': datetime.strptime('2023-03-10', '%Y-%m-%d')},
    # {'code': '600860', 'end_date': datetime.strptime('2021-11-24', '%Y-%m-%d')},
    # {'code': '002992', 'end_date': datetime.strptime('2022-06-23', '%Y-%m-%d')},
    # {'code': '603322', 'end_date': datetime.strptime('2022-05-23', '%Y-%m-%d')},
    # {'code': '601138', 'end_date': datetime.strptime('2023-03-08', '%Y-%m-%d')},
    # {'code': '601858', 'end_date': datetime.strptime('2023-03-31', '%Y-%m-%d')},
    # {'code': '601949', 'end_date': datetime.strptime('2023-04-19', '%Y-%m-%d')},
]

format_date = '%Y-%m-%d'
minus_days = 30 * 3
latest_close_price_min = 4
latest_close_price_max = 20


class Chooser(object):
    def __init__(self):
        pass

    def choose(self):
        # ds = BaoDataSource()
        ds = EfDataSource()
        strategy = Strategy()
        end_date = ds.get_end_date(test_stock_dict)
        start_date = end_date - timedelta(days=minus_days)
        start_date_str = start_date.strftime(format_date)
        end_date_str = end_date.strftime(format_date)
        # end_date_str = '2023-06-15'
        print('{}--->{}'.format(start_date_str, end_date_str))
        code_list = ds.get_all_stock_code_list(end_date_str)
        count = 0
        e_count = 0
        for code in code_list:
            count += 1
            if count % 2000 == 0:
                print('count: {}, e_count: {}'.format(count, e_count))
            filtered = ds.is_code_filtered(code)
            if filtered:
                continue
            # if '002456' not in code and not test_stock_dict:  # 605028
            #     continue
            test_code = test_stock_dict[-1]['code'] if test_stock_dict else None
            if test_code and test_code not in code:
                continue
            k_line_list = ds.get_stock_kline_history(code, start_date_str, end_date_str)
            total_count = len(k_line_list)
            if total_count < int(minus_days / 2):
                continue
            latest_close_price = float(k_line_list[-1]['close'])
            if latest_close_price < latest_close_price_min or latest_close_price > latest_close_price_max:
                continue
            e_count += 1
            # strategy.strategy_1(code, k_line_list, m_day=12)
            # strategy.strategy_2(code, k_line_list, m_day=8)
            # k_line_list = k_line_list[-30:]
            strategy.strategy_3(code, k_line_list, m_day=11)


if __name__ == '__main__':
    c = Chooser()
    c.choose()