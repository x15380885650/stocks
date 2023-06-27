pct_change_max_i = 9.9
pct_change_max_j = 19.0
turn_max_i = 15.5
turn_max_j = 25


class Strategy(object):
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

    def get_up_and_down_num(self, data_list):
        up_num = down_num = 0
        for data in data_list:
            close_price = data['close']
            open_price = data['open']
            pct_chg = data['pct_chg']
            if not close_price or not open_price:
                continue
            r = (float(close_price) - float(open_price)) / float(open_price) * 100
            if r > 0 or (r < 0 and abs(r) < 0.15):
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
            if pct_chg < 0 and abs(pct_chg) > 1:
                t_n_day += 1
        if t_n_day >= t_n_day_max:
            return False
        return True

    def get_pct_chg_sum(self, data_list):
        pct_chg_sum = 0
        for d in data_list:
            pct_chg = float(d['pct_chg'])
            pct_chg_sum += pct_chg
        return pct_chg_sum

    def strategy_1(self, code, k_line_list, m_day):
        k_line_list_m_day = k_line_list[-m_day:]
        pct_chg_list = []
        for k_line in k_line_list_m_day:
            pct_chg = k_line['pct_chg']
            if float(pct_chg) >= pct_change_max:
                pct_chg_list.append(1)
            else:
                pct_chg_list.append(0)
        index_list = []
        for i, v in enumerate(pct_chg_list):
            if v == 1:
                index_list.append(i)
        if len(index_list) < 2 or len(index_list) > 5:
            return False
        l_index = None
        r_index = index_list[-1]
        for i in index_list[-2::-1]:
            gap = r_index - i - 1
            if 3 <= gap <= 6:
                l_index = i
                break
            r_index = i
        if l_index is None:
            return False
        x_max_high_price = self.get_max_high_price(k_line_list_m_day)
        y_max_high_price = self.get_max_high_price(k_line_list)
        if x_max_high_price < y_max_high_price:
            return False
        l_high_price = float(k_line_list_m_day[l_index]['high'])
        r_high_price = float(k_line_list_m_day[r_index]['high'])
        if r_high_price < l_high_price:
            return False
        k_line_list_l_r = k_line_list_m_day[l_index + 1:r_index]
        up_num, down_num = self.get_up_and_down_num(k_line_list_l_r)
        up_ratio = 100 * up_num / float(up_num + down_num)
        if up_ratio < 25:
            return False
        x_total_count = len(k_line_list_m_day)
        if r_index == x_total_count - 1:
            return False
        data_n = k_line_list_m_day[-1]
        data_n_close_price = float(data_n['close'])
        max_close_price = self.get_max_close_price(k_line_list_m_day)
        if data_n_close_price < max_close_price:
            return False
        max_turn = self.get_max_turn(k_line_list_m_day)
        if max_turn >= turn_max:
            print('max_turn: {} >= {}'.format(max_turn, turn_max))
            return False
        data_r_p = k_line_list_m_day[r_index+1:]
        data_a_b = k_line_list_m_day[l_index:r_index + 1]
        avg_turn = self.get_avg_turn(data_a_b)
        r_turn = 1.8
        f_turn_dict = {}
        alarm_turn = avg_turn * r_turn
        for d in data_r_p:
            turn_r_p = float(d['turn'])
            if turn_r_p >= alarm_turn:
                date = d['date']
                f_turn_dict[date] = {'turn': turn_r_p}
        if len(f_turn_dict) > 0:
            print('f_turn_dict: {}, alarm_turn: {}, code: {}, not ok'.format(f_turn_dict, alarm_turn, code))
            return False
        print('code: {}, avg_turn: {}, alarm_turn: {}, cond_3_ok'.format(code, avg_turn, alarm_turn))
        # data_30 = data[-30:]
        # min_low_price = get_min_low_price(data_30)
        # max_high_price = get_max_high_price(data_30)
        # r_price = 100 * (max_high_price - min_low_price)/min_low_price
        # print(r_price)
        return True

    def strategy_2(self, code, k_line_list, m_day):
        day_gap_min = 3
        con_high_day = 2
        close_ratio_max = 20
        k_line_list_m_day = k_line_list[-m_day:]
        pct_chg_list = []
        for k_line in k_line_list_m_day:
            pct_chg = k_line['pct_chg']
            if isinstance(pct_chg, str) and not pct_chg:
                continue
            if float(pct_chg) >= pct_change_max:
                pct_chg_list.append(1)
            else:
                pct_chg_list.append(0)
        index_list = []
        for i, v in enumerate(pct_chg_list):
            if v == 1:
                index_list.append(i)
        if len(index_list) != con_high_day:
            return False
        if index_list[1] - index_list[0] != 1:
            return False

        l_index = index_list[1] + 1
        day_gap = m_day - l_index
        if day_gap < day_gap_min:
            return False
        r_index = m_day - 1
        k_line_list_l_r = k_line_list_m_day[l_index:r_index+1]
        close_t = float(k_line_list_m_day[index_list[-2]]['close'])
        close_price_list = []
        for k_line in k_line_list_l_r:
            close = float(k_line['close'])
            close_ratio = 100 * (close - close_t) / close_t
            if close_ratio < 0 and abs(close_ratio) > 1:
                continue
            date = k_line['date']
            close_price_list.append({'date': date, 'close': close, 'close_ratio': close_ratio})
        if len(close_price_list) < day_gap:
            # print('code: {},  not strategy_2_ok'.format(code))
            return False
        for close_p in close_price_list:
            close_ratio = close_p['close_ratio']
            if close_ratio > close_ratio_max:
                # print('code: {},  not strategy_2_ok'.format(code))
                return False
        max_turn = self.get_max_turn(k_line_list_m_day)
        if max_turn >= turn_max:
            # print('code: {}, max_turn: {} >= {}, not strategy_2_ok'.format(code, max_turn, turn_max))
            return False
        print('code: {},  strategy_2_ok'.format(code))
        return True

    def strategy_3(self, code, k_line_list, m_day):
        k_line_list_m_day = k_line_list[-m_day:]
        x_max_high_price = self.get_max_high_price(k_line_list_m_day)
        y_max_high_price = self.get_max_high_price(k_line_list)
        max_price_ratio = (x_max_high_price - y_max_high_price) / x_max_high_price * 100
        if max_price_ratio < -10:
            return False

        max_turn = self.get_max_turn(k_line_list_m_day)
        # print('max_turn: {}'.format(max_turn))
        turn_max = turn_max_i
        if code.startswith('sz.30') or code.startswith('30'):
            turn_max = turn_max_j
        if max_turn >= turn_max:
            return False
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
        if len(index_list) not in [1, 2, 3]:
            return False

        l_index = index_list[-1] + 1
        day_gap = m_day - l_index
        if day_gap != 1:
            return False
        up_prev_index = index_list[-1] - 3
        if up_prev_index < 0:
            return False
        w_list = k_line_list_m_day[up_prev_index: index_list[-1]]
        pct_chg_sum = self.get_pct_chg_sum(w_list)
        if pct_chg_sum < 0:
            return False
        # print('pct_chg_sum: {}'.format(pct_chg_sum))
        up_num, down_num = self.get_up_and_down_num(w_list)
        if down_num > 1:
            return False
        whole_up = self.is_stock_whole_up(w_list)
        if not whole_up:
            return False
        r_index = m_day - 1
        k_line_list_l_r = k_line_list_m_day[l_index:r_index + 1]
        # all_green = self.is_data_list_all_green(k_line_list_l_r)
        # if all_green:
        #     return False
        close_t = float(k_line_list_m_day[index_list[-1]]['close'])
        open_t = float(k_line_list_m_day[index_list[-1]]['open'])
        close_t_l = float(k_line_list_m_day[index_list[-1]-1]['close'])
        close_price_list = []
        for k_line in k_line_list_l_r:
            close = float(k_line['close'])
            _open = float(k_line['open'])
            high = float(k_line['high'])
            _pct_chg = float(k_line['pct_chg'])
            r_1 = 100 * (close - open_t) / open_t
            r_2 = 100 * (close - _open) / _open
            r_3 = 100 * (close - close_t_l) / close
            if r_1 < 0 and r_3 < 0:
                # print('code: {},  was give up'.format(code))
                return False
            # if r_2 < 0 or _pct_chg < 0:
            #     continue
            if r_2 < 0:
                continue
            date = k_line['date']
            close_price_list.append({'date': date, 'close': close, 'r_1': r_1, 'r_2': r_2})
        if len(close_price_list) < day_gap:
            # print('code: {},  was beated to lenggong'.format(code))
            return False

        print('code: {},  strategy_3_ok'.format(code))
        return True

    def strategy_4(self, code, k_line_list, m_day):
        k_line_list_m_day = k_line_list[-m_day:]
        x_max_high_price = self.get_max_high_price(k_line_list_m_day)
        y_max_high_price = self.get_max_high_price(k_line_list)
        max_price_ratio = (x_max_high_price - y_max_high_price) / x_max_high_price * 100
        if max_price_ratio < -6:
            return False

        max_turn = self.get_max_turn(k_line_list_m_day)
        # print('max_turn: {}'.format(max_turn))
        turn_max = turn_max_i
        if code.startswith('sz.30') or code.startswith('30'):
            turn_max = turn_max_j
        if max_turn >= turn_max:
            return False
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
        pch_chg_zt_index_list = []
        for i, v in enumerate(pct_chg_list):
            if v == 1:
                pch_chg_zt_index_list.append(i)
        if len(pch_chg_zt_index_list) not in [2, 3, 4]:
            return False
        if pch_chg_zt_index_list[-1] != m_day - 1:
            return False
        if pch_chg_zt_index_list[-2] == m_day - 2:
            return False

        l_index = None
        r_index = pch_chg_zt_index_list[-1]
        for i in pch_chg_zt_index_list[-2::-1]:
            gap = r_index - i - 1
            if 4 <= gap <= 7:
                l_index = i
                break
            r_index = i
        if l_index is None:
            return False
        up_prev_index = l_index - 3
        if up_prev_index < 0:
            return False
        w_list = k_line_list_m_day[up_prev_index: l_index]
        pct_chg_sum = self.get_pct_chg_sum(w_list)
        # print('pct_chg_sum: {}'.format(pct_chg_sum))
        if pct_chg_sum <= 0:
            return False
        # up_num, down_num = self.get_up_and_down_num(w_list)
        # if down_num > 1:
        #     return False
        # whole_up = self.is_stock_whole_up(w_list)
        # if not whole_up:
        #     return False
        k_line_list_l_r = k_line_list_m_day[l_index+1:r_index]
        all_green = self.is_data_list_all_green(k_line_list_l_r)
        if all_green:
            return False
        open_t = float(k_line_list_m_day[l_index]['open'])
        close_t_l = float(k_line_list_m_day[l_index-1]['close'])
        close_price_list = []
        for k_line in k_line_list_l_r:
            close = float(k_line['close'])
            _open = float(k_line['open'])
            high = float(k_line['high'])
            _pct_chg = float(k_line['pct_chg'])
            r_1 = 100 * (close - open_t) / open_t
            # r_2 = 100 * (close - _open) / _open
            r_3 = 100 * (close - close_t_l) / close
            if r_1 < 0 and abs(r_1) > 1 and r_3 < 0 and abs(r_3) > 1:
                print('code: {},  was give up'.format(code))
                return False
        print('code: {},  strategy_4_ok'.format(code))
        return True



