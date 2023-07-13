latest_close_price_min = 4
latest_close_price_max = 20

latest_close_price_min_adv = 4
latest_close_price_max_adv = 20

pct_change_max_i = 9.8
pct_change_max_j = 19.0

turn_max_i = 12
turn_max_i_adv = 18

turn_min_i = 4


class Strategy(object):
    def __init__(self):
        self.e_count = 0
        self.e_count_adv = 0

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
            if r >= 0:
                up_num += 1
            else:
                down_num += 1
        return up_num, down_num

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

    def get_pct_chg_sum(self, data_list):
        pct_chg_sum = 0
        for d in data_list:
            pct_chg = float(d['pct_chg'])
            pct_chg_sum += pct_chg
        return pct_chg_sum

    def strategy_match(self, code, k_line_list, m_day, is_test=False, adventure=False):
        latest_close_price = float(k_line_list[-1]['close'])
        if is_test:
            print('latest_close_price: {}'.format(latest_close_price))
        if not adventure and not (latest_close_price_min <= latest_close_price <= latest_close_price_max):
            return False
        if adventure and not (latest_close_price_min_adv <= latest_close_price <= latest_close_price_max_adv):
            return False
        total_count = len(k_line_list)
        k_line_list_m_day = k_line_list[-m_day:]
        x_max_high_price = self.get_max_high_price(k_line_list_m_day)
        y_max_high_price = self.get_max_high_price(k_line_list)
        max_price_ratio = (x_max_high_price - y_max_high_price) / x_max_high_price * 100
        if is_test:
            print('max_price_ratio: {}'.format(max_price_ratio))
        # if max_price_ratio < 0 and abs(max_price_ratio) > 5:
        #     return False
        if max_price_ratio != 0:
            return False
        if not adventure:
            self.e_count += 1
        else:
            self.e_count_adv += 1
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
        if len(index_list) not in [2, 3]:
            return False
        if index_list[-1] != m_day - 1:
            return False
        sum_index_list = sum(index_list)
        if sum_index_list > 8:
            return False

        l_index = index_list[-2]
        l_index_close = float(k_line_list_m_day[l_index]['close'])
        r_data_list = k_line_list[:total_count-m_day+l_index+1]
        r_max_close_price = self.get_max_close_price(r_data_list)
        if is_test:
            print('l_index_close: {}, r_max_close_price: {}'.format(l_index_close, r_max_close_price))
        # if not adventure and l_index_close < r_max_close_price:
        #     return False
        r_index = m_day - 1
        k_line_list_l_r = k_line_list_m_day[l_index:r_index + 1]
        up_num, down_num = self.get_up_and_down_num(k_line_list_l_r)
        ration_up = 100 * up_num / (up_num + down_num)
        if is_test:
            print('ration_up: {}'.format(ration_up))
        if ration_up < 80:
            return False
        max_turn = self.get_max_turn(k_line_list_l_r)
        # min_turn = self.get_min_turn(k_line_list_l_r)
        if is_test:
            print('max_turn: {}'.format(max_turn))
        # if max_turn < turn_min_i:
        #     return False
        if not adventure and max_turn > turn_max_i:
            return False
        if adventure and max_turn > turn_max_i_adv:
            return False
        return True



