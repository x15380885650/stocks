import copy
import pandas as pd
from stockstats import StockDataFrame
from constants import *

COND_INTERVAL = 'cond_interval'
COND_MACD_DIFF = 'cond_macd_diff'
COND_MACD_GOLD = 'cond_macd_gold'
COND_MA_UP = 'cond_ma_up'
COND_MA_20 = 'cond_ma_20'
COND_MA_15 = 'cond_ma_15'
COND_CLOSE_PRICE = 'cond_close_price'
COND_UP_RATIO_INTERVAL = 'cond_up_ratio_interval'
COND_PCT_CHG_INTERVAL = 'cond_pct_chg_interval'
COND_PCT_CHG_NUM_EXCEED = 'cond_pct_chg_num_exceed'
COND_PCT_CHG_NUM_LESS = 'cond_pct_chg_num_less'
CONDE_KEY_PCT_CHG_MAX = 'cond_key_pct_chg_max'
COND_MAX_PCT_CHG_INTERVAL = 'cond_max_pct_chg_interval'
COND_MAX_PCT_CHG_INDEX = 'cond_max_pct_chg_index'
OK = 'ok'


class Strategist(object):
    def __init__(self):
        pass

    def is_red(self, data):
        return float(data['close']) > float(data['open'])

    def is_green(self, data):
        return float(data['close']) < float(data['open'])

    def get_min_pct_chg_2(self, data_list):
        min_pct_chg_2 = 0
        for data in data_list:
            pct_chg_2 = self.get_pct_chg_2(data)
            if pct_chg_2 < min_pct_chg_2:
                min_pct_chg_2 = pct_chg_2
        return min_pct_chg_2

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
            pct_chg = data['pct_chg']
            if not close_price or not open_price:
                continue
            r = (float(close_price) - float(open_price)) / float(open_price) * 100
            if r == 0:
                continue
            elif r > 0:
                up_num += 1
            else:
                down_num += 1
        return up_num, down_num

    def get_up_and_down_num_2(self, data_list):
        up_num = down_num = 0
        for data in data_list:
            pct_chg = data['pct_chg']
            if pct_chg > 0:
                up_num += 1
            else:
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

    def get_max_pct_chg(self, data_list):
        max_pct_chg = float(data_list[0]['pct_chg'])
        for data in data_list:
            pct_chg = data['pct_chg']
            if max_pct_chg < float(pct_chg):
                max_pct_chg = float(pct_chg)
        return max_pct_chg

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
            # if r < -0.25:
            #     return False
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



    # def get_first_strategy_res(self, code, k_line_list, m_day):
    #     k_line_list_m_day = k_line_list[-m_day:]
    #     prev_close_price = k_line_list[-2]['close']
    #     now_ideal_close_price = prev_close_price * 1.1
    #     x_max_close_price = self.get_max_close_price(k_line_list_m_day[:-1])
    #     x_max_high_price = self.get_max_high_price(k_line_list_m_day[:-1])
    #     # max_price_ratio = (now_ideal_close_price - x_max_close_price) / x_max_close_price * 100
    #     max_price_ratio = (now_ideal_close_price - x_max_high_price) / x_max_high_price * 100
    #     if max_price_ratio < 9.5:
    #         return False
    #     latest_days_k_line_list = k_line_list[-7:-1]
    #     max_turn = self.get_max_turn(latest_days_k_line_list)
    #     avg_turn = self.get_avg_turn(latest_days_k_line_list)
    #     now_turn = k_line_list[-1]['turn']
    #     turn_ratio = now_turn / avg_turn
    #     # print('max_turn: {}, avg_turn: {}, now_turn: {}, turn_ratio: {}, max_price_ratio: {}, code: {}'
    #     #       .format(max_turn, avg_turn, now_turn, turn_ratio, max_price_ratio, code))
    #     # if avg_turn > 3:
    #     #     return False
    #     # if max_turn > 4:
    #     #     return False
    #     # if float(now_turn) > 4:
    #     #     return False
    #     # if turn_ratio > 8:
    #     #     return False
    #     # return False
    #     pct_chg_list = []
    #     for k_line in k_line_list_m_day:
    #         pct_chg = k_line['pct_chg']
    #         if isinstance(pct_chg, str) and not pct_chg:
    #             continue
    #         pct_chg_max = pct_change_max_i
    #         if code.startswith('sz.30') or code.startswith('30'):
    #             pct_chg_max = pct_change_max_j
    #         if float(pct_chg) >= pct_chg_max:
    #             pct_chg_list.append(1)
    #         else:
    #             pct_chg_list.append(0)
    #     index_list = []
    #     for i, v in enumerate(pct_chg_list):
    #         if v == 1:
    #             index_list.append(i)
    #     if len(index_list) != 2:
    #         return False
    #     if index_list[-1] != m_day - 1 or index_list[-2] != m_day - 2:
    #         return False
    #     last_k_line_data = k_line_list[-1]
    #     last_k_line_open = last_k_line_data['open']
    #     last_k_line_close = last_k_line_data['close']
    #     if last_k_line_open != last_k_line_close:
    #         return False
    #     return True

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
        # prev_macd_value = self.get_macd_value(data_list=k_line_list[0:-1])
        # if prev_macd_value < -0.1 or opt_macd_value < 0:
        #     return False
        k_line_list_opt = copy.deepcopy(k_line_list)
        k_line_list_opt[-1]['close'] = now_ideal_close_price
        stock_tech = self.get_stock_tech(k_line_list=k_line_list_opt)
        diff, dea = stock_tech['macd'].iloc[-1], stock_tech['macds'].iloc[-1]
        return round(diff, 2), round(dea, 2)

    def get_stock_prev_macd(self, k_line_list):
        # prev_close_price = k_line_list[-2]['close']
        # now_ideal_close_price = prev_close_price * 1.1
        # # prev_macd_value = self.get_macd_value(data_list=k_line_list[0:-1])
        # # if prev_macd_value < -0.1 or opt_macd_value < 0:
        # #     return False
        # k_line_list_opt = copy.deepcopy(k_line_list)
        # k_line_list_opt[-1]['close'] = now_ideal_close_price
        stock_tech = self.get_stock_tech(k_line_list=k_line_list)
        diff, dea = stock_tech['macd'].iloc[-2], stock_tech['macds'].iloc[-2]
        return round(diff, 2), round(dea, 2)

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

    def is_ma_up_1(self, k_line_list):
        prev_close_price = k_line_list[-2]['close']
        now_ideal_close_price = prev_close_price * 1.1
        k_line_list_opt = copy.deepcopy(k_line_list)
        k_line_list_opt[-1]['close'] = now_ideal_close_price
        stock_tech = self.get_stock_tech(k_line_list=k_line_list_opt)
        ma_5_price = stock_tech['boll_{}'.format(5)].iloc[-1]
        ma_10_price = stock_tech['boll_{}'.format(10)].iloc[-1]
        ma_20_price = stock_tech['boll_{}'.format(20)].iloc[-1]
        ma_30_price = stock_tech['boll_{}'.format(30)].iloc[-1]
        # print(ma_5_price, ma_10_price, ma_20_price, ma_30_price)
        if ma_5_price < ma_10_price or ma_5_price < ma_20_price or ma_5_price < ma_30_price:
            return False
        if ma_10_price < ma_20_price:
            return False
        ma_5_price_prev = round(stock_tech['boll_{}'.format(5)].iloc[-2], 2)
        ma_10_price_prev = round(stock_tech['boll_{}'.format(10)].iloc[-2], 2)
        ma_20_price_prev = round(stock_tech['boll_{}'.format(20)].iloc[-2], 2)
        ma_30_price_prev = round(stock_tech['boll_{}'.format(30)].iloc[-2], 2)
        cond_1 = ma_5_price_prev >= ma_10_price_prev and ma_5_price_prev >= ma_20_price_prev and ma_5_price_prev >= ma_30_price_prev
        cond_2 = ma_10_price_prev >= ma_20_price_prev
        if not cond_1 and not cond_2:
            return False
        return True

    def is_ma_up_2(self, k_line_list):
        prev_close_price = k_line_list[-2]['close']
        now_ideal_close_price = prev_close_price * 1.1
        k_line_list_opt = copy.deepcopy(k_line_list)
        k_line_list_opt[-1]['close'] = now_ideal_close_price
        stock_tech = self.get_stock_tech(k_line_list=k_line_list_opt)
        ma_5_price = stock_tech['boll_{}'.format(5)].iloc[-1]
        ma_10_price = stock_tech['boll_{}'.format(10)].iloc[-1]
        ma_20_price = stock_tech['boll_{}'.format(20)].iloc[-1]
        ma_30_price = stock_tech['boll_{}'.format(30)].iloc[-1]
        print(ma_5_price, ma_10_price, ma_20_price, ma_30_price)
        if ma_5_price < ma_10_price or ma_5_price < ma_20_price or ma_5_price < ma_30_price:
            return False
        if ma_10_price < ma_30_price or ma_20_price < ma_30_price:
            return False
        return True

    def retain_decimals_no_rounding(self, number, decimals=2):
        return int(number*10**decimals) / 10**decimals

    def is_macd_latest_gold(self, k_line_list):
        prev_close_price = k_line_list[-2]['close']
        now_ideal_close_price = prev_close_price * 1.1
        k_line_list_opt = copy.deepcopy(k_line_list)
        k_line_list_opt[-1]['close'] = now_ideal_close_price
        stock_tech = self.get_stock_tech(k_line_list=k_line_list_opt)
        is_gold = False
        for i in range(1, 7):
            diff_prev, dea_prev = stock_tech['macd'].iloc[-i - 1], stock_tech['macds'].iloc[-i - 1],
            diff, dea = stock_tech['macd'].iloc[-i], stock_tech['macds'].iloc[-i]
            if dea > diff:
                continue
            r = (diff_prev-dea_prev) * (diff-dea)
            # print(r)
            if r <= 0.00005:
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

    def is_open_price_high(self, k_line_list):
        prev_close_price = k_line_list[-2]['close']
        now_open_price = k_line_list[-1]['open']
        open_close_ratio = 100 * (now_open_price - prev_close_price) / prev_close_price
        # print(open_close_ratio)
        if open_close_ratio > 2 or open_close_ratio < -1.5:
            return True
        return False

    def get_first_strategy_res(self, code, k_line_list, min_opt_macd_diff=0):
        open_high = self.is_open_price_high(k_line_list)
        if open_high:
            return False, 'a'
        prev_close_price = k_line_list[-2]['close']
        now_ideal_close_price = prev_close_price * 1.1
        range_days = 50
        close_price = k_line_list[-1]['close']
        open_price = k_line_list[-1]['open']
        k_line_list_range_day = k_line_list[-range_days:]
        min_low_price = self.get_min_low_price(k_line_list_range_day)
        interval = self.get_interval_to_latest(min_low_price, k_line_list_range_day, 'low')
        if not 7 <= interval < 20:
            return False, 'aaa'
        opt_macd_diff, opt_macd_dea = self.get_stock_opt_macd(k_line_list)
        if opt_macd_diff < min_opt_macd_diff or opt_macd_diff < opt_macd_dea:
            return False, 'bbb'
        price_exceed_ma_20 = self.is_close_price_exceed_ma(k_line_list, boll_days=20, days_count=4)
        if not price_exceed_ma_20:
            return False, 'bbb'
        price_exceed_ma_15 = self.is_close_price_exceed_ma(k_line_list, boll_days=15, days_count=4)
        if not price_exceed_ma_15:
            return False, 'bbb'
        ma_up = self.is_ma_up_1(k_line_list)
        if not ma_up:
            return False, 'bbb'
        k_line_list_interval = k_line_list[-interval - 1:-1]
        max_close_price_interval = self.get_max_close_price(k_line_list_interval)
        if max_close_price_interval > now_ideal_close_price:
            return False, 'ccc'
        up_num, down_num = self.get_up_and_down_num(k_line_list_interval)
        up_ratio_interval_day = round(100 * up_num / (up_num + down_num), 0)
        key_k_line = k_line_list[-interval - 2]
        key_k_line_close_price = key_k_line['close']
        pct_chg_interval_day = round(100 * (prev_close_price-key_k_line_close_price)/key_k_line_close_price, 0)
        if not 50 < up_ratio_interval_day <= 90:
            return False, 'ddd'
        if not 2 < pct_chg_interval_day <= 15:
            return False, 'ddd'
        pct_chg_num_exceed = self.get_pct_chg_num_exceed(5, k_line_list_interval)
        if pct_chg_num_exceed > 0:
            return False, 'ddd'
        pct_chg_num_less = self.get_pct_chg_num_less(-5, k_line_list_interval)
        if pct_chg_num_less > 0:
            return False, 'ddd'
        key_k_line_pct_chg = key_k_line['pct_chg']
        key_k_line_pct_chg_2 = self.get_pct_chg_2(d=key_k_line)
        # print(key_k_line_pct_chg, key_k_line_pct_chg_2)
        key_pct_chg_max = 3
        if key_k_line_pct_chg >= key_pct_chg_max or key_k_line_pct_chg_2 >= key_pct_chg_max:
            return False, 'eee'
        interval_2 = self.get_interval_to_latest(5, k_line_list_interval, 'pct_chg', cond='>=')
        if interval_2 < 5:
            return False, 'eee'
        print('interval: {}, up_ratio: {}, pct_chg: {}, open_price: {}, close_price: {},code: {}'
              .format(interval, up_ratio_interval_day, pct_chg_interval_day, open_price, close_price, code))
        return True, OK

    def get_second_strategy_res(self, code, k_line_list, min_opt_macd_diff=0):
        open_high = self.is_open_price_high(k_line_list)
        if open_high:
            return False, 'a'
        range_days = 70
        close_price = k_line_list[-1]['close']
        open_price = k_line_list[-1]['open']
        k_line_list_range_day = k_line_list[-range_days:]
        min_low_price = self.get_min_low_price(k_line_list_range_day)
        interval = self.get_interval_to_latest(min_low_price, k_line_list_range_day, 'low')
        if not 20 <= interval <= 35:
            return False, 'aaa'

        prev_close_price = k_line_list[-2]['close']
        now_ideal_close_price = prev_close_price * 1.1
        opt_macd_diff, opt_macd_dea = self.get_stock_opt_macd(k_line_list)
        if opt_macd_diff < min_opt_macd_diff or opt_macd_diff < opt_macd_dea:
            return False, 'bbb'
        is_gold = self.is_macd_latest_gold(k_line_list)
        if not is_gold:
            return False, 'bbb'
        ma_up = self.is_ma_up_2(k_line_list)
        if not ma_up:
            return False, 'bbb'
        key_k_line = k_line_list[-interval - 2]
        key_k_line_pct_chg = key_k_line['pct_chg']
        key_k_line_pct_chg_2 = self.get_pct_chg_2(d=key_k_line)
        key_ptc_chg_max = 5
        if key_k_line_pct_chg >= key_ptc_chg_max or key_k_line_pct_chg_2 >= key_ptc_chg_max:
            return False, 'ccc'
        k_line_list_interval = k_line_list[-interval-1:-1]
        max_close_price_interval = self.get_max_close_price(k_line_list_interval)
        if max_close_price_interval > now_ideal_close_price:
            return False, 'ddd'
        up_num, down_num = self.get_up_and_down_num(k_line_list_interval)
        up_ratio_interval_day = round(100 * up_num / (up_num+down_num), 0)
        key_k_line_close_price = key_k_line['close']
        pct_chg_interval_day = round(100 * (prev_close_price - key_k_line_close_price) / key_k_line_close_price, 0)
        if not 40 <= up_ratio_interval_day <= 90:
            return False, 'eee'
        if not 3 <= pct_chg_interval_day <= 20:
            return False, 'eee'
        pct_chg_num_exceed = self.get_pct_chg_num_exceed(5, k_line_list_interval)
        pct_chg_2_num_exceed = self.get_pct_chg_2_num_exceed(5, k_line_list_interval)
        if pct_chg_num_exceed > 2 or pct_chg_2_num_exceed > 2:
            return False, 'fff'
        pct_chg_num_less = self.get_pct_chg_num_less(-5, k_line_list_interval)
        pct_chg_2_num_less = self.get_pct_chg_2_num_less(-5, k_line_list_interval)
        if pct_chg_num_less > 0 or pct_chg_2_num_less > 0:
            return False, 'fff'
        interval_2 = self.get_interval_to_latest(7, k_line_list_interval, 'pct_chg', cond='>=')
        if interval_2 < 15:
            return False, 'fff'
        print('interval: {}, up_ratio: {}, pct_chg: {}, close_price: {}, open_price: {}, code: {}'
              .format(interval, up_ratio_interval_day, pct_chg_interval_day, close_price, open_price, code))
        return True, OK

    def get_third_strategy_res(self, code, k_line_list, min_opt_macd_diff=0):
        open_high = self.is_open_price_high(k_line_list)
        if open_high:
            return False, 'a'

        range_days = 9
        latest_range_days_k_line_list = k_line_list[-range_days:-1]
        temp_k_line_list = k_line_list[-range_days-1:-1]
        max_pct_chg_binary_list = self.get_max_pct_chg_binary_list(latest_range_days_k_line_list)
        max_pct_chg_index_list = []
        for i, v in enumerate(max_pct_chg_binary_list):
            if v == 1:
                max_pct_chg_index_list.append(i)
        if len(max_pct_chg_index_list) not in [1, 2]:
            return False, "aaa"
        if max_pct_chg_index_list[-1] > 2:
            return False, "aaa"
        target_index = max_pct_chg_index_list[-1]
        t_1_k_line = latest_range_days_k_line_list[target_index]
        t_s_count = range_days - target_index - 2
        latest_target_days_k_line_list = latest_range_days_k_line_list[target_index+1:]
        prev_t_low_p = -1
        no_sat_count = 0
        for t_k_line in latest_target_days_k_line_list:
            close_p = t_k_line['close']
            open_p = t_k_line['open']
            t_low_p = open_p if close_p > open_p else close_p
            if prev_t_low_p != -1 and prev_t_low_p < t_low_p:
                no_sat_count += 1
            prev_t_low_p = t_low_p
        no_sat_ratio = 100 * no_sat_count / t_s_count
        if no_sat_ratio > 45:
            return False, 'bbb'
        # print(no_sat_ratio)
        target_close_p = latest_range_days_k_line_list[target_index]['close']
        target_open_p = latest_range_days_k_line_list[target_index]['open']
        temp_prev_close_p = temp_k_line_list[target_index]['close']
        if temp_prev_close_p < target_open_p:
            target_open_p = temp_prev_close_p

        latest_close_p = latest_target_days_k_line_list[-1]['close']
        latest_open_p = latest_target_days_k_line_list[-1]['open']
        if latest_open_p < target_open_p or latest_open_p > target_close_p:
            return False, 'ccc'
        if latest_close_p < target_open_p or latest_close_p > target_close_p:
            return False, 'ccc'
        min_pct_chg_2 = self.get_min_pct_chg_2(latest_target_days_k_line_list)
        t_min_pct_chg_2 = self.retain_decimals_no_rounding(min_pct_chg_2, 1)
        if t_min_pct_chg_2 < -5.5:
            return False, 'ccc'

        for t_k_line in latest_target_days_k_line_list:
            close_p = t_k_line['close']
            open_p = t_k_line['open']
            if close_p < target_open_p or open_p < target_open_p:
                return False, 'ddd'

        up_num, down_num = self.get_up_and_down_num(latest_target_days_k_line_list)
        up_num_2, down_num_2 = self.get_up_and_down_num_2(latest_target_days_k_line_list)
        if down_num not in [3, 4] and down_num_2 not in [3, 4]:
            return False, 'eee'

        t_2_k_line = latest_target_days_k_line_list[-2]
        t_2_k_line_green_ok = self.is_green(t_2_k_line)
        if not t_2_k_line_green_ok:
            return False, 'fff'
        t_3_k_line = latest_target_days_k_line_list[0]
        t_3_k_line_green_ok = self.is_green(t_3_k_line)
        if t_3_k_line_green_ok:
            t_1_k_line_close = t_1_k_line['close']
            t_3_k_line_high = t_3_k_line['high']
            t_t_ratio = 100 * (t_3_k_line_high - t_1_k_line_close) / t_1_k_line_close
            t_3_k_line_open = t_3_k_line['open']
            t_3_k_line_close = t_3_k_line['close']
            if t_3_k_line_close > t_1_k_line_close or t_t_ratio > 5:
                return False, 'fff'
            # if t_t_ratio > 5:
            #     return False, 'fff'

        price_exceed_ma_20 = self.is_close_price_exceed_ma(k_line_list, boll_days=20, days_count=t_s_count)
        if not price_exceed_ma_20:
            return False, 'ggg'
        price_exceed_ma_15 = self.is_close_price_exceed_ma(k_line_list, boll_days=15, days_count=4)
        if not price_exceed_ma_15:
            return False, 'ggg'
        price_exceed_ma_10 = self.is_close_price_exceed_ma(k_line_list, boll_days=10, days_count=1)
        if not price_exceed_ma_10:
            return False, 'ggg'
        ma_up = self.is_ma_up_1(k_line_list)
        if not ma_up:
            return False, 'ggg'

        return True, OK

    def get_fourth_strategy_res(self, code, k_line_list, min_opt_macd_diff=0):
        open_high = self.is_open_price_high(k_line_list)
        if open_high:
            return False, 'a'

        prev_close_price = k_line_list[-2]['close']
        range_days = 30
        k_line_list_range_day = k_line_list[-range_days:]
        min_low_price = self.get_min_low_price(k_line_list_range_day)
        interval = self.get_interval_to_latest(min_low_price, k_line_list_range_day, 'low')
        # if not 7 <= interval < 15:
        #     return False, 'aaa'
        t_range_days = 7
        k_line_list_latest = k_line_list[-t_range_days-1: -1]
        k_line_list_interval = k_line_list[-interval - 1: -1]
        up_num, down_num = self.get_up_and_down_num(k_line_list_latest)
        up_num_2, down_num_2 = self.get_up_and_down_num_2(k_line_list_latest)
        if up_num < t_range_days-1:
            return False, 'bbb'
        if up_num_2 < t_range_days-1:
            return False, 'bbb'

        max_pct_chg_latest = self.get_max_pct_chg(k_line_list_latest)
        if max_pct_chg_latest > 7.5:
            return False, 'ccc'
        sum_pch_chg_latest = self.get_pct_chg_sum(k_line_list_latest)
        if not 5 <= sum_pch_chg_latest <= 15:
            return False, 'ccc'
        sum_pch_chg_interval = self.get_pct_chg_sum(k_line_list_interval)
        if not 5 <= sum_pch_chg_interval <= 20:
            return False, 'ccc'
        pct_chg_num_exceed = self.get_pct_chg_num_exceed(3.2, k_line_list_latest)
        if pct_chg_num_exceed > 1:
            return False, 'ddd'
        pct_chg_num_less = self.get_pct_chg_num_less(-1.5, k_line_list_latest)
        if pct_chg_num_less > 0:
            return False, 'ddd'
        max_close_price_interval = self.get_max_close_price(k_line_list_interval)
        if prev_close_price < max_close_price_interval:
            return False, 'eee'
        return True, OK





