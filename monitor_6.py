from monitor import Monitor

TEST_CODE_DICT = {
# '000721': '2022-11-03',
# '601595': '2023-03-20',
#
# '600083': '2024-03-15',
# '000737': '2024-03-29',
# '002455': '2024-04-29',
# '000679': '2024-07-30',
# '002693': '2024-08-27',
# '002388': '2024-08-30',
# '600463': '2024-09-26',
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