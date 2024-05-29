from monitor import Monitor

TEST_CODE_DICT = {
# '605011': '2023-05-12',
# # '002902': '2023-05-30',
# '002238': '2023-11-02',
# # '603729': '2023-11-02',
# '000056': '2023-11-07',
# # '000017': '2024-01-09',
# '603739': '2024-04-26',
# '600505': '2024-05-06',
# '600889': '2024-05-10',

# '600719': '2024-05-08',
# '002112': '2024-05-27',
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