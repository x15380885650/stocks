from monitor import Monitor

TEST_CODE_DICT = {
# '002927': '2023-01-12',
# '002835': '2023-01-20',
# '002877': '2023-01-30',
# '605011': '2023-05-12',
# '603933': '2023-05-19',
# '600355': '2023-09-20',
# '002682': '2023-10-20',
# '603729': '2023-11-02',
# '000056': '2023-11-07',
# '600506': '2023-11-09',
# '600053': '2023-11-21',
# '000017': '2024-01-09',
# '000008': '2024-03-07',
}


class FirstMonitor(Monitor):
    def __init__(self):
        super(FirstMonitor, self).__init__(key_prefix='monitor_1')
        self.test_code_dict = TEST_CODE_DICT

    def get_strategy_res(self, code, stock_kline_list, min_opt_macd_diff=0):
        return self.strategist.get_first_strategy_res(code, stock_kline_list, min_opt_macd_diff)


if __name__ == '__main__':
    monitor = FirstMonitor()
    monitor.run()