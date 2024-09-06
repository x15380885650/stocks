from monitor import Monitor

TEST_CODE_DICT = {
'000678': '2023-06-26',
'002103': '2023-11-16',
'603536': '2023-11-24',
'600250': '2023-11-28',
'600661': '2023-12-01',
'600635': '2024-07-25',
'002104': '2024-09-05',
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