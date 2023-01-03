import baostock as bs
import pandas as pd
from datetime import datetime, timedelta

# http://baostock.com/baostock/index.php/Python_API%E6%96%87%E6%A1%A3

format_date = '%Y-%m-%d'
minus_days = 1
end_date = datetime.now().date()
start_date = end_date - timedelta(days=minus_days)
ratio_min = 20
print(start_date)
print(end_date)


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
        if count % 100 == 0:
            print(count)
        k_rs = bs.query_history_k_data_plus(code, "date,code,open,high,low,close,pctChg", start_date_str, end_date_str)
        data = k_rs.get_data()
        if data.empty:
            continue
        # print(data['open'])
        # print(data['close'])
        close_price = float(data['close'].iloc[-1])
        start_price = float(data['open'].iloc[0])
        ratio = ((close_price-start_price)/start_price)*100
        if ratio >= ratio_min:
            print(code)
    bs.logout()
    # data_df.to_csv("demo_assignDayData.csv", encoding="gbk", index=False)
    # print(data_df)


if __name__ == '__main__':
    # 获取指定日期全部股票的日K线数据
    download_data()