import os
from collections import defaultdict
from datetime import datetime, timedelta
from itertools import islice
from chinese_calendar import is_holiday, is_workday
from data_source_bao import BaoDataSource
from data_source_ef import EfDataSource
from strategy import Strategy
from constants import pct_change_max_i, pct_change_max_j, latest_close_price_max, latest_close_price_min, \
    stock_value_min, stock_value_max
from dumper_loader import load_data_append_by_json_dump, save_data_append_by_json_dump
from email_helper.email_sender import EmailSender

# https://github.com/mouday/email_helper

test_stock_list = [
]

format_date = '%Y-%m-%d'
minus_days = 30 * 6


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

    def get_valid_stock_list_kline_list(self, code_list, start_date_str, end_date_str):
        stock_list_kline = self.ds.get_stock_list_kline_history(code_list, start_date_str, end_date_str)
        new_stock_list_kline = []
        for stock_k_line in stock_list_kline:
            total_count = len(stock_k_line)
            if total_count < int(minus_days / 2):
                continue
            last_date = stock_k_line[-1]['date']
            if last_date != end_date_str:
                continue
            new_stock_list_kline.append(stock_k_line)
        return new_stock_list_kline

    def get_monitor_code_list(self):
        stock_list = self.ds.get_stocks_realtime_quotes()
        filtered_list = []
        for stock in stock_list.iterrows():
            code = stock[1][0]
            # if code != '000536':
            #     continue
            name = stock[1][1]
            filtered = self.ds.is_code_filtered(code)
            if filtered:
                continue
            if 'ST' in name:
                continue
            try:
                pct_chg = float(stock[1][2])
                if pct_chg < 6:
                    continue
                pct_change_max = self.get_pct_change_max(code)
                if pct_chg >= pct_change_max:
                    continue
                latest_close_price = float(stock[1][3])
                if not (latest_close_price_min <= latest_close_price <= latest_close_price_max):
                    continue
                stock_value = stock[1][15] / 10000 / 10000
                if stock_value > stock_value_max or stock_value < stock_value_min:
                    continue
            except Exception as e:
                # print(e)
                continue
            filtered_list.append(code)
        return filtered_list

    def run(self):
        import time
        strategy = Strategy()
        end_date = datetime.now().date()
        m_day = 60
        test_code_dict = {
            # '603106': '2023-08-04',
            # '603536': '2023-11-24',
            # '000903': '2023-11-27',
            # '600444': '2023-12-04',
            # '600302': '2023-12-06',
            # '603660': '2023-12-07',
            # '002678': '2023-12-12',
            # '603789': '2023-12-15',
            # '600819': '2024-01-12',
            # '002211': '2024-01-15',
        }

        if test_code_dict:
            for stock_code, end_date_str in test_code_dict.items():
                test_end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                test_start_date = test_end_date - timedelta(days=minus_days)
                start_date_str = test_start_date.strftime(format_date)
                stock_list_kline_list = self.get_valid_stock_list_kline_list(
                    [stock_code], start_date_str, end_date_str)
                for stock_kline in stock_list_kline_list:
                    code = stock_kline[-1]['code']
                    strategy.strategy_match_7(code, stock_kline, m_day=m_day)
            return
        start_date = end_date - timedelta(days=minus_days)
        start_date_str = start_date.strftime(format_date)
        end_date_str = end_date.strftime(format_date)
        file_folder = 'data/{}'.format(end_date_str[:end_date_str.rfind('-')])
        notified_file_path = '{}/{}_codes_notified_a.json'.format(file_folder, end_date_str)
        notified_set = set(load_data_append_by_json_dump(notified_file_path, ret_type=[]))
        sleep_time = 2
        while True:
            hour, minute = datetime.now().hour, datetime.now().minute
            if hour != 9 and not (40 <= minute <= 50):
                continue
            try:
                monitor_stock_list = self.get_monitor_code_list()
                print('monitor_stock_list_len: {}'.format(len(monitor_stock_list)))
                stock_list_kline_list = self.get_valid_stock_list_kline_list(
                    monitor_stock_list, start_date_str, end_date_str)
                for stock_kline in stock_list_kline_list:
                    code = stock_kline[-1]['code']
                    strategy_7_ok = strategy.strategy_match_7(code, stock_kline, m_day=m_day)
                    if strategy_7_ok and code not in notified_set:
                        self.notify(code)
                        print('join strategy_7_ok, code: {}'.format(code))
                        save_data_append_by_json_dump(notified_file_path, code)
                        notified_set.add(code)
            except Exception as e:
                print(e)
            print('now: {}, sleep: {}'.format(datetime.now(), sleep_time))
            time.sleep(sleep_time)

    def notify(self, code):
        email = EmailSender("xcg19865@126.com", "HIPJLVTIFUZQKEYB", server='smtp.126.com')
        email.set_header(code)
        email.add_text(code)
        # email.add_receiver("531309575@qq.com")
        email.add_receiver("xucg025@qq.com")
        email.send()


if __name__ == '__main__':
    c = Chooser()
    c.run()