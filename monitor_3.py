from monitor import Monitor

TEST_CODE_DICT = {
# '600178': '2023-11-23',
# '002146': '2024-05-16',
# '603386': '2024-06-25',
}


class ThirdMonitor(Monitor):
    def __init__(self):
        super(ThirdMonitor, self).__init__(key_prefix='monitor_3')
        self.test_code_dict = TEST_CODE_DICT

    def get_strategy_res(self, code, stock_kline_list, min_opt_macd_diff=0):
        return self.strategist.get_third_strategy_res(code, stock_kline_list, min_opt_macd_diff)


if __name__ == '__main__':
    monitor = ThirdMonitor()
    monitor.run()