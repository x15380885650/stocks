from redis import StrictRedis


class Persister(object):
    def __init__(self, key_prefix):
        redis_conf = {'host': '127.0.0.1', 'port': 6408, 'password': 'iscas139', 'db': 0}
        self.redis = StrictRedis(**redis_conf, decode_responses=True)
        self.key_prefix = key_prefix

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

    def get_monitor_pch_chg(self):
        key = '{}:pct_chg'.format(self.key_prefix)
        pct_chg = self.redis.get(key)
        if pct_chg is None:
            pct_chg = 8
            self.redis.set(key, pct_chg)
        return float(pct_chg)

