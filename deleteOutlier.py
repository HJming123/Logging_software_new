import sys

import numpy as np
from PyQt5.QtCore import Qt, QEvent, QRegularExpression, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QRegularExpressionValidator
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QFrame, QHBoxLayout, QMainWindow, QWidget
from qfluentwidgets import SplitFluentWindow, CardWidget, SearchLineEdit, StrongBodyLabel, LineEdit, PrimaryPushButton, \
    CaptionLabel, MSFluentTitleBar, InfoBarPosition, DoubleSpinBox, CompactDateTimeEdit, CompactDoubleSpinBox
from qfluentwidgets import FluentIcon as FIF

import pyqtgraph as pg

import Globals

from Function import DataBaseConnection, InformationShow, CurveFunction
from ui import deleteOutlier

class CustomTitleBar(MSFluentTitleBar):     # 设置标题栏的UI
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        pass
        theTrackNameLabel = StrongBodyLabel()
        theTrackNameLabel.setText(f"{Globals.theTrackName}曲线")
        # self.setWindowTitle(theTrackNameLabel)
        self.hBoxLayout.insertWidget(0, theTrackNameLabel, Qt.AlignLeft)
        self.hBoxLayout.insertSpacing(10, 30)

class DeleteOutlierMainWindow(SplitFluentWindow):
    def __init__(self, LTop, RBottom):
        super().__init__()
        self.setupUi(LTop, RBottom)

    def setupUi(self, LTop, RBottom):
        self.setGeometry(250,150,300,150)
        self.setFixedSize(400, 415)
        self.deleteOutlierInterface = DeleteOutlier(LTop, RBottom, 'AddWellLayerLine Interface', self)
        self.navigationInterface.hide()
        self.addSubInterface(self.deleteOutlierInterface, FIF.ADD, '剔除异常值')
        self.setTitleBar(CustomTitleBar(self))

        self.deleteOutlierInterface.closeButton.clicked.connect(self.close)


    def close(self):
        super().close()
        for child_widget in Globals.theTrack[1].children():
            if isinstance(child_widget, pg.PlotWidget):
                child_widget.removeItem(Globals.rectItem)
                print('已经移出了矩形块')

