from datetime import datetime, timedelta


class DataSource(object):
    def __init__(self, test_stock_dict):
        self.test_stock_dict = test_stock_dict
        self.format_date = '%Y-%m-%d'

    def get_all_stock_list(self):
        raise NotImplementedError

    def get_stock_kline_history(self, code, start_date, end_date):
        raise NotImplementedError
