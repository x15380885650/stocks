import efinance as ef
from datetime import datetime, timedelta

from data_source import DataSource


class EfDataSource(DataSource):
    def __init__(self):
        super(EfDataSource, self).__init__()

    def get_end_date(self):
        now_hour = datetime.now().hour
        if now_hour >= 15:
            return datetime.now().date()
        else:
            return datetime.now().date() - timedelta(days=1)

    def is_code_filtered(self, code):
        if not code.startswith('00') and not code.startswith('60'):
            return True
        # if code.startswith('000') or code.startswith('sh.688'):
        #     return True
        # if code.startswith('300') or code.startswith('688'):
        #     return True
        return False

    def get_all_stock_code_list(self, end_date_str):
        stock_list = []
        df = ef.stock.get_realtime_quotes()
        for s in df.iterrows():
            stock_list.append(s[1][0])
        stock_list.sort(reverse=True)
        return stock_list

    def get_stock_kline_history(self, code, start_date, end_date):
        kline_history = []
        start_date = start_date.replace('-', '')
        end_date = end_date.replace('-', '')
        df = ef.stock.get_quote_history(code, beg=start_date, end=end_date, fqt=0)
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



