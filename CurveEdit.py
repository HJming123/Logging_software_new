import sys
from PyQt5.QtCore import Qt, QAbstractTableModel, QItemSelectionModel, QItemSelection, QSize
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QApplication, QFrame, QHBoxLayout, QTableWidgetItem, QCompleter, \
    QGroupBox, QHeaderView, QTableView, QAbstractItemView, QInputDialog, QLineEdit
from qfluentwidgets import CardWidget, MSFluentWindow, FluentWindow, SplashScreen, TableWidget, PrimaryPushButton, \
    SearchLineEdit, StrongBodyLabel, TransparentToolButton, TableView, ScrollArea, TransparentPushButton, \
    TransparentDropDownPushButton, RoundMenu, CommandBar, setFont, CommandBarView
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets.window.fluent_window import FluentWindowBase, SplitFluentWindow, MSFluentTitleBar
from  qfluentwidgets import Action
from ui import curve
import pyqtgraph as pg
import numpy as np
import Globals
import Curve
from ui import openWell

from Function import DataBaseConnection, CurveFunction, CurveEditFunction

class CurveEditTableMainWindow(SplitFluentWindow):
    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        self.setGeometry(300, 50, 750, 700)
        self.setFixedSize(750, 700)
        self.curveEditInterface = CurveEdit('CurveEdit Interface', self)
        self.navigationInterface.hide()
        self.addSubInterface(self.curveEditInterface, FIF.ADD, '曲线编辑')


