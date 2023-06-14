import efinance as ef
from datetime import datetime, timedelta

from data_source import DataSource


class EfDataSource(DataSource):
    def __init__(self, test_stock_dict):
        super(EfDataSource, self).__init__(test_stock_dict)

    def get_end_date(self):
        end_date_t = self.test_stock_dict[-1]['end_date'] if self.test_stock_dict else datetime.now().date()
        return end_date_t

    def get_all_stock_code_list(self):
        stock_list = []
        df = ef.stock.get_realtime_quotes()
        for s in df.iterrows():
            stock_list.append(s[1][0])
        return stock_list

    def get_stock_kline_history(self, code, start_date, end_date):
        kline_history = []
        df = ef.stock.get_quote_history(code, beg=start_date, end=end_date)
        for s in df.iterrows():
            arr = s[1]
            code = arr[1]
            date = arr[2]
            _open = arr[3]
            close = arr[4]
            high = arr[5]
            low = arr[6]
            volume = arr[7]
            amount = arr[8]
            pct_chg = arr[10]
            turn = arr[12]
            kline_history.append({'code': code, 'date': date, 'open': _open, 'close': close, 'high': high, 'low': low,
                                  'volume': volume, 'amount': amount, 'pct_chg': pct_chg, 'turn': turn})
        return kline_history



