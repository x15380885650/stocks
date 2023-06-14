if __name__ == '__main__':
    from data_source_ef import EfDataSource
    from data_source_bao import BaoDataSource
    s = EfDataSource()
    s = BaoDataSource()
    # s.get_all_stock_list()
    # s.get_stock_kline_history('000917', start_date='20230614', end_date='20230614')
    s.get_stock_kline_history('sz.000917', start_date='2023-06-14', end_date='2023-06-14')