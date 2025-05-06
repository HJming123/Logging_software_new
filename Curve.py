from PyQt5.QtGui import QCursor, QPixmap, QPainter, QLinearGradient, QBrush, QColor
from PyQt5.QtWidgets import QFrame, QWidget, QPushButton, QVBoxLayout, QScrollArea, QGroupBox, QHBoxLayout, QSplitter, \
    QMenu, QAction
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QFrame
from qfluentwidgets import ScrollArea, CardWidget, TransparentPushButton, TransparentToolButton, StrongBodyLabel
from PyQt5.QtCore import Qt, QPoint, QTimer, QRectF, pyqtSignal
import pyqtgraph as pg
import numpy as np

from deleteOutlier import DeleteOutlierMainWindow
from ui import curve
from qfluentwidgets import FluentIcon as FIF
import Globals
from AddWellLayerLine import AddWellLayerLineMainWindow
from CustomInfiniteLine import CustomLayeredLine, CustomTextItem
from Function import DataBaseConnection
import Cursor

class Curve(pg.GraphicsLayoutWidget):   # 定义了一个自定义的小部件类 Widget，继承自 QFrame。用于显示界面中的一些基本信息，如应用程序名称、图标等。

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(' ', '-'))
        self.setBackground('w')
        self.scroll_content_bottom = None
        self.setupUi()

    def returnScroll_content_bottom(self):
        return self.scroll_content_bottom

    def setupUi(self):
        self.resize(1000,1000)
        self.setBackground((249, 249, 249))
        # 为曲线道设置宽
        self.curveFrame_width = 200

        # 为深度道设置宽
        self.depthFrame_width = 100

        # 为曲道设置高
        self.frame_height = 1000

        # 设置曲道之间的间距
        self.frame_margin = 0

        # 下一个框架的 x 坐标
        self.next_x_position = 0

        # 给主窗口设置一个垂直布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50,30,50,30)
        self.setLayout(main_layout)

        # 添加滚动区域
        self.scroll_area = ScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll_area)
        self.scroll_content = QWidget(self.scroll_area)
        self.scroll_content.setObjectName("scroll_content")
        self.scroll_area.setWidget(self.scroll_content)
        # 设置滚动区域的样式
        self.scroll_area.setStyleSheet("""
            ScrollArea{
                    background-color: rgb(249,249,249);
                    border-radius: 10px;
                    border: 1px solid rgb(234, 234, 234)
                }
                """)
        self.scroll_content.setStyleSheet("""
            #scroll_content{
                background-color: rgb(249,249,249);
                border-radius: 10px;
                border: 1px solid rgb(234, 234, 234)
                }
        """)

        # 创建上半部分
        self.scroll_content_top = QWidget(self.scroll_content)
        self.scroll_content_top.setGeometry(0,0,0,0)  # 设置起始位置和起始大小

        # 创建下半部分
        self.scroll_content_bottom_outer = QWidget(self.scroll_content)
        self.scroll_content_bottom_outer.setObjectName('scroll_content_bottom_outer')
        self.scroll_content_bottom_outer.setGeometry(0,102,0,0) # 设置起始位置和起始大小
        self.scroll_content_bottom_outer_layout = QVBoxLayout(self.scroll_content_bottom_outer)
        self.scroll_content_bottom_outer_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_content_bottom = pg.PlotWidget(self.scroll_content_bottom_outer)    # 创建plotWidget_outer
        self.scroll_content_bottom.setObjectName("scroll_content_bottom")
        self.scroll_content_bottom.getPlotItem().setMouseEnabled(x=False, y=True)
        # self.
        self.scroll_content_bottom.invertY(True)
        self.scroll_content_bottom.hideAxis('bottom')
        self.scroll_content_bottom.hideAxis('left')

        self.scroll_content_bottom_outer_layout.addWidget(self.scroll_content_bottom)

        # # 添加测试用的按钮：曲线道、深度道、分层
        # self.curveButton = QPushButton('曲线道', self)
        # self.curveButton.clicked.connect(self.addCurveTrack)
        # self.curveButton.setGeometry(0, 0, 50, 30)
        #
        # self.depthButton = QPushButton('深度道', self)
        # self.depthButton.clicked.connect(self.addDepthTrack)
        # self.depthButton.setGeometry(0, 35, 50, 30)
        #
        # self.layeredButton = QPushButton('分层', self)
        # self.layeredButton.clicked.connect(self.addLayerLine)
        # self.layeredButton.setGeometry(0, 70, 50, 30)

        # 用于后续方便的一些工具
        self.frame_num = 0  # 用来统计当前曲线道和深度道的总数量，
        # self.track = []
        self.tracks = []    # 创建一个数组用来存储曲线道和深度道对象
        self.curveTrackTops = []    # 创建一个数组用来存储创建的
        self.layerLines_outer = []  # 外层列表，里面需要包含列表

    # 添加分层线
    def addLayerLine(self):
        print('点击了添加分层线按钮')
        Globals.sign_addLayeredLine = not Globals.sign_addLayeredLine   # 切换添加分层模式
        Globals.sign_deleteLayerLine = False    # 当点击添加分层按钮后，将删除分层线标志设为False
        Globals.sign_isClickedOutlierEliminator = False

    # 删除分层线
    def deleteLayerLine(self):
        print('点击了删除分层线的按钮')
        Globals.sign_deleteLayerLine = not Globals.sign_deleteLayerLine  # 切换删除分层模式
        Globals.sign_addLayeredLine = False     # 当点击删除分层按钮后，将添加分层按钮标志设为False
        Globals.sign_isClickedOutlierEliminator = False


    # 加载分层线
    def loadLayerLine(self):
        try:
            print('开始执行加载分层操作')
            connection = DataBaseConnection.connect_to_database_test()
            cursor = connection.cursor()

            cursor.execute(f"SELECT LayerLineName, Depth FROM layerlines WHERE WellID = {Globals.theOpenedWellId};")
            layerLines_list = cursor.fetchall()
            for layer in layerLines_list:
                layerName = layer[0]    # 分层线名称
                layerDepth = layer[1]   # 分层线深度
                # 遍历所有的曲道
                for track in Globals.tracks:
                    for child_widget in track[1].children():
                        if isinstance(child_widget, pg.PlotWidget):
                            # 创造一个分层线
                            layerLine = CustomLayeredLine(pos=layerDepth, angle=0,
                                                        movable=Globals.sign_LayerLineIsMovable)
                            layerLine.setPen(pg.mkPen('r', width=5))
                            child_widget.addItem(layerLine)
                            # 如果为深度道
                            if not child_widget.sign_curveOrdepth:
                                # 创建一个分层名标签
                                child_widget.layerNameLabel = CustomTextItem(text=layerName, color=(255, 0, 0),
                                                                          anchor=(0.5, 1))
                                child_widget.layerNameLabel.setFont(pg.QtGui.QFont('Arial', 12))
                                child_widget.addItem(child_widget.layerNameLabel)
                                if hasattr(child_widget,
                                           'layerNameLabel') and child_widget.layerNameLabel is not None:
                                    child_widget.layerNameLabel.setPos(1.5, layerDepth)
                                    # 向分层线列表中添加分层线对象和分层线名称标签
                                    layerLine = [layerLine, child_widget.layerNameLabel]
                                    Globals.layerLines.append(layerLine)
                            else:
                                layerLine= [layerLine, None]
                                Globals.layerLines.append(layerLine)

        except Exception as e:
            print(f"加载分层线出错：{e}")

    # 添加深度道
    def addDepthTrack(self):
        print('点击了添加深度道按钮')
        self.frame_num += 1

        depthSubComponent = TrackSubComponent()
        # 创建深度道的top部分
        depthTrackTop = depthSubComponent.depthTrackTop
        depthTrackTop.setParent(self.scroll_content_top)
        depthTrackTop.setGeometry(self.next_x_position, 0, self.depthFrame_width, 31+71)

        # 含有关闭按钮的顶层工具栏
        depthToolBar = depthTrackTop.findChild(CardWidget, 'depthToolBar')
        depthToolBar.resize(self.depthFrame_width, 31)
        # 创建关闭按钮的样式，并将关闭按钮添加到顶层工具栏的布局里边
        closeDepthButton = TransparentToolButton('images/close.png', depthTrackTop)
        depthToolBar_layout = QHBoxLayout()
        depthToolBar_layout.addStretch()
        depthToolBar_layout.addWidget(closeDepthButton)
        depthToolBar.setLayout(depthToolBar_layout)

        #将关闭按钮连接到关闭曲线道这一函数上
        closeDepthButton.clicked.connect(lambda : self.closeDepthTrack(depthtrack, depthTrackTop, depthContent))

        # 显示深度道名称的CardWidget
        depthTrackTop.findChild(CardWidget, 'depthTitleBar').resize(self.depthFrame_width, 71)

        # 显示深度尺子的区域
        depthContent = depthSubComponent.depthContent
        depthContent.setParent(self.scroll_content_bottom)
        depthContent_layout = QVBoxLayout(depthContent)
        depthContent_layout.setContentsMargins(0, 0, 0, 0)
        plotWidget = CustomPlotWidget(False, depthContent)
        plotWidget.setStyleSheet("border: 1px solid rgb(180, 180, 180)")
        plotWidget.setBackground('w')
        plotWidget.getPlotItem().setMouseEnabled(x=False, y=True)
        plotWidget.setYLink(self.scroll_content_bottom)
        plotWidget.invertY(True)
        plotWidget.hideAxis('bottom')   # 隐藏x轴
        plotWidget.hideAxis('left')
        plotWidget.showGrid(x=False, y=True)
        plotWidget.setXRange(0, 3)
        plotWidget.setYRange(Globals.depth_min, Globals.depth_max)
        plotWidget.setLimits(yMin=-10000, yMax=10000)
        self.addGridLines(plotWidget)
        self.addHorizontalLine(plotWidget)
        self.addLabelToDepthTrack(plotWidget)

        depthContent.setGeometry(self.next_x_position, 0, self.depthFrame_width, self.frame_height-31-71)
        depthContent_layout.addWidget(plotWidget)

        depthtrack = [depthTrackTop, depthContent]

        self.tracks.append(depthtrack)
        Globals.tracks.append(depthtrack)
        self.next_x_position += self.depthFrame_width

        depthTrackTop.show()
        depthContent.show()

        self.adjust_scroll_area()
        self.adjust_scroll_content_top()
        self.adjust_scroll_content_bottom()

        self.loadLayerLine()

    # 添加曲线道
    def addCurveTrack(self):
        try:
            self.frame_num += 1 # 当添加曲线道的时候，将曲道总数目+1

            curveSubComponent = TrackSubComponent()
            curveTrackTop = CurveTrackTop(self.next_x_position, self.curveFrame_width)
            curveTrackTop.setParent(self.scroll_content_top)
            curveTrackTop.closeCurveButton.clicked.connect(lambda :self.closeCurveTrack(curvetrack, curveTrackTop, curveContent))
            # 绘制曲线图的区域
            curveContent = curveSubComponent.curveContent
            curveContent.setObjectName('curveContent')
            curveContent.setParent(self.scroll_content_bottom)

            curveContent_layout = QVBoxLayout(curveContent)
            curveContent_layout.setContentsMargins(0, 0, 0, 0)
            plotWidget = CustomPlotWidget(True, curveContent)     # 创建自定义的PlotWidget的对象
            plotWidget.setParent(curveContent)
            plotWidget.setStyleSheet("border: 1px solid rgb(180, 180, 180)")
            plotWidget.setBackground('w')
            plotWidget.getPlotItem().setMouseEnabled(x=False, y=True)
            # curveContent.setYRange(0,10)
            plotWidget.setYLink(self.scroll_content_bottom)
            plotWidget.invertY(True)
            plotWidget.hideAxis('left')     # 隐藏y轴
            plotWidget.hideAxis('bottom')   # 隐藏x轴
            self.addGridLines(plotWidget)   # 设置网格线
            self.addHorizontalLine(plotWidget)
            plotWidget.setYRange(Globals.depth_min, Globals.depth_max)
            plotWidget.setLimits(yMin = -10000, yMax = 10000)
            # self.addCrossLine(plotWidget)
            self.scroll_content_bottom_outer_width = self.curveFrame_width
            # curveContent.setGeometry(self.next_x_position, 0, self.scroll_content_bottom_outer_width, self.frame_height-31-71)
            curveContent.setGeometry(self.next_x_position, 0, self.scroll_content_bottom_outer_width, self.frame_height-31-71)
            curveContent_layout.addWidget(plotWidget)

            curvetrack = [curveTrackTop, curveContent]  # 创建含有curveTrackTop和curveContent两个部对象元素的曲线道数组

            self.tracks.append(curvetrack)  # 向数组中添加曲线道对象
            Globals.tracks.append(curvetrack)
            self.curveTrackTops.append(curveTrackTop)   # 像数组中添加曲线道顶部
            self.next_x_position += self.curveFrame_width  # 更新下一个框架的 x 坐标

            curveTrackTop.show()
            curveContent.show()

            self.adjust_scroll_area()
            self.adjust_scroll_content_top()
            self.adjust_scroll_content_bottom()

            self.loadLayerLine()

        except Exception as e:
            print(e)

    # 设置curveTrackTop中显示x轴范围的GroupBox
    def fillTheXRangeGroupBox(self, theXRangeGroupBox):
        theXRangeGroupBox.theXMin_label = StrongBodyLabel(theXRangeGroupBox)
        theXRangeGroupBox.theXMin_label.setParent(theXRangeGroupBox)
        theXRangeGroupBox.theXMax_label = StrongBodyLabel(theXRangeGroupBox)
        theXRangeGroupBox.theXMax_label.setParent(theXRangeGroupBox)
        if not theXRangeGroupBox.sign_isFilled:
            theXRangeGroupBox_layout = QHBoxLayout(theXRangeGroupBox)
            theXRangeGroupBox.setLayout(theXRangeGroupBox_layout)

            theXRange_line = QFrame(theXRangeGroupBox)
            theXRange_line.setFrameShape(QFrame.HLine)  # 设置为水平线
            theXRange_line.setFrameShadow(QFrame.Sunken)
            theXRange_line.setFixedWidth(100)   # 设置水平线的长度
            theXRange_line.setLineWidth(5)  # 设置水平线的粗细

            theXRange_line.setStyleSheet("background-color: black;")

            # 测试布局效果
            # theXMax_label.setText('300')
            # theXMin_label.setText('100')

            theXRangeGroupBox_layout.addStretch()
            theXRangeGroupBox_layout.addWidget(theXRangeGroupBox.theXMin_label)
            theXRangeGroupBox_layout.addStretch()
            theXRangeGroupBox_layout.addWidget(theXRange_line)
            theXRangeGroupBox_layout.addStretch()
            theXRangeGroupBox_layout.addWidget(theXRangeGroupBox.theXMax_label)
            theXRangeGroupBox_layout.addStretch()

            theXRangeGroupBox.sign_isFilled = True
            return theXRangeGroupBox.theXMin_label, theXRangeGroupBox.theXMax_label
        # else:
        #     return theXRangeGroupBox.theXMin_label, theXRangeGroupBox.theXMax_label

    # 设置曲道的深度范围
    def setTrackYRange(self):
        connection = DataBaseConnection.connect_to_database_test()
        cursor = connection.cursor()

        cursor.execute(f'SELECT depth FROM {Globals.theOpenedWellName.lower()}')
        # cursor.execute(f'SELECT depth FROM x12')

        depth = np.squeeze(np.array(cursor.fetchall()))
        # print(f'depth:{depth}')
        depth_min = np.floor(np.min(depth))
        depth_max = np.ceil(np.max(depth))
        zero_list= [0]*len(depth)

        for track in self.tracks:
            for child_widget in track[1].children():
                if isinstance(child_widget, pg.PlotWidget):
                    child_widget.plot(zero_list, depth, pen=(255, 255, 255, 0))
                    child_widget.setYRange(depth_max, depth_min)

    # 添加十字线的垂直线
    def addVerticalLine(self, plotWidget, action_title, curveTrack):
        plotWidget.vLine = pg.InfiniteLine(angle=90, movable=Globals.sign_LayerLineIsMovable)
        plotWidget.vLine.setPen(pg.mkPen(color='b', width=1))
        plotWidget.addItem(plotWidget.vLine, ignoreBounds=True)

        plotWidget.proxy = pg.SignalProxy(plotWidget.scene().sigMouseMoved, rateLimit=50,
                                          slot=lambda evt: self.mouseMoved(plotWidget, action_title, curveTrack, evt))

    # 添加十字线的水平线
    def addHorizontalLine(self, plotWidget):
        plotWidget.hLine = pg.InfiniteLine(angle=0, movable=Globals.sign_LayerLineIsMovable)  # 水平线
        plotWidget.hLine.setPen(pg.mkPen(color='b', width=1))
        plotWidget.addItem(plotWidget.hLine, ignoreBounds=True)

        plotWidget.proxy = pg.SignalProxy(plotWidget.scene().sigMouseMoved, rateLimit=50,
                                          slot=lambda evt: self.mouseMoved_horizontal(plotWidget, evt))

    # 向深度道中添加标签，该标签用于显示当前深度
    def addLabelToDepthTrack(self, plotWidget):
        plotWidget.label = pg.TextItem(text='', color=(0, 0, 0), anchor=(0.5, 1))
        plotWidget.addItem(plotWidget.label)
        plotWidget.proxy = pg.SignalProxy(plotWidget.scene().sigMouseMoved, rateLimit=50,
                                          slot=lambda evt: self.mouseMoved_horizontal(plotWidget, evt))

    # 垂直方向和水平方向的鼠标移动
    def mouseMoved(self, plotWidget, action_title, curveTrack1, evt):
        pos = evt[0]  # 获取鼠标位置
        if plotWidget.sceneBoundingRect().contains(pos):
            mousePoint_x = plotWidget.plotItem.vb.mapSceneToView(pos)
            mousePoint_y = self.scroll_content_bottom.plotItem.vb.mapSceneToView(pos)
            # 设置垂直线的位置
            plotWidget.vLine.setPos(mousePoint_x.x())
            # 设值水平线的位置
            for curveTrack in self.tracks:
                for child_widget in curveTrack[1].children():
                    if isinstance(child_widget, pg.PlotWidget):
                        if hasattr(child_widget, 'hLine') and child_widget.hLine is not None:
                            child_widget.hLine.setPos(mousePoint_y.y())
                        if hasattr(child_widget, 'label') and child_widget.label is not None:
                            child_widget.label.setText(f'Y: {mousePoint_y.y():.3f}')
                            child_widget.label.setPos(1.5, mousePoint_y.y())
            # 更新 curveNameLabel 的内容：曲线值的大小
            curveTrack1[0].findChild(StrongBodyLabel, 'curveName').setText(f'{action_title}: {mousePoint_x.x():.6f}')
            # 矩形框
            if Globals.sign_isClickedOutlierEliminator:
                if plotWidget.sign_isPressed:
                    currentPos = mousePoint_x
                    currentWidth = currentPos.x() - plotWidget.startPos.x()
                    currentHeight = currentPos.y() - plotWidget.startPos.y()
                    plotWidget.rectItem.setSize([currentWidth, currentHeight])

    # 水平方向的鼠标移动
    def mouseMoved_horizontal(self, plotWidget, evt):
        pos = evt[0]  # 获取鼠标位置
        if plotWidget.sceneBoundingRect().contains(pos):
            mousePoint_y = self.scroll_content_bottom.plotItem.vb.mapSceneToView(pos)
            for curveTrack in self.tracks:
                for child_widget in curveTrack[1].children():
                    if isinstance(child_widget, pg.PlotWidget):
                        if hasattr(child_widget, 'hLine') and child_widget.hLine is not None:
                            child_widget.hLine.setPos(mousePoint_y.y())
                        if hasattr(child_widget, 'label') and child_widget.label is not None:
                            child_widget.label.setText(f'Y: {mousePoint_y.y():.3f}')
                            child_widget.label.setPos(1.5, mousePoint_y.y())

    # 添加网格线
    def addGridLines(self, plotWidget):
        grid = pg.GridItem()
        plotWidget.addItem(grid)
        grid.setPen(pg.mkPen('k', width=0))
        # grid.getAxis("bottom").setStyle(showValues=False)

    # 调整top区域大小
    def adjust_scroll_content_top(self):
        self.scroll_content_top_width = self.next_x_position + self.frame_margin
        self.scroll_content_top.setMinimumSize(self.scroll_content_top_width, 31+71)
        self.scroll_content_top.setGeometry(0, 0, self.scroll_content_top_width, 31+71)

    # 调整bottom区域大小
    def adjust_scroll_content_bottom(self):
        self.scroll_content_bottom_outer_width = self.next_x_position + self.frame_margin
        self.scroll_content_bottom_outer.setMinimumSize(self.scroll_content_bottom_outer_width, self.frame_height-31-71)
        self.scroll_content_bottom_outer.setGeometry(0, 31+71, self.scroll_content_bottom_outer_width, self.frame_height-31-71)

    # 调整滚动区域的大小
    def adjust_scroll_area(self):
        content_width = self.next_x_position + self.frame_margin
        self.scroll_content.setMinimumSize(content_width, self.frame_height)
        self.scroll_content.setGeometry(0, 0, content_width, self.frame_height)

    # 关闭深度道
    def closeDepthTrack(self, depthtrack, depthTrackTop, depthContent):
        try:
            depthTrackTop.deleteLater() # 销毁depthTrack
            depthContent.deleteLater()
            self.tracks.remove(depthtrack)  # 从列表中移出被关闭的深度轨道
            Globals.tracks.remove(depthtrack)

            # 计算被关闭的曲线轨道的宽度，用于后续的重新布局
            closed_track_width = self.depthFrame_width + self.frame_margin

            # 重新布局后面的曲线轨道
            current_x_position = 0 # 从初始位置开始重新布局
            for track in self.tracks:
                if track != depthtrack:
                    sign_curveOrdepth = False   # 默认为深度道
                    for child_widget in track[1].children():
                        if isinstance(child_widget, pg.PlotWidget):
                           sign_curveOrdepth = child_widget.sign_curveOrdepth
                    if sign_curveOrdepth:   # 说明是曲线道
                        track[0].setGeometry(current_x_position, 0, self.curveFrame_width, 31+71)
                        track[1].setGeometry(current_x_position, 0, self.curveFrame_width, self.frame_height-31-71)
                        current_x_position += self.curveFrame_width # 更新x坐标
                    else:   # 说明是深度道
                        track[0].setGeometry(current_x_position, 0, self.depthFrame_width, 31 + 71)
                        track[1].setGeometry(current_x_position, 0, self.depthFrame_width, self.frame_height - 31 - 71)
                        current_x_position += self.depthFrame_width  # 更新x坐标

            self.next_x_position = current_x_position
            self.adjust_scroll_area()
            self.adjust_scroll_content_top()
            self.adjust_scroll_content_bottom()
        except Exception as e:
            print(f'关闭深度道报错：{e}')

    # 关闭曲线道
    def closeCurveTrack(self, curvetrack, curveTrackTop, curveContent):
        try:
            curveTrackTop.deleteLater()    # 销毁curveTrack
            curveContent.deleteLater()
            self.tracks.remove(curvetrack)  # 从列表中移除被关闭的曲线轨道
            Globals.tracks.remove(curvetrack)

            # 计算被关闭的曲线轨道的宽度，用于后续的重新布局
            closed_track_width = self.curveFrame_width + self.frame_margin

            # 重新布局后面的曲线轨道
            current_x_position = 0  # 从初始位置开始重新布局
            for track in self.tracks:
                if track != curvetrack:
                    sign_curveOrdepth = False  # 默认为深度道
                    for child_widget in track[1].children():
                        if isinstance(child_widget, pg.PlotWidget):
                            sign_curveOrdepth = child_widget.sign_curveOrdepth
                    if sign_curveOrdepth:  # 说明是曲线道
                        track[0].setGeometry(current_x_position, 0, self.curveFrame_width, 31 + 71)
                        track[1].setGeometry(current_x_position, 0, self.curveFrame_width, self.frame_height - 31 - 71)
                        current_x_position += self.curveFrame_width  # 更新x坐标
                    else:  # 说明是深度道
                        track[0].setGeometry(current_x_position, 0, self.depthFrame_width, 31 + 71)
                        track[1].setGeometry(current_x_position, 0, self.depthFrame_width, self.frame_height - 31 - 71)
                        current_x_position += self.depthFrame_width  # 更新x坐标

            # 更新下一个框架的 x 坐标
            self.next_x_position = current_x_position
            self.adjust_scroll_area()
            self.adjust_scroll_content_top()
            self.adjust_scroll_content_bottom()
        except Exception as e:
            print(f'关闭曲线道报错：{e}')


