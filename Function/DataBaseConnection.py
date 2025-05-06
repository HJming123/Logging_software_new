# import mysql.connector
#
# def connect_to_database():
#     connection = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="8420jjph",
#         database="logging"
#     )
#     return connection
#
# def connect_to_database_test():
#     connection = mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="8420jjph",
#         database="logging_test"
#     )
#     return connection

import sqlite3

def connect_to_database_test():
    connection = sqlite3.connect("logging.sqlite")
    if connection is None:
        print('没有连接数SQLite据库')
    else:
        print('连接到数据库')

    cursor = connection.cursor()

    # 创建well表
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS well(
                WellID INTEGER PRIMARY KEY,
                WellName TEXT NOT NULL,
                CurveNumber INTEGER,
                LayerLineNumber INTEGER
            )
    ''')
    # print('well表创建成功')

    # 创建layerlines表
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS layerlines(
                LayerLineID INTEGER PRIMARY KEY,
                LayerLineName TEXT NOT NULL,
                Depth REAL NOT NULL,
                WellID INTEGER
            )
    ''')
    # print('layerlines表创建成功')

    # 提交事务
    connection.commit()

    return connection