import baostock as bs
from datetime import datetime, timedelta
from collections import Counter

# http://baostock.com/baostock/index.php/Python_API%E6%96%87%E6%A1%A3

format_date = '%Y-%m-%d'
minus_days = 30*6
ratio_min = 20
pct_change_min = 3
pct_change_h = 9.9
pct_change_i = 19.5
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


def is_stock_continue_up(data, t_n_day_max):
    prev_close_price = 0
    t_n_day = 0
    for _, d in data.iterrows():
        close_price = d['close']
        open_price = d['open']
        pct_change = d['pctChg']
        if not close_price or not open_price or not pct_change:
            continue
        # r = float(pct_change)
        r = (float(close_price) - float(open_price)) / float(open_price) * 100
        if r < -0.1:
            return False
        if prev_close_price != 0:
            t_ratio = abs((float(close_price) - prev_close_price) / prev_close_price) * 100
            # if t_ratio <= 0.15:
            #     print(t_ratio)

            if t_ratio > 0.15 and float(close_price) - prev_close_price < 0:
                t_n_day += 1
        prev_close_price = float(close_price)
    if t_n_day >= t_n_day_max:
        return False
    return True


def cond_1(code, data, m_day, p_day):  # 例如5天内有2天涨停
    data_x = data[-m_day:]
    chg_list = []
    for chg in data_x['pctChg']:
        if not chg:
            continue
        if not code.startswith('sz.30'):
            if float(chg) >= pct_change_h:
                chg_list.append(1)
            else:
                chg_list.append(0)
        else:
            if float(chg) >= pct_change_i:
                chg_list.append(1)
            else:
                chg_list.append(0)
    if all(chg_list):
        return False
    if not any(chg_list):
        return False
    res = Counter(chg_list)
    up_days = res[1]
    if up_days > m_day - 3:
        return False

    p_chg_list = chg_list[:p_day]
    if not any(p_chg_list):
        return False
    if chg_list[-1] or chg_list[-2]:
        return False
    prev_close_price = 0
    t_n_day = 0
    for _, d in data_x.iterrows():
        close_price = d['close']
        open_price = d['open']
        pct_change = d['pctChg']
        if not close_price or not open_price or not pct_change:
            continue
        # r = float(pct_change)
        r = (float(close_price) - float(open_price)) / float(open_price) * 100
        if r < -0.1:
            return False
        if prev_close_price != 0:
            t_ratio = abs((float(close_price) - prev_close_price) / prev_close_price) * 100
            # if t_ratio <= 0.15:
            #     print(t_ratio)

            if t_ratio > 0.15 and float(close_price) - prev_close_price < 0:
                t_n_day += 1
        prev_close_price = float(close_price)
    if t_n_day >= 1:
        print('code: {}, t_n_day={}'.format(code, t_n_day))
        return False
    return True


def cond_2(code, data, m_day, p_day):
    data_x = data[-m_day:]
    chg_list = []
    for chg in data_x['pctChg']:
        if not chg:
            continue
        pct_change_x = pct_change_h if not code.startswith('sz.30') else pct_change_i
        if float(chg) >= pct_change_x:
            chg_list.append(1)
        else:
            chg_list.append(0)
    if sum(chg_list) not in [1]:
        return False

    is_continue = is_stock_continue_up(data_x, t_n_day_max=2)
    if not is_continue:
        return False

    return True


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
        # if code.startswith('sz.30'):
        #     continue
        # # print(code)
        # if '000066' not in code:  #600731  600733
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
        if latest_close_price < 5 or latest_close_price > 30:
            continue
        # if latest_close_price > 40:
        #     continue

        # cond_1_ok = cond_1(code, data[-30:], m_day=5, p_day=3)
        # if cond_1_ok:
        #     print('code: {}, cond_1_ok'.format(code))
        cond_2_ok = cond_2(code, data[-30:], m_day=6, p_day=3)
        if cond_2_ok:
            print('code: {}, cond_2_ok'.format(code))
        # cond_5_ok = cond_5(code, data[-60:])
        # if cond_5_ok:
        #     print('code: {}, cond_5_ok'.format(code))
    bs.logout()


if __name__ == '__main__':
    # 获取指定日期全部股票的日K线数据
    run()