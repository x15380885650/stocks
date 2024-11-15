import copy
import pandas as pd
from datetime import datetime
from stockstats import StockDataFrame
from constants import *
OK = 'ok'


class Strategist(object):
    def __init__(self):
        pass

    def is_red(self, data, equal_ok=False):
        if not equal_ok:
            return float(data['close']) > float(data['open'])
        else:
            return float(data['close']) >= float(data['open'])

    def is_green(self, data):
        return float(data['close']) < float(data['open'])

    def get_min_pct_chg_2(self, data_list):
        min_pct_chg_2 = 0
        for data in data_list:
            pct_chg_2 = self.get_pct_chg_2(data)
            if pct_chg_2 < min_pct_chg_2:
                min_pct_chg_2 = pct_chg_2
        return min_pct_chg_2

    def get_max_pct_chg_2(self, data_list):
        max_pct_chg_2 = 0
        for data in data_list:
            pct_chg_2 = self.get_pct_chg_2(data)
            if pct_chg_2 > max_pct_chg_2:
                max_pct_chg_2 = pct_chg_2
        return max_pct_chg_2

    def is_data_list_all_green(self, data_list):
        green_tag_list = []
        for data in data_list:
            close_price = data['close']
            open_price = data['open']
            if not close_price or not open_price:
                continue
            r = float(close_price) - float(open_price)
            if r <= 0:
                green_tag_list.append(1)
            else:
                green_tag_list.append(0)
        if all(green_tag_list):
            return True
        return False

    def is_data_list_all_red(self, data_list):
        red_tag_list = []
        for data in data_list:
            close_price = data['close']
            open_price = data['open']
            if not close_price or not open_price:
                continue
            r = float(close_price) - float(open_price)
            if r >= 0:
                red_tag_list.append(1)
            else:
                red_tag_list.append(0)
        if all(red_tag_list):
            return True
        return False

    def get_up_and_down_num(self, data_list):
        up_num = down_num = 0
        for data in data_list:
            close_price = data['close']
            open_price = data['open']
            if not close_price or not open_price:
                continue
            r = (float(close_price) - float(open_price)) / float(open_price) * 100
            if r > 0:
                # print(r)
                up_num += 1
            else:
                down_num += 1
        return up_num, down_num

    def get_up_and_down_num_2(self, data_list):
        pct_chg_zero_count = 0
        up_num = down_num = 0
        for data in data_list:
            pct_chg = data['pct_chg']
            if pct_chg == 0:
                pct_chg_zero_count += 1
                continue
            if pct_chg > 0:
                up_num += 1
            else:
                down_num += 1
        if pct_chg_zero_count == 1:
            down_num += 1
        return up_num, down_num

    def get_max_high_close_ratio(self, data_list):
        max_ratio = 0
        for data in data_list:
            close_price = data['close']
            high_price = data['high']
            ratio = high_price / close_price
            if ratio > max_ratio:
                max_ratio = ratio
        return max_ratio

    def get_max_high_prev_close_ratio(self, data_list):
        max_ratio = 0
        for data in data_list:
            prev_close_price = data['prev_close']
            high_price = data['high']
            ratio = 100 * (high_price-prev_close_price) / prev_close_price
            ratio = round(ratio, 2)
            if ratio > max_ratio:
                max_ratio = ratio
        return max_ratio

    def get_min_low_prev_close_ratio(self, data_list):
        min_ratio = 0
        for data in data_list:
            prev_close_price = data['prev_close']
            low_price = data['low']
            ratio = 100 * (low_price-prev_close_price) / prev_close_price
            ratio = round(ratio, 2)
            if ratio < min_ratio:
                min_ratio = ratio
        return min_ratio


    def get_max_pct_chg(self, data_list):
        max_pct_chg = float(data_list[0]['pct_chg'])
        for data in data_list:
            pct_chg = data['pct_chg']
            if max_pct_chg < float(pct_chg):
                max_pct_chg = float(pct_chg)
        return max_pct_chg

    def get_min_pct_chg(self, data_list):
        min_pct_chg = float(data_list[0]['pct_chg'])
        for data in data_list:
            pct_chg = data['pct_chg']
            if min_pct_chg > float(pct_chg):
                min_pct_chg = float(pct_chg)
        return min_pct_chg

    def get_max_high_price(self, data_list):
        max_high = float(data_list[0]['high'])
        for data in data_list:
            high = data['high']
            if max_high < float(high):
                max_high = float(high)
        return max_high

    def get_max_close_price(self, data_list):
        max_close = float(data_list[0]['close'])
        for data in data_list:
            close = data['close']
            if max_close < float(close):
                max_close = float(close)
        return max_close

    def get_min_close_price(self, data_list):
        min_close = float(data_list[0]['close'])
        for data in data_list:
            close = data['close']
            if min_close > float(close):
                min_close = float(close)
        return min_close

    def get_min_low_price(self, data_list):
        min_low = float(data_list[0]['low'])
        for data in data_list:
            low = data['low']
            if min_low > float(low):
                min_low = float(low)
        return min_low

    def get_max_turn(self, data_list):
        max_turn = 0
        for data in data_list:
            turn = data['turn']
            if not turn:
                continue
            if max_turn < float(turn):
                max_turn = float(turn)
        return max_turn

    def get_min_turn(self, data_list):
        min_turn = 100
        for data in data_list:
            turn = data['turn']
            if not turn:
                continue
            if min_turn > float(turn):
                min_turn = float(turn)
        return min_turn

    def get_avg_turn(self, data_list):
        sum_turn = 0
        count = len(data_list)
        for data in data_list:
            turn = data['turn']
            if not turn:
                count -= 1
                continue
            sum_turn += float(turn)
        return sum_turn / count

    def get_close_price_list(self, data_list):
        close_price_list = []
        for data in data_list:
            close = data['close']
            close_price_list.append(float(close))
        return close_price_list

    def is_stock_whole_up(self, data_list):
        pct_chg_list = []
        for d in data_list:
            pct_chg = float(d['pct_chg'])
            if pct_chg < 0:
                close_price = d['close']
                open_price = d['open']
                r = (float(close_price) - float(open_price)) / float(open_price) * 100
                if r > pct_chg:
                    pct_chg = r
            pct_chg_list.append(pct_chg)

        # pct_chg_list = [float(d['pct_chg']) for d in data_list]
        pct_chg_list_tag = [0 if pct_chg < 0 and abs(pct_chg) > 0.2 else 1 for pct_chg in pct_chg_list]
        if sum(pct_chg_list_tag) < len(pct_chg_list_tag) - 1:
            return False
        if not pct_chg_list_tag[0]:
            return True

        t_n_day = 0
        t_n_day_max = 1
        for pct_chg in pct_chg_list:
            if pct_chg < 0 and abs(pct_chg) > 1.5:
                t_n_day += 1
        if t_n_day >= t_n_day_max:
            return False
        return True

    def is_stock_complete_up(self, data_list):
        prev_close_price = float(data_list[0]['close'])
        prev_open_price = float(data_list[0]['open'])
        for i, d in enumerate(data_list):
            close_price = float(d['close'])
            open_price = float(d['open'])
            if close_price < open_price:
                return False
            if i == 0:
                continue
            # if not (prev_open_price <= open_price <= prev_close_price):
            if not (open_price <= prev_close_price):
                return False
            if close_price < prev_close_price:
                return False
            prev_close_price = close_price
            prev_open_price = open_price
        return True

    def is_stock_all_red(self, data_list):
        for i, d in enumerate(data_list):
            close_price = float(d['close'])
            open_price = float(d['open'])
            r = (float(close_price) - float(open_price)) / float(open_price) * 100
            if r < 0:
                return False
        return True

    def get_pct_chg_sum(self, data_list):
        pct_chg_sum = 0
        for d in data_list:
            pct_chg = float(d['pct_chg'])
            pct_chg_sum += pct_chg
        return round(pct_chg_sum, 2)

    def get_pct_chg_bitmap(self, k_line_list, pct_chg_max):
        pct_chg_bitmap = []
        for k_line in k_line_list:
            pct_chg = k_line['pct_chg']
            if isinstance(pct_chg, str) and not pct_chg:
                continue
            if float(pct_chg) >= pct_chg_max:
                pct_chg_bitmap.append(1)
            else:
                pct_chg_bitmap.append(0)
        return pct_chg_bitmap

    def get_pct_chg_index_list(self, k_line_list, pct_chg_max):
        pct_chg_bitmap = self.get_pct_chg_bitmap(k_line_list, pct_chg_max)
        index_list = []
        for i, v in enumerate(pct_chg_bitmap):
            if v == 1:
                index_list.append(i)
        return index_list

    def get_pct_chg_num_exceed(self, value, data_list):
        _num = 0
        for data in data_list:
            pct_chg = data['pct_chg']
            if pct_chg >= value:
                _num += 1
        return _num

    def get_pct_chg_num_between(self, v1, v2, data_list):
        _num = 0
        for data in data_list:
            pct_chg = data['pct_chg']
            if v1 <= pct_chg <= v2:
                _num += 1
        return _num

    def get_pct_chg_2_num_exceed(self, value, data_list):
        _num = 0
        for data in data_list:
            pct_chg_2 = self.get_pct_chg_2(d=data)
            if pct_chg_2 >= value:
                _num += 1
        return _num

    def get_pct_chg_2_num_between(self, v1, v2, data_list):
        _num = 0
        for data in data_list:
            pct_chg_2 = self.get_pct_chg_2(d=data)
            if v1 <= pct_chg_2 <= v2:
                _num += 1
        return _num

    def get_pct_chg_num_less(self, value, data_list):
        _num = 0
        for data in data_list:
            pct_chg = data['pct_chg']
            if pct_chg <= value:
                _num += 1
        return _num

    def get_pct_chg_2_num_less(self, value, data_list):
        _num = 0
        for data in data_list:
            pct_chg_2 = self.get_pct_chg_2(d=data)
            if pct_chg_2 <= value:
                _num += 1
        return _num

    def get_interval_to_latest(self, price, data_list, key, cond='=='):
        for idx, data in enumerate(data_list[-1::-1]):
            if cond == '==':
                if data[key] == price:
                    return idx - 1
            else:
                if data[key] >= price:
                    return idx - 1
        return 1000

    def get_pct_chg_2(self, d):
        close_price = float(d['close'])
        open_price = float(d['open'])
        r = (float(close_price) - float(open_price)) / float(open_price) * 100
        return r

    def get_stock_tech(self, k_line_list):
        # https://github.com/jealous/stockstats
        temp_list = []
        for k_line in k_line_list:
            temp_list.append([k_line['date'], k_line['open'], k_line['high'], k_line['low'],
                              k_line['close'], k_line['volume']])
        pd_data = pd.DataFrame(temp_list, columns=['date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        pd_data.set_index('date')
        stock_tech = StockDataFrame.retype(pd_data)
        return stock_tech

    def get_stock_opt_macd(self, k_line_list):
        prev_close_price = k_line_list[-2]['close']
        now_ideal_close_price = prev_close_price * 1.1
        k_line_list_opt = copy.deepcopy(k_line_list)
        k_line_list_opt[-1]['close'] = now_ideal_close_price
        stock_tech = self.get_stock_tech(k_line_list=k_line_list_opt)
        diff, dea = stock_tech['macd'].iloc[-1], stock_tech['macds'].iloc[-1]
        return round(diff, 2), round(dea, 2)

    def get_stock_opt_kdj(self, k_line_list):
        prev_close_price = k_line_list[-2]['close']
        now_ideal_close_price = prev_close_price * 1.1
        k_line_list_opt = copy.deepcopy(k_line_list)
        k_line_list_opt[-1]['close'] = now_ideal_close_price
        stock_tech = self.get_stock_tech(k_line_list=k_line_list_opt)
        k = stock_tech['kdjk']
        d = stock_tech['kdjd']
        j = stock_tech['kdjj']
        return k, d, j

    def get_stock_prev_macd(self, k_line_list):
        stock_tech = self.get_stock_tech(k_line_list=k_line_list)
        diff, dea = stock_tech['macd'].iloc[-2], stock_tech['macds'].iloc[-2]
        return round(diff, 2), round(dea, 2)

    def is_stock_range_macd_gt_0(self, k_line_list, range_days):
        stock_tech = self.get_stock_tech(k_line_list=k_line_list)
        for i in range(2, range_days+2):
            diff, dea = stock_tech['macd'].iloc[-i], stock_tech['macds'].iloc[-i]
            diff, dea = round(diff, 2), round(dea, 2)
            if diff < 0 or dea < 0:
                return False
        return True


    def is_close_price_exceed_ma(self, k_line_list, boll_days=20, days_count=4):
        count = 0
        stock_tech = self.get_stock_tech(k_line_list=k_line_list)
        boll = stock_tech['boll_{}'.format(boll_days)]
        boll_price_series = boll.iloc[-days_count-1:-1]
        for k_line in k_line_list[-days_count-1: -1]:
            close_price = round(k_line['close'], 2)
            ma_price = round(boll_price_series[k_line['date']], 2)
            # print('close_price: {}, ma_20_price: {}'.format(close_price, ma_20_price))
            if close_price < ma_price:
                return False
            if close_price > ma_price:
                count += 1
        if count >= days_count-1:
            return True
        return False

    def get_close_price_exceed_ma_days(self, k_line_list, boll_days, days_interval):
        count = 0
        stock_tech = self.get_stock_tech(k_line_list=k_line_list)
        boll = stock_tech['boll_{}'.format(boll_days)]
        boll_price_series = boll.iloc[-days_interval-1:-1]
        for k_line in k_line_list[-days_interval-1: -1]:
            close_price = round(k_line['close'], 2)
            ma_price = round(boll_price_series[k_line['date']], 2)
            if close_price >= ma_price:
                count += 1
        return count

    def get_low_price_exceed_ma_days(self, k_line_list, boll_days, days_interval):
        count = 0
        stock_tech = self.get_stock_tech(k_line_list=k_line_list)
        boll = stock_tech['boll_{}'.format(boll_days)]
        boll_price_series = boll.iloc[-days_interval-1:-1]
        for k_line in k_line_list[-days_interval-1: -1]:
            low_price = round(k_line['low'], 2)
            ma_price = round(boll_price_series[k_line['date']], 2)
            if low_price > ma_price:
                count += 1
        return count

    def get_one_day_ma(self, stock_tech, ma_day, date_str):
        ma_series = stock_tech['boll_{}'.format(ma_day)]
        ma_dict = ma_series.to_dict()
        ma_val = round(ma_dict[date_str], 2)
        return ma_val



    def get_close_or_open_price_exceed_ma_days(self, k_line_list, boll_days, days_interval):
        count = 0
        stock_tech = self.get_stock_tech(k_line_list=k_line_list)
        boll = stock_tech['boll_{}'.format(boll_days)]
        boll_price_series = boll.iloc[-days_interval-1:-1]
        for k_line in k_line_list[-days_interval-1: -1]:
            close_price = round(k_line['close'], 2)
            open_price = round(k_line['open'], 1)
            _price = open_price if close_price > open_price else close_price
            ma_price = round(boll_price_series[k_line['date']], 2)
            if _price >= ma_price:
                count += 1
        return count

    def get_prev_ma_gt_later_ma_days(self, k_line_list, prev_boll_days, later_boll_days, days_interval):
        count = 0
        stock_tech = self.get_stock_tech(k_line_list=k_line_list)
        boll_prev_boll_days = stock_tech['boll_{}'.format(prev_boll_days)]
        boll_prev_boll_days_price_series = boll_prev_boll_days.iloc[-days_interval-1:-1]
        boll_later_boll_days = stock_tech['boll_{}'.format(later_boll_days)]
        boll_later_boll_days_price_series = boll_later_boll_days.iloc[-days_interval - 1:-1]
        for k_line in k_line_list[-days_interval-1: -1]:
            ma_price_prev_boll_days = round(boll_prev_boll_days_price_series[k_line['date']], 2)
            ma_price_later_boll_days = round(boll_later_boll_days_price_series[k_line['date']], 2)
            if ma_price_prev_boll_days >= ma_price_later_boll_days:
                count += 1
        return count


    def get_latest_close_price_continue_less_ma_days(self, k_line_list, boll_days, days_interval):
        count = 0
        stock_tech = self.get_stock_tech(k_line_list=k_line_list)
        boll = stock_tech['boll_{}'.format(boll_days)]
        boll_price_series = boll.iloc[-2::-1]
        for k_line in k_line_list[-2::-1]:
            close_price = round(k_line['close'], 2)
            ma_price = round(boll_price_series[k_line['date']], 2)
            if close_price >= ma_price:
                break
            else:
                count += 1
        return count

    def get_close_price_exceed_target_price_days(self, k_line_list, target_price):
        count = 0
        for k_line in k_line_list:
            close_price = round(k_line['close'], 2)
            if close_price >= target_price:
                count += 1
        return count

    def is_ma_up_1(self, k_line_list, days, stat_day_min=2):
        prev_close_price = k_line_list[-2]['close']
        now_ideal_close_price = prev_close_price * 1.1
        k_line_list_opt = copy.deepcopy(k_line_list)
        k_line_list_opt[-1]['close'] = now_ideal_close_price
        stock_tech = self.get_stock_tech(k_line_list=k_line_list_opt)
        sat_day = 0
        for i in range(1, days+1):
            ma_5_price = round(stock_tech['boll_{}'.format(5)].iloc[-i], 2)
            ma_10_price = round(stock_tech['boll_{}'.format(10)].iloc[-i], 2)
            ma_20_price = round(stock_tech['boll_{}'.format(20)].iloc[-i], 2)
            ma_30_price = round(stock_tech['boll_{}'.format(30)].iloc[-i], 2)
            # print(ma_5_price, ma_10_price, ma_20_price, ma_30_price)
            # if ma_20_price <= ma_10_price <= ma_5_price:
            if ma_30_price <= ma_20_price <= ma_10_price <= ma_5_price:
                sat_day += 1
            else:
                break
        if sat_day < stat_day_min:
            return False
        return True

    def get_latest_price_continue_exceed_ma_days(self, k_line_list, days):
        prev_close_price = k_line_list[-2]['close']
        now_ideal_close_price = prev_close_price * 1.1
        k_line_list_opt = copy.deepcopy(k_line_list)
        k_line_list_opt[-1]['close'] = now_ideal_close_price
        stock_tech = self.get_stock_tech(k_line_list=k_line_list_opt)
        sat_day = 0
        for i in range(2, days+1):
            close_price = k_line_list[-i]['close']
            ma_5_price = round(stock_tech['boll_{}'.format(5)].iloc[-i], 2)
            ma_10_price = round(stock_tech['boll_{}'.format(10)].iloc[-i], 2)
            ma_20_price = round(stock_tech['boll_{}'.format(20)].iloc[-i], 2)
            ma_30_price = round(stock_tech['boll_{}'.format(30)].iloc[-i], 2)
            if close_price >= ma_5_price or close_price >= ma_10_price:
                sat_day += 1
            else:
                break
        return sat_day

    def get_latest_continue_red_days(self, k_line_list, days):
        sat_day = 0
        for i in range(2, days+1):
            k_line = k_line_list[-i]
            k_line_red = self.is_red(k_line, equal_ok=False)
            if k_line_red:
                sat_day += 1
            else:
                break
        return sat_day

    def get_latest_continue_green_days(self, k_line_list, days):
        sat_day = 0
        for i in range(2, days+1):
            k_line = k_line_list[-i]
            k_line_green = self.is_green(k_line)
            if k_line_green:
                sat_day += 1
            else:
                break
        return sat_day

    def get_latest_continue_exceed_target_close_days(self, k_line_list, days, target_close):
        sat_day = 0
        for i in range(2, days+1):
            k_line = k_line_list[-i]
            close = k_line['close']
            if close >= target_close:
                sat_day += 1
            else:
                break
        return sat_day

    def ma_20_30_golden_days(self, k_line_list, days, stat_day_min=2):
        prev_close_price = k_line_list[-2]['close']
        now_ideal_close_price = prev_close_price * 1.1
        k_line_list_opt = copy.deepcopy(k_line_list)
        k_line_list_opt[-1]['close'] = now_ideal_close_price
        stock_tech = self.get_stock_tech(k_line_list=k_line_list_opt)
        sat_day = 0

        for i in range(2, days+1):
            ma_20_price = round(stock_tech['boll_{}'.format(20)].iloc[-i], 3)
            ma_30_price = round(stock_tech['boll_{}'.format(30)].iloc[-i], 3)
            sat_day += 1
            # print(ma_20_price, ma_30_price)
            if ma_20_price < ma_30_price:
                break
        return sat_day




    def retain_decimals_no_rounding(self, number, decimals=2):
        return int(number*10**decimals) / 10**decimals

    def is_macd_latest_gold(self, k_line_list, days=7):
        prev_close_price = k_line_list[-2]['close']
        now_ideal_close_price = prev_close_price * 1.1
        k_line_list_opt = copy.deepcopy(k_line_list)
        k_line_list_opt[-1]['close'] = now_ideal_close_price
        stock_tech = self.get_stock_tech(k_line_list=k_line_list_opt)
        is_gold = False
        for i in range(1, days):
            diff_prev, dea_prev = stock_tech['macd'].iloc[-i - 1], stock_tech['macds'].iloc[-i - 1],
            diff, dea = stock_tech['macd'].iloc[-i], stock_tech['macds'].iloc[-i]
            if dea > diff:
                continue
            r = (diff_prev-dea_prev) * (diff-dea)
            # print(r)
            if r <= 0:
                is_gold = True
                break
        return is_gold

    def get_max_pct_chg_binary_list(self, k_line_list):
        max_pct_chg_list = []
        for k_line in k_line_list:
            pct_chg = k_line['pct_chg']
            if isinstance(pct_chg, str) and not pct_chg:
                continue
            pct_chg_max = pct_change_max_i
            if float(pct_chg) >= pct_chg_max:
                max_pct_chg_list.append(1)
            else:
                max_pct_chg_list.append(0)
        return max_pct_chg_list

    def is_open_price_high(self, k_line_list, open_close_ratio_max=3.0, open_close_ratio_mim=-3.0):
        prev_close_price = k_line_list[-2]['close']
        now_open_price = k_line_list[-1]['open']
        open_close_ratio = 100 * (now_open_price - prev_close_price) / prev_close_price
        open_close_ratio = self.retain_decimals_no_rounding(open_close_ratio, decimals=1)
        # print(open_close_ratio)
        if open_close_ratio > open_close_ratio_max or open_close_ratio < open_close_ratio_mim:
            return True
        return False

    def get_diff_sat_count(self, k_line_list, days, dea_min_check=False):
        sat_count = 0
        stock_tech = self.get_stock_tech(k_line_list=k_line_list)
        for i in range(1, days):
            diff, dea = stock_tech['macd'].iloc[-i - 1], stock_tech['macds'].iloc[-i - 1]
            diff = round(diff, 2)
            dea = round(dea, 2)
            if not dea_min_check:
                if diff >= 0 and diff >= dea:
                    sat_count += 1
            else:
                if diff >= 0 and diff >= dea >= 0:
                    sat_count += 1
        return sat_count

    def is_prev_macd_gold(self, k_line_list):
        prev_close_price = k_line_list[-2]['close']
        now_ideal_close_price = prev_close_price * 1.1
        k_line_list_opt = copy.deepcopy(k_line_list)
        k_line_list_opt[-1]['close'] = now_ideal_close_price
        stock_tech = self.get_stock_tech(k_line_list=k_line_list_opt)
        is_gold = False
        for i in range(1, 2):
            diff_prev, dea_prev = stock_tech['macd'].iloc[-i - 2], stock_tech['macds'].iloc[-i - 2],
            diff, dea = stock_tech['macd'].iloc[-i], stock_tech['macds'].iloc[-i]
            if dea > diff:
                continue
            r = (diff_prev - dea_prev) * (diff - dea)
            # print(r)
            if r <= 0:
                is_gold = True
                break
        return is_gold

    def is_prev_kdj_gold(self, k_line_list):
        k, d, j = self.get_stock_opt_kdj(k_line_list)
        k_prev_v, d_prev_v, j_prev_v = k.iloc[-2], d.iloc[-2], j.iloc[-2]
        k_v, d_v, j_v = k.iloc[-1], d.iloc[-1], j.iloc[-1]
        print(k_prev_v, d_prev_v, j_prev_v)
        print(k_v, d_v, j_v)
        if not (j_prev_v < k_prev_v < d_prev_v):
            return False
        if not (d_v < k_v < j_v):
            return False
        if not (k_v > k_prev_v and d_v > d_prev_v and j_v > j_prev_v):
            return False
        return True

    def is_target_day_zt_time_ok(self, target_close_p, temp_prev_close_p, k_line_list):
        for minute_k_line in k_line_list[0]:
            minute_k_line_close = minute_k_line['close']
            temp_prev_close_p_ratio = 100 * (minute_k_line_close-temp_prev_close_p)/temp_prev_close_p
            if (minute_k_line_close == target_close_p) or (temp_prev_close_p_ratio>9):
            # if minute_k_line_close == target_close_p:
                # print(minute_k_line['date'])
                time_obj = datetime.strptime(minute_k_line['date'], "%Y-%m-%d %H:%M")
                hour = time_obj.hour
                if hour < 12:
                    return True
                else:
                    return False
        return True

    def get_first_strategy_res(self, code, k_line_list, min_opt_macd_diff=0):
        return False, 'a'

    def get_second_strategy_res(self, k_line_list, c_fetcher):
        # code = k_line_list[-1]['code']
        open_high = self.is_open_price_high(k_line_list, open_close_ratio_max=3, open_close_ratio_mim=-3)
        if open_high:
            return False, 'a'
        # print(k_line_list[-1]['close'])
        s_pct_chg_sum = 0
        for s in k_line_list[-20:-1]:
            pct_chg = s['pct_chg']
            s_pct_chg_sum += pct_chg
        s_pct_chg_sum = self.retain_decimals_no_rounding(s_pct_chg_sum, decimals=0)
        if s_pct_chg_sum > 45:
            return False, 'aaa'
        range_days = 9
        latest_range_days_k_line_list = k_line_list[-range_days:-1]
        temp_k_line_list = k_line_list[-range_days - 1:-1]
        max_pct_chg_binary_list = self.get_max_pct_chg_binary_list(latest_range_days_k_line_list)
        max_pct_chg_index_list = []
        for i, v in enumerate(max_pct_chg_binary_list):
            if v == 1:
                max_pct_chg_index_list.append(i)
        if len(max_pct_chg_index_list) not in [1]:
            return False, "aaa"
        origin_stock_tech = self.get_stock_tech(k_line_list=k_line_list)
        target_index = max_pct_chg_index_list[-1]
        t_s_count = range_days - target_index - 2
        if t_s_count not in [5, 6]:
            return False, 'aaa'
        latest_target_days_k_line_list = latest_range_days_k_line_list[target_index + 1:]
        target_k_line = latest_range_days_k_line_list[target_index]
        target_date_p = target_k_line['date']
        target_close_p = target_k_line['close']
        target_open_p = target_k_line['open']
        target_prev_k_line = temp_k_line_list[target_index]
        target_prev_close_p = target_prev_k_line['close']
        target_prev_date_p = target_prev_k_line['date']
        target_prev_ma_5_val = self.get_one_day_ma(origin_stock_tech, ma_day=5, date_str=target_prev_date_p)
        target_prev_ma_10_val = self.get_one_day_ma(origin_stock_tech, ma_day=10, date_str=target_prev_date_p)
        target_prev_ma_val = target_prev_ma_5_val if target_prev_ma_5_val < target_prev_ma_10_val else target_prev_ma_10_val
        target_val = target_open_p if target_open_p > target_prev_close_p else target_prev_close_p
        if target_val < target_prev_ma_val:
            return False, "aaa"
        latest_k_line = latest_target_days_k_line_list[-1]
        latest_close_p = latest_k_line['close']
        l_r_close_ratio = 100 * (latest_close_p - target_close_p) / target_close_p
        l_r_close_ratio = self.retain_decimals_no_rounding(l_r_close_ratio, 1)
        # print(l_r_close_ratio, t_s_count)
        l_r_r_close_ratio = (l_r_close_ratio/t_s_count)
        if l_r_r_close_ratio > 1.2:
            return False, 'ccc'
        max_close_price_interval = self.get_max_close_price(latest_target_days_k_line_list)
        now_ideal_close_price = round(k_line_list[-2]['close'] * 1.1, 2)
        if max_close_price_interval < target_close_p:
            return False, 'ccc'
        if max_close_price_interval > now_ideal_close_price:
            return False, 'ccc'
        if now_ideal_close_price < target_close_p:
            return False, 'ccc'

        close_open_p_count = 0
        close_p_count = 0
        open_p_count = 0
        low_p_count = 0
        # target_open_p_adjust = target_prev_close_p if target_prev_close_p < target_open_p else target_open_p
        # print(target_prev_close_p, target_open_p)
        target_open_p_adjust = target_open_p
        for t_k_line in latest_target_days_k_line_list:
            close_p = t_k_line['close']
            open_p = t_k_line['open']
            low_p = t_k_line['low']
            if close_p < target_open_p_adjust or open_p < target_open_p_adjust or low_p < target_open_p_adjust:
                return False, 'ddd'
            if close_p >= target_close_p or open_p >= target_close_p:
                close_open_p_count += 1
            if close_p >= target_close_p:
                close_p_count += 1
            if open_p >= target_close_p:
                open_p_count += 1
            if low_p >= target_close_p:
                low_p_count += 1
        low_p_count_ratio = 100 * (low_p_count/t_s_count)
        low_p_count_ratio = self.retain_decimals_no_rounding(low_p_count_ratio, decimals=0)
        close_open_p_count_ratio = 100 * close_open_p_count / t_s_count
        # print(low_p_count, t_s_count, low_p_count_ratio, close_open_p_count_ratio)
        if low_p_count_ratio > 70:
            return False, 'ddd'
        if close_open_p_count_ratio < 40:
            return False, 'ddd'

        up_num, down_num = self.get_up_and_down_num(latest_target_days_k_line_list)
        up_num_2, down_num_2 = self.get_up_and_down_num_2(latest_target_days_k_line_list)
        # print(down_num, down_num_2, t_s_count)
        if down_num + down_num_2 <= 3:
            return False, 'eee'
        if down_num not in [2, 3, 4] and down_num_2 not in [2, 3, 4]:
            return False, 'eee'

        t_l_k_line_low = latest_target_days_k_line_list[-1]['low']
        t_l_1_ratio = 100 * (t_l_k_line_low - latest_target_days_k_line_list[-2]['close']) / \
                      latest_target_days_k_line_list[-2]['close']
        t_l_2_ratio = latest_target_days_k_line_list[-1]['pct_chg']
        t_l_1_ratio = self.retain_decimals_no_rounding(t_l_1_ratio, decimals=1)
        t_l_2_ratio = self.retain_decimals_no_rounding(t_l_2_ratio, decimals=1)
        # print(f't_l_1_ratio: {t_l_1_ratio}, t_l_2_ratio: {t_l_2_ratio}')
        if t_l_1_ratio < -8 or t_l_2_ratio < -6:
            return False, 'fff'
        #
        pct_chg_lt_0_list = []
        pct_chg_gt_0_list = []
        for t_k_line in latest_target_days_k_line_list:
            prev_close_p = t_k_line['prev_close']
            open_p = t_k_line['open']
            high_p = t_k_line['high']
            close_p = t_k_line['close']
            pct_chg_p = t_k_line['pct_chg']
            if pct_chg_p < 0:
                pct_chg_lt_0_list.append(pct_chg_p)
            if pct_chg_p > 0:
                pct_chg_gt_0_list.append(pct_chg_p)
            t_t_ratio_3 = 100 * (high_p - close_p)/close_p
            if t_t_ratio_3 > 11:
                return False, 'fff'
        max_pct_chg = self.get_max_pct_chg(latest_target_days_k_line_list)
        min_pct_chg = self.get_min_pct_chg(latest_target_days_k_line_list)
        min_pct_chg = self.retain_decimals_no_rounding(min_pct_chg, decimals=1)
        max_pct_chg = self.retain_decimals_no_rounding(max_pct_chg, decimals=1)
        # print(max_pct_chg, min_pct_chg)
        if max_pct_chg > 8.5 or min_pct_chg < -7:
            return False, 'fff'
        # min_pct_chg_ratio = round(100*min_pct_chg/t_s_count, 0)
        # max_pct_chg_ratio = round(100*max_pct_chg/t_s_count, 0)
        # print(max_pct_chg, min_pct_chg, t_s_count, min_pct_chg_ratio, max_pct_chg_ratio)
        # if min_pct_chg_ratio > -50 or max_pct_chg_ratio < 45:
        #     return False, 'fff'

        t_3_k_line = latest_target_days_k_line_list[0]
        t_1_k_line = latest_range_days_k_line_list[target_index]
        t_3_k_line_green_ok = self.is_green(t_3_k_line)
        if t_3_k_line_green_ok:
            t_1_k_line_close = t_1_k_line['close']
            t_3_k_line_high = t_3_k_line['high']
            t_3_k_line_open = t_3_k_line['open']
            t_3_k_pct_chg = t_3_k_line['pct_chg']
            t_t_ratio = 100 * (t_3_k_line_high - t_1_k_line_close) / t_1_k_line_close
            t_t_ratio_2 = 100 * (t_3_k_line_high - t_3_k_line_open) / t_3_k_line_open
            t_t_ratio = self.retain_decimals_no_rounding(t_t_ratio, 1)
            # print(f't_t_ratio:{t_t_ratio}, t_3_k_pct_chg:{t_3_k_pct_chg}')
            if t_t_ratio > 9 or t_3_k_pct_chg > 3:
                return False, 'fff'

        boll_days_30_count___ = self.get_close_or_open_price_exceed_ma_days(k_line_list, boll_days=30, days_interval=t_s_count+1)
        boll_days_20_count___ = self.get_close_or_open_price_exceed_ma_days(k_line_list, boll_days=20,days_interval=t_s_count + 1)
        boll_days_30_count___ratio = 100 * boll_days_30_count___ / (t_s_count+1)
        boll_days_20_count___ratio = 100 * boll_days_20_count___ / (t_s_count+1)
        if boll_days_20_count___ratio != 100 and boll_days_30_count___ratio != 100:
            return False, 'ggg'
        #
        boll_days_30_count = self.get_close_or_open_price_exceed_ma_days(k_line_list, boll_days=30, days_interval=t_s_count)
        boll_days_30_count_ = self.get_low_price_exceed_ma_days(k_line_list, boll_days=30, days_interval=t_s_count)
        boll_days_30_count_ratio = 100 * boll_days_30_count / t_s_count
        if boll_days_30_count_ratio < 100 or boll_days_30_count_ != boll_days_30_count:
            return False, 'ggg'
        boll_days_20_count = self.get_close_or_open_price_exceed_ma_days(k_line_list, boll_days=20, days_interval=t_s_count)
        boll_days_20_count_ = self.get_low_price_exceed_ma_days(k_line_list, boll_days=20, days_interval=t_s_count)
        boll_days_20_count_ratio = 100 * boll_days_20_count / t_s_count
        if boll_days_20_count_ratio < 100 or boll_days_20_count_ != boll_days_20_count:
            return False, 'ggg'
        boll_days_10_count = self.get_close_or_open_price_exceed_ma_days(k_line_list, boll_days=10, days_interval=t_s_count)
        boll_days_10_count_ = self.get_low_price_exceed_ma_days(k_line_list, boll_days=10, days_interval=t_s_count)
        boll_days_10_count_ratio = 100 * boll_days_10_count / t_s_count
        boll_days_10_count__ratio = 100 * boll_days_10_count_ / t_s_count
        if boll_days_10_count_ratio < 60 or boll_days_10_count__ratio < 40:
            return False, 'ggg'
        boll_days_5_count = self.get_close_or_open_price_exceed_ma_days(k_line_list, boll_days=5, days_interval=t_s_count)
        boll_days_5_count_ratio = 100 * boll_days_5_count / t_s_count
        if boll_days_5_count_ratio < 20:
            return False, 'ggg'
        ma_up = self.is_ma_up_1(k_line_list, t_s_count+1, stat_day_min=2)
        if not ma_up:
            return False, 'ggg'
        continue_exceed_ma_days = self.get_latest_price_continue_exceed_ma_days(k_line_list, t_s_count + 1)
        if continue_exceed_ma_days < 1:
            return False, 'ggg'
        continue_red_days = self.get_latest_continue_red_days(k_line_list, t_s_count + 1)
        continue_red_days_ratio = 100 * continue_red_days / t_s_count
        if continue_red_days_ratio > 20:
            return False, 'ggg'
        diff_sat_count = self.get_diff_sat_count(k_line_list, t_s_count + 1)
        diff_sat_count_ratio = 100 * diff_sat_count / t_s_count
        if diff_sat_count_ratio < 100:
            return False, 'ggg'
        # minute_k_line_list = c_fetcher.get_stock_list_minute_kline_list([code], target_date_p, target_date_p)
        # if minute_k_line_list:
        #     zt_time_ok = self.is_target_day_zt_time_ok(target_close_p, target_prev_close_p, minute_k_line_list)
        #     if not zt_time_ok:
        #         return False, 'ggg'
        return True, OK

    def get_third_strategy_res(self, k_line_list, c_fetcher):
        return False, 'a'

    def get_fourth_strategy_res(self, k_line_list, c_fetcher):
        open_high = self.is_open_price_high(k_line_list, open_close_ratio_max=5, open_close_ratio_mim=-11)
        if open_high:
            return False, 'aaa'
        latest_30_days_k_line_list = k_line_list[-31:-1]
        range_days = 7
        latest_range_days_k_line_list = k_line_list[-range_days:-1]
        temp_k_line_list = k_line_list[-range_days - 1:-1]
        max_pct_chg_binary_list = self.get_max_pct_chg_binary_list(latest_range_days_k_line_list)
        max_pct_chg_index_list = []
        for i, v in enumerate(max_pct_chg_binary_list):
            if v == 1:
                max_pct_chg_index_list.append(i)
        if len(max_pct_chg_index_list) not in [3, 4]:
            return False, "aaa"
        if max_pct_chg_index_list[-1] != 4 or max_pct_chg_index_list[-2] != 3 or max_pct_chg_index_list[-3] != 2:
            return False, "bbb"
        target_index = max_pct_chg_index_list[-1]
        latest_target_days_k_line_list = latest_range_days_k_line_list[target_index + 1:]
        latest_k_line = latest_target_days_k_line_list[-1]
        latest_k_line_green = self.is_green(latest_k_line)
        if not latest_k_line_green:
            return False, 'ccc'
        latest_k_line_pct_chg = latest_k_line['pct_chg']
        latest_k_line_pct_chg = self.retain_decimals_no_rounding(latest_k_line_pct_chg, decimals=1)
        if latest_k_line_pct_chg >= 0:
            return False, 'ddd'
        latest_prev_k_line = latest_range_days_k_line_list[-2]
        latest_prev_k_line_close = latest_prev_k_line['close']
        now_k_line_open = k_line_list[-1]['open']
        latest_prev_k_line_close_ratio = 100 * (latest_prev_k_line_close-now_k_line_open)/now_k_line_open
        if latest_prev_k_line_close_ratio <= 0:
            return False, 'aaa'
        latest_30_days_high_max = self.get_max_high_price(latest_30_days_k_line_list)
        latest_k_line_high = latest_k_line['high']
        if latest_k_line_high != latest_30_days_high_max:
            return False, 'eee'
        code = latest_range_days_k_line_list[-1]['code']
        zt_list = []
        for k_line in latest_range_days_k_line_list[-2::-1]:
            zt_minute_count = 0
            total_minute_count = 0
            k_line_date = k_line['date']
            k_line_pct_chg = k_line['pct_chg']
            k_line_close = k_line['close']
            if k_line_pct_chg < pct_change_max_i:
                continue
            zt_first_time = None
            minute_k_line_list = c_fetcher.get_stock_list_minute_kline_list([code], k_line_date, k_line_date)
            if minute_k_line_list:
                for minute_k_line in minute_k_line_list[0]:
                    minute_k_line_close = minute_k_line['close']
                    total_minute_count += 1
                    if minute_k_line_close == k_line_close:
                        if not zt_first_time:
                            zt_first_time = minute_k_line['date']
                        zt_minute_count += 1
            zt_list.append({'zt_first_time': zt_first_time, 'zt_minute_count': zt_minute_count, 'total_minute_count': total_minute_count})
        if len(zt_list) != len(max_pct_chg_index_list):
            return False, 'fff'
        # print(zt_minute_list)
        zt_minute_ok_list = []
        for idx, zt in enumerate(zt_list):
            zt_first_time = zt['zt_first_time']
            zt_minute_ratio = round(100*zt['zt_minute_count'] / zt['total_minute_count'], 2)
            # print(zt_first_time, zt_minute_ratio)
            if idx == 0 and zt_minute_ratio < 95:
                zt_minute_ok_list.append(False)
                continue
            time_obj = datetime.strptime(zt_first_time, "%Y-%m-%d %H:%M")
            hour = time_obj.hour
            minute = time_obj.minute
            if hour <= 9 and minute <= 45:
                zt_minute_ok_list.append(True)
            else:
                zt_minute_ok_list.append(False)
        # print(zt_minute_ok_list)
        if not zt_minute_ok_list[0] or not zt_minute_ok_list[1]:
            return False, 'ggg'
        pct_chg_sum = 0
        for t_k_line in latest_range_days_k_line_list:
            pct_chg_sum += t_k_line['pct_chg']
        t_t_kline_close = latest_range_days_k_line_list[-1]['close']
        t_t_kline_open = latest_range_days_k_line_list[0]['open']
        t_t_kline_ratio = 100 * (t_t_kline_close-t_t_kline_open)/t_t_kline_open
        if t_t_kline_ratio > 35:
            return False, 'hhh'
        return True, OK

    def get_fifth_strategy_res(self, code, k_line_list, min_opt_macd_diff=0):
        return False, 'a'

    def is_target_k_line_ok(self, range_days, k_line_list, max_pct_chg_index_list, latest_range_days_k_line_list):
        stock_tech = self.get_stock_tech(k_line_list=k_line_list)
        target_v_k_line_index = max_pct_chg_index_list[-2]
        target_v_k_line_interval = -1
        target_v_k_line_interval_ok = False
        for idx, target_v_k_line in enumerate(latest_range_days_k_line_list[target_v_k_line_index::-1]):
            target_v_k_line_interval = idx
            for day in [5, 10]:
                boll_day = stock_tech['boll_{}'.format(day)]
                boll_day_price = round(boll_day.iloc[-range_days + target_v_k_line_index - idx], 2)
                target_v_k_line_open = target_v_k_line['open']
                target_v_k_line_close = target_v_k_line['close']
                # if not (boll_day_price < target_v_k_line_close and boll_day_price < target_v_k_line_open):
                # print(boll_day_price, target_v_k_line_open)
                boll_day_price = round(boll_day_price, 1)
                target_v_k_line_open = round(target_v_k_line_open, 1)
                # print(boll_day_price, target_v_k_line_open)
                if boll_day_price <= target_v_k_line_open:
                    target_v_k_line_interval_ok = True
                    break
            if target_v_k_line_interval_ok:
                break
        v_v_v = target_v_k_line_index - target_v_k_line_interval
        if len(max_pct_chg_index_list) > 2:
            if v_v_v == max_pct_chg_index_list[-2]:
                return True
        else:
            # if v_v_v == max_pct_chg_index_list[0] or v_v_v == max_pct_chg_index_list[0]-1:
            if v_v_v == max_pct_chg_index_list[0]:
                return True
        return False

    def get_sixth_strategy_res(self, k_line_list, c_fetcher):
        open_high = self.is_open_price_high(k_line_list, open_close_ratio_max=2, open_close_ratio_mim=-2)
        if open_high:
            return False, 'a'
        range_days = 18
        latest_range_days_k_line_list = k_line_list[-range_days:-1]
        temp_k_line_list = k_line_list[-range_days - 1:-1]
        max_pct_chg_binary_list = self.get_max_pct_chg_binary_list(latest_range_days_k_line_list)
        max_pct_chg_index_list = []
        v_k_line_count = 0
        target_v_k_line = None
        for i, v in enumerate(max_pct_chg_binary_list):
            if v == 1:
                max_pct_chg_index_list.append(i)
                v_k_line = latest_range_days_k_line_list[i]
                if not target_v_k_line:
                    target_v_k_line = v_k_line
                v_k_line_open = v_k_line['open']
                v_k_line_close = v_k_line['close']
                if v_k_line_open == v_k_line_close:
                    v_k_line_count += 1

        max_pct_chg_index_list_len = len(max_pct_chg_index_list)
        if max_pct_chg_index_list_len not in [2, 3, 4]:
            return False, "aaa"
        if max_pct_chg_index_list_len == 2:
            if max_pct_chg_index_list[-1] - max_pct_chg_index_list[-2] > 1:
                return False, "aaa"
        elif max_pct_chg_index_list_len == 3:
            if max_pct_chg_index_list[-1] - max_pct_chg_index_list[-2] > 5:
                return False, "aaa"
        if max_pct_chg_index_list[-1] > 11 or max_pct_chg_index_list[-1] < 6:
            return False, "aaa"
        kkk_pct_chg_sum = 0
        for kkk in latest_range_days_k_line_list[max_pct_chg_index_list[0]: max_pct_chg_index_list[-1] + 1]:
            kkk_pct_chg_sum += kkk['pct_chg']
        if kkk_pct_chg_sum > 35:
            return False, "aaa"
        diffs = [max_pct_chg_index_list[i + 1] - max_pct_chg_index_list[i] for i in
                 range(len(max_pct_chg_index_list) - 1)]
        if 1 not in diffs:
            return False, 'aaa'
        target_k_line_ok = self.is_target_k_line_ok(range_days, k_line_list, max_pct_chg_index_list, latest_range_days_k_line_list)
        if not target_k_line_ok:
            return False, "aaa"

        t_t_kline = latest_range_days_k_line_list[max_pct_chg_index_list[-1]]
        t_t_t_kline = latest_range_days_k_line_list[max_pct_chg_index_list[-2]]
        t_t_t_kline_close = t_t_t_kline['close']
        t_t_kline_close = t_t_kline['close']
        t_t_kline_close_ratio = 100 * (t_t_kline_close - t_t_t_kline_close) / t_t_t_kline_close
        if t_t_kline_close_ratio < -5:
            return False, 'aaa'

        target_index = max_pct_chg_index_list[-1]
        t_1_k_line = latest_range_days_k_line_list[target_index]
        t_s_count = range_days - target_index - 2
        latest_target_days_k_line_list = latest_range_days_k_line_list[target_index + 1:]

        target_close_p = latest_range_days_k_line_list[target_index]['close']
        target_open_p = latest_range_days_k_line_list[target_index]['open']
        temp_prev_close_p = temp_k_line_list[target_index]['close']
        if temp_prev_close_p < target_open_p:
            target_open_p = temp_prev_close_p

        latest_close_p = latest_target_days_k_line_list[-1]['close']
        l_r_close_ratio = 100 * (latest_close_p - target_close_p) / target_close_p
        l_r_close_ratio = self.retain_decimals_no_rounding(l_r_close_ratio, decimals=1)
        if l_r_close_ratio > 6:
            return False, 'ccc'

        max_close_price_interval = self.get_max_close_price(latest_target_days_k_line_list)
        max_high_price_interval = self.get_max_high_price(latest_target_days_k_line_list)
        if max_close_price_interval < target_close_p and max_high_price_interval < target_close_p:
            return False, 'ccc'

        now_ideal_close_price = round(k_line_list[-2]['close'] * 1.1, 2)
        if max_close_price_interval > now_ideal_close_price:
            return False, 'ccc'
        if now_ideal_close_price < target_close_p:
            return False, 'ccc'
        #
        gt_target_close_days = 0
        gt_target_high_days = 0
        low_p_days = 0
        open_close_ratio_max = 0
        for t_k_line in latest_target_days_k_line_list:
            prev_close_p = t_k_line['prev_close']
            open_p = t_k_line['open']
            high_p = t_k_line['high']
            close_p = t_k_line['close']
            low_p = t_k_line['low']
            pct_chg = t_k_line['pct_chg']
            t_t_ratio_3 = 100 * (high_p - close_p) / close_p
            if t_t_ratio_3 > 12 and pct_chg < -4:
                return False, 'fff'
            open_close_ratio = 100 * (open_p-close_p)/close_p
            if open_close_ratio_max < open_close_ratio:
                open_close_ratio_max = open_close_ratio

            if close_p < target_open_p or open_p < target_open_p:
                return False, 'ddd'
            if low_p < target_open_p:
                low_p_days += 1
            if close_p >= target_close_p:
                gt_target_close_days += 1
            if high_p >= target_close_p:
                gt_target_high_days += 1
        gt_target_close_days_ratio = 100 * (gt_target_close_days/t_s_count)
        gt_target_high_days_ratio = 100 * (gt_target_high_days / t_s_count)
        low_p_days_days_ratio = 100 * (low_p_days / t_s_count)
        # print(f'open_close_ratio_max: {open_close_ratio_max}')
        if open_close_ratio_max > 15:
            return False, 'ddd'
        if gt_target_close_days_ratio < 20 and gt_target_high_days_ratio < 25:
            return False, 'ddd'
        if low_p_days_days_ratio >= 40:
            return False, 'ddd'

        up_num, down_num = self.get_up_and_down_num(latest_target_days_k_line_list)
        up_num_2, down_num_2 = self.get_up_and_down_num_2(latest_target_days_k_line_list)
        down_num_ratio_1 = 100*down_num/t_s_count
        down_num_ratio_2 = 100*down_num_2/t_s_count
        down_num_ratio = down_num_ratio_1 if down_num_ratio_1 > down_num_ratio_2 else down_num_ratio_2
        if not (40 <= down_num_ratio <= 80):
            return False, 'eee'

        t_l_k_line_low = latest_target_days_k_line_list[-1]['low']
        t_l_1_ratio = 100 * (t_l_k_line_low - latest_target_days_k_line_list[-2]['close']) / \
                      latest_target_days_k_line_list[-2]['close']
        t_l_2_ratio = latest_target_days_k_line_list[-1]['pct_chg']
        t_l_1_ratio = self.retain_decimals_no_rounding(t_l_1_ratio, decimals=1)
        t_l_2_ratio = self.retain_decimals_no_rounding(t_l_2_ratio, decimals=1)
        # print(f't_l_1_ratio: {t_l_1_ratio}, t_l_2_ratio: {t_l_2_ratio}')
        if t_l_1_ratio < -7 or t_l_2_ratio < -6:
            return False, 'fff'

        boll_days_30_count___ = self.get_close_or_open_price_exceed_ma_days(k_line_list, boll_days=30, days_interval=t_s_count + 1)
        boll_days_20_count___ = self.get_close_or_open_price_exceed_ma_days(k_line_list, boll_days=20, days_interval=t_s_count + 1)
        boll_days_30_count___ratio = 100 * boll_days_30_count___ / (t_s_count + 1)
        boll_days_20_count___ratio = 100 * boll_days_20_count___ / (t_s_count + 1)
        if boll_days_20_count___ratio != 100 or boll_days_30_count___ratio != 100:
            prev_ma_gt_later_ma_days_count = self.get_prev_ma_gt_later_ma_days(
                k_line_list, prev_boll_days=20, later_boll_days=30, days_interval=t_s_count + 1)
            prev_ma_gt_later_ma_days_count_ratio = 100 * prev_ma_gt_later_ma_days_count / (t_s_count + 1)
            if prev_ma_gt_later_ma_days_count_ratio != 100 or t_s_count < 6:
                return False, 'ggg'

        boll_days_30_count = self.get_close_price_exceed_ma_days(k_line_list, boll_days=30, days_interval=t_s_count)
        boll_days_30_count_ratio = 100 * boll_days_30_count / t_s_count
        if boll_days_30_count_ratio < 100:
            return False, 'ggg'
        boll_days_20_count = self.get_close_price_exceed_ma_days(k_line_list, boll_days=20, days_interval=t_s_count)
        boll_days_20_count_ratio = 100 * boll_days_20_count / t_s_count
        if boll_days_20_count_ratio < 90:
            return False, 'ggg'
        boll_days_10_count = self.get_close_price_exceed_ma_days(k_line_list, boll_days=10, days_interval=t_s_count)
        boll_days_10_count_ratio = 100 * boll_days_10_count / t_s_count
        if boll_days_10_count_ratio < 60:
            return False, 'ggg'
        boll_days_5_count = self.get_close_price_exceed_ma_days(k_line_list, boll_days=5, days_interval=t_s_count)
        boll_days_5_count_ratio = 100 * boll_days_5_count / t_s_count
        if boll_days_5_count_ratio < 40:
            return False, 'ggg'
        ma_up = self.is_ma_up_1(k_line_list, t_s_count + 1, stat_day_min=1)
        if not ma_up:
            return False, 'ggg'
        diff_sat_count = self.get_diff_sat_count(k_line_list, t_s_count + 1)
        diff_sat_count_ratio = 100 * diff_sat_count / t_s_count
        if diff_sat_count_ratio < 90:
            return False, 'ggg'
        return True, OK





