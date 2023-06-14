# import easyquotation  # https://github.com/shidenggui/easyquotation
#
# # quotation = easyquotation.use('sina') # 新浪 ['sina'] 腾讯 ['tencent', 'qq']
# #
# # # ddd = quotation.market_snapshot(prefix=True) # prefix 参数指定返回的行情字典中的股票代码 key 是否带 sz/sh 前缀
# # # print(ddd)
# #
# # ddd = quotation.real('sz000917') # 支持直接指定前缀，如 'sh000001'
# # print(ddd)
#
# quotation = easyquotation.use("timekline")
# data = quotation.real('sz000917', prefix=True)
# print(data)

import efinance as ef  # https://github.com/Micro-sheep/efinance   https://zhuanlan.zhihu.com/p/388088384
# stock_code = '000917'
# ddd = ef.stock.get_quote_history(stock_code, beg='20230401', end='20230614')
# ef.stock.get_quote_snapshot
# 获取沪深全市场股票整体状况
df = ef.stock.get_realtime_quotes()
print(df)