from monitor import Monitor

TEST_CODE_DICT = {
# '605011': '2023-05-12',
# '002238': '2023-11-02',
# '000056': '2023-11-07',
# # '603739': '2024-04-26',
# # # '600505': '2024-05-06',
# '600889': '2024-05-10',

# '002823': '2024-07-08',

}


class FirstMonitor(Monitor):
    def __init__(self):
        super(FirstMonitor, self).__init__(key_prefix='monitor_1')
        self.test_code_dict = TEST_CODE_DICT

    def get_strategy_res(self, code, stock_kline_list, min_opt_macd_diff=0):
        return self.strategist.get_first_strategy_res(code, stock_kline_list, min_opt_macd_diff)


if __name__ == '__main__':
    monitor = FirstMonitor()
    monitor.run()