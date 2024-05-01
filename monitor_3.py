from monitor import Monitor

TEST_CODE_DICT = {
# '600083': '2024-03-15',
# '000737': '2024-03-29',
# '000506': '2024-04-02',
# '603657': '2024-04-12',
# '002455': '2024-04-29',

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