class CurveEdit(CardWidget):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.curveName = Globals.theTrackName   # 选择的曲线名
        self.editHistory = []  # 记录编辑历史的列表
        self.rowsToDB = []
        print(self.curveName)

        # 创建数据库链接
        connection = DataBaseConnection.connect_to_database_test()
        cursor = connection.cursor()
        # 曲线数值
        self.curve_data = np.squeeze(np.array(CurveEditFunction.get_theChooseCurveData(cursor, self.curveName)))
        # 这个是用来绘制曲线的曲线值列表
        self.curve_data_plot = np.where(self.curve_data == -99999.000, np.nan, self.curve_data)
        # 测深
        self.depth = np.squeeze(np.array(CurveEditFunction.getDepth(cursor)))
        # 序号
        self.numbers = [num for num in range(1, len(self.depth)+1)]
        # 关闭
        cursor.close()
        connection.close()

        # 保存最近点的索引
        self.nearest_idx = None

        # 保存模型方便后续使用
        self.model = None

        # 设置ObjectName
        self.setObjectName(text.replace(' ', '-'))

        # 初始化
        self.intiUi()

        # 创建一个curve对象
        self.curve = Curve.Curve('curve a')


    def intiUi(self):
        # self.resize(561, 567)
        # 窗口主布局
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(11, 40, 11, 11)
        self.setLayout(main_layout)

        curveTableGroupBox = QGroupBox('曲线数据表格', self)
        curveTableGroupBox.setGeometry(0, 0, 375, 700)
        curvePlotGroupBox = QGroupBox('曲线预览', self)
        curvePlotGroupBox.setGeometry(375, 0, 375, 700)
        main_layout.addWidget(curveTableGroupBox)
        main_layout.addWidget(curvePlotGroupBox)

        # curveTableGroupBox_layout = QVBoxLayout(curveTableGroupBox)
        # curvePlotGroupBox_layout = QHBoxLayout(curvePlotGroupBox)

        # 左边表格
        # 表格命令栏
        self.commandBar = CommandBarView(curveTableGroupBox)
        self.setBackgroundColor(QColor(255, 255, 255))
        # self.commandBar.sizeHint()
        self.commandBar.addAction(Action(FIF.SAVE, '保存(Ctrl+S)', shortcut='Ctrl+S'))
        self.commandBar.addAction(Action(QIcon("images/withdraw.png"), '撤回(Ctrl+Z)', shortcut='Ctrl+Z'))
        self.commandBar.addAction(Action(QIcon("images/scroll-top.png"), '滚动到顶层'))
        self.commandBar.addAction(Action(QIcon("images/scroll-bottom.png"), '滚动到底层'))
        # self.commandBar.addAction(Action())
        # self.commandBar.addAction(Action())
        # self.commandBar.addAction(Action())
        # self.commandBar.addAction(Action())
        # self.applyButton
        # self.commandBar.addAction(Action(QIcon("images/apply_red.png"), '应用'))
        actions = self.commandBar.actions()
        self.saveButton = actions[0]
        self.withdrawButton = actions[1]
        self.scrollToTopButton = actions[2]
        self.scrollToBottomButton = actions[3]
        self.applyButton = TransparentToolButton(QIcon('images/apply_red.png'))
        self.applyButton.setToolTip('应用')
        # self.commandBar.resizeToSuitableWidth()
        self.commandBar.setIconSize(QSize(14, 14))
        self.commandBar.hBoxLayout.insertWidget(5, self.applyButton, Qt.AlignRight)
        self.commandBar.hBoxLayout.setSizeConstraint(2)
        self.commandBar.hBoxLayout.insertSpacing(5, 30)

        # self.commandBar.
        self.commandBar.setGeometry(0, 20, 361, 1)
        print(f"self.commandBar.size():{self.commandBar.size()}")

        # 槽函数
        self.saveButton.triggered.connect(self.saveDataToDatabase)
        self.withdrawButton.triggered.connect(self.undoEdit)
        self.scrollToTopButton.triggered.connect(lambda :self.scroll_to_top(curveTable))
        self.scrollToBottomButton.triggered.connect(lambda :self.scroll_to_bottom(curveTable))
        self.applyButton.clicked.connect(self.applyDataToTrackPlot)

        # 创建一个滚动区域，并将curveTable小部件设置为其小部件
        scrollArea = ScrollArea(curveTableGroupBox)
        scrollArea.setWidgetResizable(True)  # 允许小部件随滚动区域调整大小
        scrollArea.setGeometry(0, 66, 375, 580)  # 根据需要调整几何属性

        # 表格数据展示区
        curveTable = QTableView(curveTableGroupBox)
        curveTable.setWordWrap(False)    # ??????????
        curveTable.verticalHeader().hide()  # 隐藏垂直标题栏
        curveTable.setSortingEnabled(False) # 不允许排序
        curveTable.setGeometry(0, 20, 370, 580)
        curveTable.setSelectionBehavior(QTableView.SelectRows)  # 将表格设置为，选中直接选中一整行
        curveTable.setSortingEnabled(True)  # 点击表头可以进行排序
        # 将表格小部件设置为滚动区域的小部件
        scrollArea.setWidget(curveTable)

        # 曲线道顶层
        curvePlotTop = CurveTrackTop(curvePlotGroupBox)
        curvePlotTop.setParent(curvePlotGroupBox)
        curvePlotTop.setGeometry(0, 20, 361, 71)
        curvePlotTop.findChild(StrongBodyLabel, 'curveName').setText(self.curveName)

        # 曲线道
        curvePlot = pg.PlotWidget(curvePlotGroupBox)
        # curvePlotGroupBox_layout.addWidget(curvePlot)
        curvePlot.setParent(curvePlotGroupBox)
        curvePlot.setGeometry(0, 71+20, 375, 563)
        curvePlot.setStyleSheet("border: 1px solid rgb(180, 180, 180)")
        curvePlot.setBackground('w')    # 设置背景颜色
        curvePlot.getPlotItem().setMouseEnabled(x=False, y=True)    # 只允许上下鼠标拖动，不允许左右鼠标拖动
        curvePlot.invertY(True) # 逆置纵坐标，从上到下：由小到大
        curvePlot.hideAxis("left")  # 隐藏y轴
        curvePlot.hideAxis("bottom")    # 隐藏x轴
        curvePlot.setLimits(yMin = -1000, yMax = 5000)

        # 填充表格
        self.loadDataToTable(curveTable)

        # 绘图
        self.loadDataToPlot(curvePlot, curvePlotTop)

        # 设置网格线
        self.addGridLines(curvePlot)
        # 添加水平线
        self.addHorizontalLine(curvePlot)
        # 添加垂直线
        self.addVerticalLine(curvePlotTop, curvePlot)

        # 创建一个透明的白色填充色
        transparent_white = pg.QtGui.QColor(255, 255, 255, 0)
        # 创建散点图对象并设置边框颜色为红色，填充色为透明的白色
        self.scatter = pg.ScatterPlotItem(size = 8, pen = pg.mkPen(color='r'), brush=transparent_white)
        self.scatter.setData([self.depth[0]], [self.curve_data_plot[0]])
        curvePlot.addItem(self.scatter)

        # 鼠标点击绘图区域，将表格滚动到当前scatter所在的深度
        curvePlot._proxy = pg.SignalProxy(curvePlot.scene().sigMouseClicked, rateLimit = 50, slot = lambda evt: self.mouseClicked(curveTable))

        # 实现 双击 表格视图编辑功能
        # curveTable.setEditTriggers(QTableView.DoubleClicked)
        curveTable.doubleClicked.connect(self.editTableItem)
        # self.model.dataChanged.connect(self.tableItemChanged)

        # 实现 点击 表格视图将scatter跳动到当前点击行的对应深度
        curveTable.clicked.connect(lambda index:self.moveScatterToDepth(curvePlot, curvePlotTop, index))  # 连接点击信号到槽函数

        # 表格数据更新的话，则图像也跟着更新
        self.model.dataChanged.connect(lambda topLeft, bottomRight, roles:self.tableDataChanged(curvePlot, curvePlotTop, topLeft, bottomRight, roles))

    # 实现 点击 表格视图将scatter跳动到当前点击行的对应深度
    def moveScatterToDepth(self, plotWidget, plotWidgetTop, index):
        if index.isValid():
            row = index.row()   # 获取行号

            depth_value = self.model.data(self.model.index(row, 1), Qt.DisplayRole) # 获取这一行的测深值
            curve_data = self.model.data(self.model.index(row, 2), Qt.DisplayRole)  # 获取这一行的曲线值
            if curve_data == -99999.000:    # 如果曲线值为-99999.000则将它视为nan
                curve_data = np.nan

            # 设置scatter的位置
            if depth_value is not None and curve_data is not None:
                depth_value = float(depth_value)
                curve_data = float(curve_data)
                self.scatter.setData([curve_data], [depth_value])

            # 设置垂直线的位置
            plotWidget.vLine.setPos(curve_data)

            # 设值水平线的位置
            if hasattr(plotWidget, 'hLine') and plotWidget.hLine is not None:
                plotWidget.hLine.setPos(depth_value)
            if hasattr(plotWidget, 'label') and plotWidget.label is not None:
                plotWidget.label.setText(f'Y: {depth_value:.3f}')
                plotWidget.label.setPos(1.5, depth_value)
            # 更新 curveNameLabel 的内容：曲线值的大小
            plotWidgetTop.findChild(StrongBodyLabel, 'curveName').setText(
                f'{self.curveName}: {curve_data:.6f}')

    # 保存操作
    def saveDataToDatabase(self):
        # 将撤回列表置空
        self.editHistory.clear()

    # 撤回操作
    def undoEdit(self):
        if self.editHistory:
            # 获取最后一次编辑的数据
            last_edit = self.editHistory.pop()
            row, col, old_value = last_edit
            # 更新数据模型
            self.model.setData(self.model.index(row, col), old_value, Qt.EditRole)
            # 由于撤回了，将需要导入数据库的行，给去掉
            thePopRow = self.rowsToDB.pop()

    # 滚动到顶部
    def scroll_to_top(self, curveTable):
        top_index = self.model.index(0, 0)
        curveTable.scrollTo(top_index)
        print('执行了滚动到顶部')

    # 滚动到底部
    def scroll_to_bottom(self, curveTable):
        last_row_index = self.model.index(self.model.rowCount() - 1, 0)
        curveTable.scrollTo(last_row_index)
        print('执行了滚动到底部')


    # 点击应用按钮后进行的操作
    def applyDataToTrackPlot(self):
        # 将修改后的数据导入到数据库中
        try:
            if self.rowsToDB:
                # 连接到数据库
                connection = DataBaseConnection.connect_to_database_test()
                cursor = connection.cursor()

                for rowToDB in self.rowsToDB:
                    # 构建 SQL 更新语句
                    sql_update = f"UPDATE {Globals.theOpenedWellName.lower()} SET {Globals.theTrackName} = ? WHERE id = {rowToDB[0]+1}"

                    # 执行sql语句
                    cursor.execute(sql_update, (rowToDB[1],))

                connection.commit()
                print('更新成功')

                # 将撤回列表置空
                self.editHistory.clear()
                # 将记录需要传到数据库的行这一列表置空
                self.rowsToDB.clear()
            else:
                pass
        except Exception as e:
            print(f"更新失败:{e}")
        finally:
            cursor.close()
            connection.close()

        # 重新绘制曲线
        try:
            # 建立数据库连接
            connection = DataBaseConnection.connect_to_database_test()
            cursor = connection.cursor()

            cursor.execute(f"SELECT {Globals.theTrackName} FROM {Globals.theOpenedWellName.lower()}")
            # 获取曲线值数据
            curveData = np.squeeze(np.array(cursor.fetchall()))
            filtered_curve_data = np.where(curveData == -99999.00, np.nan, curveData)

            cursor.close()
            connection.close()

            for child_widget in Globals.theTrack[1].children():
                if isinstance(child_widget, pg.PlotWidget):
                    child_widget.removeItem(child_widget.plotCurve)
                    # 重新画图
                    child_widget.plotCurve = child_widget.plot(filtered_curve_data, self.depth, pen=pg.mkPen('k',width=1)) # 绘图

                    # 重新设置曲道顶部
                    # 真实的最大值和最小值-->>曲线值
                    curve_data_min = np.nanmin(filtered_curve_data) if not np.isnan(
                        np.nanmin(filtered_curve_data)) else 0
                    curve_data_max = np.nanmax(filtered_curve_data) if not np.isnan(
                        np.nanmax(filtered_curve_data)) else 1

                    # floor(最小值)和ceil(最大值)-->>曲线值
                    curve_data_min_floor = np.floor(curve_data_min)
                    curve_data_max_ceil = np.ceil(curve_data_max)

                    depth_min = np.floor(np.min(self.depth))
                    depth_max = np.ceil(np.max(self.depth))

                    theXRangeGroupBox = Globals.theTrack[0].findChild(QGroupBox, 'theXRangeGroupBox')
                    theXRangeGroupBox.theXMin_label.setText(f"{curve_data_min_floor}")
                    theXRangeGroupBox.theXMax_label.setText(f"{curve_data_max_ceil}")
                    if curve_data_max_ceil - curve_data_min_floor <= 2:
                        child_widget.setXRange(curve_data_min, curve_data_max)
                        child_widget.setYRange(depth_min, depth_max)
                    else:
                        child_widget.setXRange(curve_data_min_floor, curve_data_max_ceil)
                        child_widget.setYRange(depth_min, depth_max)
                    # 重新添加分层线
                    Curve.Curve.loadLayerLine(self)
            print('重新绘制曲线成功')
        except Exception as e:
            print(f'重新绘制曲线失败：{e}')
        # finally:
        #     cursor.close()
        #     connection.close()

    # 编辑表格功能
    def editTableItem(self, index):
        if index.isValid() and index.column() == 2:
            self.row = index.row()
            self.col = index.column()
            # 获取点击的单元格数据
            data = self.model.data(index, Qt.DisplayRole)
            old_data = data  # 记录旧数据
            # 弹出对话框或者其他方式进行数据修改
            new_data, ok = QInputDialog.getText(self, '修改数据', f'修改数据为:', QLineEdit.Normal, data)
            if ok:
                # 将修改后的数据设置回模型
                if new_data == -99999.000 or new_data == '':    # 如果修改后的曲线值为-99999.000，或者为空
                    new_data = -99999.000
                    self.model.setData(index, new_data, Qt.EditRole)
                    # 记录编辑历史
                    self.editHistory.append((self.row, self.col, old_data))
                    # 记录所改变的行，以及他的新数据---->用来更新数据库
                    rowToDB = [self.row, new_data]
                    self.rowsToDB.append(rowToDB)
                else:
                    self.model.setData(index, new_data, Qt.EditRole)
                    # 记录编辑历史
                    self.editHistory.append((self.row, self.col, old_data))
                    # 记录所改变的行，以及他的新数据---->用来更新数据库
                    rowToDB = [self.row, new_data]
                    self.rowsToDB.append(rowToDB)


    def tableDataChanged(self, curvePlot, curvePlotTop, topLeft, bottomRight, roles):
        self.updatePlotData(curvePlot, curvePlotTop, topLeft, bottomRight, roles)

    # 更新绘图数据，并重新绘图
    def updatePlotData(self, curvePlot, curvePlotTop, topLeft, bottomRight, roles):
        # 从表格模型中获取数据
        data = self.model._data  # 假设模型中的数据结构与初始化时一致

        # 更新曲线绘图的数据
        curve_datas = np.array([float(row[2]) for row in data])  # 第三列是曲线数据
        filtered_curve_data = np.where(curve_datas == -99999.00, np.nan, curve_datas)
        depth = np.array([float(row[1]) for row in data])  # 第二列是深度数据

        curvePlot.removeItem(self.plot)  # 清除之前的绘图
        curvePlot.removeItem(self.scatter)
        self.plot = curvePlot.plot(filtered_curve_data, depth, pen=pg.mkPen(color=(135, 206, 250), width=1))  # 重新绘制曲线

        # 创建一个透明的白色填充色
        transparent_white = pg.QtGui.QColor(255, 255, 255, 0)
        # 创建散点图对象并设置边框颜色为红色，填充色为透明的白色
        self.scatter = pg.ScatterPlotItem(size=8, pen=pg.mkPen(color='r'), brush=transparent_white)
        self.scatter.setData([self.depth[0]], [filtered_curve_data[0]])
        curvePlot.addItem(self.scatter)

        # 真实的最大值和最小值-->>曲线值
        curve_data_min = np.nanmin(filtered_curve_data) if not np.isnan(np.nanmin(filtered_curve_data)) else 0
        curve_data_max = np.nanmax(filtered_curve_data) if not np.isnan(np.nanmax(filtered_curve_data)) else 1

        # floor(最小值)和ceil(最大值)-->>曲线值
        curve_data_min_floor = np.floor(curve_data_min)
        curve_data_max_ceil = np.ceil(curve_data_max)

        depth_min = np.floor(np.min(depth))
        depth_max = np.ceil(np.max(depth))
        self.theXMin_label.setText(f"{curve_data_min}")
        self.theXMax_label.setText(f"{curve_data_max}")
        if curve_data_max_ceil - curve_data_min_floor <= 2:
            print(f"曲线表格编辑：curve_data_min:{curve_data_min}")
            print(f"曲线表格编辑：curve_data_max:{curve_data_max}")
            curvePlot.setXRange(curve_data_min, curve_data_max)
            curvePlot.setYRange(depth_min, depth_max)
        else:
            curvePlot.setXRange(curve_data_min_floor, curve_data_max_ceil)
            curvePlot.setYRange(depth_min, depth_max)

        # 获取数据发生改变的行的索引
        if topLeft.isValid() and topLeft == bottomRight:
            # 获取发生改变的单个索引
            row = topLeft.row()

            print(f"row:{row}")
            # 这里的深度值和曲线值用来设置，水平线和垂直线以及scatter的位置
            depth_value = self.model.data(self.model.index(row, 1), Qt.DisplayRole)
            curve_value = self.model.data(self.model.index(row, 2), Qt.DisplayRole)
            if curve_value == -99999.000:
                curve_value = np.nan
            if depth_value is not None and curve_value is not None:
                depth_value = float(depth_value)
                curve_value = float(curve_value)

                # 设置垂直线的位置
                curvePlot.vLine.setPos(curve_value)
                # 设置水平线的位置
                if hasattr(curvePlot, 'hLine') and curvePlot.hLine is not None:
                    curvePlot.hLine.setPos(depth_value)
                if hasattr(curvePlot, 'label') and curvePlot.label is not None:
                    curvePlot.label.setText(f'Y: {depth_value:.3f}')
                    curvePlot.label.setPos(1.5, depth_value)
                # 更新 curveNameLabel 的内容：曲线值的大小
                curvePlotTop.findChild(StrongBodyLabel, 'curveName').setText(
                    f'{self.curveName}: {curve_value:.6f}')
                # 设置sactter的位置
                self.scatter.setData([curve_value], [depth_value])

    def mouseClicked(self, curveTable):
        model = curveTable.model()  # 获取mQTableView的模型对象
        if model:
            index = model.index(self.nearest_idx, 1)
            curveTable.scrollTo(index, QAbstractItemView.PositionAtTop)
            selectionModel = curveTable.selectionModel()  # 获取 QTableView 的选择模型对象

            # 并且将这一行设置为选中状态
            if index.isValid():
                topLeft = model.index(index.row(), 0)
                bottomRight = model.index(index.row(), model.columnCount() - 1)
                selection = QItemSelection(topLeft, bottomRight)
                selectionModel.clearSelection()
                selectionModel.select(selection, QItemSelectionModel.Select)

    # 加载数据道表格
    def loadDataToTable(self, curveTable):
        data = [[num, depth, curve] for num, depth, curve in zip(self.numbers, self.depth, self.curve_data)]
        print(type(data))

        # 创建模型
        self.model = CustomTableModel(data, 2, self)

        # 设置表头的格式，最后一列无限延伸
        curveTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        curveTable.horizontalHeader().setStretchLastSection(True)
        # 隐藏垂直表头
        curveTable.verticalHeader().setVisible(False)
        # 设置表格视图的模型
        curveTable.setModel(self.model)

    # 加载数据道绘图区域-->>进行绘图
    def loadDataToPlot(self, curvePlot, curvePlotTop):

        # 真实的最大值和最小值-->>曲线值
        curve_data_min = np.nanmin(self.curve_data_plot) if not np.isnan(np.nanmin(self.curve_data_plot)) else 0
        curve_data_max = np.nanmax(self.curve_data_plot) if not np.isnan(np.nanmax(self.curve_data_plot)) else 1

        # floor(最小值)和ceil(最大值)-->>曲线值
        curve_data_min_floor = np.floor(curve_data_min)
        curve_data_max_ceil = np.ceil(curve_data_max)

        depth_min = np.floor(np.min(self.depth))
        depth_max = np.ceil(np.max(self.depth))

        theXMinAndMax_label = self.fillTheXRangeGroupBox(curvePlotTop.findChild(QGroupBox, 'theXRangeGroupBox'))
        theXMinAndMax_label[0].setText(f"{curve_data_min_floor}")
        theXMinAndMax_label[1].setText(f"{curve_data_max_ceil}")

        self.plot = curvePlot.plot(self.curve_data_plot, self.depth, pen=pg.mkPen(color=(135, 206, 250), width=1))  # 绘图
        if curve_data_max - curve_data_min < 1:
            curvePlot.setXRange(curve_data_min, curve_data_max)
            curvePlot.setYRange(depth_min, depth_max)
        else:
            curvePlot.setXRange(curve_data_min_floor, curve_data_max_ceil)
            curvePlot.setYRange(depth_min, depth_max)


    # 设置curveTrackTop中显示x轴范围的GroupBox
    def fillTheXRangeGroupBox(self, theXRangeGroupBox):
        theXRangeGroupBox_layout = QHBoxLayout(theXRangeGroupBox)
        theXRangeGroupBox.setLayout(theXRangeGroupBox_layout)

        theXRange_line = QFrame(theXRangeGroupBox)
        theXRange_line.setFrameShape(QFrame.HLine)  # 设置为水平线
        theXRange_line.setFrameShadow(QFrame.Sunken)
        theXRange_line.setFixedWidth(200)  # 设置水平线的长度
        theXRange_line.setLineWidth(5)  # 设置水平线的粗细

        theXRange_line.setStyleSheet("background-color: black;")

        self.theXMin_label = StrongBodyLabel(theXRangeGroupBox)
        self.theXMin_label.setParent(theXRangeGroupBox)
        self.theXMax_label = StrongBodyLabel(theXRangeGroupBox)
        self.theXMax_label.setParent(theXRangeGroupBox)

        theXRangeGroupBox_layout.addStretch()
        theXRangeGroupBox_layout.addWidget(self.theXMin_label)
        theXRangeGroupBox_layout.addStretch()
        theXRangeGroupBox_layout.addWidget(theXRange_line)
        theXRangeGroupBox_layout.addStretch()
        theXRangeGroupBox_layout.addWidget(self.theXMax_label)
        theXRangeGroupBox_layout.addStretch()

        return self.theXMin_label, self.theXMax_label

    # 添加网格线
    def addGridLines(self, plotWidget):
        grid = pg.GridItem()
        plotWidget.addItem(grid)
        grid.setPen(pg.mkPen('k', width=0))

    # 添加十字线的垂直线
    def addVerticalLine(self, plotWidgetTop, plotWidget):
        plotWidget.vLine = pg.InfiniteLine(angle=90, movable=Globals.sign_LayerLineIsMovable)
        plotWidget.vLine.setPen(pg.mkPen(color='k', width=1))
        plotWidget.addItem(plotWidget.vLine, ignoreBounds=True)

        plotWidget.proxy = pg.SignalProxy(plotWidget.scene().sigMouseMoved, rateLimit=50,
                                          slot=lambda evt: self.mouseMoved(plotWidgetTop, plotWidget,
                                                                           evt))

    # 添加十字线的水平线
    def addHorizontalLine(self, plotWidget):
        plotWidget.hLine = pg.InfiniteLine(angle=0, movable=Globals.sign_LayerLineIsMovable)  # 水平线
        plotWidget.hLine.setPen(pg.mkPen(color='k', width=1))
        plotWidget.addItem(plotWidget.hLine, ignoreBounds=True)

        plotWidget.proxy = pg.SignalProxy(plotWidget.scene().sigMouseMoved, rateLimit=50,
                                          slot=lambda evt: self.mouseMoved_horizontal(plotWidget, evt))

    # 垂直方向和水平方向的鼠标移动
    def mouseMoved(self, plotWidgetTop, plotWidget, evt):
        pos = evt[0]  # 获取鼠标位置
        if plotWidget.sceneBoundingRect().contains(pos):
            mousePoint_x = plotWidget.plotItem.vb.mapSceneToView(pos)
            mousePoint_y = plotWidget.plotItem.vb.mapSceneToView(pos)

            x = mousePoint_x.x()
            y = mousePoint_x.y()

            # 设置垂直线的位置
            plotWidget.vLine.setPos(mousePoint_x.x())
            # 设值水平线的位置
            if hasattr(plotWidget, 'hLine') and plotWidget.hLine is not None:
                plotWidget.hLine.setPos(mousePoint_y.y())
            if hasattr(plotWidget, 'label') and plotWidget.label is not None:
                plotWidget.label.setText(f'Y: {mousePoint_y.y():.3f}')
                plotWidget.label.setPos(1.5, mousePoint_y.y())
            # 更新 curveNameLabel 的内容：曲线值的大小
            plotWidgetTop.findChild(StrongBodyLabel, 'curveName').setText(
                f'{self.curveName}: {mousePoint_x.x():.6f}')

            # 设置scatter的值
            distances_y = np.sqrt((np.array(self.plot.yData) - y) ** 2)
            min_distance_idx = np.argmin(distances_y)   # 获取索引
            if min_distance_idx != self.nearest_idx:
                nearest_x = self.plot.xData[min_distance_idx]
                nearest_y = self.plot.yData[min_distance_idx]
                if not np.isnan(nearest_x):
                    self.scatter.setData([nearest_x], [nearest_y])
                    self.nearest_idx = min_distance_idx

    # 水平方向的鼠标移动
    def mouseMoved_horizontal(self, plotWidget, evt):
        pos = evt[0]  # 获取鼠标位置
        if plotWidget.sceneBoundingRect().contains(pos):
            mousePoint_y = plotWidget.plotItem.vb.mapSceneToView(pos)

            if hasattr(plotWidget, 'hLine') and plotWidget.hLine is not None:
                plotWidget.hLine.setPos(mousePoint_y.y())
            if hasattr(plotWidget, 'label') and plotWidget.label is not None:
                plotWidget.label.setText(f'Y: {mousePoint_y.y():.3f}')
                plotWidget.label.setPos(1.5, mousePoint_y.y())


