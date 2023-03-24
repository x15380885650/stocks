import baostock as bs
from datetime import datetime, timedelta

# http://baostock.com/baostock/index.php/Python_API%E6%96%87%E6%A1%A3

format_date = '%Y-%m-%d'
minus_days = 30*6
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


def cond_1(data, min_max_day):  # 例如5天内有2天涨停
    day = 0
    for chg in data['pctChg']:
        if not chg:
            return False
        if float(chg) >= pct_change_h:
            day += 1
        if day >= min_max_day:
            return True
    return False


def cond_2(data, half_count):   # 近期最高点，且涨幅在0-10
    last_half_max_price = get_max_high_price(data[0:half_count])
    next_half_max_price = get_max_high_price(data[half_count:])
    latest_some_days_max_price = get_max_high_price(data[-1:])
    if latest_some_days_max_price == next_half_max_price:
        i_ratio = ((latest_some_days_max_price-last_half_max_price)/last_half_max_price)*100
        if 0 <= i_ratio <= 20:
            return True
    return False


def cond_3(code, data, min_up_days):   # 5天内涨了5次
    l_up_days = []
    for _, d in data[-10:].iterrows():
        close_price = d['close']
        open_price = d['open']
        if not close_price or not open_price:
            return False
        r = (float(close_price) - float(open_price)) / float(open_price) * 100
        if r >= -0.1:
            l_up_days.append(1)
        else:
            l_up_days.append(0)
    t_flag_days = l_up_days[-min_up_days:]
    if not all(t_flag_days):
        return False

    # t_flag = l_up_days[-8]
    # if t_flag == 1:
    #     return False

    flag_days = l_up_days[-(min_up_days + 1):]
    if all(flag_days):
        return False

    prev_close_price = 0
    latest_data = data[-min_up_days:]
    t_n_day = 0
    for _, d in latest_data.iterrows():
        close_price = d['close']
        open_price = d['open']
        if not close_price or not open_price:
            continue
        # r = (float(close_price) - float(open_price))/float(open_price) * 100
        # if r < -0.1 or r > 3.5:
        #     return False
        if prev_close_price != 0:
            t_ratio = abs((float(close_price) - prev_close_price) / prev_close_price) * 100
            # if t_ratio <= 0.15:
            #     print(t_ratio)

            if t_ratio > 0.15 and float(close_price) - prev_close_price < 0:
                t_n_day += 1
        prev_close_price = float(close_price)
    if t_n_day > 0:
        return False
    min_low_price = get_min_low_price(data)
    r = (float(data.iloc[-1]['close']) - min_low_price)/min_low_price * 100
    # if r < 20:
    #     return False

    return True


def cond_8(code, data, min_up_days=5):   # 5天内涨了5次
    print(code)
    l_up_days = []
    for _, d in data[-10:].iterrows():
        close_price = d['close']
        open_price = d['open']
        pct_change = d['pctChg']
        if not close_price or not open_price or not pct_change:
            continue
        # r_1 = float(pct_change)
        r_2 = (float(close_price) - float(open_price)) / float(open_price) * 100
        r_1 = r_2
        if r_1 >= -0.1 or r_2 >= -0.1:
            l_up_days.append(1)
        else:
            l_up_days.append(0)
    t_flag_days = l_up_days[-min_up_days:]
    if sum(t_flag_days) not in [min_up_days-1, min_up_days]:
        return False
    # print(sum(t_flag_days))
    # if not all(t_flag_days):
    #     return False

    # t_flag = l_up_days[-8]
    # if t_flag == 1:
    #     return False

    flag_days = l_up_days[-(min_up_days + 1):]
    if all(flag_days):
        return False

    prev_close_price = 0
    latest_data = data[-min_up_days:]
    t_n_day = 0
    for _, d in latest_data.iterrows():
        close_price = d['close']
        open_price = d['open']
        pct_change = d['pctChg']
        if not close_price or not open_price or not pct_change:
            continue
        # r = float(pct_change)
        r = (float(close_price) - float(open_price)) / float(open_price) * 100
        if r < -0.1 or r > 2.5:
            return False
        if prev_close_price != 0:
            t_ratio = abs((float(close_price) - prev_close_price) / prev_close_price) * 100
            # if t_ratio <= 0.15:
            #     print(t_ratio)

            if t_ratio > 0.15 and float(close_price) - prev_close_price < 0:
                t_n_day += 1
        prev_close_price = float(close_price)
    if t_n_day > 1:
        return False
    min_low_price = get_min_low_price(data)
    r = (float(data.iloc[-1]['close']) - min_low_price)/min_low_price * 100
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


def get_max_high_volume(data):
    max_volume = 0
    for volume in data['volume']:
        if not volume:
            continue
        if max_volume < int(volume):
            max_volume = int(volume)
    return max_volume


def get_latest_low_index(data, low_price):
    latest_index = -1
    for index, price in enumerate(data['low']):
        if not low_price:
            continue
        if float(price) == low_price:
            latest_index = index
    return latest_index

