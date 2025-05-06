import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QApplication, QFrame, QHBoxLayout, QTableWidgetItem, QCompleter
from qfluentwidgets import CardWidget, MSFluentWindow, FluentWindow, SplashScreen, TableWidget, PrimaryPushButton, \
    SearchLineEdit, ProgressBar
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets.window.fluent_window import FluentWindowBase, SplitFluentWindow

import Globals
from ui import openWell

from Function import DataBaseConnection

class OpenWellMainWindow(SplitFluentWindow):
    def __init__(self, openWellButton):
        super().__init__()
        self.openWellButton = openWellButton
        self.setupUi()

    def setupUi(self):
        self.setGeometry(300, 150, 450, 400)
        self.setFixedSize(450, 400)
        self.openWellInterface = OpenWell('OpenWell Interface', self)
        self.navigationInterface.hide()
        self.addSubInterface(self.openWellInterface, FIF.ADD, '井列表')
        # self.openWellInterface.closeButton.clicked.connect(self.close)  # 点击关闭按钮，关闭窗口
        self.openWellInterface.okButton.clicked.connect(self.openWellInterface.open_well_okbutton)  # 选中一行，打开所选中行对应的井
        self.openWellInterface.okButton.clicked.connect(self.close)     # 点击确认按钮，关闭窗口
        self.openWellInterface.wellTable.doubleClicked.connect(self.openWellInterface.open_well)  # 设置表格的双击触发的功能
        self.openWellInterface.wellTable.doubleClicked.connect(self.close)  # 双击井表格，关闭窗口
        self.openWellInterface.deleteButton.clicked.connect((self.openWellInterface.deletebutton_onClicked))    # 选中一行，删除一行对应的井

    def close(self):
        super().close()
        self.openWellButton.setEnabled(True)