class CustomTableModel(QAbstractTableModel):
    def __init__(self, data, editableColumn, parent=None):
        super().__init__(parent)

        # 遍历每一行并将第二列和第三列的元素转换为浮点数，其他列的元素保持不变
        self._data = [[row[0]] + [float(row[i]) if i in [1, 2] else row[i] for i in range(1, len(row))] for row in data]

        # 可以被编辑的列为第editableColumn列
        self.editableColumn = editableColumn
        # print(type(self._data))

        # 设置表头
        self.header_labels = ['序号', '测深', '数值']  # 例子中的表头标签

    # 行数
    def rowCount(self, parent=None):
        return len(self._data)

    # 列数
    def columnCount(self, parent=None):
        return len(self._data[0])

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if role == Qt.DisplayRole:
            return str(self._data[row][col])  # 根据你的数据结构进行调整

        return None

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            row = index.row()
            col = index.column()
            if col == self.editableColumn:
                try:
                    self._data[row][col] = float(value)  # 将输入值转换为浮点数
                except ValueError:
                    return False  # 如果转换失败，返回 False

                self.dataChanged.emit(index, index, [Qt.EditRole])
                self.sort(0, Qt.AscendingOrder)  # 在数据修改后触发排序操作
                return True
        return False

    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()
        self._data.sort(key=lambda x: x[column], reverse=order == Qt.DescendingOrder)
        self.layoutChanged.emit()

    # 设置表头文字
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.header_labels[section]

        return super().headerData(section, orientation, role)


