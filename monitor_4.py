from monitor import Monitor

TEST_CODE_DICT = {
# '600501': '2024-05-28',
# '002811': '2024-06-03',
}


class FourthMonitor(Monitor):
    def __init__(self):
        super(FourthMonitor, self).__init__(key_prefix='monitor_4')
        self.test_code_dict = TEST_CODE_DICT

    def get_strategy_res(self, code, stock_kline_list, min_opt_macd_diff=0):
        return self.strategist.get_fourth_strategy_res(code, stock_kline_list, min_opt_macd_diff)


if __name__ == '__main__':
    monitor = FourthMonitor()
    monitor.run()