from monitor import Monitor

TEST_CODE_DICT = {
# '002861': '2024-06-26',
# '002857': '2024-06-26'
# '603256': '2024-06-28'

}


class FirstMonitor(Monitor):
    def __init__(self):
        super(FirstMonitor, self).__init__(key_prefix='monitor_5')
        self.test_code_dict = TEST_CODE_DICT

    def get_strategy_res(self, code, stock_kline_list, min_opt_macd_diff=0):
        return self.strategist.get_fifth_strategy_res(code, stock_kline_list, min_opt_macd_diff)


if __name__ == '__main__':
    monitor = FirstMonitor()
    monitor.run()