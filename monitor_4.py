from monitor import Monitor

TEST_CODE_DICT = {
# '000702': '2024-05-20',
# '002055': '2024-05-31',
# '002356': '2024-06-06',
# '001298': '2024-06-11',


# '600716': '2024-04-23',
# '600992': '2024-06-07',
# '600119': '2024-06-12',
# '603105': '2024-06-03',
# '600774': '2024-06-04',
# '600353': '2024-06-13',
# '603132': '2024-06-14',

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