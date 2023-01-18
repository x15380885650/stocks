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


def cond_3(data, min_up_days):   # 5天内涨了4次
    days = 0
    for _, d in data.iterrows():
        close_price = d['close']
        open_price = d['open']
        if not close_price or not open_price:
            return False
        r = (float(close_price) - float(open_price))/float(open_price) * 100
        if r >= 0:
            days += 1
    if days >= min_up_days:
        r = (float(data.iloc[-1]['close']) - float(data.iloc[0]['open']))/float(data.iloc[0]['open']) * 100
        if 5 <= r <= 10:
            return True

    return False


def get_max_high_price(data):
    max_price = float(data['high'].iloc[0])
    for price in data['high']:
        if max_price < float(price):
            max_price = float(price)
    return max_price


def get_max_high_volume(data):
    max_volume = float(data['volume'].iloc[0])
    for volume in data['volume']:
        if not volume:
            continue
        if max_volume < float(volume):
            max_volume = float(volume)
    return max_volume


# def cond_5(data):
#     for row in data[['date', 'volume']].itertuples(index=False):
#         print(row)



def cond_4(data):
    window_size = 10
    volume_up_ratio_min = 40
    volume_down_ratio_min = 50
    volume_down_days_min = int(window_size/2)-1
    window_pre_sorted_volume_list = []
    window_next_sorted_volume_list = []
    for volume in data[:-window_size]['volume']:
        if not volume:
            continue
        window_pre_sorted_volume_list.append(float(volume))
    if not window_pre_sorted_volume_list:
        return False
    for volume in data[-window_size:]['volume']:
        if not volume:
            continue
        window_next_sorted_volume_list.append(float(volume))
    if not window_next_sorted_volume_list:
        return False
    window_pre_sorted_volume_list.sort(reverse=True)
    window_next_sorted_volume_list.sort(reverse=True)
    window_pre_max_volume = window_pre_sorted_volume_list[0]
    window_next_max_volume = window_next_sorted_volume_list[0]
    if window_pre_max_volume > window_next_max_volume:
        return False
    volume_up_days = 0
    for v in window_next_sorted_volume_list:
        volume_up_ratio = (v - window_pre_max_volume) / window_pre_max_volume * 100
        if volume_up_ratio >= volume_up_ratio_min:
            volume_up_days += 1
    if volume_up_days <= 0:
        return False

    # print('code: {}'.format(data['code'].iloc[0]))
    volume_down_days = 0
    for v in window_next_sorted_volume_list[1:]:
        volume_down_ratio = abs((v - window_next_max_volume) / window_next_max_volume * 100)
        if volume_down_ratio <= volume_down_ratio_min:
            volume_down_days += 1
    if volume_down_days <= volume_down_days_min:
        return False
    window_next_max_price = get_max_high_price(data[-window_size:])
    # print(window_next_max_price)
    max_price_ok = False
    for price in data[-3:]['high']:
        # print(price)
        if float(price) == window_next_max_price:
            max_price_ok = True
            break
    if not max_price_ok:
        return False
    return True


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
        if code.startswith('sh.000'):
            continue
        if '002441' not in code:  #600731  600733
            continue
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
        trade_status = data['tradestatus'].iloc[-1]
        if trade_status == '0':
            continue
        latest_close_price = float(data['close'].iloc[-1])
        if latest_close_price < 5 or latest_close_price > 25:
            continue

        red = is_red(data.iloc[-1])
        if not red:
            continue

        # cond_2_ok = cond_2(data, half_count)
        # if not cond_2_ok:
        #     continue
        #
        # cond_1_ok = cond_1(data[-5:], min_max_day=1)
        # if not cond_1_ok:
        #     continue

        # cond_3_ok = cond_3(data[-5:], min_up_days=4)
        # if not cond_3_ok:
        #     continue

        # cond_4_ok = cond_4(data[-60:])
        # if not cond_4_ok:
        #     continue

        cond_5(data[-60:])

        print(code)
    bs.logout()


if __name__ == '__main__':
    # 获取指定日期全部股票的日K线数据
    run()