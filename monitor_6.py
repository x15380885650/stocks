from monitor import Monitor

TEST_CODE_DICT = {
# '000062': '2024-08-15',
# '000755': '2024-08-20',
# '002403': '2024-08-20',
#
#
# '002479': '2024-08-22',
# '002780': '2024-08-22',
# '000546': '2024-08-22',
# '002762': '2024-08-22',
# '600757': '2024-08-23',
# '600198': '2024-08-23',
# '002396': '2024-08-23',
#
# '605089': '2024-08-30',
# '600587': '2024-08-30',
# '605507': '2024-08-30',
# '603386': '2024-08-30',
# '603609': '2024-08-30',
# '002695': '2024-08-30',
# '603043': '2024-08-30',
# '002029': '2024-08-30',
# '600558': '2024-08-30',
# '605179': '2024-08-30',
# '600305': '2024-08-30',

}


class SixthMonitor(Monitor):
    def __init__(self):
        super(SixthMonitor, self).__init__(key_prefix='monitor_6')
        self.test_code_dict = TEST_CODE_DICT

    def get_strategy_res(self, code, stock_kline_list, min_opt_macd_diff=0):
        return self.strategist.get_sixth_strategy_res(code, stock_kline_list, min_opt_macd_diff)


if __name__ == '__main__':
    monitor = SixthMonitor()
    monitor.run()