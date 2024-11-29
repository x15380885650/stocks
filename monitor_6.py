from monitor import Monitor

TEST_CODE_DICT = {
# '000721': '2022-11-03',
# '601595': '2023-03-20',
# '002703': '2023-06-30',
#
# '600083': '2024-03-15',
# '002455': '2024-04-29',
# '002693': '2024-08-27',
# '002388': '2024-08-30',
# '002253': '2024-10-25',
# '600203': '2024-10-28',
# '000566': '2024-11-05',
# '600787': '2024-11-26',


# '603616': '2024-10-16',
# '002649': '2024-10-17',
# '002856': '2024-10-17',
# '002123': '2024-10-24',
# '600724': '2024-11-05',
# '002622': '2024-11-08',
# '600537': '2024-11-11',
# '603883': '2024-11-12',
# '000679': '2024-11-29',
}


class SixthMonitor(Monitor):
    def __init__(self):
        super(SixthMonitor, self).__init__(key_prefix='monitor_6')
        self.test_code_dict = TEST_CODE_DICT

    def get_strategy_res(self, stock_kline_list, c_fetcher, is_test=False):
        return self.strategist.get_sixth_strategy_res(stock_kline_list, c_fetcher, is_test=is_test)


if __name__ == '__main__':
    monitor = SixthMonitor()
    monitor.run()