# 曲道的子部件
class TrackSubComponent(QMainWindow, curve.Ui_Frame):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

# 创建曲线曲线道的top部分
class CurveTrackTop(CardWidget):
    def __init__(self, next_x_position, curveFrame_width):
        super().__init__()
        # self.clicked = pyqtSignal(CardWidget)

        self.initUi(next_x_position, curveFrame_width)
        self.sign_theTitleNameIsChanged = False
        self.theXRangeGroupBox.sign_isFilled = False
    def mousePressEvent(self, event):
        try:
            # if event.button() == Qt.LeftButton:
            # print('点击了曲线道顶部')
            Globals.sign_clicked_inside_curveTrackTop = False
            self.changeColor()
        except Exception as e:
            print(e)

    def changeColor(self):
        Globals.curveEditButton.setEnabled(False)
        Globals.curveEditTable_tool.setEnabled(False)
        Globals.OutlierEliminator_tool.setEnabled(False)
        for track in Globals.tracks:
            curveTrackTop = track[0]
            if isinstance(curveTrackTop, CurveTrackTop):
                Globals.sign_clicked_inside_curveTrackTop = True
                if curveTrackTop == self:
                    if track == Globals.theTrack:
                        Globals.theTrack = track
                        Globals.theTrackName = self.get_characters_before_char(
                            track[0].findChild(StrongBodyLabel, 'curveName').text(), ":")
                    else:
                        Globals.theTrack = track
                        Globals.theTrackName = self.get_characters_before_char(track[0].findChild(StrongBodyLabel, 'curveName').text(), ":")
                        Globals.sign_isClickedOutlierEliminator = False
                        Globals.OutlierEliminator_tool.setChecked(Globals.sign_isClickedOutlierEliminator)
                        for track in Globals.tracks:
                            for child_widget in track[1].children():
                                if isinstance(child_widget, CustomPlotWidget):
                                    child_widget.getPlotItem().setMouseEnabled(x=False,
                                                                               y=not Globals.sign_isClickedOutlierEliminator)
                        # print(Globals.theTrackName)
                    curveTrackTop.curveToolBar.setStyleSheet("border-top: 3px solid red;")
                    if self.sign_theTitleNameIsChanged:
                        Globals.curveEditButton.setEnabled(True)
                        Globals.curveEditTable_tool.setEnabled(True)
                        Globals.OutlierEliminator_tool.setEnabled(True)
                else:
                    curveTrackTop.curveToolBar.setStyleSheet("border-top: 1px solid rgb(234, 234, 234)")

    # 获得该字符前面的所有字符
    def get_characters_before_char(self, string, char):
        index = string.find(char)  # 获取字符在字符串中的索引
        if index != -1:  # 如果找到了该字符
            return string[:index]  # 使用切片获取该字符前面的所有字符
        else:
            return string

    def initUi(self, next_x_position, curveFrame_width):
        curveSubComponent = TrackSubComponent()

        self.curveToolBar = curveSubComponent.findChild(CardWidget, 'curveToolBar')
        self.curveToolBar.resize(curveFrame_width, 31)
        # 创建关闭按钮的样式，并将关闭按钮添加道顶层工具栏的布局里边
        self.closeCurveButton = TransparentToolButton('images/close.png', self)
        curveToolBar_Layout = QHBoxLayout()
        self.curveToolBar.setLayout(curveToolBar_Layout)  # 为顶层工具栏设置水平布局
        curveToolBar_Layout.addStretch()  # 向水平布局添加一个弹簧
        curveToolBar_Layout.addWidget(self.closeCurveButton)  # 向水平布局中再添加一个closeButton关闭按钮

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

        self.setGeometry(next_x_position, 0, curveFrame_width, 31 + 71)
        self.curveToolBar.setParent(self)
        self.curveToolBar.setGeometry(0, 0, curveFrame_width, 31)
        self.curveTitleBar.setParent(self)
        self.curveTitleBar.setGeometry(0, 31, curveFrame_width, 71)



