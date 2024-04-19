from monitor import Monitor

TEST_CODE_DICT = {
# '603657': '2024-04-12',
# '603929': '2024-04-15',

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