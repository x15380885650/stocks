from monitor import Monitor

TEST_CODE_DICT = {
# '600083': '2024-03-15',
# '000737': '2024-03-29',
# '002455': '2024-04-29',
# '002685': '2024-07-26',
# '000679': '2024-07-30',
# '002647': '2024-08-19',
# '002388': '2024-08-30',
# '000595': '2024-09-12',
# '002123': '2024-09-25',
# '600439': '2024-10-21',
# '600753': '2024-10-24',
# '000639': '2024-10-31',
# '000973': '2024-10-31',
# '002068': '2024-11-04',
# '600676': '2024-11-15',


# # # # #
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
# '000672': '2024-10-30',
# '002581': '2024-10-31',
# '002630': '2024-10-31',
# '600613': '2024-11-06',
# '000590': '2024-11-07',
# '002622': '2024-11-08',
# '002175': '2024-11-11',
# '600212': '2024-11-13',
# '002780': '2024-11-18',
}


class SecondMonitor(Monitor):
    def __init__(self):
        super(SecondMonitor, self).__init__(key_prefix='monitor_2')
        self.test_code_dict = TEST_CODE_DICT

    def get_strategy_res(self, stock_kline_list, c_fetcher):
        return self.strategist.get_second_strategy_res(stock_kline_list, c_fetcher)


if __name__ == '__main__':
    monitor = SecondMonitor()
    monitor.run()