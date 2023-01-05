import baostock as bs
import pandas as pd
from datetime import datetime, timedelta

# http://baostock.com/baostock/index.php/Python_API%E6%96%87%E6%A1%A3

format_date = '%Y-%m-%d'
minus_days = 30*12
end_date = datetime.now().date() - timedelta(days=1)
start_date = end_date - timedelta(days=minus_days)
ratio_min = 20
pct_change_min = 3
pct_change_h = 9.5
print(start_date)
print(end_date)


def cond_1(data):
    close_price = float(data['close'].iloc[-1])
    start_price = float(data['open'].iloc[0])
    ratio = ((close_price - start_price) / start_price) * 100
    if not data['pctChg'].iloc[-1]:
        return False
    pct_chg = float(data['pctChg'].iloc[-1])
    if ratio < ratio_min or pct_chg < pct_change_min:
        return False
    for chg in data['pctChg']:
        if float(chg) >= pct_change_h:
            return True
    return False


def cond_2(data):
    for chg in data['pctChg']:
        if not chg or float(chg) <= 0:
            return False
    return True


def get_max_high_price(data):
    max_price = float(data['high'].iloc[0])
    for price in data['high']:
        if max_price < float(price):
            max_price = float(price)
    return max_price


def download_data():
    bs.login()
    start_date_str = start_date.strftime(format_date)
    end_date_str = end_date.strftime(format_date)
    stock_rs = bs.query_all_stock(end_date_str)
    stock_df = stock_rs.get_data()
    if stock_df.empty:
        print('no data')
        bs.logout()
        return
    count = 0
    for code in stock_df["code"]:
        count += 1
        if count % 1000 == 0:
            print(count)
        if code.startswith('sh.000'):
            continue
        # if '002336' not in code:
        #     continue
        k_rs = bs.query_history_k_data_plus(code, "date,code,open,high,low,close,pctChg,tradestatus,isST",
                                            start_date_str, end_date_str)
        data = k_rs.get_data()
        if data.empty:
            continue
        data_shape = data.shape
        if data_shape[0] < int(minus_days/2):
            continue
        is_st = data['isST'].iloc[-1]
        if is_st == '1':
            continue
        trade_status = data['tradestatus'].iloc[-1]
        if trade_status == '0':
            continue

        last_5_data = data[-5:]
        # cond_1_ok = cond_1(last_5_data)
        # if not cond_1_ok:
        #     continue
        # cond_2_ok = cond_2(last_5_data)
        # if not cond_2_ok:
        #     continue
        max_high_price = get_max_high_price(data)
        latest_high_price = float(data['high'].iloc[-1])
        if latest_high_price >= max_high_price:
            print(code)
    bs.logout()


if __name__ == '__main__':
    # 获取指定日期全部股票的日K线数据
    download_data()