from monitor import Monitor

TEST_CODE_DICT = {
# '603739': '2024-04-26',
# '603222': '2024-05-07',
# '600774': '2024-05-08',
# '600682': '2024-05-08',


# '600789': '2024-04-29',
# '002868': '2024-05-09',
# '000695': '2024-05-09',
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