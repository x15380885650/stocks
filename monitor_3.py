from monitor import Monitor

TEST_CODE_DICT = {
# '002717': '2024-09-19',
# '002640': '2024-11-27',
# '002131': '2024-11-27',

# '600249': '2024-11-28',
# '002076': '2024-11-28',
# '002137': '2024-12-02',

}


class ThirdMonitor(Monitor):
    def __init__(self):
        super(ThirdMonitor, self).__init__(key_prefix='monitor_3')
        self.test_code_dict = TEST_CODE_DICT

    def get_strategy_res(self, stock_kline_list, c_fetcher, is_test=False):
        return self.strategist.get_third_strategy_res(stock_kline_list, c_fetcher, is_test=is_test)


if __name__ == '__main__':
    monitor = ThirdMonitor()
    monitor.run()