# 曲道的子部件
class TrackSubComponent(QMainWindow, curve.Ui_Frame):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

class CurveTrackTop(CardWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        # self.clicked = pyqtSignal(CardWidget)
        self.initUi()
        self.sign_theTitleNameIsChanged = False

    def initUi(self):
        curveSubComponent = TrackSubComponent()
        curveFrame_width = 375

        # 显示当前是哪个曲线的CardWidget
        self.curveTitleBar = curveSubComponent.findChild(CardWidget, 'curveTitleBar')
        self.curveTitleBar.resize(curveFrame_width, 71)
        self.curveNameGroupBox = curveSubComponent.findChild(QGroupBox, 'curveNameGroupBox')  # 显示曲线的标签所在的GroupBox
        # self.curveNameGroupBox.reszie(curveFrame_width, 31)
        self.theXRangeGroupBox = curveSubComponent.findChild(QGroupBox, 'theXRangeGroupBox')
        self.theXRangeGroupBox.resize(curveFrame_width, 40)
        self.curveNameGroupBox.setParent(self.curveTitleBar)
        self.theXRangeGroupBox.setParent(self.curveTitleBar)
        self.curveNameGroupBox.setGeometry(0, 0, curveFrame_width, 31)
        self.theXRangeGroupBox.setGeometry(0, 31, curveFrame_width, 40)

        self.setGeometry(0, 0, curveFrame_width, 31 + 71)
        self.curveTitleBar.setParent(self)
        self.curveTitleBar.setGeometry(0, 0, curveFrame_width, 71)



if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    # Curve_window = Curve("Curve Interface")
    # Curve_window.show()
    openWell_window = CurveEditTableMainWindow()
    openWell_window.show()

    # openWell_window1 = OpenWell()
    # openWell_window1.show()

    sys.exit(app.exec_())