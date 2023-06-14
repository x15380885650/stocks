import baostock as bs
from datetime import datetime, timedelta
from data_source import DataSource


class BaoDataSource(DataSource):
    def __init__(self, test_stock_dict):
        super(BaoDataSource, self).__init__(test_stock_dict)
        bs.login()

    def get_end_date(self):
        end_date_t = self.test_stock_dict[-1]['end_date'] if self.test_stock_dict else datetime.now().date()
        for _ in range(10):
            end_date_str = end_date_t.strftime(self.format_date)
            stock_rs = bs.query_all_stock(end_date_str)
            stock_df = stock_rs.get_data()
            if not stock_df.empty:
                return end_date_t
            else:
                end_date_t = end_date_t - timedelta(days=1)
        return None

    def get_all_stock_list(self):
        stock_list = []
        stock_rs = bs.query_all_stock()
        stock_df = stock_rs.get_data()
        for code in stock_df["code"]:
            stock_list.append(code)
        return stock_list

    def get_stock_kline_history(self, code, start_date, end_date):
        kline_history = []
        k_rs = bs.query_history_k_data_plus(
            code, "date,code,open,high,low,close,pctChg,tradestatus,isST,volume,amount,turn,peTTM", start_date, end_date)
        df = k_rs.get_data()
        for s in df.iterrows():
            stock = s[1]
            code = stock['code']
            date = stock['date']
            _open = stock['open']
            close = stock['close']
            high = stock['high']
            low = stock['low']
            volume = stock['volume']
            amount = stock['amount']
            pct_chg = stock['pctChg']
            turn = stock['turn']
            kline_history.append({'code': code, 'date': date, 'open': _open, 'close': close, 'high': high, 'low': low,
                                  'volume': volume, 'amount': amount, 'pct_chg': pct_chg, 'turn': turn})
        return kline_history


if __name__ == '__main__':
    s = BaoDataSource()
    # s.get_all_stock_list()
    s.get_stock_kline_history('sz.000917', start_date='2023-06-14', end_date='2023-06-14')