class DeleteOutlier(CardWidget):
    def __init__(self, LTop, RBottom, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(' ', '-'))

        self.initUi(LTop, RBottom)
        self.getTheMinAndMax_startAndEnd()

    def initUi(self, LTop, RBottom):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(11, 40, 11, 11)
        self.setLayout(main_layout)

        subComponent = SubComponent()

        deleteOutlierWidget = subComponent.deleteOutlierWidget
        Globals.deleteOutlierWidget = deleteOutlierWidget
        deleteOutlierWidget.setParent(self)

        main_layout.addWidget(deleteOutlierWidget)

        # theTrackNameLabel = subComponent.theTrackNameLabel
        # theTrackNameLabel.setText(f'{Globals.theTrackName}')

        groupBox_L = subComponent.groupBox_L
        groupBox_R = subComponent.groupBox_R

        # self.xLineEdit_L = CustomLineEdit('x_L', groupBox_L)
        # self.yLineEdit_L = CustomLineEdit('y_L', groupBox_L)
        # self.xLineEdit_L.setText(format(LTop.x(), '.7f'))
        # self.yLineEdit_L.setText(format(LTop.y(), '.3f'))
        # self.xLineEdit_L.setGeometry(40, 30, 105, 33)
        # self.yLineEdit_L.setGeometry(40, 80, 105, 33)
        # self.xLineEdit_R = CustomLineEdit('x_R', groupBox_R)
        # self.yLineEdit_R = CustomLineEdit('y_R', groupBox_R)
        # self.xLineEdit_R.setText(format(RBottom.x(), '.7f'))
        # self.yLineEdit_R.setText(format(RBottom.y(), '.3f'))
        # self.xLineEdit_R.setGeometry(40, 30, 105, 33)
        # self.yLineEdit_R.setGeometry(40, 80, 105, 33)
        curve_data = np.squeeze(np.array(CurveFunction.get_theChooseAction_CurveData(Globals.theTrackName)))
        filtered_curve_data = np.where(curve_data == -99999.000, np.nan, curve_data)
        # 真实的最大值和最小值-->>曲线值
        curve_data_min = np.nanmin(filtered_curve_data) if not np.isnan(np.nanmin(filtered_curve_data)) else 0
        curve_data_max = np.nanmax(filtered_curve_data) if not np.isnan(np.nanmax(filtered_curve_data)) else 1
        # floor(最小值)和ceil(最大值)-->>曲线值
        curve_data_min_floor = np.floor(curve_data_min)
        curve_data_max_ceil = np.ceil(curve_data_max)
        # 创建输入框：起始点坐标、释放点坐标
        self.xLineEdit_L = CompactDoubleSpinBox(groupBox_L)
        self.yLineEdit_L = CompactDoubleSpinBox(groupBox_L)
        self.xLineEdit_R = CompactDoubleSpinBox(groupBox_R)
        self.yLineEdit_R = CompactDoubleSpinBox(groupBox_R)
        # 设置最大最小值范围
        self.xLineEdit_L.setRange(-99999.000, 99999.000)
        self.yLineEdit_L.setRange(-99999.000, 99999.000)
        self.xLineEdit_R.setRange(-99999.000, 99999.000)
        self.yLineEdit_R.setRange(-99999.000, 99999.000)
        # 设置位置、大小
        self.xLineEdit_L.setGeometry(40, 30, 105, 33)
        self.yLineEdit_L.setGeometry(40, 80, 105, 33)
        self.xLineEdit_R.setGeometry(40, 30, 105, 33)
        self.yLineEdit_R.setGeometry(40, 80, 105, 33)
        # 设值小数点后的位数
        self.yLineEdit_L.setDecimals(3)
        self.yLineEdit_R.setDecimals(3)
        if curve_data_max_ceil - curve_data_min_floor <= 2:
            self.xLineEdit_L.setDecimals(6)
            self.xLineEdit_R.setDecimals(6)
            self.xLineEdit_L.setSingleStep(0.000001)
            self.xLineEdit_R.setSingleStep(0.000001)
        else:
            self.xLineEdit_L.setDecimals(3)
            self.xLineEdit_R.setDecimals(3)
            # self.xLineEdit_L.setSingleStep(1)
            # self.xLineEdit_R.setSingleStep(1)
        # 设置默认值
        self.xLineEdit_L.setValue(LTop.x())
        self.yLineEdit_L.setValue(LTop.y())
        self.xLineEdit_R.setValue(RBottom.x())
        self.yLineEdit_R.setValue(RBottom.y())

        # 设置坐标输入框的textChange槽函数连接
        self.xLineEdit_L.textChanged.connect(self.adjustRectItem_pos)
        self.yLineEdit_L.textChanged.connect(self.adjustRectItem_pos)
        self.xLineEdit_R.textChanged.connect(self.adjustRectItem_Size)
        self.yLineEdit_R.textChanged.connect(self.adjustRectItem_Size)

        # 曲线保存名称输入框
        self.saveNameLineEdit = CustomLineEdit('saveName', deleteOutlierWidget)
        self.saveNameLineEdit.setGeometry(87, 240, 201, 33)
        self.saveNameLineEdit.setPlaceholderText('请输入保存曲线名称')
        # 创建正则表达式验证器
        regex = QRegularExpression(r'^[a-zA-Z][a-zA-Z0-9_]{0,63}$')
        validator = QRegularExpressionValidator(regex)
        self.saveNameLineEdit.setValidator(validator)

        self.xmistake_L = subComponent.xmistake_L
        self.ymistake_L = subComponent.ymistake_L
        self.xmistake_R = subComponent.xmistake_R
        self.ymistake_R = subComponent.ymistake_R
        self.mistake3 = subComponent.mistake3
        self.mistakeOkButton = subComponent.mistakeOkButton
        self.xmistake_L.setStyleSheet('font-size: 10px; color: red;')
        self.ymistake_L.setStyleSheet('font-size: 10px; color: red;')
        self.xmistake_R.setStyleSheet('font-size: 10px; color: red;')
        self.ymistake_R.setStyleSheet('font-size: 10px; color: red;')
        self.mistake3.setStyleSheet('font-size: 10px; color: red;')
        self.mistakeOkButton.setStyleSheet('font-size: 10px; color: red;')
        self.xmistake_L.setText('')
        self.ymistake_L.setText('')
        self.xmistake_R.setText('')
        self.ymistake_R.setText('')
        self.mistake3.setText('')
        self.mistakeOkButton.setText('')


        Globals.xmistake_L = self.xmistake_L
        Globals.ymistake_L = self.ymistake_L
        Globals.xmistake_R = self.xmistake_R
        Globals.ymistake_R = self.ymistake_R
        Globals.mistake3 = self.mistake3

        self.okButton = subComponent.okButton
        self.okButton.clicked.connect(self.okButton_clicked)
        self.closeButton = subComponent.closeButton
        self.progressBar = subComponent.ProgressBar

    def adjustRectItem_pos(self):
        try:
            newXPos = float(self.xLineEdit_L.text().strip())
            newYPos = float(self.yLineEdit_L.text().strip())
            print(f"新坐标:({newXPos},{newYPos})")
            Globals.rectItem.setPos([newXPos, newYPos])
            self.adjustRectItem_Size()
        except Exception:
            pass

    def adjustRectItem_Size(self):
        newWidth = float(self.xLineEdit_R.text().strip()) - float(self.xLineEdit_L.text().strip())
        newHeight = float(self.yLineEdit_R.text().strip()) - float(self.yLineEdit_L.text().strip())
        print(f"当前矩形框大小:[{newWidth},{newHeight}]")
        Globals.rectItem.setSize([newWidth, newHeight])

    def getTheMinAndMax_startAndEnd(self):
        self.depth_min = None
        self.depth_max = None
        self.curve_min = None
        self.curve_max = None


        depth_L = float(self.yLineEdit_L.text().strip())
        depth_R = float(self.yLineEdit_R.text().strip())

        curve_L = float(self.xLineEdit_L.text().strip())
        curve_R = float(self.xLineEdit_R.text().strip())

        if depth_L < depth_R:
            self.depth_min = depth_L
            self.depth_max = depth_R
        else:
            self.depth_min = depth_R
            self.depth_max = depth_L

        if curve_L < curve_R:
            self.curve_min = curve_L
            self.curve_max = curve_R
        else:
            self.curve_min = curve_R
            self.curve_max = curve_L

    def mousePressEvent(self, event):
        self.xLineEdit_L.clearFocus()
        self.yLineEdit_L.clearFocus()
        self.xLineEdit_R.clearFocus()
        self.yLineEdit_R.clearFocus()
        self.saveNameLineEdit.clearFocus()

    class DataImportThread(QThread):
        progress_updated = pyqtSignal(float)
        infor_signal = pyqtSignal(bool)
        def __init__(self, superior):
            super().__init__()
            self.superior = superior
            self.depth_min = superior.depth_min
            self.depth_max = superior.depth_max
            self.curve_min = superior.curve_min
            self.curve_max = superior.curve_max
            # 曲线名称
            self.saveName = superior.saveName
            # self.result_list = superior.result_list
            self.waittingInfor = superior.waittingInfor

        def run(self):
            self.task_progress = 0

            connection = DataBaseConnection.connect_to_database_test()
            try:
                cursor = connection.cursor()
                try:
                    print('1')
                    # # 开始事务
                    # cursor.execute('START TRANSACTION')
                    print('2')
                    # # 在表格中添加新列
                    cursor.execute(f"ALTER TABLE {Globals.theOpenedWellName} ADD COLUMN {self.saveName} FLOAT")
                    # sql = "ALTER TABLE ? ADD COLUMN ? FLOAT"
                    print(f"self.saveName:{self.saveName}")
                    # cursor.execute(sql, (Globals.theOpenedWellName, self.saveName))
                    # cursor.execute(f"ALTER TABLE x12 ADD COLUMN {self.outputName} FLOAT")
                    self.task_progress = 10
                    self.progress_updated.emit(self.task_progress)
                    print('3')
                    connection.commit()
                    print('成功向表中插入新列')

                    # 将well表中的CurveNumber + 1
                    sql_update_well = "UPDATE well SET CurveNumber = CurveNumber + 1 WHERE WellID = ?"
                    values_update = (Globals.theOpenedWellId,)
                    cursor.execute(sql_update_well, values_update)
                    self.task_progress = 15
                    self.progress_updated.emit(self.task_progress)
                    connection.commit()
                    print('曲线数量+1')

                    # 查询符合条件的行id
                    cursor.execute(
                        f"SELECT id FROM {Globals.theOpenedWellName} WHERE depth >= {self.depth_min} AND depth <= {self.depth_max}")
                    id_depth_start_list = cursor.fetchall()
                    print(f"id_depth_start_list:{id_depth_start_list}")
                    self.task_progress = 20
                    self.progress_updated.emit(self.task_progress)
                    id_depth_list = []
                    for id_tuple in id_depth_start_list:
                        id_depth_list.append(id_tuple[0])

                    id_depth_set = set(id_depth_list)

                    cursor.execute(
                        f"SELECT id FROM {Globals.theOpenedWellName} WHERE {Globals.theTrackName} >= {self.curve_min} AND {Globals.theTrackName} <= {self.curve_max}")
                    id_curve_start_list = cursor.fetchall()
                    print(f"id_curve_start_list:{id_curve_start_list}")
                    self.task_progress = 25
                    self.progress_updated.emit(self.task_progress)
                    id_curve_list = []
                    for id_tuple in id_curve_start_list:
                        id_curve_list.append(id_tuple[0])

                    id_curve_set = set(id_curve_list)

                    id_set = id_depth_set.intersection(id_curve_set)
                    print(f"id_set:{id_set}")
                    id_list = list(id_set)
                    print(f"id_list:{id_list}")

                    # 获取所选中的曲线的所有值
                    cursor.execute(f"SELECT {Globals.theTrackName} FROM {Globals.theOpenedWellName}")
                    curve_start_list = cursor.fetchall()
                    self.task_progress = 30
                    self.progress_updated.emit(self.task_progress)
                    curve_list = []
                    for curve_tuple in curve_start_list:
                        curve_list.append(curve_tuple[0])
                    # 将原曲线将要删除的部分，更换为-99999.000
                    for id in id_list:
                        curve_list[id - 1] = -99999.000

                    step_len = 70 / len(curve_list)

                    # 更新新列的数据，将Null更新为计算后得到的数据
                    for idx, curve_data in enumerate(curve_list, start=1):
                        self.task_progress += step_len
                        cursor.execute(
                            f"UPDATE {Globals.theOpenedWellName} SET {self.saveName} = ? WHERE id = ?",
                            (curve_data, idx))  # 使用 id 来更新每行数据
                        self.progress_updated.emit(self.task_progress)
                    connection.commit()
                    print("成功向新列中插入数据")
                    self.infor_signal.emit(True)
                    for child_widget in Globals.theTrack[1].children():
                        if isinstance(child_widget, pg.PlotWidget):
                            child_widget.removeItem(Globals.rectItem)
                            print('已经移出了矩形块')

                except Exception as e:
                    # 回滚事务
                    connection.rollback()
                    self.infor_signal.emit(False)
                    print(f'添加计算得到的新曲线失败：{e}')
                finally:
                    cursor.close()
            finally:
                connection.close()

    def okButton_clicked(self):
        try:
            sign1 = False
            sign2 = False
            sign3 = False
            sign4 = False
            sign5 = False

            self.saveName = self.saveNameLineEdit.text()

            xLineEdit_L_input = self.xLineEdit_L.text().strip()
            if xLineEdit_L_input == '':
                self.xmistake_L.setText("必填项！")
            else:
                try:
                    float_value = float(xLineEdit_L_input)
                    self.xmistake_L.setText('')
                    sign1 = True
                except Exception as e:
                    self.xmistake_L.setText("请输入有效值！")

            yLineEdit_L_input = self.yLineEdit_L.text().strip()
            if yLineEdit_L_input == '':
                self.ymistake_L.setText("必填项！")
            else:
                try:
                    float_value = float(yLineEdit_L_input)
                    self.ymistake_L.setText('')
                    sign2 = True
                except Exception as e:
                    self.ymistake_L.setText("请输入有效值！")

            xLineEdit_R_input = self.xLineEdit_R.text().strip()
            if xLineEdit_R_input == '':
                self.xmistake_R.setText("必填项！")
            else:
                try:
                    float_value = float(xLineEdit_R_input)
                    self.xmistake_R.setText('')
                    sign3 = True
                except Exception as e:
                    self.xmistake_R.setText("请输入有效值！")

            yLineEdit_R_input = self.yLineEdit_R.text().strip()
            if yLineEdit_R_input == '':
                self.ymistake_R.setText("必填项！")
            else:
                try:
                    float_value = float(yLineEdit_R_input)
                    self.ymistake_R.setText('')
                    sign4 = True
                except Exception as e:
                    self.ymistake_R.setText("请输入有效值！")

            if self.saveName == '':
                self.mistakeOkButton.setText('请核实你的输入')
                self.mistake3.setText('必填项！')
            else:
                sign5 = True

            if sign1 and sign2 and sign3 and sign4 and sign5:
                self.mistakeOkButton.setText('')
                # 信息提示-->>正在导入新曲线
                self.waittingInfor = InformationShow.showInformation_Waitting(self, f"正在添加{self.saveName}曲线", InfoBarPosition.TOP_LEFT)
                # 创建子线程(数据导入)
                self.dataImportThread = self.DataImportThread(self)
                self.dataImportThread.progress_updated.connect(self.setProgressBarValue)
                self.dataImportThread.infor_signal.connect(self.control_inforShow)
                self.dataImportThread.start()
        except Exception as e:
            pass

    # 更新进度栏
    def setProgressBarValue(self, taskprogress):
        self.progressBar.setValue(int(taskprogress))

    # 提示信息-->>用来显示是否完成新曲线的导入
    def control_inforShow(self, sign_IsCurveCalculateImport):
        self.waittingInfor.close()
        if sign_IsCurveCalculateImport:
            InformationShow.showInformation_Success(self, f'成功添加{self.saveName}曲线',InfoBarPosition.TOP_LEFT)
        else:
            InformationShow.showInformation_Error(self, f'添加{self.saveName}失败', InfoBarPosition.TOP_LEFT)

