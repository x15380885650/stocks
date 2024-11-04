from monitor import Monitor

TEST_CODE_DICT = {
# '001330': '2024-11-04',

}


class ThirdMonitor(Monitor):
    def __init__(self):
        super(ThirdMonitor, self).__init__(key_prefix='monitor_3')
        self.test_code_dict = TEST_CODE_DICT

    def get_strategy_res(self, stock_kline_list, c_fetcher):
        return self.strategist.get_third_strategy_res(stock_kline_list, c_fetcher)


if __name__ == '__main__':
    monitor = ThirdMonitor()
    monitor.run()