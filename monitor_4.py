from monitor import Monitor

TEST_CODE_DICT = {
# '000158': '2024-09-25',
# '002583': '2024-10-11',
# '002094': '2024-10-17',
# '000016': '2024-10-24',
# '002542': '2024-10-24',
# '600130': '2024-11-04',

}


class FourthMonitor(Monitor):
    def __init__(self):
        super(FourthMonitor, self).__init__(key_prefix='monitor_4')
        self.test_code_dict = TEST_CODE_DICT

    def get_strategy_res(self, stock_kline_list, c_fetcher):
        return self.strategist.get_fourth_strategy_res(stock_kline_list, c_fetcher)


if __name__ == '__main__':
    monitor = FourthMonitor()
    monitor.run()