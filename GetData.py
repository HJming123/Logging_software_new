import os.path
import sys

import numpy
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
import lasio

import Globals
from Function import DataBaseConnection, InformationShow


class GetData(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_name = '' # 打开的文件名
        Globals.sign_whetherTheWellFileIsOpened = False   # 用来判断.las文件是否已经导入数据库，导入成功为True，导入失败为False


    def import_las_file(self, infor_signal, waitting_infor_signal, progress_updated, file_path):      # 导入las文件
        Globals.sign_hasSameWellName = False
        self.task_progress = 0
        # 获取打开的文件路径
        if file_path:
            # 如果文件打开了将file_name设置成所打开的文件名
            self.file_name, _ = os.path.splitext(os.path.basename(file_path))
            wellName_existed = self.getWellName_Existed(progress_updated)
            for well_name in wellName_existed:
                if self.file_name == well_name:
                    # print('已导入该井！')
                    Globals.sign_hasSameWellName = True
                    # waitting_infor_signal.emit(False)
                    infor_signal.emit(False)
                    break
                else:
                    # print('该井尚未导入！')
                    Globals.sign_hasSameWellName = False

            if not Globals.sign_hasSameWellName:
                try:
                    waitting_infor_signal.emit(True)
                    self.import_las_to_database(file_path, self.file_name, progress_updated)
                    # Globals.sign_whetherTheWellFileIsOpened = True
                    # waitting_infor_signal.emit(False)
                    infor_signal.emit(True)
                except Exception as e:
                    # Globals.sign_whetherTheWellFileIsOpened = False
                    # waitting_infor_signal.emit(False)
                    infor_signal.emit(False)
                    print(f'导入文件错误：{e}')
                finally:
                    waitting_infor_signal.emit(False)
        else:
            print('没有选择文件打开')
            # waitting_infor_signal.emit(False)
            infor_signal.emit(False)

    def getWellName_Existed(self, progress_updated):
        connection = DataBaseConnection.connect_to_database_test()
        cursor = connection.cursor()

        cursor.execute(f"SELECT WellName FROM well")
        result = cursor.fetchall()
        wellName_existed = []
        for sub_tuple in result:
            wellName_existed.append(sub_tuple[0])
        # print(f"wellName_existed:{wellName_existed}")
        print(wellName_existed)

        self.task_progress = 20
        progress_updated.emit(self.task_progress)

        return wellName_existed

    def import_las_to_database(self, file_path, file_name, progress_updated):  # 将las文件中的数据导入到数据库中
        # 连接到数据库
        connection = DataBaseConnection.connect_to_database_test()
        cursor = connection.cursor()

        # 在控制台输出选中的.las文件名
        print(f'选中的.las文件名为：{file_name}')

        # 解析LAS文件，获取曲线信息
        las = lasio.read(file_path)
        curve_mnemonic = [] # 用来保存除去DEPT的所有曲线名
        for curve in las.curves:
            # print(curve.data)   # curve.data是某一个曲线的那一列数值
            curve_mnemonic.append(curve.mnemonic)
        curve_mnemonic.pop(0)   # 除去DEPT的新数组
        print(curve_mnemonic)   # 此时curve_mnemonic存储的是除去DEPT的所有曲线名
        try:
            # 向数据库中的well表，插入数据
            insert_well_query = """
                INSERT INTO well (WellName, CurveNumber, LayerLineNumber)
                VALUES (?, ?, 0)
            """

            # 使用占位符?，并传入参数以避免 SQL 注入攻击
            cursor.execute(insert_well_query, (file_name, len(curve_mnemonic)))
        except Exception as e:
            print(f'向well表中插入数据错误：{e}')
            print("向well表中插入数据错误：已经导入过相同的.las井数据文件")

        self.task_progress = 20
        progress_updated.emit(self.task_progress)

        # # 在Mysql数据库中创建一个新的表，并设置该表的表结构，表名为选中的.las文件名
        # create_table_query = f"""
        #             CREATE TABLE IF NOT EXISTS {file_name} (
        #                 id INT AUTO_INCREMENT PRIMARY KEY,
        #                 depth FLOAT,
        #             """

        # SQLite
        create_table_query = f"""
                            CREATE TABLE IF NOT EXISTS {file_name} (
                                id INTEGER PRIMARY KEY,
                                depth REAL,
                            """

        # print(curve_mnemonic)
        # print(len(curve_mnemonic))
        # # MySql
        # for curve in curve_mnemonic:
        #     create_table_query += f"{curve} FLOAT,"

        # SQLite
        for curve in curve_mnemonic:
            create_table_query += f"{curve} REAL,"

        # 调整create_table_query的语句格式，是他符合sql语法
        # 去掉create_table_query语句前后“,”，并在最后加上一个“)”
        create_table_query = create_table_query.rstrip(",") + ")"

        # 执行创建表结构的SQL语句
        cursor.execute(create_table_query)
        self.task_progress = 30
        progress_updated.emit(self.task_progress)
        # 插入数据
        insert_query = f"INSERT INTO {file_name} (depth, {', '.join([c for c in curve_mnemonic])}) VALUES (?, {'?,' * len(curve_mnemonic)})"
        insert_query = insert_query.strip(',)') + ')'   # 最终处理语句，后面还需要传数据给占位符
        # print(insert_query)

        # 构建数据列表，并保留指定的精度
        self.depth_data = las["DEPT"].data     # las["DEPT"].data：名为DEPT的曲线字段的的数据
        new_data = []

        step = 30/len(self.depth_data)
        # for i in range(50):     # 调试：前五十行的数据
        for i in range(len(self.depth_data)):
            new_row = []
            for curve in las.curves:
                new_row.append(numpy.nan_to_num(curve.data[i], nan=-99999.000, posinf=np.nan))

            new_data.append(new_row)
            self.task_progress += step
            progress_updated.emit(self.task_progress)

        # 执行插入语句
        cursor.executemany(insert_query, new_data)

        # 提交事务
        connection.commit()

        # 关闭游标和连接
        cursor.close()
        connection.close()

        self.task_progress = 100
        progress_updated.emit(self.task_progress)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GetData()
    window.show()
    sys.exit(app.exec_())
