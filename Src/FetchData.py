#!/usr/bin/env python
# -*- coding:utf-8 -*-
import sys
import os
import pandas
import tushare as ts
import sqlite3 as sql

__DBFile=r"Stock.db"
__conn=None # 
__StockInfoTableName=r"StockInfo"
___k_data_table=r"""k_data"""
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


def to_sql_value_string(data):
    if type(data) == str:
        return r"""'"""+data+r"""'"""
    else:
        return str(data)

def store_stock_list_to_db(stock_base=None,conn=None):
    """
        把dataframe格式的股票信息存储到数据表里头
    parameter
    ---
        stock_base:
            dataframe格式的股票信息
    """
    if stock_base is None:
        return
    global __conn
    # as default, use the global connection.
    # for test , use input parameter
    if conn is None:
        c=get_db_connection()
    else:
        c=conn

    fieldstr=r''
    valueStr=r''
    for index,row in stock_base.iterrows():
        fieldstr=r'code'
        valueStr=r"""'"""+index+r"""'"""
        for i in range(len(row)):
            fieldstr = fieldstr + r',' + row.index[i]
            # sql 要求字符串用‘’括起来
            valueStr = valueStr +r',' + to_sql_value_string(row.values[i])
        print(fieldstr)
        print(valueStr)
        global __StockInfoTableName

        queryStrStart = r"""insert or replace into """+ __StockInfoTableName +r""" (""" + fieldstr + r""" ) values ("""
        queryStrEnd=r""")"""

        execStr = queryStrStart + valueStr + queryStrEnd

        #print(queryStr) 

        if c is not None:
            print("sql string:"+execStr)
            c.execute(execStr)


    
    if c is not None:
        c.commit()

def store_k_data_to_db(data, conn=None):
    global ___k_data_table
    # check and create table
    sqlStr=r"""CREATE TABLE IF NOT EXISTS `"""+___k_data_table+r"""` (
        `date`  TEXT,
        `open`  REAL,
        `close` REAL,
        `high`  REAL,
        `low`   REAL,
        `volume`    REAL,
        `code`  TEXT
        );"""
    if conn is None:
        conn=get_db_connection()

    conn.execute(sqlStr)
    conn.commit()

    if data is None:
        print("data is None")
        return

    for index,row in data.iterrows():
        
        valueStr=''
        fieldstr=''
        for i in range(len(row)):
            if i==0:
                fieldstr = row.index[i]
                valueStr = to_sql_value_string(row.values[i])
            else:    
                fieldstr = fieldstr + r',' + row.index[i]
                valueStr = valueStr +r',' + to_sql_value_string(row.values[i])


        queryStrStart = r"""insert or replace into """+ ___k_data_table +r""" (""" + fieldstr + r""" ) values ("""
        queryStrEnd=r""")"""

        execStr = queryStrStart + valueStr + queryStrEnd
        #print( execStr)
        if conn is not None:
            conn.execute(execStr)
        
    
    if conn is not None:
        conn.commit()

            

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
    global __NetworkConnected
    global __StockInfoTableName
    try:
        b=ts.get_stock_basics()
        print(r'ts.get_stock_basics returns')

    except:
        print(r'ts.get_stock_basics raise errors')
        error_type, error_value, trace_back = sys.exc_info()
        print(error_value)
        __NetworkConnected=False
    conn=get_db_connection()
    if __NetworkConnected:
        store_stock_list_to_db(b,conn)
    
    return pandas.read_sql(r"""SELECT * FROM """+ __StockInfoTableName ,conn)
   
 
def get_k_data(code=None,dbconn=None,start='',end=''):
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
    global __NetworkConnected
    global ___k_data_table
    
    if dbconn is None:
        conn = get_db_connection()
    else:
        conn = dbconn
    #print("conn",conn)
    if __NetworkConnected == True:
    
        #
        # todo 增补数据库的数据
        try:
            k_net=ts.get_k_data(code,start,end)
            #print("get network data")
        except:
            print(r'tu.get_k_data raise error')
            error_type, error_value, trace_back = sys.exc_info()
            k_net = None
            print(error_value)
        
        #print("before call tore_k_data_to_db")
        #print(k_net)
        store_k_data_to_db(k_net,conn)

    # load data from db
    execStrStart=r"""SELECT * FROM """ + ___k_data_table + r""" WHERE code = """ + to_sql_value_string(code) + r""" """
    dateStr = ''
    execStrEnd=r""" order by date"""
    if (start == '') and (end == ''):
        dateStr = ''
    elif (start != '') and (end != ''):
        dateStr = r""" AND date >= """ + to_sql_value_string(start) + r"""and date <= """ + to_sql_value_string(end)
    elif (start != '') and (end == ''):
        dateStr = r"""AND date >= """ + to_sql_value_string(start)
    elif (start == '') and (end != ''):
        dateStr = r""" AND date <= """ + to_sql_value_string(end)
    
    execStr = execStrStart + dateStr + execStrEnd
    #print(execStr)

    if conn is not None:
        return pandas.read_sql(execStr,conn)
    else:
        return None



   
if __name__ == "__main__":
    #get_k_data()
    get_db_connection()
    print("This module used for get stock data")
