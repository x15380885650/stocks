from monitor import Monitor

TEST_CODE_DICT = {
# '600083': '2024-03-15',
# '000737': '2024-03-29',
# '603657': '2024-04-12',
# '002455': '2024-04-29',

# '600661': '2024-05-14',
# '600228': '2024-05-16',
# '603612': '2024-05-17',
# '600744': '2024-05-20',
# '603612': '2024-05-21',
# '002379': '2024-05-21',
# '002246': '2024-05-23',
}


class ThirdMonitor(Monitor):
    def __init__(self):
        super(ThirdMonitor, self).__init__(key_prefix='monitor_3')
        self.test_code_dict = TEST_CODE_DICT

    def get_strategy_res(self, code, stock_kline_list, min_opt_macd_diff=0):
        return self.strategist.get_third_strategy_res(code, stock_kline_list, min_opt_macd_diff)


if __name__ == '__main__':
    monitor = ThirdMonitor()
    monitor.run()