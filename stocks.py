import baostock as bs
from datetime import datetime, timedelta

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

    # flag_days = l_up_days[-(min_up_days + 3):]
    # if all(flag_days):
    #     return False

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
    if t_n_day > 1:
        return False
    min_low_price = get_min_low_price(data)
    r = (float(data.iloc[-1]['close']) - min_low_price)/min_low_price * 100
    if r > 20:
        return False

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


def cond_5(code, data, latest_days=5):
    volume_up_ratio_min = 40
    volume_down_ratio_min = 50
    count = data.shape[0]
    scope_interval_days_min = 5
    volume_date_dict = {}
    for row in data[['date', 'volume']].itertuples(index=False):
        vol = row[1]
        date = row[0]
        if not vol or not date:
            continue
        volume_date_dict[int(vol)] = datetime.strptime(date, format_date)
    if not volume_date_dict:
        return False
    sorted_date_volume = sorted(volume_date_dict.items(), key=lambda x: x[0], reverse=True)
    date_list = []
    sorted_volume_list = []
    for item in sorted_date_volume:
        date_list.append(item[1])
        sorted_volume_list.append(item[0])
    sorted_date_list = sorted(date_list)
    max_vol_date_index = sorted_date_list.index(date_list[0])
    if (count-max_vol_date_index) > latest_days:  # 最大量必须在最近的时间内
        return False
    pivot_vol = get_max_high_volume(data[0:count-latest_days])
    q_date_vol_dict = {}
    for index, vol in enumerate(sorted_volume_list):
        volume_up_ratio = (vol-pivot_vol) / pivot_vol * 100
        if volume_up_ratio >= volume_up_ratio_min:
            q_date_vol_dict[volume_date_dict[vol]] = vol
    if not q_date_vol_dict:
        return False
    sorted_q_date_list = sorted(list(q_date_vol_dict.keys()))
    f_date_index = sorted_date_list.index(sorted_q_date_list[0])
    l_scope_days = count-f_date_index
    # if l_scope_days < scope_interval_days_min:
    #     return False
    if l_scope_days not in [3, 4, 5]:
        return False
    f_max_vol = q_date_vol_dict[sorted_q_date_list[0]]
    volume_down_days_min = int(l_scope_days / 2)
    volume_down_days = 0
    l_scope_volumes = list(volume_date_dict.keys())[f_date_index:]
    for vol in l_scope_volumes:
        volume_down_ratio = (vol - f_max_vol) / f_max_vol * 100
        if volume_down_ratio >= -volume_down_ratio_min:
            volume_down_days += 1
    if volume_down_days < volume_down_days_min:
        return False

    latest_days_max_price = get_max_high_price(data[-latest_days:])
    max_price_ok = False
    for price in data[-3:]['high']:
        if float(price) == latest_days_max_price:
            max_price_ok = True
            break
    if not max_price_ok:
        return False

    red_days = 0
    for i in range(f_date_index, count):
        one_data = data.iloc[i]
        red = is_red(one_data)
        if red:
            red_days += 1
    if (red_days/l_scope_days) <= 0.5:
        return False
    pch_chg_count = 0
    pch_chg_sum = 0
    for pct_chg in data[f_date_index:]['pctChg']:
        if not pct_chg:
            continue
        if float(pct_chg) > 6:
            pch_chg_count += 1
        pch_chg_sum += float(pct_chg)
    if pch_chg_count < 1:
        return False
    if pch_chg_sum >= 20:
        # print(pch_chg_sum)
        return False
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
        if code.startswith('sh.000'):
            continue
        if not code.startswith('sz.300'):
            continue
        # # print(code)
        # if '300024' not in code:  #600731  600733
        #     continue
        # if not code.startswith('sz.300'):
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
        if latest_close_price < 5 or latest_close_price > 15:
            continue

        # red = is_red(data.iloc[-1])
        # if not red:
        #     continue

        # cond_2_ok = cond_2(data, half_count)
        # if not cond_2_ok:
        #     continue
        #
        # cond_1_ok = cond_1(data[-5:], min_max_day=1)
        # if not cond_1_ok:
        #     continue

        cond_3_ok = cond_3(code, data[-60:], min_up_days=7)
        if not cond_3_ok:
            continue

        # cond_4_ok = cond_4(data[-60:])
        # if not cond_4_ok:
        #     continue

        # cond_5_ok = cond_5(code, data[-60:])
        # if not cond_5_ok:
        #     continue

        # cond_6_ok = cond_6(code, data[-180:])
        # if not cond_6_ok:
        #     continue


        print(code)
    bs.logout()


if __name__ == '__main__':
    # 获取指定日期全部股票的日K线数据
    run()