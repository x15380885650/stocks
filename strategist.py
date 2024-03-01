import copy
from constants import pct_change_max_i, pct_change_max_j
from technical_indicator.momentum import MACD


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
        return pct_chg_sum

    def get_first_strategy_res(self, code, k_line_list, m_day):
        k_line_list_m_day = k_line_list[-m_day:]
        prev_close_price = k_line_list[-2]['close']
        now_ideal_close_price = prev_close_price * 1.1
        x_max_close_price = self.get_max_close_price(k_line_list_m_day[:-1])
        x_max_high_price = self.get_max_high_price(k_line_list_m_day[:-1])
        # max_price_ratio = (now_ideal_close_price - x_max_close_price) / x_max_close_price * 100
        max_price_ratio = (now_ideal_close_price - x_max_high_price) / x_max_high_price * 100
        if max_price_ratio < 9.5:
            return False
        latest_days_k_line_list = k_line_list[-7:-1]
        max_turn = self.get_max_turn(latest_days_k_line_list)
        avg_turn = self.get_avg_turn(latest_days_k_line_list)
        now_turn = k_line_list[-1]['turn']
        turn_ratio = now_turn / avg_turn
        # print('max_turn: {}, avg_turn: {}, now_turn: {}, turn_ratio: {}, max_price_ratio: {}, code: {}'
        #       .format(max_turn, avg_turn, now_turn, turn_ratio, max_price_ratio, code))
        # if avg_turn > 3:
        #     return False
        # if max_turn > 4:
        #     return False
        # if float(now_turn) > 4:
        #     return False
        # if turn_ratio > 8:
        #     return False
        # return False
        pct_chg_list = []
        for k_line in k_line_list_m_day:
            pct_chg = k_line['pct_chg']
            if isinstance(pct_chg, str) and not pct_chg:
                continue
            pct_chg_max = pct_change_max_i
            if code.startswith('sz.30') or code.startswith('30'):
                pct_chg_max = pct_change_max_j
            if float(pct_chg) >= pct_chg_max:
                pct_chg_list.append(1)
            else:
                pct_chg_list.append(0)
        index_list = []
        for i, v in enumerate(pct_chg_list):
            if v == 1:
                index_list.append(i)
        if len(index_list) != 2:
            return False
        if index_list[-1] != m_day - 1 or index_list[-2] != m_day - 2:
            return False
        last_k_line_data = k_line_list[-1]
        last_k_line_open = last_k_line_data['open']
        last_k_line_close = last_k_line_data['close']
        if last_k_line_open != last_k_line_close:
            return False
        return True

    def get_num_exceed(self, value, data_list):
        _num = 0
        for data in data_list:
            pct_chg = data['pct_chg']
            if pct_chg >= value:
                _num += 1
        return _num

    def get_interval_to_latest(self, price, data_list, key):
        for idx, data in enumerate(data_list[-1::-1]):
            if data[key] == price:
                return idx - 1
        return -100

    def get_second_strategy_res(self, code, k_line_list):
        range_days = 70
        close_price = k_line_list[-1]['close']
        k_line_list_range_day = k_line_list[-range_days:]
        min_low_price = self.get_min_low_price(k_line_list_range_day)
        interval = self.get_interval_to_latest(min_low_price, k_line_list_range_day, 'low')
        if not 20 <= interval <= 35:
            return False
        k_line_list_interval = k_line_list[-interval-1:-1]
        up_num, down_num = self.get_up_and_down_num(k_line_list_interval)
        up_ratio_interval_day = 100 * up_num / (up_num+down_num)
        pct_chg_interval_day = self.get_pct_chg_sum(k_line_list_interval)
        print('interval: {}, up_ratio_interval_day: {}, pct_chg_interval_day: {}, close_price: {}'
              .format(interval, up_ratio_interval_day, pct_chg_interval_day, close_price))
        # if not 50 <= up_ratio_interval_day <= 90:
        #     return False
        if not 5 <= pct_chg_interval_day <= 20:
            return False
        _num = self.get_num_exceed(5, k_line_list_interval)
        if _num > 2:
            return False
        return True

    def get_third_strategy_res(self, code, k_line_list, min_opt_macd=0):
        opt_macd = self.get_stock_opt_macd(k_line_list)
        if opt_macd < min_opt_macd:
            return False
        range_days = 50
        close_price = k_line_list[-1]['close']
        open_price = k_line_list[-1]['open']
        k_line_list_range_day = k_line_list[-range_days:]
        min_low_price = self.get_min_low_price(k_line_list_range_day)
        interval = self.get_interval_to_latest(min_low_price, k_line_list_range_day, 'low')
        if not 7 <= interval < 20:
            return False
        k_line_list_interval = k_line_list[-interval-1:-1]
        up_num, down_num = self.get_up_and_down_num(k_line_list_interval)
        up_ratio_interval_day = 100 * up_num / (up_num+down_num)
        pct_chg_interval_day = self.get_pct_chg_sum(k_line_list_interval)
        print('interval: {}, up_ratio_interval_day: {}, pct_chg_interval_day: {}, open_price: {}, close_price: {}'
              .format(interval, up_ratio_interval_day, pct_chg_interval_day, open_price, close_price))
        if not 50 < up_ratio_interval_day <= 90:
            return False
        if not 5 < pct_chg_interval_day <= 15:
            return False
        _num = self.get_num_exceed(5, k_line_list_interval)
        if _num > 1:
            return False
        return True

    def get_stock_opt_macd(self, k_line_list):
        prev_close_price = k_line_list[-2]['close']
        now_ideal_close_price = prev_close_price * 1.1
        # prev_macd_value = self.get_macd_value(data_list=k_line_list[0:-1])
        # if prev_macd_value < -0.1 or opt_macd_value < 0:
        #     return False
        k_line_list_opt = copy.deepcopy(k_line_list)
        k_line_list_opt[-1]['close'] = now_ideal_close_price
        opt_value = self.get_macd(data_list=k_line_list_opt)
        return opt_value

    def get_macd(self, data_list):
        fast_period = 12
        slow_period = 26
        close_price_list = self.get_close_price_list(data_list)
        m = MACD(close_price_list, fast_period, slow_period)
        v = m.calculate_macd()
        rounded_v = round(v, 2)
        return rounded_v


