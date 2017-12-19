#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import tushare as ts

def get_all_stock_list(code=None):
    """
        获取系统中的所有股票列表。股票列表为本地数据库和当天交易的并集。
    parameter
    ---
       None

    return
    ---
        [股票代码，股票名称]
    """
    pass

def get_k_data(code=None,start=None,end=None):
    """
        获取指定股票的从 start 到 end的k线数据。
        在获取数据时，会先从本地数据库中获取数据，再从网络中补充数据。
        补充的数据会自动保存到数据库中。
    parameters
    ------
    code:string
         股票代码 e.g. 600848
    start:string
         开始日期 format：YYYY-MM-DD 为空时取到API所提供的最早日期数据
    end:string
         结束日期 format：YYYY-MM-DD 为空时取到最近一个交易日数据
    ktype：string
         数据类型，D=日k线 W=周 M=月 5=5分钟 15=15分钟 30=30分钟 60=60分钟，默认为D

    return
    ------
    """
#
# todo 增补数据库的数据



if __name__ == "__main__":
    print("This module used for get stock data")
