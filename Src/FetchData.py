#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import os
import tushare as ts
import sqlite3 as sql

__DBFile=r"Stock.db"
__conn=None # 
__StockInfoTableName=r"StockInfo"
__StockInfoTableVersion=1   # 如果表中的版本和当前版本不一样，则需要更新到当前版本
__NetworkConnected=True
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
	`code`	TEXT,
	`name`	TEXT,
	`industry`	TEXT,
	`area`	TEXT,
	`pe`	REAL,
	`outstanding`	REAL,
	`totals`	REAL,
	`totalAssets`	REAL,
	`liquidAssets`	REAL,
	`fixedAssets`	REAL,
	`reserved`	REAL,
	`reservedPerShare`	REAL,
	`esp`	REAL,
	`bvps`	REAL,
	`pb`	REAL,
	`timeToMarket`	INTEGER,
	`undp`	REAL,
	`perundp`	REAL,
	`rev`	REAL,
	`profit`	REAL,
	`gpr`	REAL,
	`npr`	REAL,
	`holders`	REAL,
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

def store_stock_list_to_db(stock_base=None):
    """
        把dataframe格式的股票信息存储到数据表里头
    parameter
    ---
        stock_base:
            dataframe格式的股票信息
    """
    if stock_base is None:
        return

    if __conn is None:
        return

     # 准备列名称
    indexhead=[]
    tmp=stock_base.columns.tolist()
    headlist=indexhead+tmp
    fieldstr=r'code'
    for head in headlist:
        fieldstr=fieldstr + head
    
    fieldStr=r'code'
    for head in headlist:
        fieldstr=fieldstr + head

    queryStrStart = r"""insert or replace into StockInfo (""" + fieldStr + r""" ) values ("""
    queryStrEnd=r""")"""

    valueStr=""""""
    # create value string for each row

    queryStr=queryStrStart + valueStr + queryStrEnd

     

    
    pass




def get_all_stock_list(code=None):
    """
        首先会试图获取网络上的股票信息，如果获取失败，则说明没有联网，则会设置__NetworkConnected为False。
	在后续的操作中，如果__NetworkConnected为False，则只使用本地数据
        获取系统中的所有股票列表。
        股票列表为本地数据库和当天交易的并集。
        并用网络上的股票信息更新数据库中的表
    parameter
    ---
       None

    return
    ---
        dataframe
    """
    try:
        b=ts.get_stock_basics()
        print(r'ts.get_stock_basics returns')

    except:
        print(r'ts.get_stock_basics raise errors')
        error_type, error_value, trace_back = sys.exc_info()
        print(error_value)
        __NetworkConnected=False
    if __NetworkConnected:
        store_stock_list_to_db(b)
        
   
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