# 自定义的PlotWidget
class CustomPlotWidget(pg.PlotWidget):
    def __init__(self, sign_curveOrdepth, parent=None):
        super().__init__(parent)
        # self.ExSign_addLayeredLine = False
        # 该标签用来判断该曲道是曲线道还是深度道
        self.sign_curveOrdepth = sign_curveOrdepth
        self.sign_isPressed = False
        self.sign_isPloted = False

        self.crossCursor = Cursor.createCrossCursor()
        self.XCursor = Cursor.createXCursor()

        self.theMousePressXPos = 0
        self.theMousePressYPos = 0

        self.setMouseTracking(True)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)  # 设置为单次触发模式
        self.timer.timeout.connect(self.hideVLineIfVisible)

        self.timer_AddCursor = QTimer(self)
        self.timer_AddCursor.setSingleShot(True)
        self.timer_AddCursor.timeout.connect(self.Add_restoreDefaultCursor)

        self.timer_DeleteCuesor = QTimer(self)
        self.timer_DeleteCuesor.setSingleShot(True)
        self.timer_DeleteCuesor.timeout.connect(self.Add_restoreDefaultCursor)

    def changeColor(self):
        # theTrack = None
        Globals.curveEditButton.setEnabled(False)
        Globals.curveEditTable_tool.setEnabled(False)
        Globals.OutlierEliminator_tool.setEnabled(False)
        for index, track in enumerate(Globals.tracks):
            curveTrackTop1 = track[0]
            if isinstance(curveTrackTop1, CurveTrackTop):
                curveTrackTop1.curveToolBar.setStyleSheet("border-top: 1px solid rgb(234, 234, 234)")
            for child_widget in track[1].children():
                if isinstance(child_widget, CustomPlotWidget):
                    if child_widget.sign_curveOrdepth:
                        if child_widget == self:
                            if track == Globals.theTrack:
                                Globals.theTrack = track
                                Globals.theTrackName = self.get_characters_before_char(
                                    track[0].findChild(StrongBodyLabel, 'curveName').text(), ":")
                            else:
                                Globals.theTrack = track
                                Globals.theTrackName = self.get_characters_before_char(track[0].findChild(StrongBodyLabel, 'curveName').text(), ":")
                                Globals.sign_isClickedOutlierEliminator = False
                                Globals.OutlierEliminator_tool.setChecked(Globals.sign_isClickedOutlierEliminator)
                                for track in Globals.tracks:
                                    for child_widget in track[1].children():
                                        if isinstance(child_widget, CustomPlotWidget):
                                            child_widget.getPlotItem().setMouseEnabled(x=False,
                                                                                       y=not Globals.sign_isClickedOutlierEliminator)
                                print(f"当前曲道名称：{Globals.theTrackName}")
                            break
                    else:
                        if child_widget == self:
                            Globals.theTrack = track
                            print(Globals.theTrackName)
                            break
        curveTrackTop = Globals.theTrack[0]
        if isinstance(curveTrackTop, CurveTrackTop):
            Globals.sign_clicked_inside_curveTrackTop = True
            curveTrackTop.curveToolBar.setStyleSheet("border-top: 3px solid red;")
            if curveTrackTop.sign_theTitleNameIsChanged:
                Globals.curveEditButton.setEnabled(True)
                Globals.curveEditTable_tool.setEnabled(True)
                Globals.OutlierEliminator_tool.setEnabled(True)

    def get_characters_before_char(self, string, char):
        index = string.find(char)  # 获取字符在字符串中的索引
        if index != -1:  # 如果找到了该字符
            return string[:index]  # 使用切片获取该字符前面的所有字符
        else:
            return string

    # 鼠标点击事件
    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        print('outer')

        # print('点击了曲线道绘图区域')
        Globals.sign_clicked_inside_curveTrackTop = False
        self.changeColor()
        event.accept()
        # 获取鼠标点击事件
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            # 将坐标转换为PlotWidget的坐标系下的横纵坐标
            view_pos = self.plotItem.vb.mapSceneToView(pos)
            if self.cursor() == self.crossCursor:
                print(self.cursor())
                # print(f"self.cursor().shape():{self.cursor().shape()}")
                # 将鼠标是否按下的标志设为True
                Globals.Sign_WhetherMousePressed = True
                # 获取鼠标点击位置在PlotWidget中的坐标

                self.theMousePressXPos = view_pos.x()
                self.theMousePressYPos = view_pos.y()

                self.theMousePressXGlobalPos = event.x()
                self.theMousePressYGlobalPos = event.y()

                # # 将分层标记设为Flase，并且鼠标恢复为默认状态
                # Globals.sign_addLayeredLine = False
                cursor = QCursor(Qt.ArrowCursor)
                self.setCursor(cursor)

                print(f'Gloabl   左键：x:{self.theMousePressXGlobalPos}, y:{self.theMousePressYGlobalPos}')
                print(f'坐标系    左键：x:{self.theMousePressXPos}, y:{self.theMousePressYPos}')

                # 将坐标已经转换为PlotWidget的坐标系下的横纵坐标赋值给全局变量
                Globals.theMousePressXPos = self.theMousePressXPos
                Globals.theMousePressYPos = self.theMousePressYPos

                addWellLayerLine_window = AddWellLayerLineMainWindow('NewLayer', round(Globals.theMousePressYPos, 3))
                addWellLayerLine_window.show()
                addWellLayerLine_window.addWellLayerLineInterface.okButton.clicked.connect(self.loadLayerLine)
                addWellLayerLine_window.addWellLayerLineInterface.okButton.clicked.connect(addWellLayerLine_window.close)

            elif self.cursor() == self.XCursor:
                self.deleteLayerLine(pos)

            elif Globals.sign_isClickedOutlierEliminator and self.sign_isPloted:
                self.startPos = view_pos
                print(f"初始位置:{self.startPos}")
                self.rectItem = pg.RectROI([self.startPos.x(), self.startPos.y()], [0, 0], pen=pg.mkPen(color=(0, 255, 0), width=3), movable=False)
                Globals.rectItem = self.rectItem
                self.addItem(self.rectItem)
                self.sign_isPressed = True

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        # 鼠标释放时移出矩形框
        pos = event.pos()
        if Globals.sign_isClickedOutlierEliminator and self.sign_isPloted:
            # 将坐标转换为PlotWidget的坐标系下的横纵坐标
            endPos = self.plotItem.vb.mapSceneToView(pos)
            print(f'结束位置:{endPos}')
            width = endPos.x() - self.startPos.x()
            height = endPos.y() - self.startPos.y()
            print(f'宽度:{width}')
            print(f'高度:{height}')
            self.rectItem.setSize([width, height])
            print(f'矩形框的大小:{self.rectItem.size()}')
            # self.removeItem(self.rectItem)

            self.sign_isPressed = False
            topLeft = self.startPos
            bottomRight = endPos
            self.deleteOutlierMainWindow = DeleteOutlierMainWindow(topLeft, bottomRight)
            self.deleteOutlierMainWindow.show()

            # self.rectItem = None

    # 从数据库中加载分层线
    def loadLayerLine(self):
        try:
            connection = DataBaseConnection.connect_to_database_test()
            cursor = connection.cursor()
            cursor.execute(f"SELECT LayerLineName, Depth FROM layerlines WHERE WellID = {Globals.theOpenedWellId};")
            layerLines_list = cursor.fetchall()
            for layer in layerLines_list:
                layerName = layer[0]
                print(f'layerName:{layerName}')
                layerDepth = layer[1]
                print(f'layerDepth:{layerDepth}')
                for track in Globals.tracks:
                    for child_widget in track[1].children():
                        if isinstance(child_widget, pg.PlotWidget):
                            layerLine = CustomLayeredLine(pos=layerDepth, angle=0, movable=Globals.sign_LayerLineIsMovable)
                            layerLine.setPen(pg.mkPen('r', width=5))
                            child_widget.addItem(layerLine)
                            if not child_widget.sign_curveOrdepth:
                                child_widget.layerNameLabel = CustomTextItem(text=layerName, color=(0, 0, 0), anchor=(0.5, 1))
                                child_widget.layerNameLabel.setFont(pg.QtGui.QFont('Arial', 12))
                                child_widget.addItem(child_widget.layerNameLabel)
                                if hasattr(child_widget,'layerNameLabel') and child_widget.layerNameLabel is not None:
                                    child_widget.layerNameLabel.setPos(1.5, layerDepth)
                                    # 向分层线列表中添加分层线对象和分层线名称标签
                                    layerLine = [layerLine, child_widget.layerNameLabel]
                                    Globals.layerLines.append(layerLine)
        except Exception as e:
            print(f"插入分层线出错：{e}")

    def deleteLayerLine(self, pos):
        def connect_to_database():
            connection = DataBaseConnection.connect_to_database_test()
            cursor = connection.cursor()
            return connection, cursor

        def get_well_id(well_name, cursor):
            cursor.execute("SELECT WellID FROM well WHERE WellName = ?", (well_name.upper(),))
            row_wellid = cursor.fetchone()
            return row_wellid[0] if row_wellid else None

        def delete_layer_data(depth, well_id, cursor, connection):
            sql_delete = "DELETE FROM layerlines WHERE Depth = ? AND WellID = ?"
            values_delete = (depth, well_id)
            cursor.execute(sql_delete, values_delete)
            sql_update = "UPDATE well SET LayerLineNumber = LayerLineNumber -1 WHERE WellID = ?"
            values_update = (well_id,)
            cursor.execute(sql_update, values_update)
            connection.commit()

        self.the_delete_item_pos = None
        # 点击删除模式下的水平线
        for track in Globals.tracks:
            for child_widget in track[1].children():
                if isinstance(child_widget, CustomPlotWidget):
                    print(child_widget.sign_curveOrdepth)
                    items = child_widget.items(pos)
                    for item in items:
                        if isinstance(item, CustomLayeredLine):
                            self.the_delete_item_pos = item.pos()
                            print(f"the_delete_item_pos:{self.the_delete_item_pos}")
                            break

        for track in Globals.tracks:
            for child_widget in track[1].children():
                if isinstance(child_widget, CustomPlotWidget):
                    if self.the_delete_item_pos is not None:
                        # print('a')
                        items1 = child_widget.items()
                        for item1 in items1:
                            # print('b')
                            if isinstance(item1, (CustomLayeredLine, CustomTextItem)):
                                child_widget.removeItem(item1)
                                print(item1)

        if self.the_delete_item_pos is not None:
            connection, cursor = connect_to_database()
            well_id = get_well_id(Globals.theOpenedWellName, cursor)

            if well_id is not None:
                delete_layer_data(self.the_delete_item_pos.y(), well_id, cursor, connection)
                print('分层线删除成功')
            else:
                print('没有找到匹配的WellID')

            self.loadLayerLine()
        else:
            print('没有点击道分层线')

    # 鼠标进入事件
    def enterEvent(self, event):
        super().enterEvent(event)
        if hasattr(self, 'vLine') and self.vLine is not None:
            self.vLine.show()
            self.timer.stop()  # 鼠标进入时停止定时器
        if  Globals.sign_addLayeredLine:
            self.setCursor(self.crossCursor)
            self.timer_AddCursor.stop()
        if Globals.sign_deleteLayerLine:
            self.setCursor(self.XCursor)
            self.timer_DeleteCuesor.stop()

    # 鼠标离开事件
    def leaveEvent(self, event):
        super().leaveEvent(event)
        if hasattr(self, 'vLine') and self.vLine is not None:
            if self.vLine.isVisible():
                self.vLine.hide()
                QTimer.singleShot(5, self.timerTimeout)  # 鼠标离开后启动定时器
        if Globals.sign_addLayeredLine:
            self.setCursor(self.crossCursor)
            QTimer.singleShot(5, self.timerTimeout_AddCursor)
        if Globals.sign_deleteLayerLine:
            self.setCursor(self.XCursor)
            QTimer.singleShot(5, self.timerTimeout_XCursor)

    def timerTimeout(self):
        self.timer.start(5)  # 启动定时器

    def timerTimeout_AddCursor(self):
        self.timer_AddCursor.start(5)

    def timerTimeout_XCursor(self):
        self.timer_DeleteCuesor.start(5)

    def hideVLineIfVisible(self):
        if hasattr(self, 'vLine') and self.vLine is not None:
            if self.vLine.isVisible():
                self.vLine.hide()

    def X_restoreDefaultCursor(self):
        if self.cursor().shape() == self.XCursor.shape():
            cursor = QCursor(Qt.ArrowCursor)
            self.setCursor(cursor)

    def Add_restoreDefaultCursor(self):
        if self.cursor().shape() == self.crossCursor.shape():
            cursor = QCursor(Qt.ArrowCursor)
            self.setCursor(cursor)


if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    Curve_window = Curve("Curve Interface")
    Curve_window.show()
    sys.exit(app.exec_())


