import sys
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QFrame, QHBoxLayout
from qfluentwidgets import SplitFluentWindow, CardWidget, SearchLineEdit, StrongBodyLabel, LineEdit, PrimaryPushButton
from qfluentwidgets import FluentIcon as FIF

import Globals
from Function import DataBaseConnection

class AddWellLayerLineMainWindow(SplitFluentWindow):
    def __init__(self, layerName, depth):
        super().__init__()
        self.setupUi(layerName, depth)

    def setupUi(self, layerName, depth):
        self.setGeometry(250,150,300,150)
        self.setFixedSize(300,160)
        self.addWellLayerLineInterface = AddWellLayerLine(layerName, depth,'AddWellLayerLine Interface', self)
        self.navigationInterface.hide()
        self.addSubInterface(self.addWellLayerLineInterface, FIF.ADD, '添加分层')

        self.addWellLayerLineInterface.closeButton.clicked.connect(self.close)
        self.addWellLayerLineInterface.okButton.clicked.connect(self.addWellLayerLineInterface.import_theLayer_to_dataBase)


class AddWellLayerLine(CardWidget):
    def __init__(self, layerName, depth, text: str, parent=None):
        super().__init__(parent=parent)
        self.initUi(layerName, depth)
        self.setObjectName(text.replace(' ', '-'))

    def initUi(self, layerName, depth):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(11, 40, 11, 11)
        self.setLayout(main_layout)
        # 分层名称
        self.Frame_layerName = QFrame(self)
        self.layout_layerName = QHBoxLayout()
        self.layout_layerName.setContentsMargins(0, 0, 0, 0)
        self.label_layerName = StrongBodyLabel('分层名称', self)
        self.lineEdit_layerName = LineEdit(self)
        self.lineEdit_layerName.setText(f'{layerName}')
        self.lineEdit_layerName.setClearButtonEnabled(True)
        self.layout_layerName.addWidget(self.label_layerName)
        self.layout_layerName.addWidget(self.lineEdit_layerName)
        self.Frame_layerName.setLayout(self.layout_layerName)
        # 深度
        self.Frame_depth = QFrame(self)
        self.layout_depth = QHBoxLayout()
        self.layout_depth.setContentsMargins(0,0,0,0)
        self.label_depth = StrongBodyLabel('深度(米) ', self)
        self.lineEdit_depth = LineEdit(self)
        self.lineEdit_depth.setText(f'{depth}')
        self.lineEdit_depth.setClearButtonEnabled(True)
        self.layout_depth.addWidget(self.label_depth)
        self.layout_depth.addWidget(self.lineEdit_depth)
        self.Frame_depth.setLayout(self.layout_depth)
        # 按钮
        self.Frame_button = QFrame(self)
        self.layout_button = QHBoxLayout()
        self.layout_button.setContentsMargins(0, 5, 0, 0)
        self.okButton = PrimaryPushButton('确定', self)
        self.okButton.setToolTip("确定")
        self.closeButton = PrimaryPushButton('关闭', self)
        self.closeButton.setToolTip("关闭窗口")
        self.layout_button.addStretch()
        self.layout_button.addWidget(self.okButton)
        self.layout_button.addStretch()
        self.layout_button.addWidget(self.closeButton)
        self.layout_button.addStretch()
        self.Frame_button.setLayout(self.layout_button)
        # 将分层名称框架 和深度框架加入到窗口主布局中
        main_layout.addWidget(self.Frame_layerName)
        main_layout.addWidget(self.Frame_depth)
        main_layout.addWidget(self.Frame_button)

    def import_theLayer_to_dataBase(self):
        def connect_to_database():
            connection = DataBaseConnection.connect_to_database_test()
            cursor = connection.cursor()
            return connection, cursor

        def get_well_id(well_name, cursor):
            print(well_name.upper())
            cursor.execute("SELECT WellID FROM well WHERE WellName = ?", (well_name.upper(),))
            row_wellid = cursor.fetchone()
            print(f'row_wellid:{row_wellid}')
            return row_wellid[0] if row_wellid is not None else None

        def insert_layer_data(layer_name, depth, well_id, cursor, connection):
            try:
                # cursor.execute("START TRANSACTION")
                sql_insert = "INSERT INTO layerlines (LayerLineName, Depth, WellID) VALUES (?, ?, ?)"
                values_insert = (layer_name, depth, well_id)
                cursor.execute(sql_insert, values_insert)

                sql_update = "UPDATE well SET LayerLineNumber = LayerLineNumber + 1 WHERE WellID = ?"
                values_update = (well_id,)
                cursor.execute(sql_update, values_update)

                connection.commit()
            except Exception as e:
                print(f'插入分层线数据错误:{e}')
                connection.rollback()

        try:
            # 连接数据库
            connection, cursor = connect_to_database()

            # 获取输入框输入的数据
            layerName = self.lineEdit_layerName.text()
            depth = self.lineEdit_depth.text()
            print(f"layerName: {layerName}")
            print(f"depth: {depth}")

            # 从数据库的well表中查询当前打开井对应的WellID
            # well_id = get_well_id(Globals.theOpenedWellName, cursor)
            well_id = get_well_id(Globals.theOpenedWellName, cursor)

            # 在数据库的layerlines表中插入分层数据
            # 在数据库well表中，将LayerLineNumber的值加1
            if well_id is not None:
                # 插入分层数据并更新 LayerLineNumber
                insert_layer_data(layerName, depth, well_id, cursor, connection)
                print('数据插入成功')
            else:
                print("没有找到匹配的WellID")


            Globals.Sign_WhetherAddLayerIsOk=True
            # Globals.ExSign_addLayeredLine = False

        except Exception as e:
            print(e)

        finally:
            # 关闭链接
            cursor.close()
            connection.close()



if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    # Curve_window = Curve("Curve Interface")
    # Curve_window.show()
    addWellLayerLine_window = AddWellLayerLineMainWindow('001', 1800)
    addWellLayerLine_window.show()

    # openWell_window1 = OpenWell()
    # openWell_window1.show()

    sys.exit(app.exec_())