def get_avg_volume(volumes):
    sum_volume = 0
    count = len(volumes)
    for vol in volumes:
        sum_volume += float(vol)
    return int(sum_volume/count)


def cond_5(code, data):
    total_count = data.shape[0]
    volume_list = []
    date_list = []
    for row in data[['date', 'volume']].itertuples(index=False):
        vol = row[1]
        date = row[0]
        if not vol:
            continue
        volume_list.append(int(vol))
        date_list.append(date)
    f_avg_volume = 0
    f_l_count = 0
    f_index = 0
    for index, volume in enumerate(volume_list):
        if index == 0:
            continue
        avg_volume = f_avg_volume if f_avg_volume else get_avg_volume(volume_list[:index])
        if volume >= avg_volume*4:
            if f_index == 0:
                f_index = index
            f_avg_volume = avg_volume
            f_l_count += 1
    if f_index == 0:
        return False
    l_f_count = total_count - f_index
    ra = (f_l_count / l_f_count) * 100
    # print(code, l_f_count, ra)
    if l_f_count < 9 or l_f_count > 20:
        return False
    if ra < 70:
        return False
    l_f_data = data[-l_f_count:]
    red_count = 0
    for _, _d in l_f_data.iterrows():
        close_price = _d['close']
        open_price = _d['open']
        if not close_price or not open_price:
            continue
        if float(close_price) > float(open_price):
            red_count += 1
    rb = (red_count / l_f_count) * 100
    if rb < 65:
        return False
    r_high_price = get_max_high_price(l_f_data[:-1])
    n_high_price = float(data.iloc[-1]['high'])
    rc = (n_high_price - r_high_price) / n_high_price * 100
    # print(code, l_f_count, ra, rb, rc)
    if rc < -5:
        return False
    print(code, l_f_count, ra, rb, rc)
    return True


def cond_6(code, data, latest_days=30):
    count = data.shape[0]
    date_low_price_dict = {}
    for row in data[['date', 'low']].itertuples(index=False):
        low_price = row[1]
        date = row[0]
        if not low_price or not date:
            continue
        date_low_price_dict[datetime.strptime(date, format_date)] = float(low_price)
    if not date_low_price_dict:
        return False
    sorted_date_low_price = sorted(date_low_price_dict.items(), key=lambda x: x[1], reverse=False)
    date_list = []
    sorted_price_list = []
    for item in sorted_date_low_price:
        date_list.append(item[0])
        sorted_price_list.append(item[1])
    # sorted_date_list = sorted(date_list)
    min_low_price = get_min_low_price(data[-latest_days:])
    for row in data[['date', 'low']].itertuples(index=False):
        low_price = row[1]
        date = row[0]
        if not low_price or not date:
            continue
        date_low_price_dict[datetime.strptime(date, format_date)] = float(low_price)
    # min_low_price_date_index = sorted_date_list.index(date_list[0])
    # if (count-min_low_price_date_index) > latest_days:  # 最大量必须在最近的时间内
    #     return False
    min_low_price_date_index = get_latest_low_index(data, min_low_price)
    max_high_price = get_max_high_price(data)
    now_date_close_price = float(data.iloc[-1]['close'])
    min_date_open_price = float(data.iloc[min_low_price_date_index]['open'])
    # min_low_price = sorted_price_list[0]
    down_ratio = (max_high_price-min_low_price)/max_high_price * 100
    if down_ratio < 45:
        return False
    up_ratio = (now_date_close_price-min_date_open_price)/min_date_open_price * 100
    if up_ratio < 0 or up_ratio > 15:
        return False
    print(code, down_ratio, up_ratio, max_high_price)
    return True


def cond_7(code, data, min_up_days=5):
    days = 0
    for _, d in data.iterrows():
        close_price = d['close']
        open_price = d['open']
        if not close_price or not open_price:
            return False
        r = (float(close_price) - float(open_price)) / float(open_price) * 100
        if r >= 0:
            days += 1
    if days >= min_up_days:
        r = (float(data.iloc[-1]['close']) - float(data.iloc[0]['open'])) / float(data.iloc[0]['open']) * 100
        if 10 <= r <= 15:
            return True

    return False

def is_red(one_data):
    return float(one_data['close']) > float(one_data['open'])


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
    for code in stock_df["code"]:
        count += 1
        if count % 1000 == 0:
            print(count)
        if not (code.startswith('sh') or code.startswith('sz')):
            continue
        if code.startswith('sh.000') or code.startswith('sh.688'):
            continue

        # if not code.startswith('sz.30'):
        #     continue
        # # print(code)
        # if '603108' not in code:  #600731  600733
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
        # if latest_close_price < 5 or latest_close_price > 25:
        #     continue
        if latest_close_price > 25:
            continue

        cond_5_ok = cond_5(code, data[-60:])
        if not cond_5_ok:
            continue

        # cond_6_ok = cond_6(code, data[-180:])
        # if not cond_6_ok:
        #     continue

        # cond_8_ok = cond_8(code, data[-180:])
        # if not cond_8_ok:
        #     continue

        print(code)
    bs.logout()


if __name__ == '__main__':
    # 获取指定日期全部股票的日K线数据
    run()