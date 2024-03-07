import copy
import pandas as pd
from stockstats import wrap, StockDataFrame
from constants import pct_change_max_i, pct_change_max_j


class Strategist(object):
    def __init__(self):
        pass

    def is_red(self, data):
        return float(data['close']) > float(data['open'])

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


    def get_num_exceed(self, value, data_list):
        _num = 0
        for data in data_list:
            pct_chg = data['pct_chg']
            if pct_chg >= value:
                _num += 1
        return _num

    def get_num_less(self, value, data_list):
        _num = 0
        for data in data_list:
            pct_chg = data['pct_chg']
            if pct_chg <= value:
                _num += 1
        return _num

    def get_interval_to_latest(self, price, data_list, key):
        for idx, data in enumerate(data_list[-1::-1]):
            if data[key] == price:
                return idx - 1
        return -100

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

    def is_close_price_exceed_ma_20(self, k_line_list, days=4):
        stock_tech = self.get_stock_tech(k_line_list=k_line_list)
        boll = stock_tech['boll']
        boll_price_series = boll.iloc[-days-1:-1]
        for k_line in k_line_list[-days-1: -1]:
            close_price = round(k_line['close'], 2)
            ma_20_price = round(boll_price_series[k_line['date']], 2)
            # print('close_price: {}, ma_20_price: {}'.format(close_price, ma_20_price))
            if close_price < ma_20_price:
                return False
        return True

    def is_macd_latest_gold(self, k_line_list):
        prev_close_price = k_line_list[-2]['close']
        now_ideal_close_price = prev_close_price * 1.1
        k_line_list_opt = copy.deepcopy(k_line_list)
        k_line_list_opt[-1]['close'] = now_ideal_close_price
        stock_tech = self.get_stock_tech(k_line_list=k_line_list_opt)
        is_gold = False
        for i in range(1, 6):
            diff_prev, dea_prev = round(stock_tech['macd'].iloc[-i-1], 2), round(stock_tech['macds'].iloc[-i-1], 2)
            diff, dea = round(stock_tech['macd'].iloc[-i], 2), round(stock_tech['macds'].iloc[-i], 2)
            if dea > diff:
                continue
            r = (diff_prev-dea_prev) * (diff-dea)
            if r <= 0:
                is_gold = True
                break
        return is_gold

    def get_first_strategy_res(self, code, k_line_list, min_opt_macd_diff=0):
        # prev_macd_diff, prev_macd_dea = self.get_stock_opt_macd(k_line_list[0:-1])
        # print('prev_macd_diff: {}, prev_macd_dea: {}'.format(prev_macd_diff, prev_macd_dea))
        opt_macd_diff, opt_macd_dea = self.get_stock_opt_macd(k_line_list)
        if opt_macd_diff < min_opt_macd_diff or opt_macd_diff < opt_macd_dea:
            return False
        price_exceed_ma_20 = self.is_close_price_exceed_ma_20(k_line_list, days=4)
        if not price_exceed_ma_20:
            return False
        range_days = 50
        close_price = k_line_list[-1]['close']
        open_price = k_line_list[-1]['open']
        k_line_list_range_day = k_line_list[-range_days:]
        min_low_price = self.get_min_low_price(k_line_list_range_day)
        interval = self.get_interval_to_latest(min_low_price, k_line_list_range_day, 'low')
        if not 7 <= interval < 20:
            return False
        key_k_line = k_line_list[-interval-2]
        key_k_line_pct_chg = key_k_line['pct_chg']
        if key_k_line_pct_chg >= 2:
            return False
        k_line_list_interval = k_line_list[-interval - 1:-1]
        up_num, down_num = self.get_up_and_down_num(k_line_list_interval)
        up_ratio_interval_day = round(100 * up_num / (up_num + down_num), 2)
        pct_chg_interval_day = self.get_pct_chg_sum(k_line_list_interval)
        # avg_turn = self.get_avg_turn(data_list=k_line_list_interval)
        # print('avg_turn: {}'.format(avg_turn))
        if not 50 < up_ratio_interval_day <= 90:
            return False
        if not 2.5 < pct_chg_interval_day <= 13.5:
            return False
        num_exceed = self.get_num_exceed(5, k_line_list_interval)
        if num_exceed > 1:
            return False
        num_less = self.get_num_less(-5, k_line_list_interval)
        if num_less > 0:
            return False
        print('interval: {}, up_ratio: {}, pct_chg: {}, open_price: {}, close_price: {}, '
              'code: {}'.format(interval, up_ratio_interval_day, pct_chg_interval_day, open_price, close_price, code))
        return True

    def get_second_strategy_res(self, code, k_line_list, min_opt_macd_diff=0):
        opt_macd_diff, opt_macd_dea = self.get_stock_opt_macd(k_line_list)
        if opt_macd_diff < min_opt_macd_diff or opt_macd_diff < opt_macd_dea:
            return False
        is_gold = self.is_macd_latest_gold(k_line_list)
        if not is_gold:
            return False
        # price_exceed_ma_20 = self.is_close_price_exceed_ma_20(k_line_list, days=3)
        # if not price_exceed_ma_20:
        #     return False
        range_days = 70
        close_price = k_line_list[-1]['close']
        open_price = k_line_list[-1]['open']
        k_line_list_range_day = k_line_list[-range_days:]
        min_low_price = self.get_min_low_price(k_line_list_range_day)
        interval = self.get_interval_to_latest(min_low_price, k_line_list_range_day, 'low')
        if not 20 <= interval <= 35:
            return False
        key_k_line = k_line_list[-interval - 2]
        key_k_line_pct_chg = key_k_line['pct_chg']
        if key_k_line_pct_chg >= 5:
            return False
        k_line_list_interval = k_line_list[-interval-1:-1]
        up_num, down_num = self.get_up_and_down_num(k_line_list_interval)
        up_ratio_interval_day = 100 * up_num / (up_num+down_num)
        pct_chg_interval_day = self.get_pct_chg_sum(k_line_list_interval)
        print('interval: {}, up_ratio_interval_day: {}, pct_chg_interval_day: {}, close_price: {}, open_price: {}, code: {}'
              .format(interval, up_ratio_interval_day, pct_chg_interval_day, close_price, open_price, code))
        # if not 50 <= up_ratio_interval_day <= 90:
        #     return False
        if not 5 <= pct_chg_interval_day <= 20:
            return False
        _num = self.get_num_exceed(5, k_line_list_interval)
        if _num > 2:
            return False
        __num = self.get_num_less(-5, k_line_list_interval)
        if __num > 0:
            return False
        return True

    def get_third_strategy_res(self, code, k_line_list, min_opt_macd_diff=0):
        # opt_macd_diff, opt_macd_dea = self.get_stock_opt_macd(k_line_list)
        # if opt_macd_diff < min_opt_macd_diff or opt_macd_diff < opt_macd_dea:
        #     return False
        # price_exceed_ma_20 = self.is_close_price_exceed_ma_20(k_line_list, days=3)
        # if not price_exceed_ma_20:
        #     return False
        range_days = 10
        close_price = k_line_list[-1]['close']
        open_price = k_line_list[-1]['open']
        k_line_list_range_day = k_line_list[-range_days:]
        pct_chg_index_list = self.get_pct_chg_index_list(k_line_list[-range_days:-1], pct_chg_max=8.0)
        if len(pct_chg_index_list) not in [1, 2]:
            return False
        # if zt_pct_chg_index_list[-1] != range_days - 2:
        #     return False
        latest_2_zt_gap = range_days - 1 - pct_chg_index_list[-1] - 1
        if not 6 <= latest_2_zt_gap <= 7:
            return False
        k_line_list_interval = k_line_list_range_day[pct_chg_index_list[-1]+1:-1]
        up_num, down_num = self.get_up_and_down_num(k_line_list_interval)
        up_ratio_interval_day = round(100 * up_num / (up_num + down_num), 2)
        pct_chg_interval_day = self.get_pct_chg_sum(k_line_list_interval)
        if not 50 < up_ratio_interval_day <= 100:
            return False
        if not 0 < pct_chg_interval_day <= 5:
            return False
        # _num = self.get_num_exceed(5, k_line_list_interval)
        # if _num > 1:
        #     return False
        return True







