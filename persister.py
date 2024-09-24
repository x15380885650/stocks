from redis import StrictRedis


class Persister(object):
    def __init__(self, key_prefix):
        # config set requirepass iscas139
        redis_conf = {'host': '127.0.0.1', 'port': 6408, 'password': 'iscas139', 'db': 0}
        # redis_conf = {'host': '39.107.138.33', 'port': 6408, 'password': 'iscas139', 'db': 0}
        self.redis = StrictRedis(**redis_conf, decode_responses=True)
        self.key_prefix = key_prefix

    def scan_keys(self, pattern):
        cursor = '0'
        keys = []
        while cursor != 0:
            cursor, data = self.redis.scan(cursor=cursor, match=pattern)
            keys.extend(data)
        return keys

    def save_code_to_monitor(self, date, code):
        key = '{}:{}:monitor'.format(self.key_prefix, date)
        self.redis.sadd(key, code)

    def save_code_to_notifier(self, date, code):
        key = '{}:{}:notifier'.format(self.key_prefix, date)
        self.redis.sadd(key, code)

    def get_monitor_code_list(self, date):
        monitor_key = '{}:{}:monitor'.format(self.key_prefix, date)
        notifier_key = '{}:{}:notifier'.format(self.key_prefix, date)
        diff = self.redis.sdiff(monitor_key, notifier_key)
        return list(diff)

    def get_all_monitor_code_list(self, date):
        pattern_monitor = '{}:{}:monitor'.format(self.key_prefix, date)
        monitor_keys = self.scan_keys(pattern_monitor)
        code_list = []
        for monitor_key in monitor_keys:
            notifier_key = monitor_key.replace(':monitor', ':notifier')
            diff = self.redis.sdiff(monitor_key, notifier_key)
            code_list.extend(list(diff))
        return list(set(code_list))

    def clear_monitor_code_list_except_date(self, date):
        pattern_monitor = f'{self.key_prefix}:20*:monitor'
        monitor_keys = self.scan_keys(pattern_monitor)
        monitor_date_key = f'{self.key_prefix}:{date}:monitor'
        for monitor_key in monitor_keys:
            if monitor_key == monitor_date_key:
                continue
            self.redis.delete(monitor_key)

    def get_all_buy_code_list(self):
        pattern_buy_code_list = '*:buy_stock_list'
        buy_stock_list_keys = self.scan_keys(pattern_buy_code_list)
        code_list = []
        for buy_stock_list_key in buy_stock_list_keys:
            code_set = self.redis.smembers(buy_stock_list_key)
            for code in code_set:
                if code:
                    code_list.append(code)
        return list(set(code_list))

    def get_max_monitor_show_count(self):
        key = '{}:max_show_count_monitor'.format(self.key_prefix)
        val = self.redis.get(key)
        if val is None:
            val = 5
            self.redis.set(key, val)
        return int(val)

    def get_email_dict(self):
        key = '{}:email'.format(self.key_prefix)
        val = self.redis.hgetall(key)
        if not val:
            self.redis.hset(key, 'xucg025@qq.com', 1)
        return self.redis.hgetall(key)

    def clear_monitor_code_list(self, date):
        monitor_key = '{}:{}:monitor'.format(self.key_prefix, date)
        self.redis.delete(monitor_key)

    def remove_monitor_code(self, date, code):
        monitor_key = '{}:{}:monitor'.format(self.key_prefix, date)
        self.redis.srem(monitor_key, code)

    def get_buy_code_list(self):
        key = '{}:buy_stock_list'.format(self.key_prefix)
        code_set = self.redis.smembers(key)
        if not code_set:
            self.redis.sadd(key, '')
            return []
        code_list = []
        for code in code_set:
            if code:
                code_list.append(code)
        return code_list

    def get_min_pct_chg_notifier(self):
        key = '{}:min_pct_chg_notifier'.format(self.key_prefix)
        pct_chg = self.redis.get(key)
        if pct_chg is None:
            pct_chg = 6.5
            self.redis.set(key, pct_chg)
        return float(pct_chg)

    def get_min_pct_chg_monitor(self):
        key = '{}:min_pct_chg_monitor'.format(self.key_prefix)
        pct_chg = self.redis.get(key)
        if pct_chg is None:
            pct_chg = 0
            self.redis.set(key, pct_chg)
        return float(pct_chg)

    def save_min_pct_chg_monitor(self, pct_chg_monitor):
        key = '{}:min_pct_chg_monitor'.format(self.key_prefix)
        self.redis.set(key, pct_chg_monitor)

    def get_sleep_time_notifier(self):
        key = '{}:sleep_time_notifier'.format(self.key_prefix)
        sleep_time = self.redis.get(key)
        if sleep_time is None:
            sleep_time = 2
            self.redis.set(key, sleep_time)
        return float(sleep_time)

    def get_stop_status(self):
        key = '{}:is_stop'.format(self.key_prefix)
        is_stop = self.redis.get(key)
        if is_stop is None:
            is_stop = 0
            self.redis.set(key, is_stop)
        return int(is_stop)

    def get_clear_monitor_status(self):
        key = '{}:clear_monitor'.format(self.key_prefix)
        is_clear_monitor = self.redis.get(key)
        if is_clear_monitor is None:
            is_clear_monitor = 0
            self.redis.set(key, is_clear_monitor)
        return int(is_clear_monitor)

    def get_sleep_time_monitor(self):
        key = '{}:sleep_time_monitor'.format(self.key_prefix)
        sleep_time = self.redis.get(key)
        if sleep_time is None:
            sleep_time = 0.5
            self.redis.set(key, sleep_time)
        return float(sleep_time)

    def get_min_opt_macd_diff(self):
        key = '{}:min_opt_macd_diff'.format(self.key_prefix)
        macd_value = self.redis.get(key)
        if macd_value is None:
            macd_value = 0
            self.redis.set(key, macd_value)
        return float(macd_value)

    def get_show_code_status(self):
        key = '{}:show_code'.format(self.key_prefix)
        is_show_code = self.redis.get(key)
        if is_show_code is None:
            is_show_code = 1
            self.redis.set(key, is_show_code)
        return int(is_show_code)
