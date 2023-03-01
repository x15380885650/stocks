import baostock as bs
from datetime import datetime, timedelta
from dumper_loader import FileDataDumper, load_data_append_simple

# http://baostock.com/baostock/index.php/Python_API%E6%96%87%E6%A1%A3

format_date = '%Y-%m-%d'
minus_days = 30*12
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


def cond(code, data, min_up_days=6, i_pct_chg=True):   # 5天内涨了5次
    l_up_days = []
    for _, d in data[-20:].iterrows():
        close_price = d['close']
        open_price = d['open']
        pct_chg = d['pctChg']
        if not close_price or not open_price or not pct_chg:
            return False
        r_1 = (float(close_price) - float(open_price)) / float(open_price) * 100
        if r_1 >= 0:
            l_up_days.append(1)
            continue
        r_2 = float(pct_chg)
        if r_2 >= 0 and abs(r_1) <= 0.05:
            l_up_days.append(1)
            continue
        l_up_days.append(0)
        # r = r_1
        # if r >= 0 or (r < 0 and abs(r) <= 0.35):
        #     l_up_days.append(1)
        # else:
        #     l_up_days.append(0)
    if not all(l_up_days[-min_up_days:]):
        return False
    # print('code: {}, noticed'.format(code))
    if all(l_up_days[-min_up_days-1:]):
        return False
    # print('code: {}, noticed'.format(code))

    # t_flag_days_ok = False
    # for i in [0, 1, 2, 3]:
    #     t_flag_days = l_up_days[-min_up_days-i:-i] or l_up_days[-min_up_days-i:]
    #     if all(t_flag_days):
    #         t_flag_days_ok = True
    #         break
    # if not t_flag_days_ok:
    #     return False

    prev_close_price = 0
    latest_data = data[-min_up_days:]
    # if i != 0:
    #     latest_data = data[-(min_up_days+i):-i]
    # else:
    #     latest_data = data[-(min_up_days + i):]
    t_n_day = 0
    for _, d in latest_data.iterrows():
        close_price = d['close']
        open_price = d['open']
        if not close_price or not open_price:
            continue
        r = (float(close_price) - float(open_price))/float(open_price) * 100
        if r > 5:
            return False
        if prev_close_price != 0:
            if float(close_price) - prev_close_price < 0:
                return False
            # t_ratio = abs((float(close_price) - prev_close_price) / prev_close_price) * 100
            # if t_ratio > 0.15 and float(close_price) - prev_close_price < 0:
            #     t_n_day += 1
        prev_close_price = float(close_price)
    # if t_n_day > 0:
    #     return False
    min_low_price = get_min_low_price(data)
    r = (float(data.iloc[-1]['close']) - min_low_price)/min_low_price * 100
    print('code: {}, r: {}'.format(code, r))
    # if r < 20:
    #     return False

    return True


def get_max_high_price(data):
    max_price = float(data['high'].iloc[0])
    for price in data['high']:
        if max_price < float(price):
            max_price = float(price)
    return max_price


def get_min_low_price(data):
    min_price = float(data['low'].iloc[0])
    for price in data['low']:
        if min_price > float(price):
            min_price = float(price)
    return min_price


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
    file_path = 'stocks.txt'
    target_stocks_list = load_data_append_simple(file_path, ret_type=[])
    dumper = FileDataDumper(file_path, mode='a+')
    for code in stock_df["code"]:
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
        # if '600064' not in code:  #600731  600733
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

        cond_ok = cond(code, data[-60:], min_up_days=6)
        if not cond_ok:
            continue
        if code not in target_stocks_list:
            dumper.dump_data_by_append(code, json_dumps=False)
        print(code)
    bs.logout()


if __name__ == '__main__':
    # 获取指定日期全部股票的日K线数据
    run()