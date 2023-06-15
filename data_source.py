

class DataSource(object):
    def __init__(self):
        pass

    def get_all_stock_code_list(self, end_date_str):
        raise NotImplementedError

    def get_stock_kline_history(self, code, start_date, end_date):
        raise NotImplementedError

    def is_code_filtered(self, code):
        raise NotImplementedError
