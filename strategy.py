from data_source_bao import BaoDataSource
from data_source_ef import EfDataSource

test_stock_dict = [
    # {'code': '601595', 'end_date': datetime.strptime('2023-03-21', '%Y-%m-%d')},
    # {'code': '600629', 'end_date': datetime.strptime('2023-04-21', '%Y-%m-%d')},
    # {'code': '601949', 'end_date': datetime.strptime('2023-04-21', '%Y-%m-%d')},
    # {'code': '603918', 'end_date': datetime.strptime('2023-05-26', '%Y-%m-%d')},
]


class Strategy(object):
    def __init__(self):
        pass

    def run(self):
        ds = BaoDataSource(test_stock_dict)
        ds = EfDataSource(test_stock_dict)
        ds.get_end_date()


if __name__ == '__main__':
    s = Strategy()
    s.run()