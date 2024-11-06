from monitor import Monitor

TEST_CODE_DICT = {
# '000721': '2022-11-03',
# '601595': '2023-03-20',
# '002703': '2023-06-30',
# '600178': '2023-11-23',
#
# '600083': '2024-03-15',
# '002455': '2024-04-29',
# '002693': '2024-08-27',
# '002388': '2024-08-30',
# '600463': '2024-09-25',
# '002253': '2024-10-25',
# '600203': '2024-10-28',

# '600724': '2024-11-05',


# '603616': '2024-10-16',
# '002649': '2024-10-17',
# '002856': '2024-10-17',
# '002123': '2024-10-24',
}


class SixthMonitor(Monitor):
    def __init__(self):
        super(SixthMonitor, self).__init__(key_prefix='monitor_6')
        self.test_code_dict = TEST_CODE_DICT

    def get_strategy_res(self, k_line_list, c_fetcher):
        return self.strategist.get_sixth_strategy_res(k_line_list, c_fetcher)


if __name__ == '__main__':
    monitor = SixthMonitor()
    monitor.run()