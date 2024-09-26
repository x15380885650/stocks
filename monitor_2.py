from monitor import Monitor

TEST_CODE_DICT = {
# '603528': '2023-11-13',
#
# '600083': '2024-03-15',
# '000737': '2024-03-29',
# '603657': '2024-04-12',
# '002455': '2024-04-29',
# '000422': '2024-05-06',
# '600101': '2024-05-24',
# '603890': '2024-05-31',
# '603836': '2024-06-04',
# '000679': '2024-07-30',
# '603389': '2024-08-08',
# '600552': '2024-08-20',
# '002388': '2024-08-30',
# '000058': '2024-09-03',
# '600698': '2024-09-23',




# '600661': '2024-05-13',
# '600661': '2024-05-14',
# '600228': '2024-05-16',
# '600744': '2024-05-20',
# '603612': '2024-05-21',
# '002888': '2024-08-28',
# '002915': '2024-08-19',
# '603602': '2024-08-07',
# '000668': '2024-09-25',
# '603778': '2024-09-25',
# '002162': '2024-09-25',
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