from monitor import Monitor

TEST_CODE_DICT = {
# '603528': '2023-11-13',
#
# '600083': '2024-03-15',
# '000737': '2024-03-29',
# '002455': '2024-04-29',
# '600101': '2024-05-24',
# '000679': '2024-07-30',
# '002647': '2024-08-19',
# '600552': '2024-08-20',
# '002388': '2024-08-30',
# '000058': '2024-09-03',
# '000595': '2024-09-12',
# '002123': '2024-09-25',
# '002488': '2024-10-17',
# '600439': '2024-10-21',
# '600753': '2024-10-24',
# '603958': '2024-10-24',
# '002253': '2024-10-25',
# '600203': '2024-10-28',


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
# '002163': '2024-09-26',
# '002066': '2024-09-26',
# '000850': '2024-09-26',
# '002093': '2024-10-23',
# '002793': '2024-10-28',
# '600889': '2024-10-28',

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