import baostock as bs
from datetime import datetime, timedelta
from dumper_loader import FileDataDumper, load_data_append_simple

# http://baostock.com/baostock/index.php/Python_API%E6%96%87%E6%A1%A3

format_date = '%Y-%m-%d'
minus_days = 30*2
ratio_min = 20
pct_change_min = 3
pct_change_h = 9.5
close_price_max = 25


def get_end_date():
    end_date_t = datetime.now().date()
    for _ in range(10):
        end_date_str = end_date_t.strftime(format_date)
        stock_rs = bs.query_all_stock(end_date_str)
        stock_df = stock_rs.get_data()
        if not stock_df.empty:
            return end_date_t
        else:
            end_date_t = end_date_t - timedelta(days=1)
    return None


def cond(code, data, min_up_days=6):   # 5天内涨了5次
    from collections import OrderedDict
    p_days = 15
    p_data = data[-p_days:]
    close_price = float(data.iloc[-1]['close'])
    open_price = float(data.iloc[-1]['open'])
    pct_chg = float(data.iloc[-1]['pctChg'])
    pct_chg_max = 9.5
    if pct_chg < pct_chg_max:
        return False

    date_pct_chg_dict = OrderedDict()
    for row in p_data[['date', 'pctChg']].itertuples(index=False):
        chg = row[1]
        date = row[0]
        if not chg or not date:
            continue
        date_pct_chg_dict[datetime.strptime(date, format_date)] = float(chg)
    if not date_pct_chg_dict:
        return False
    ptc_chg_list = list(date_pct_chg_dict.values())
    m_chg_list = list(filter(lambda x: x > pct_chg_max, ptc_chg_list))
    if len(m_chg_list) != 2:
        return False
    start_index = -1
    end_index = -1
    for i, val in enumerate(ptc_chg_list):
        if start_index == -1 and val > pct_chg_max:
            start_index = i
        if start_index != -1 and val > pct_chg_max:
            end_index = i
    # print(start_index, end_index)
    if end_index - start_index < 3:
        return False
    return True


def get_max_high_price(data):
    max_price = float(data['high'].iloc[0])
    for price in data['high']:
        if max_price < float(price):
            max_price = float(price)
    return max_price


def get_max_pct_chg(data):
    max_pct_chg = float(data['pctChg'].iloc[0])
    for pch_chg in data['pctChg']:
        if max_pct_chg < float(pch_chg):
            max_pct_chg = float(pch_chg)
    return max_pct_chg


def get_min_low_price(data):
    min_price = float(data['low'].iloc[0])
    for price in data['low']:
        if min_price > float(price):
            min_price = float(price)
    return min_price


def get_avg_volume(data):
    sum_volume = 0
    count = data.shape[0]
    for vol in data['volume']:
        if not vol:
            count -= 1
            continue
        sum_volume += float(vol)
    return sum_volume/count

def get_high_close_ratio(one_data):
    try:
        close_price = float(one_data['close'])
        high_price = float(one_data['high'])
        open_price = float(one_data['open'])
        return (high_price-close_price)/(close_price-open_price)
    except Exception as e:
        print(e)
        return -1


def run():
    bs.login()
    end_date = get_end_date()
    if not end_date:
        bs.logout()
        return
    start_date = end_date - timedelta(days=minus_days)
    start_date_str = start_date.strftime(format_date)
    end_date_str = end_date.strftime(format_date)
    print(start_date_str, end_date_str)
    stock_rs = bs.query_all_stock(end_date_str)
    stock_df = stock_rs.get_data()
    count = 0
    # file_path = 'stocks.txt'
    # target_stocks_list = load_data_append_simple(file_path, ret_type=[])
    # dumper = FileDataDumper(file_path, mode='a+')
    for code in stock_df["code"]:
        # print(code)
        count += 1
        if count % 1000 == 0:
            print(count)
        if not (code.startswith('sh') or code.startswith('sz')):
            continue
        if code.startswith('sh.000'):
            continue

        # if not code.startswith('sz.300') and not code.startswith('sz.00'):
        #     continue
        # if code in target_stocks_list:
        #     continue
        # # if not code.startswith('sz.300'):
        #     continue
        # # print(code)
        # if '300962' not in code:  #600731  600733
        #     continue
        k_rs = bs.query_history_k_data_plus(code, "date,code,open,high,low,close,pctChg,tradestatus,isST,volume,amount,turn,peTTM",
                                            start_date_str, end_date_str)
        data = k_rs.get_data()
        if data.empty:
            continue
        total_count = data.shape[0]
        if total_count < int(minus_days/2):
            continue
        half_count = int(total_count / 2)
        is_st = data['isST'].iloc[-1]
        if is_st == '1':
            continue
        pe_ttm = data['peTTM'].iloc[-1]
        # if float(pe_ttm) < 0:
        #     continue
        trade_status = data['tradestatus'].iloc[-1]
        if trade_status == '0':
            continue
        latest_close_price = float(data['close'].iloc[-1])
        if latest_close_price < 4 or latest_close_price > 25:
            continue
        # if latest_close_price < 0 or latest_close_price > 30:
        #     continue

        cond_ok = cond(code, data[-60:], min_up_days=15)
        if not cond_ok:
            continue
        # if code not in target_stocks_list:
        #     dumper.dump_data_by_append(code, json_dumps=False)
        print(code)
    bs.logout()


if __name__ == '__main__':
    # 获取指定日期全部股票的日K线数据
    run()