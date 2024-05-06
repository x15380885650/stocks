import os
from itertools import islice
from dumper_loader import load_data_append_by_json_dump, save_data_list_append_by_json_dump
from constants import pct_change_max_i, pct_change_max_j, latest_close_price_max, latest_close_price_min,\
    stock_value_min, stock_value_max


class CodeFetcher(object):
    def __init__(self, ds):
        self.ds = ds

    def get_pct_change_max(self, code):
        if code.startswith('30') or code.startswith('sz.30'):
            return pct_change_max_j
        return pct_change_max_i

    def fetch_zt_code_list_quick(self, end_date_str):
        file_folder = 'data/{}'.format(end_date_str[:end_date_str.rfind('-')])
        if not os.path.exists(file_folder):
            os.makedirs(file_folder)
        file_path = '{}/{}_codes.json'.format(file_folder, end_date_str)
        if os.path.exists(file_path):
            print('fetch_zt_code_list_quick by file_path: {}'.format(file_path))
            return load_data_append_by_json_dump(file_path, ret_type=[])
        stock_list = self.ds.get_stocks_realtime_quotes()
        filtered_list = []
        for stock in stock_list.iterrows():
            code = stock[1][0]
            name = stock[1][1]
            filtered = self.ds.is_code_filtered(code)
            if filtered:
                continue
            if 'ST' in name:
                continue
            try:
                pct_chg = float(stock[1][2])
                pct_change_max = self.get_pct_change_max(code)
                if pct_chg < pct_change_max:
                    continue
                filtered_list.append(code)
            except Exception as e:
                continue
        if filtered_list:
            save_data_list_append_by_json_dump(file_path, filtered_list)
        return filtered_list

    def fetch_zt_code_list_slow(self, end_date_str):
        file_folder = 'data/{}'.format(end_date_str[:end_date_str.rfind('-')])
        if not os.path.exists(file_folder):
            os.makedirs(file_folder)
        file_path = '{}/{}_codes.json'.format(file_folder, end_date_str)
        file_path_all = '{}/{}_codes_all.json'.format(file_folder, end_date_str)
        file_path_already = '{}/{}_codes_already.json'.format(file_folder, end_date_str)
        if os.path.exists(file_path) and not os.path.exists(file_path_already) and not os.path.exists(file_path_all):
            print('fetch_zt_code_list_slow by file_path: {}'.format(file_path))
            return load_data_append_by_json_dump(file_path, ret_type=[])
        all_code_list = load_data_append_by_json_dump(file_path_all, ret_type=[])
        already_code_list = load_data_append_by_json_dump(file_path_already, ret_type=[])
        filtered_code_list = []
        if not all_code_list:
            all_code_list = self.ds.get_all_stock_code_list(end_date_str)
            save_data_list_append_by_json_dump(file_path_all, all_code_list)
        for index, code in enumerate(all_code_list):
            filtered = self.ds.is_code_filtered(code)
            if filtered:
                continue
            if code in already_code_list:
                continue
            filtered_code_list.append(code)
        print('all_code_list: {}, filtered_code_list: {}'.format(len(all_code_list), len(filtered_code_list)))
        stream = iter(filtered_code_list)
        batch_size = 1000
        count = 0
        while True:
            batch_top_pct_chg_code_list = []
            batch_already_code_list = []
            batch = list(islice(stream, 0, batch_size))
            count += len(batch)
            if batch:
                kline_history_list = self.ds.get_stock_list_kline_history(batch, end_date_str, end_date_str)
                for stock_kline in kline_history_list:
                    if not stock_kline:
                        continue
                    last_date = stock_kline[-1]['date']
                    code = stock_kline[-1]['code']
                    batch_already_code_list.append(code)
                    if last_date != end_date_str:
                        print('code: {}, last_date: {} != end_date_str: {}'.format(code, last_date, end_date_str))
                        continue
                    latest_pct_chg = float(stock_kline[-1]['pct_chg'])
                    pct_change_max = self.get_pct_change_max(code)
                    if latest_pct_chg < pct_change_max:
                        continue
                    batch_top_pct_chg_code_list.append(code)
                save_data_list_append_by_json_dump(file_path, batch_top_pct_chg_code_list)
                save_data_list_append_by_json_dump(file_path_already, batch_already_code_list)
                print('this loop: top_pct_chg_code_count: {}'.format(len(batch_top_pct_chg_code_list)))
            else:
                os.remove(file_path_all)
                os.remove(file_path_already)
                break
        return load_data_append_by_json_dump(file_path, ret_type=[])

    def get_stock_list_kline_list(self, code_list, start_date_str, end_date_str):
        stock_list_kline = self.ds.get_stock_list_kline_history(code_list, start_date_str, end_date_str)
        new_stock_list_kline = []
        for stock_k_line in stock_list_kline:
            last_date = stock_k_line[-1]['date']
            if last_date != end_date_str:
                continue
            new_stock_list_kline.append(stock_k_line)
        return new_stock_list_kline

    def is_stock_basic_satisfied(self, stock):
        try:
            code = stock[1][0]
            name = stock[1][1]
            pct_chg = float(stock[1][2])
            latest_close_price = float(stock[1][3])
            stock_value = stock[1].iloc[15] / 10000 / 10000
            if 'ST' in name:
                return False
            filtered = self.ds.is_code_filtered(code)
            if filtered:
                return False
            if not (latest_close_price_min <= latest_close_price <= latest_close_price_max):
                return False
            if stock_value > stock_value_max or stock_value < stock_value_min:
                return False
            pct_change_max = self.get_pct_change_max(code)
            if pct_chg >= pct_change_max:
                return False
            # stock_total_count += 1
            # if pct_chg > 0:
            #     stock_up_count += 1
            # elif pct_chg < 0:
            #     stock_down_count += 1
            # if pct_chg < pct_chg_min:
            #     continue
            # stock_pct_chg_count += 1
            #
        except Exception as e:
            # print(e)
            return False
        return True

    def fetch_real_time_filtered_code_list(self, pct_chg_min=4):
        stock_list = self.ds.get_stocks_realtime_quotes()
        filtered_list = []
        stock_total_count = 0
        for stock in stock_list.iterrows():
            basic_satisfied = self.is_stock_basic_satisfied(stock)
            if not basic_satisfied:
                continue
            stock_total_count += 1
            pct_chg = float(stock[1][2])
            if pct_chg < pct_chg_min:
                continue
            code = stock[1][0]
            filtered_list.append(code)
        pct_chg_count_ratio = 100 * len(filtered_list) / stock_total_count
        print('stock_total_count: {}, pct_chg>={} count:{}, pct_chg_count_ratio: {}'
              .format(stock_total_count, pct_chg_min, len(filtered_list), pct_chg_count_ratio))
        return filtered_list, pct_chg_count_ratio
