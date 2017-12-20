#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import tushare as ts
import sqlite3 as sql

__DBFile=r"Stock.db"
__conn=None # 
__StockInfoTableName=r"StockInfo"
def check_stockInfoTable(c):
    """
        检查数据库中是否有股票信息表。如果没有则建立之
    Parameters
    ---
        c  sqlite3.Connection
    Return
    ---
        None

    """
    execStr=""" CREATE TABLE IF NOT EXISTS """+__StockInfoTableName +r""" 
        (
        `code`  INTEGER NOT NULL,
        `Name`  TEXT,
        PRIMARY KEY(code)
        )"""
    cursor= c.execute(execStr)
    print("try to creat "+__StockInfoTableName)
    c.commit()


def get_db_connection():
    """
        获取数据库连接。 如果数据库已经打开，则直接返回 conn；否则打开数据库文件
    Parameters
    ---
        None

    return
    ---
        sqlite3.Connection database connection


    """
    global __conn
    global __DBFile

    if __conn==None:
        print("open db file"+__DBFile)
        __conn=sql.connect(__DBFile)
        check_stockInfoTable(__conn)
        return __conn

    else:
        return __conn

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
    #get_k_data()
    get_db_connection()
    print("This module used for get stock data")
