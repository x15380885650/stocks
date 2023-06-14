from datetime import datetime, timedelta
from data_source_bao import BaoDataSource
from data_source_ef import EfDataSource

test_stock_dict = [
    # {'code': '601595', 'end_date': datetime.strptime('2023-03-21', '%Y-%m-%d')},
    # {'code': '600629', 'end_date': datetime.strptime('2023-04-21', '%Y-%m-%d')},
    # {'code': '601949', 'end_date': datetime.strptime('2023-04-21', '%Y-%m-%d')},
    # {'code': '603918', 'end_date': datetime.strptime('2023-05-26', '%Y-%m-%d')},
]

format_date = '%Y-%m-%d'
minus_days = 30*3
pct_change_h = 9.9
pct_change_i = 19.5


class Strategy(object):
    def __init__(self):
        pass

    def run(self):
        ds = BaoDataSource(test_stock_dict)
        # ds = EfDataSource(test_stock_dict)
        end_date = ds.get_end_date()
        start_date = end_date - timedelta(days=minus_days)
        start_date_str = start_date.strftime(format_date)
        end_date_str = end_date.strftime(format_date)
        print('{}--->{}'.format(start_date_str, end_date_str))
        code_list = ds.get_all_stock_code_list()
        count = 0
        for code in code_list:
            count += 1
            if count % 1000 == 0:
                print(count)
            filtered = ds.is_code_filtered(code)
            if filtered:
                continue
            # if '000917' not in code and not test_stock_dict:  # 605028
            #     continue
            test_code = test_stock_dict[-1]['code'] if test_stock_dict else None
            if test_code and test_code not in code:
                continue
            k_line_list = ds.get_stock_kline_history(code, start_date_str, end_date_str)
            total_count = len(k_line_list)
            if total_count < int(minus_days / 2):
                continue
            # is_st = data['isST'].iloc[-1]
            # if is_st == '1':
            #     continue
            # pe_ttm = data['peTTM'].iloc[-1]
            # # if float(pe_ttm) < 0:
            # #     continue
            # trade_status = data['tradestatus'].iloc[-1]
            # if trade_status == '0':
            #     continue
            # latest_close_price = float(data['close'].iloc[-1])
            # if latest_close_price < 5 or latest_close_price > 30:
            #     continue


if __name__ == '__main__':
    s = Strategy()
    s.run()