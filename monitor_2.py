from monitor import Monitor

TEST_CODE_DICT = {
# '002246': '2024-05-23',
# '600101': '2024-05-24',
# '603890': '2024-05-31',

# '600661': '2024-05-14',
# '600228': '2024-05-16',
# '600744': '2024-05-20',
# '603612': '2024-05-21',
# '002379': '2024-05-21',
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