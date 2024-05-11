from monitor import Monitor

TEST_CODE_DICT = {
# '601566': '2023-02-24',
# '600822': '2023-06-01',
# '603767': '2023-06-16',
# '002377': '2023-07-26',
# '000628': '2023-09-26',
# '002456': '2023-09-28',
# '600678': '2023-12-05',
# '600715': '2023-12-06',
# '603660': '2023-12-07',

}


class SecondMonitor(Monitor):
    def __init__(self):
        super(SecondMonitor, self).__init__(key_prefix='monitor_2')
        self.test_code_dict = TEST_CODE_DICT

    def get_strategy_res(self, code, stock_kline_list, min_opt_macd_diff=0):
        return self.strategist.get_second_strategy_res(code, stock_kline_list, min_opt_macd_diff)


if __name__ == '__main__':
    monitor = SecondMonitor()
    monitor.run()