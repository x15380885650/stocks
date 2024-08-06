from monitor import Monitor

TEST_CODE_DICT = {
# '603390': '2024-08-01',
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