class SubComponent(QMainWindow, deleteOutlier.Ui_deleteOutlier):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

class CustomLineEdit(LineEdit):
    def __init__(self, text, parent = None):
        super().__init__(parent)
        self.sign = text

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        input_text = self.text().strip()
        if self.sign == 'x_L':
            if input_text == '':
                Globals.xmistake_L.setText('必填项！')
            else:
                try:
                    float_value = float(input_text)
                    Globals.xmistake_L.setText('')
                except Exception as e:
                    Globals.xmistake_L.setText('请输入有效值！')
        elif self.sign == 'y_L':
            if input_text == '':
                Globals.ymistake_L.setText('必填项！')
            else:
                try:
                    float_value = float(input_text)
                    Globals.ymistake_L.setText('')
                except Exception as e:
                    Globals.ymistake_L.setText('请输入有效值！')
        elif self.sign == 'x_R':
            if input_text == '':
                Globals.xmistake_R.setText('必填项！')
            else:
                try:
                    float_value = float(input_text)
                    Globals.xmistake_R.setText('')
                except Exception as e:
                    Globals.xmistake_R.setText('请输入有效值！')
        elif self.sign == 'y_R':
            if input_text == '':
                Globals.ymistake_R.setText('必填项！')
            else:
                try:
                    float_value = float(input_text)
                    Globals.ymistake_R.setText('')
                except Exception as e:
                    Globals.ymistake_R.setText('请输入有效值！')
        else:
            if self.sign == 'saveName':
                self.inforWidget.close()
                if input_text == '':
                    Globals.mistake3.setText('必填项！')
                else:
                    Globals.sign_isDuplicationOfName = False
                    Globals.sign_isCompliance = False
                    curves_name = self.getCurvesName()
                    for curve_name in curves_name:
                        if input_text == curve_name:
                            Globals.sign_isDuplicationOfName = True
                            break
                    if Globals.sign_isDuplicationOfName:
                        Globals.mistake3.setText('曲线名字已存在！')
                    else:
                        Globals.mistake3.setText('')

    def focusInEvent(self, event):
        super().focusInEvent(event)  # 调用父类的focusInEvent方法

        def createInfoInfoBar(parent):
            self.inforWidget = QWidget(parent)
            self.inforWidget.setStyleSheet("border-radius: 10px;")
            self.inforWidget.setContentsMargins(11, 11, 11, 11)
            # self.inforWidget.setEnabled(False)
            # self.inforWidget.setBackgroundColor(QColor(0, 0, 0))
            self.inforLayout = QVBoxLayout()
            self.inforWidget.setLayout(self.inforLayout)
            self.inforLabel = CaptionLabel("可以使用字母、数字和下划线\n不能以数字开头\n不能包含空格或其他特殊字符", self.inforWidget)
            self.inforLabel.setContentsMargins(11, 11, 11, 11)
            self.inforLayout.addWidget(self.inforLabel)
            self.inforLabel.setStyleSheet("background-color: black; color: white;")
            # self.inforWidget.setGeometry(245, 418, 210, 100)
            self.inforWidget.setGeometry(180, 160, 210, 100)
            self.inforWidget.show()
            font = QFont("Arial Rounded MT", 8)
            self.inforLabel.setFont(font)

        if self.sign == 'saveName':
            createInfoInfoBar(Globals.deleteOutlierWidget)

    def getCurvesName(self):
        connection = DataBaseConnection.connect_to_database_test()
        try:
            cursor = connection.cursor()
            try:
                curves_name = []
                cursor.execute(f"PRAGMA table_info({Globals.theOpenedWellName})")
                columns = cursor.fetchall()
                print(f'columns:{columns}')
                headers = [column[1] for column in columns]

                for header in headers:
                    if header != 'id' and header != 'depth':
                        curves_name.append(header)

                print(f"curves_name:{curves_name}")

                return curves_name
            except Exception as e:
                print(f'出错了：{e}')
            finally:
                cursor.close()
        finally:
            connection.close()
        # try:
        #     with DataBaseConnection.connect_to_database_test() as connection:
        #         with connection.cursor() as cursor:
        #             curves_name = []
        #             cursor.execute(f"PRAGMA table_info({Globals.theOpenedWellName})")
        #             columns = cursor.fetchall()
        #             print(f'columns:{columns}')
        #             headers = [column[1] for column in columns]
        #
        #             for header in headers:
        #                 if header != 'id' and header != 'depth':
        #                     curves_name.append(header)
        #
        #             print(f"curves_name:{curves_name}")
        #
        #             return curves_name
        # except Exception as e:
        #     print(f'曲线计算——获得曲线名错误:{e}')

if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    # Curve_window = Curve("Curve Interface")
    # Curve_window.show()
    addWellLayerLine_window = DeleteOutlierMainWindow('001', 1800)
    addWellLayerLine_window.show()

    # openWell_window1 = OpenWell()
    # openWell_window1.show()

    sys.exit(app.exec_())