class OpenWell(CardWidget):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(' ', '-'))
        self.intiUi()
        self.load_dataFromBaseToTable()
    def intiUi(self):
        self.resize(561, 567)
        # 窗口主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(11,35,11,11)
        self.setLayout(main_layout)

        # 创造一个OpenWellSubComponent对象，用来获取ui文件创建的对象
        openWellSubComponent = OpenWellSubComponent()

        # 搜索栏
        searchFrame = openWellSubComponent.findChild(QFrame, 'searchFrame')
        searchFrame.resize(500,43)
        self.searchLineEdit = openWellSubComponent.findChild(SearchLineEdit, 'searchLineEdit')
        self.searchLineEdit.setPlaceholderText('请输入井名')

        # 表格
        tableFrame = openWellSubComponent.findChild(QFrame, 'tableFrame')
        tableFrame_layout = QVBoxLayout(tableFrame) # 表格框架垂直布局
        tableFrame_layout.setContentsMargins(11, 0, 11, 0)
        self.wellTable = TableWidget(self)  # 创建表格
        self.wellTable.setBorderVisible(True)   # 设置边框是否可见
        self.wellTable.setBorderRadius(8)   # 设置边框为圆角
        self.wellTable.setWordWrap(False)
        self.wellTable.verticalHeader().hide()  # 隐藏垂直标题栏

        self.wellTable.setSortingEnabled(False)
        self.wellTable.resize(500, 420)

        # self.wellTable.doubleClicked.connect(self.open_well)    # 设置表格的双击触发的功能
        tableFrame_layout.addWidget(self.wellTable)
        tableFrame.setLayout(tableFrame_layout) # 设置表格框架布局为tableFrame_layout

        # 进度栏
        self.progressbar = ProgressBar()

        # 按钮
        buttonFrame = QFrame()
        buttonFrame_layout = QHBoxLayout(buttonFrame)
        buttonFrame_layout.setContentsMargins(11, 0, 11, 0)
        self.importWellButton = PrimaryPushButton('导入数据', self)
        self.okButton = PrimaryPushButton("确定", self)
        # self.closeButton = PrimaryPushButton("关闭", self)
        self.deleteButton = PrimaryPushButton('删除', self)
        buttonFrame_layout.addWidget(self.importWellButton)
        buttonFrame_layout.addStretch()
        buttonFrame_layout.addWidget(self.okButton)
        # buttonFrame_layout.addWidget(self.closeButton)
        buttonFrame_layout.addWidget(self.deleteButton)
        buttonFrame.setLayout(buttonFrame_layout)

        # 在窗口主布局中添加部件
        main_layout.addWidget(searchFrame)
        main_layout.addWidget(tableFrame)
        main_layout.addWidget(self.progressbar)
        main_layout.addWidget(buttonFrame)

    # 将well表中的数据在表格中展示出来
    def load_dataFromBaseToTable(self):
        stands_wellName = []

        connection = DataBaseConnection.connect_to_database_test()
        cursor = connection.cursor()

        cursor.execute(f"SELECT WellID, WellName, CurveNumber, LayerLineNumber FROM well")
        data = cursor.fetchall()
        # print(f"data: {data}")
        self.wellTable.setRowCount(0)
        self.wellTable.setColumnCount(4)
        self.wellTable.setHorizontalHeaderLabels(['序号', '井名', '曲线数', '分层数'])  # 给表格添加列，并设置列名
        for row_num, row_data in enumerate(data):
            self.wellTable.insertRow(row_num)
            row_data_list = list(row_data)
            row_data_list[0] = row_num+1
            stands_wellName.append(row_data_list[1])
            # print(f"row_data_list: {row_data_list}")
            for col_num, col_data in enumerate(row_data_list):
                item = QTableWidgetItem(str(col_data))
                self.wellTable.setItem(row_num, col_num, item)

        # print(stands_wellName)
        self.completer = QCompleter(stands_wellName, self.searchLineEdit)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setMaxVisibleItems(10)
        self.searchLineEdit.setCompleter(self.completer)

        cursor.close()
        connection.close()

    def getTheOpenedWellId(self, well_name):
        connection = DataBaseConnection.connect_to_database_test()
        cursor = connection.cursor()

        select_sql = f"SELECT WellID FROM well WHERE WellName = '{well_name}'"
        cursor.execute(select_sql)

        Globals.theOpenedWellId = cursor.fetchone()[0]
        print(f"Globals.theOpenedWellId:{Globals.theOpenedWellId}")

        cursor.close()
        connection.close()

    # 确认按钮执行
    def open_well_okbutton(self):
        select_row = self.wellTable.currentRow()
        if select_row != -1:
            print(select_row)
            well_name_item = self.wellTable.item(select_row, 1)

            well_name = well_name_item.text()

            Globals.theOpenedWellName = well_name.lower()
            print(Globals.theOpenedWellName)
            self.getTheOpenedWellId(well_name)

    # 双击执行
    def open_well(self, item):  # 获得打开的井名
        row = item.row()
        well_id_item = self.wellTable.item(row, 0)
        well_name_item = self.wellTable.item(row, 1)
        curve_num_item = self.wellTable.item(row, 2)
        layer_num_item = self.wellTable.item(row, 3)

        well_id = well_id_item.text()
        well_name = well_name_item.text()
        # 控制台输出所打开的井名
        print(f'Opening well: {well_name.lower()}')

        well_id_item.setFlags(well_id_item.flags() & ~Qt.ItemIsEditable)
        well_name_item.setFlags(well_name_item.flags() & ~Qt.ItemIsEditable)
        curve_num_item.setFlags(curve_num_item.flags() & ~Qt.ItemIsEditable)
        layer_num_item.setFlags(layer_num_item.flags() & ~Qt.ItemIsEditable)

        # 打开井之后设置
        Globals.theOpenedWellName = well_name.lower()
        self.getTheOpenedWellId(well_name)

    # 删除按钮执行的操作
    def deletebutton_onClicked(self):
        try:
            select_items = self.wellTable.selectedItems()
            wellsName_willBeDelete = []
            if select_items:
                select_rows = set(item.row() for item in select_items)
                for row in sorted(select_rows, reverse=True):
                    print(f"row: {row}")

                    wellName_willBeDelete_item = self.wellTable.item(row, 1)
                    if wellName_willBeDelete_item is not None:
                        wellName_willBeDelete = wellName_willBeDelete_item.text()
                        wellsName_willBeDelete.append(wellName_willBeDelete)
                    else:
                        # 处理空对象的情况，例如输出错误信息或者进行其他操作
                        print("Error: wellName_willBeDelete_item is None")

                    self.wellTable.removeRow(row)

            connection1 = DataBaseConnection.connect_to_database_test()
            cursor1 = connection1.cursor()

            # 删除数据库lyaerLines表中该井对应的分层线
            wellsId_willBeDelete = []
            for table in wellsName_willBeDelete:
                selectWellId_sql = f"SELECT WellID FROM well WHERE WellName = '{table}'"
                cursor1.execute(selectWellId_sql)
                wellsId_willBeDelete.extend(cursor1.fetchone())
                print(f"wellsId_willBeDelete:{wellsId_willBeDelete}")
            # 删除满足条件的行
            # delete_sql = f"DELETE FROM layerlines WHERE WellID IN {tuple(wellsId_willBeDelete)}"
            # cursor1.execute(delete_sql)

            delete_sql = f"DELETE FROM layerlines WHERE WellID IN ({', '.join(map(str, wellsId_willBeDelete))})"
            cursor1.execute(delete_sql)

            # 提交事务
            print('1')
            connection1.commit()

            # 删除well表中的相应井
            wells_to_delete = ",".join([f"'{name}'" for name in wellsName_willBeDelete])
            delete_query = f"DELETE FROM well WHERE WellName IN ({wells_to_delete})"

            cursor1.execute(delete_query)
            print('2')
            connection1.commit()

            

            # 删除数据库中井对应的表，如x12,x13
            # connection2 = DataBaseConnection.connect_to_database_test()
            # cursor2 = connection2.cursor()

            for table in wellsName_willBeDelete:
                delete_table_well_query = f"DROP TABLE IF EXISTS {table.lower()}"
                cursor1.execute(delete_table_well_query)

            print('3')
            connection1.commit()

            # cursor2.close()
            # connection2.close()


            # 关闭
            cursor1.close()
            connection1.close()

        except Exception as e:
            print(f"删除井失败：{e}")


        # select_row = self.wellTable.currentRow()
        # if select_row != -1:
        #     self.wellTable.removeRow(select_row)
        # else:
        #     print('没有行被选中')


class OpenWellSubComponent(QMainWindow, openWell.Ui_openWell):
    def __init__(self):
        super(OpenWellSubComponent, self).__init__()
        self.setupUi(self)
        # self.show()

if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    # Curve_window = Curve("Curve Interface")
    # Curve_window.show()
    openWell_window = OpenWellMainWindow()
    openWell_window.show()

    # openWell_window1 = OpenWell()
    # openWell_window1.show()

    sys.exit(app.exec_())