import efinance as ef
from datetime import datetime, timedelta

from data_source import DataSource


class EfDataSource(DataSource):
    def __init__(self):
        super(EfDataSource, self).__init__()

    def get_end_date(self):
        return datetime.now().date()
        # now_hour = datetime.now().hour
        # if now_hour >= 15:
        #     return datetime.now().date()
        # else:
        #     return datetime.now().date() - timedelta(days=1)

    def is_code_filtered(self, code):
        if not code.startswith('00') and not code.startswith('60'):
            return True
        # if not code.startswith('00') and not code.startswith('60') and not code.startswith('300'):
        #     return True
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
            name = arr[0]
            code = arr[1]
            date = arr[2]
            _open = arr[3]
            close = arr[4]
            high = arr[5]
            low = arr[6]
            volume = arr[7]
            amount = arr[8]
            amp = arr[9]
            pct_chg = arr[10]
            turn = arr[12]
            kline_history.append({'code': code, 'date': date, 'open': _open, 'close': close, 'high': high, 'low': low,
                                  'volume': volume, 'amount': amount, 'pct_chg': pct_chg, 'turn': turn, 'amp': amp,
                                  'name': name})
        return kline_history

    def get_stock_list_kline_history(self, code_list, start_date, end_date, klt=101):
        stock_kline_history_list = []
        start_date = start_date.replace('-', '')
        end_date = end_date.replace('-', '')
        data = ef.stock.get_quote_history(code_list, beg=start_date, end=end_date, fqt=0, klt=klt)
        for code, df in data.items():
            k_line_list = []
            prev_close = None
            for s in df.iterrows():
                arr = s[1]
                name = arr[0]
                code = arr[1]
                date = arr[2]
                _open = arr[3]
                close = arr[4]
                high = arr[5]
                low = arr[6]
                volume = arr[7]
                amount = arr[8]
                amp = arr[9]
                pct_chg = arr[10]
                turn = arr[12]
                n_item = {'code': code, 'date': date, 'open': _open, 'close': close, 'high': high, 'low': low,
                          'volume': volume, 'amount': amount, 'pct_chg': pct_chg, 'turn': turn, 'amp': amp, 'name': name}
                if prev_close:
                    n_item['prev_close'] = prev_close
                    pct_chg_high = 100 * (n_item['high'] - n_item['prev_close']) / n_item['prev_close']
                    n_item['pct_chg_high'] = round(pct_chg_high, 2)
                k_line_list.append(n_item)
                prev_close = close

            stock_kline_history_list.append(k_line_list)
        return stock_kline_history_list

    def get_daily_billboard(self, start_date, end_date):
        return ef.stock.get_daily_billboard(start_date, end_date)

    def get_stock_value(self, code):
        base_info = ef.stock.get_base_info(code)
        stock_value = base_info[4] / 10000 / 10000
        return stock_value

    def get_stocks_base_info(self, code_list):
        base_info_list = ef.stock.get_base_info(code_list)
        return base_info_list

    def get_stocks_realtime_quotes(self):
        realtime_quotes = ef.stock.get_realtime_quotes()
        return realtime_quotes


