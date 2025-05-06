from PyQt5.QtWidgets import QTableWidgetItem

import Globals
from Function.DataBaseConnection import connect_to_database_test

def getTableData():
    connection = connect_to_database_test()
    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM {Globals.theOpenedWellName}")
    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return rows

def getDepth(self):
    connection = connect_to_database_test()
    cursor = connection.cursor()

    cursor.execute(f'SELECT depth FROM {Globals.theOpenedWellName}')
    depth = cursor.fetchall()

    cursor.close()
    connection.close()

    return depth


def getCurveData(): # 获取曲线值
    connection = connect_to_database_test()
    cursor = connection.cursor()

    cursor.execute(f'SELECT * FROM {Globals.theOpenedWellName}')
    curveData = cursor.fetchall()

    cursor.close()
    connection.close()

    return curveData

def getTableHeaders():  # 获取表格的头标签栏
    connection = connect_to_database_test()
    cursor = connection.cursor()

    # cursor.execute(f"SHOW COLUMNS FROM {Globals.theOpenedWellName}")
    cursor.execute(f"PRAGMA table_info({Globals.theOpenedWellName})")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    # print(f'column_names:{column_names}')

    cursor.close()
    connection.close()

    return column_names

def load_data(self):    # 将数据库中的某一口井的数据导入到“表格界面”的表格中
    connection1 = connect_to_database_test()
    connection2 = connect_to_database_test()
    cursor1 = connection1.cursor()
    cursor2 = connection2.cursor()

    # print(f'Globals.theOpenedWellName:{Globals.theOpenedWellName}')
    # sql_select = 'SELECT depth FROM %s'
    # print(f"SQL Query: {sql_select % Globals.theOpenedWellName}")
    # cursor2.execute(sql_select, (Globals.theOpenedWellName,))
    cursor2.execute(f"SELECT depth FROM {Globals.theOpenedWellName}")
    depth_data = cursor2.fetchall()

    total_records = len(depth_data)    # 总共的行记录数
    Globals.total_pages = (total_records // Globals.page_size) + (1 if total_records % Globals.page_size > 0 else 0) # 总共的页数

    offset = (Globals.current_page - 1) * Globals.page_size
    headers = getTableHeaders()    # 获取数据标题栏

    # 分页查询语句
    cursor1.execute(f"SELECT * FROM {Globals.theOpenedWellName} LIMIT {Globals.page_size} OFFSET {offset}")
    data = cursor1.fetchall()

    # 这里操作的表格对象是“表格界面”的表格
    self.table_widget = self.tableInterface.tableView

    self.table_widget.setRowCount(0)
    self.table_widget.setColumnCount(len(headers))
    self.table_widget.setHorizontalHeaderLabels(headers)
    for row_num, row_data in enumerate(data):
        self.table_widget.insertRow(row_num)
        for col_num, col_data in enumerate(row_data):
            item = QTableWidgetItem(str(col_data))
            self.table_widget.setItem(row_num, col_num, item)

    cursor2.close()
    cursor1.close()
    connection1.close()
    connection2.close()

def load_previous_page(self):
    if Globals.current_page > 1:
        Globals.current_page -= 1
        self.load_data()
    else:
        pass


def load_next_page(self):
    if Globals.current_page < Globals.total_pages:
        Globals.current_page += 1
        self.load_data()
    else:
        pass