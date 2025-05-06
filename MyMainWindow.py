# coding:utf-8
import inspect
import sys
import numpy as np
import pyqtgraph as pg

from PyQt5.QtCore import Qt, QTimer, QEvent, QSize, QEasingCurve, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QColor, QCursor, QFont, QPixmap, QPainter, QKeySequence
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QApplication, QFrame, QStackedWidget, QTableWidgetItem, QMenu, \
    QAction, QLabel, QGroupBox, QWidget, QCheckBox, QFileDialog

from qfluentwidgets import (NavigationItemPosition, MSFluentTitleBar, MSFluentWindow,
                            TextEdit, TransparentPushButton, TransparentDropDownPushButton, RoundMenu, Action,
                            StrongBodyLabel, TogglePushButton, TransparentDropDownToolButton, BodyLabel, CheckBox,
                            PrimaryPushButton, PushButton, TransparentToolButton, PillToolButton, FlowLayout,
                            TransparentToggleToolButton, ImageLabel, InfoBarPosition)
from qfluentwidgets import FluentIcon as FIF

import CurveCalculate
import DrawText
from GetData import GetData
from Table import Table
from Curve import Curve, CurveTrackTop, CustomPlotWidget
from OpenWell import OpenWellMainWindow
from Function.DataBaseConnection import connect_to_database_test
from Function import InformationShow
from Function import TableFunction
from Function import TitleBarFunction
from Function import CurveFunction
import Globals
import CurveEdit

class Widget(QFrame):   # 定义了一个自定义的小部件类 Widget，继承自 QFrame。用于显示界面中的一些基本信息，如应用程序名称、图标等。

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(' ', '-'))

class CustomTitleBar(MSFluentTitleBar):     # 设置标题栏的UI
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi()

    def setupUi(self):
        # 设置颜色，用来给标题栏中按钮的图标设置颜色
        color = QColor(206, 206, 206)
        # 创建按钮布局
        self.toolButtonLayout = QHBoxLayout()
        # 创建一列按钮：标题栏位置
        # self.searchButton = TransparentPushButton( FIF.SEARCH_MIRROR.icon(color=color),'搜索' , self) # 搜索按钮
        self.openWellButton = TransparentPushButton(QIcon("images/OpenFile.png"), '打开井', self)  # 打开井按钮
        # self.openWellButton.clicked.connect(self.openWellButton_clicked)
        self.addMapTrackButton = TransparentDropDownPushButton(FIF.MENU, '图道', self)  # 图道按钮
        self.addMapTrackButton.setEnabled(False)
        self.layeredLineButton = TransparentDropDownPushButton(FIF.MENU, '分层', self)    # 分层按钮
        self.layeredLineButton.setEnabled(False)
        self.curveEditButton = TransparentDropDownPushButton(FIF.MENU, '曲线编辑', self)    # 曲线编辑按钮
        self.curveEditButton.setEnabled(False)
        Globals.curveEditButton = self.curveEditButton
        self.curveCalculateButton = TransparentPushButton(QIcon('images/curveCalculate.png'), '曲线计算', self)   # 曲线计算按钮
        self.curveCalculateButton.setEnabled(False)

        # 创建一个菜单栏，添加给“图道”按钮
        self.MapTrackMenu = RoundMenu(parent=self)
        self.MapTrackMenu.addAction(Action(QIcon('images/addDepthTrack.png'), '添加深度道'))
        self.MapTrackMenu.addAction(Action(QIcon('images/addCurveTrack.png'), '添加曲线道'))
        self.addDepthTrack = self.MapTrackMenu._actions[0]
        self.addCurveTrack = self.MapTrackMenu._actions[1]
        self.addMapTrackButton.setMenu(self.MapTrackMenu)

        # 创建一个菜单栏，添加给“分层"按钮
        self.LayerMenu = RoundMenu(parent=self)
        self.LayerMenu.addAction(Action(QIcon('images/addLayer'), '添加分层'))
        self.LayerMenu.addAction(Action(QIcon('images/deleteLayer'), '删除分层'))
        self.addlayeredLine = self.LayerMenu._actions[0]
        self.deletelayeredLine = self.LayerMenu._actions[1]
        self.layeredLineButton.setMenu(self.LayerMenu)

        # 创建一个菜单栏， 添加给“曲线编辑”按钮
        self.CurveEditMenu = RoundMenu(parent=self)
        self.CurveEditMenu.addAction(Action(QIcon('images/curveTableEdit.png'), '曲线数据表格编辑'))
        self.CurveEditMenu.addAction(Action(QIcon('images/eliminateOutlier.png'), '剔除异常值'))
        self.curveEditTable = self.CurveEditMenu._actions[0]
        self.OutlierEliminator = self.CurveEditMenu._actions[1]
        self.curveEditButton.setMenu(self.CurveEditMenu)

        # 为按钮设置悬停文字
        # self.searchButton.setToolTip('搜索')
        self.openWellButton.setToolTip('打开井')
        self.addMapTrackButton.setToolTip('添加图道')
        self.addlayeredLine.setToolTip('分层线')

        # 按钮布局的相关设置，并在按钮布局中添加按钮
        self.toolButtonLayout.setContentsMargins(20, 0, 20, 0)  # 上下左右内边距
        self.toolButtonLayout.setSpacing(15)    # 设置布局中组件之间的间距大小
        # self.toolButtonLayout.addWidget(self.searchButton)
        self.toolButtonLayout.addWidget(self.openWellButton)
        self.toolButtonLayout.addWidget(self.addMapTrackButton)
        self.toolButtonLayout.addWidget(self.layeredLineButton)
        self.toolButtonLayout.addWidget(self.curveEditButton)
        self.toolButtonLayout.addWidget(self.curveCalculateButton)

        # MSFluentTitleBar自带的水平布局，向里面添加自己创造的按钮布局
        self.hBoxLayout.insertLayout(4, self.toolButtonLayout)

        # 添加深度道
        self.addDepthTrack_tool = TransparentToolButton('', self)
        self.addDepthTrack_tool.setIcon("images/addDepthTrack.png")
        self.addDepthTrack_tool.setToolTip('添加深度道')
        self.addDepthTrack_tool.setEnabled(False)
        # 添加曲线道
        self.addCurveTrack_tool = TransparentToolButton('', self)
        self.addCurveTrack_tool.setIcon("images/addCurveTrack.png")
        self.addCurveTrack_tool.setToolTip('添加曲线道')
        self.addCurveTrack_tool.setEnabled(False)
        # 添加分层
        self.addLayerLine_tool = TransparentToggleToolButton('', self)
        self.addLayerLine_tool.setIcon("images/addLayer.png")
        # self.addLayerLine_tool.setShortcut(QKeySequence('1'))
        self.addLayerLine_tool.setToolTip('添加分层线')
        # self.addLayerLine_tool.setToolTip('添加分层线,快捷键:1')
        self.addLayerLine_tool.setEnabled(False)
        # 删除分层
        self.deleteLayerLine_tool = TransparentToggleToolButton('', self)
        self.deleteLayerLine_tool.setIcon("images/deleteLayer.png")
        # self.deleteLayerLine_tool.setShortcut(QKeySequence('2'))
        self.deleteLayerLine_tool.setToolTip('删除分层线')
        # self.deleteLayerLine_tool.setToolTip('删除分层线,快捷键:2')
        self.deleteLayerLine_tool.setEnabled(False)
        # 曲线表格编辑
        self.curveEditTable_tool = TransparentToolButton(QIcon('images/curveTableEdit.png'), self)
        self.curveEditTable_tool.setToolTip('曲线表格编辑')
        Globals.curveEditTable_tool = self.curveEditTable_tool
        self.curveEditTable_tool.setEnabled(False)
        # 剔除异常值
        self.OutlierEliminator_tool = TransparentToggleToolButton(QIcon('images/eliminateOutlier.png'), self)
        # self.OutlierEliminator_tool.setShortcut(QKeySequence('3'))
        self.OutlierEliminator_tool.setToolTip('剔除异常值')
        # self.OutlierEliminator_tool.setToolTip('剔除异常值,快捷键:3')
        Globals.OutlierEliminator_tool = self.OutlierEliminator_tool
        self.OutlierEliminator_tool.setEnabled(False)
        # 曲线计算
        self.curveCalculate_tool = TransparentToolButton(QIcon('images/curveCalculate.png'), self)
        self.curveCalculate_tool.setToolTip('曲线计算')
        self.curveCalculate_tool.setEnabled(False)
        # 给便捷按钮设置布局
        self.hBoxLayout.insertWidget(6, self.addDepthTrack_tool, Qt.AlignRight)
        self.hBoxLayout.insertWidget(7, self.addCurveTrack_tool, Qt.AlignRight)
        self.hBoxLayout.insertWidget(8, self.addLayerLine_tool, Qt.AlignRight)
        self.hBoxLayout.insertWidget(9, self.deleteLayerLine_tool, Qt.AlignRight)
        self.hBoxLayout.insertWidget(10, self.curveEditTable_tool, Qt.AlignRight)
        self.hBoxLayout.insertWidget(11, self.OutlierEliminator_tool, Qt.AlignRight)
        self.hBoxLayout.insertWidget(12, self.curveCalculate_tool, Qt.AlignRight)

        # avater图标
        self.avatar = TransparentDropDownToolButton('', self)

        # self.avatar.setIcon(file_name)
        self.avatar.setIconSize(QSize(26, 26))
        self.avatar.setFixedHeight(30)

        self.avatar.setEnabled(False)
        self.avatar.setContentsMargins(0, 0, 0, 0)
        # self.avatar.setFixedWidth(50)

        self.hBoxLayout.insertWidget(13, self.avatar, 0, Qt.AlignRight)
        self.hBoxLayout.insertSpacing(13, 30)

        # 创建

        # 将按钮对象传递给主窗口
        self.parent().setCustomTitleBarButtons(self.openWellButton, self.addMapTrackButton, self.addCurveTrack, self.addDepthTrack,
                                               self.layeredLineButton, self.addlayeredLine, self.deletelayeredLine,
                                               self.curveEditButton, self.curveEditTable, self.OutlierEliminator,
                                               self.curveCalculateButton, self.avatar, self.addDepthTrack_tool,
                                               self.addCurveTrack_tool, self.addLayerLine_tool, self.deleteLayerLine_tool,
                                               self.curveCalculate_tool)

    # def openWellButton_clicked(self):
    #     self.addMapTrackButton.setEnabled(True)
    #     self.layeredLineButton.setEnabled(True)
    #     self.curveEditButton.setEnabled(True)
    #     self.curveCalculateButton.setEnabled(True)

# ---------------------------------------------------------------------------------------------------------------------

class Window(MSFluentWindow):   # 主窗口

    def __init__(self):
        super().__init__()

        # 用来存放菜单栏，具体用途：待定？？？？？？？？？？？？
        self.menus = []

        # ？？？？？？？？？
        self.isMicaEnabled = False

        # 创建UI
        self.setupUi()

        # 创建GetData对象，GetData的用途: 用来获取文件名
        self.getData = GetData()



        # ？？？？？？？？？
        self.sign_iftheDatatoDatabase = False

        # 前一页、后一页按钮设置槽函数
        self.tableInterface.prev_button.clicked.connect(self.load_previous_page)    # 前一页
        self.tableInterface.next_button.clicked.connect(self.load_next_page)        # 后一页
        # self.OpenWellWindowSlotFun()

    def fenYeChaXun(self):
        self.load_data()

    def load_previous_page(self):
            TableFunction.load_previous_page(self)

    def load_next_page(self):
            TableFunction.load_next_page(self)

    def load_data(self):
        try:
            TableFunction.load_data(self)
        except Exception as e:
            print(f"加载井数据错误：{e}")

    # 自定义方法，用于接收标题栏中的按钮对象
    def setCustomTitleBarButtons(self, openWellButton, addMapTrackButton,addCurveTrackButton, addDepthTackButton, layeredLineButton, addlayeredLine, deletelayeredLine,
                                 curveEditButton, curveEditTable, OutlierEliminator, curveCalculateButton, avatar,
                                 addDepthTrack_tool, addCurveTrack_tool, addLayerLine_tool, deleteLayerLine_tool, curveCalculate_tool):

        # 连接按钮的点击信号到槽函数
        # searchButton.clicked.connect(self.handleSearchButtonClicked)    # 搜寻按钮
        openWellButton.clicked.connect(lambda :self.handleOpenWellButtonClicked(openWellButton, addMapTrackButton, layeredLineButton, curveEditButton, curveCalculateButton, avatar,
                                                                                addDepthTrack_tool, addCurveTrack_tool, addLayerLine_tool, deleteLayerLine_tool, curveCalculate_tool))  # 打开well界面
        # openWellButton.clicked.connect(self.handleOpenWellButtonClicked1)
        # openWellButton.clicked.connect(self.initMenuUi)
        addCurveTrackButton.triggered.connect(self.curveInterface.addCurveTrack)    # 添加曲线道按钮
        addCurveTrackButton.triggered.connect(self.curveTrackTopRightClicked)   # 添加曲线道按钮
        addCurveTrackButton.triggered.connect(self.curveInterface.setTrackYRange)   # 添加曲线道按钮
        addDepthTackButton.triggered.connect(self.curveInterface.addDepthTrack)     # 添加深度道按钮
        addDepthTackButton.triggered.connect(self.curveInterface.setTrackYRange)    # 添加深度道按钮

        def change_ToogleTool_status():
            addLayerLine_tool.setChecked(Globals.sign_addLayeredLine)
            deleteLayerLine_tool.setChecked(Globals.sign_deleteLayerLine)
            Globals.OutlierEliminator_tool.setChecked(Globals.sign_isClickedOutlierEliminator)
            for track in Globals.tracks:
                for child_widget in track[1].children():
                    if isinstance(child_widget, CustomPlotWidget):
                        child_widget.getPlotItem().setMouseEnabled(x=False,
                                                                   y=not Globals.sign_isClickedOutlierEliminator)

        addlayeredLine.triggered.connect(self.curveInterface.addLayerLine)      # 添加分层线按钮
        addlayeredLine.triggered.connect(change_ToogleTool_status)      # 添加分层线按钮
        deletelayeredLine.triggered.connect(self.curveInterface.deleteLayerLine)    # 删除分层线
        deletelayeredLine.triggered.connect(change_ToogleTool_status)    # 删除分层线

        # 曲线表格编辑
        curveEditTable.triggered.connect(self.handleCurveEditTableButtonClicked)
        # 曲线异常值提出
        OutlierEliminator.triggered.connect(self.handleOutlierEliminatorButtonClicked)
        OutlierEliminator.triggered.connect(change_ToogleTool_status)

        curveCalculateButton.clicked.connect(self.handleCurveCalculateButtonClicked)

        avatar.clicked.connect(lambda :self.refreshAvatar(avatar))

        # 快捷工具栏
        addDepthTrack_tool.clicked.connect(self.curveInterface.addDepthTrack)
        addDepthTrack_tool.clicked.connect(self.curveInterface.setTrackYRange)
        addCurveTrack_tool.clicked.connect(self.curveInterface.addCurveTrack)
        addCurveTrack_tool.clicked.connect(self.curveTrackTopRightClicked)
        addCurveTrack_tool.clicked.connect(self.curveInterface.setTrackYRange)

        addLayerLine_tool.clicked.connect(self.curveInterface.addLayerLine)
        addLayerLine_tool.clicked.connect(change_ToogleTool_status)
        deleteLayerLine_tool.clicked.connect(self.curveInterface.deleteLayerLine)
        deleteLayerLine_tool.clicked.connect(change_ToogleTool_status)

        Globals.curveEditTable_tool.clicked.connect(self.handleCurveEditTableButtonClicked)
        Globals.OutlierEliminator_tool.clicked.connect(self.handleOutlierEliminatorButtonClicked)
        Globals.OutlierEliminator_tool.clicked.connect(change_ToogleTool_status)
        curveCalculate_tool.clicked.connect(self.handleCurveCalculateButtonClicked)

    # 创建多线程类，用来导入井.las文件
    class WellImportThread(QThread):
        # 自定义信号，用于向主线程发送信息-->>用来控制成功或失败的信息提示
        infor_signal = pyqtSignal(bool)
        # 自定义信号，用来向主线程发送信息-->>用来控制等待信息提示
        waitting_infor_signal = pyqtSignal(bool)
        # 自定义信号
        progress_updated = pyqtSignal(float)
        def __init__(self, superior, file_path):
            super().__init__()
            self.getData = superior.getData
            self.file_path = file_path
        def run(self):
            # self.waitting_infor_signal.emit(True)
            # 在这里定义你的多线程逻辑
            self.getData.import_las_file(self.infor_signal, self.waitting_infor_signal, self.progress_updated, self.file_path)

    # 自定义方法，用于处理点击打开文件按钮点击事件
    # 点击“打开井”按钮后出发的井窗口
    def handleOpenWellButtonClicked(self, openWellButton, addMapTrackButton, layeredLineButton, curveEditButton, curveCalculateButton, avatar,
                                    addDepthTrack_tool, addCurveTrack_tool, addLayerLine_tool, deleteLayerLine_tool, curveCalculate_tool):
        # 创建打开井窗口界面
        self.openWellWindow = OpenWellMainWindow(openWellButton)
        self.openWellWindow.openWellInterface.load_dataFromBaseToTable()  # 将well表中的数据在表格中展示出来
        self.openWellWindow.show()  # 显示打开井弹窗
        openWellButton.setEnabled(False)
        # self.openWellWindow.setParent(self)

        def showWaittingInfor(sign):
            if sign:
                self.waittingInfor = InformationShow.showInformation_Waitting(self.openWellWindow, "正在导入数据...",
                                                                            InfoBarPosition.TOP_RIGHT)
            else:
                self.waittingInfor.close()

        def control_inforShow(sign_whetherTheWellFileIsOpened):
            if sign_whetherTheWellFileIsOpened:
                self.openWellWindow.openWellInterface.load_dataFromBaseToTable()
                DrawText.text_to_image(self.getData.file_name)
                InformationShow.showInformation_Success(self.openWellWindow,
                                                        f"{self.getData.file_name}.las文件已经成功导入数据库！",
                                                        InfoBarPosition.TOP_RIGHT)
            elif Globals.sign_hasSameWellName:
                InformationShow.showInformation_Error(self.openWellWindow, 'las文件导入失败：已导入该井', InfoBarPosition.TOP_RIGHT)
            else:
                InformationShow.showInformation_Error(self.openWellWindow, f".las文件导入失败！", InfoBarPosition.TOP_RIGHT)

        def importWellButtonClicked():
            print('1')
            file_path, _ = QFileDialog.getOpenFileName(self.openWellWindow, "选择LAS文件", "C:\Data\Document\毕设\dataset\data\data", "LAS Files (*.las)")
            # 创建多线程（导入井.las文件）
            self.wellImportThread = self.WellImportThread(self, file_path)
            self.wellImportThread.waitting_infor_signal.connect(showWaittingInfor)
            self.wellImportThread.infor_signal.connect(control_inforShow)
            self.wellImportThread.progress_updated.connect(self.setProgressBarValue)
            self.wellImportThread.start()

        # 打开井窗口的导入数据按钮-->>槽
        self.openWellWindow.openWellInterface.importWellButton.clicked.connect(importWellButtonClicked)

        def activateTheButton(openWellButton, addMapTrackButton, layeredLineButton, curveEditButton, curveCalculateButton, curveCalculate_tool):
            # openWellButton.setEnabled(False)

            addMapTrackButton.setEnabled(True)
            layeredLineButton.setEnabled(True)
            # curveEditButton.setEnabled(True)
            curveCalculateButton.setEnabled(True)
            self.curveItem.setDisabled(False)
            self.tableItem.setDisabled(False)
            avatar.setEnabled(True)

            addDepthTrack_tool.setEnabled(True)
            addCurveTrack_tool.setEnabled(True)
            addLayerLine_tool.setEnabled(True)
            deleteLayerLine_tool.setEnabled(True)

            curveCalculate_tool.setEnabled(True)

        # 打开井窗口的双击按钮-->>槽
        self.openWellWindow.openWellInterface.wellTable.doubleClicked.connect(lambda: activateTheButton(openWellButton, addMapTrackButton, layeredLineButton, curveEditButton, curveCalculateButton, curveCalculate_tool))
        # 打开井窗口的ok按钮-->>槽
        self.openWellWindow.openWellInterface.okButton.clicked.connect(lambda: activateTheButton(openWellButton, addMapTrackButton, layeredLineButton, curveEditButton, curveCalculateButton, curveCalculate_tool))

        self.openWellWindow.openWellInterface.wellTable.doubleClicked.connect(lambda :self.doubleClickedAndOkButtonClicked(avatar))
        self.openWellWindow.openWellInterface.okButton.clicked.connect(lambda :self.doubleClickedAndOkButtonClicked(avatar))

    def setProgressBarValue(self, task_progress):
        self.openWellWindow.openWellInterface.progressbar.setValue(int(task_progress))

    def doubleClickedAndOkButtonClicked(self, avatar):
        self.emptyTheTracks()
        self.setAvater(avatar)

    # 清空当前曲线道
    def emptyTheTracks(self):
        deleteCurveTracks = []
        deleteDepthTracks = []
        if Globals.theOpenedWellName is not None:
            for track in Globals.tracks:
                for child_widget in track[1].children():
                    if isinstance(child_widget, CustomPlotWidget):
                        # 如果是深度道
                        if child_widget.sign_curveOrdepth:
                            deleteCurveTracks.append(track)
                        else:
                            deleteDepthTracks.append(track)

            for curveTrack in deleteCurveTracks:
                self.curveInterface.closeCurveTrack(curveTrack, curveTrack[0], curveTrack[1])
            for depthTrack in deleteDepthTracks:
                self.curveInterface.closeDepthTrack(depthTrack, depthTrack[0], depthTrack[1])

            print(f"Globals.tracks:{Globals.tracks}")
            Globals.tracks = []
        else:
            pass

    # 设置：用来显示当前曲线与其状态的下拉框
    def setAvater(self, avatar):
        try:
            text = Globals.theOpenedWellName.upper()

            pixmap = DrawText.text_to_image(text)
            if pixmap:
                file_path = "images/"
                file_name = file_path + f"{Globals.theOpenedWellName}.png"
                pixmap.save(file_name)
                print(f"图片保存成功:{file_name}")

                # 设置图标
                avatar.setIcon(file_name)
                if Globals.theOpenedWellName == 'shu122':
                    avatar.setIconSize(QSize(50, 30))
                else:
                    avatar.setIconSize(QSize(50, 30))
                avatar.setFixedHeight(30)
            else:
                print("图片绘制失败")

            depth = np.squeeze(np.array(CurveFunction.getDepth()))
            Globals.depth_min = np.floor(np.min(depth))
            Globals.depth_max = np.floor(np.max(depth))

        except Exception as e:
            print(f'1:{e}')

    def refreshAvatar(self, avatar):
        try:
            if hasattr(self, 'avatarMenu') and self.avatarMenu is not None:
                self.avatarMenu.close()

            self.avatarMenu = RoundMenu(parent=self)
            avatar.setMenu(self.avatarMenu)

            # 更新曲线数量和分层数量
            self.getCurveAndLayerNum()  # 设置Globals中curveNum和layerNum的值
            curvelabelFrame = QFrame(self)
            curvelabelFrame.setFixedSize(200, 30)
            layerlabelFrame = QFrame(self)
            layerlabelFrame.setFixedSize(200, 30)
            curveImagelabel = ImageLabel("images/curve.png", curvelabelFrame)
            curveImagelabel.scaledToHeight(20)
            curveImagelabel.scaledToWidth(20)
            curveImagelabel.move(0, 5)
            layerImagelabel = ImageLabel("images/layerLine.png", layerlabelFrame)
            layerImagelabel.scaledToHeight(20)
            layerImagelabel.scaledToWidth(20)
            layerImagelabel.move(0, 5)
            curveLabel = BodyLabel(f'曲线数量: {Globals.curveNum}', curvelabelFrame)
            curveLabel.move(25, 0)
            layerLabel = BodyLabel(f'分层数量: {Globals.layerNum}', layerlabelFrame)
            layerLabel.move(25, 0)
            curveLabel.setFixedSize(175, 30)
            layerLabel.setFixedSize(175, 30)
            self.avatarMenu.addWidget(curvelabelFrame)
            self.avatarMenu.addWidget(layerlabelFrame)
            self.avatarMenu.addSeparator()

            avatarSubMenu = RoundMenu('删除曲线', parent=self.avatarMenu)
            avatarSubMenu.setIcon(FIF.SETTING)

            self.checkBox_list = []
            headers = CurveFunction.getTableHeaders()
            if len(headers) == 2:
                print('没有曲线')
                label = StrongBodyLabel("        没有曲线", self)   # 空格用来凑字数，以达到居中的效果
                label.setFixedWidth(150)
                # label.setAlignment(Qt.AlignCenter)    # 为什么不能居中？
                avatarSubMenu.addWidget(label)
            else:
                for header in headers:
                    if header != 'id' and header != 'depth':
                        # headers_new.append(header)
                        checkbox = CheckBox(f'{header}', self)
                        checkbox.setFixedWidth(150)
                        checkbox.setTristate(False)
                        avatarSubMenu.addWidget(checkbox)
                        self.checkBox_list.append(checkbox)
            # deleteCurveButton = PrimaryPushButton
            deleteCurveButton = PushButton('删除曲线',self)
            signal_method = deleteCurveButton.metaObject().method(deleteCurveButton.metaObject().indexOfSignal('clicked'))
            if deleteCurveButton.isSignalConnected(signal_method):
                deleteCurveButton.clicked.disconnect(self.deleteButton_clicked)
            deleteCurveButton.clicked.connect(self.deleteButton_clicked)
            deleteCurveButton.setFixedWidth(120)
            avatarSubMenu.addWidget(deleteCurveButton)
            avatarSubMenu.setFixedWidth(200)
            self.avatarMenu.addMenu(avatarSubMenu)

        except Exception as e:
            print(f'2:{e}')

    class CurveDeleteThread(QThread):
        # 自定义信号，用于向主线程发送信息-->>用来控制成功或失败的信息提示
        infor_signal = pyqtSignal(bool)
        # 自定义信号，用来向主线程发送信息-->>用来控制等待信息提示
        waitting_infor_signal = pyqtSignal(bool)

        def __init__(self, superior, deleteCheckBoxesName):
            super().__init__()
            self.superior = superior
            self.deleteCheckBoxesName = deleteCheckBoxesName

        def run(self):
            self.waitting_infor_signal.emit(True)
            # 在这里定义你的多线程逻辑
            self.deleteCurve()

        def deleteCurve(self):
            sign = False
            for deleteCurveName in self.deleteCheckBoxesName:
                connection = connect_to_database_test()
                try:
                    cursor = connection.cursor()
                    try:
                        # 删除列
                        cursor.execute(f'ALTER TABLE {Globals.theOpenedWellName} DROP COLUMN {deleteCurveName}')
                        connection.commit()
                        # 将well表中的CurveNumber - 1
                        sql_update_well = "UPDATE well SET CurveNumber = CurveNumber - 1 WHERE WellID = ?"
                        values_update = (Globals.theOpenedWellId,)
                        cursor.execute(sql_update_well, values_update)
                        connection.commit()
                        print("曲线数量-1")
                        sign = True
                    except Exception as e:
                        connection.rollback()
                        sign = False
                        self.waitting_infor_signal.emit(False)
                        self.infor_signal.emit(False)
                        print(f'删除曲线失败:{e}')
                    finally:
                        cursor.close()
                finally:
                    connection.close()
            if sign:
                self.waitting_infor_signal.emit(False)
                self.infor_signal.emit(True)
            else:
                self.waitting_infor_signal.emit(False)
                self.infor_signal.emit(False)

    def deleteButton_clicked(self):
        self.deleteCheckBoxesName = []
        self.deleteCheckBoxes = []
        for checkbox in self.checkBox_list:
            if checkbox.isChecked():
                self.deleteCheckBoxesName.append(checkbox.text())
                self.deleteCheckBoxes.append(checkbox)

        for deleteCheckBox in self.deleteCheckBoxes:
            self.checkBox_list.remove(deleteCheckBox)
            deleteCheckBox.deleteLater()

        print(f"self.deleteCheckBoxesName:{self.deleteCheckBoxesName}")

        def waitting_infor(sign):
            if sign:
                self.waittingInfor = InformationShow.showInformation_Waitting(self, "正在删除曲线", InfoBarPosition.TOP)
            else:
                self.waittingInfor.close()

        def control_inforShow(sign_isDeleted):
            if sign_isDeleted:
                InformationShow.showInformation_Success(self, "成功删除曲线", InfoBarPosition.TOP)
            else:
                InformationShow.showInformation_Error(self, "删除曲线失败", InfoBarPosition.TOP)

        self.curveDeleteThread = self.CurveDeleteThread(self, self.deleteCheckBoxesName)
        self.curveDeleteThread.waitting_infor_signal.connect(waitting_infor)
        self.curveDeleteThread.infor_signal.connect(control_inforShow)
        self.curveDeleteThread.start()

    def getCurveAndLayerNum(self):
        try:
            connection = connect_to_database_test()
            cursor = connection.cursor()

            cursor.execute(f'SELECT CurveNumber, LayerLineNumber FROM well WHERE WellID = {Globals.theOpenedWellId}')
            numlist = cursor.fetchall()
            print(f'numlist:{numlist}')
            # print(list)
            Globals.curveNum = numlist[0][0]
            Globals.layerNum = numlist[0][1]

            cursor.close()
            connection.close()
        except Exception as e:
            print(f'3:{e}')

    def handleCurveEditTableButtonClicked(self):
        # 创建曲线表格编辑窗口
        self.curveEditTableWindow = CurveEdit.CurveEditTableMainWindow()
        self.curveEditTableWindow.show()

    def handleOutlierEliminatorButtonClicked(self):
        Globals.sign_isClickedOutlierEliminator = not Globals.sign_isClickedOutlierEliminator
        Globals.sign_addLayeredLine = False
        Globals.sign_deleteLayerLine = False

    def handleCurveCalculateButtonClicked(self):
        self.curveCalculateWindow = CurveCalculate.CurveCalculateMainWindow()
        self.curveCalculateWindow.show()

    def OpenWellWindowSlotFun(self):
        pass

    # 设置Ui界面
    def setupUi(self):

        # self.tabBar = self.titleBar.tabBar  # type: TabBar

        # create sub interface
        # self.homeInterface = QStackedWidget(self, objectName='homeInterface')
        self.curveInterface = Curve('Curve Interface', self)
        self.tableInterface = Table('Table Interface', self)
        self.libraryInterface = Widget('library Interface', self)

        self.setTitleBar(CustomTitleBar(self))  # 将标题栏的父类设置成CustomTitleBar

        self.initNavigation()
        self.initWindow()

        # self.setupUi_BriefIntro()

    def initNavigation(self):   # 导航栏UI
        # 添加导航栏按钮
        # self.addSubInterface(self.homeInterface, FIF.HOME, '简介', FIF.HOME_FILL)
        self.addSubInterface(self.curveInterface, FIF.PENCIL_INK, '曲线')
        self.addSubInterface(self.tableInterface, FIF.TILES, '表格')

        self.curveItem = None
        self.tableItem = None

        # navigationInterface是NavigationBar
        items = list(self.navigationInterface.items.values())
        for item in items:
            if item.text() == '曲线':
                self.curveItem = item

            if  item.text() == '表格':
                self.tableItem = item
                self.tableItem.clicked.connect(lambda: TableFunction.load_data(self))

        print(self.curveItem.text())
        print(self.tableItem.text())

        self.curveItem.setDisabled(True)
        self.tableItem.setDisabled(True)

        self.navigationInterface.addItem(
            routeKey='newWindow',
            icon=QIcon("images/newWindow.png"),
            text='新建',
            onClick=self.showMessageBox_newWindow,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

        self.navigationInterface.addItem(
            routeKey='emptyTracks',
            icon=QIcon("images/emptyTracks.png"),
            text='清空',
            onClick=self.emptyTheTracks,
            selectable=False,
            position=NavigationItemPosition.BOTTOM,
        )

        # self.navigationInterface
        # self.navigationInterface.setCurrentItem()
        # self.navigationInterface.setCurrentItem(self.homeInterface.objectName())
        self.navigationInterface.setCurrentItem(self.curveInterface.objectName())

    def initWindow(self):   # 窗口UI初始化

        self.resize(1100, 750)
        self.setWindowIcon(QIcon("images/titleIcon1.png"))
        self.setWindowTitle('Logging-software')
        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.resize(w, h)
        self.move(0, 0)
        # self.move(w//2 - self.width()//2, h//2 - self.height()//2)

    def curveTrackTopRightClicked(self):
        for index, curveTrack in enumerate(self.curveInterface.tracks):
            curveTrack[0].setContextMenuPolicy(Qt.CustomContextMenu)
            # 将点击的曲线道返回
            self.curveInterface.tracks[index][0].customContextMenuRequested.connect(lambda _, theTrack=curveTrack: self.estimate_curveOrdepth(theTrack))
        print('curveTrackTopRightClicked执行了')

    def estimate_curveOrdepth(self, curveTrack):
        sign_curveOrdepth = False # 默认为深度道
        for child_Widget in curveTrack[1].children():
            if isinstance(child_Widget, pg.PlotWidget):
                sign_curveOrdepth = child_Widget.sign_curveOrdepth
        if sign_curveOrdepth:
            self.showContextMenu(curveTrack)

    def showContextMenu(self, curveTrack):     # 鼠标右键点击创建菜单栏
        print('执行了创建菜单栏的函数')
        # 先检查self是否有名为menu的属性，如果有，再检查该属性是不是None
        if hasattr(self, 'contextMenu') and self.contextMenu is not None:
            self.contextMenu.close()  # 关闭旧菜单
        self.contextMenu = RoundMenu()  # 创建一个一级菜单栏
        chooseCurveMenu = RoundMenu(f'选择曲线')   # 创建一个二级菜单栏
        headers = CurveFunction.getTableHeaders()
        for header in headers:
            if header != 'id' and header != 'depth':
                # headers_new.append(header)
                action = QAction(header)
                action.triggered.connect(lambda: self.getClickedActionTitle(curveTrack))
                chooseCurveMenu.addAction(action)
        self.contextMenu.addMenu(chooseCurveMenu)

        # 获取鼠标的全局位置
        global_pos = QCursor.pos()
        # 在鼠标的全局位置显示菜单
        self.contextMenu.exec_(global_pos)

    def getClickedActionTitle(self, curveTrack):
        sender = self.sender()  # 获取发送信号的对象-QAction
        if sender:
            action_title = sender.text()  # 获取 QAction 的标题
            print(f'Clicked Action: {action_title}')
            curve_data = np.squeeze(np.array(CurveFunction.get_theChooseAction_CurveData(action_title)))
            filtered_curve_data = np.where(curve_data == -99999.000, np.nan, curve_data)
            # curve_data_min = np.floor(np.min(filtered_curve_data))  # 曲线值的最小值，向下取整
            # curve_data_max = np.ceil(np.max(filtered_curve_data))  # 曲线值的最大值，向上取整

            # 真实的最大值和最小值-->>曲线值
            curve_data_min = np.nanmin(filtered_curve_data) if not np.isnan(np.nanmin(filtered_curve_data)) else 0
            curve_data_max = np.nanmax(filtered_curve_data) if not np.isnan(np.nanmax(filtered_curve_data)) else 1
            print(f"主窗口：curve_data_min:{curve_data_min}")
            print(f"主窗口：curve_data_max:{curve_data_max}")

            # floor(最小值)和ceil(最大值)-->>曲线值
            curve_data_min_floor = np.floor(curve_data_min)
            curve_data_max_ceil = np.ceil(curve_data_max)
            print(f"主窗口：curve_data_min_floor:{curve_data_min_floor}")
            print(f"主窗口：curve_data_max_ceil:{curve_data_max_ceil}")

            # 设置曲线道名称为选中曲线
            curveTrack[0].findChild(StrongBodyLabel, 'curveName').setText(action_title)
            curveTrack[0].sign_theTitleNameIsChanged = True
            depth = np.squeeze(np.array(CurveFunction.getDepth()))
            depth_min = np.floor(np.min(depth))
            depth_max = np.ceil(np.max(depth))

            # 设置横坐标范标识栏
            theXRangeGroupBox = curveTrack[0].findChild(QGroupBox, 'theXRangeGroupBox')
            if not theXRangeGroupBox.sign_isFilled:
                self.curveInterface.fillTheXRangeGroupBox(theXRangeGroupBox)

            theXRangeGroupBox.theXMin_label.setText(f"{curve_data_min_floor}")
            theXRangeGroupBox.theXMax_label.setText(f"{curve_data_max_ceil}")

            # 使用传递过来的
            for child_widget in curveTrack[1].children():
                if isinstance(child_widget, CustomPlotWidget):
                    self.curveInterface.addVerticalLine(child_widget, action_title, curveTrack)  # 添加垂直线
                    if hasattr(child_widget, 'plotCurve'):
                        child_widget.removeItem(child_widget.plotCurve)
                        print('已经移除原来的绘图')
                    child_widget.plotCurve = child_widget.plot(filtered_curve_data, depth, pen=pg.mkPen('k',width=1)) # 绘图
                    child_widget.sign_isPloted = True
                    # child_widget.sign_isPloted = True
                    if curve_data_max_ceil - curve_data_min_floor <= 2:
                        child_widget.setXRange(curve_data_min, curve_data_max)
                    else:
                        child_widget.setXRange(curve_data_min_floor, curve_data_max_ceil)
                    break

    def mousePressEvent(self, event):
        Globals.sign_clicked_inside_curveTrackTop = False
        if not Globals.sign_clicked_inside_curveTrackTop:
            print('点击了主窗口')
            for track in Globals.tracks:
                curveTrackTop = track[0]
                if isinstance(curveTrackTop, CurveTrackTop):
                    curveTrackTop.curveToolBar.setStyleSheet("border-top: 1px solid rgb(234, 234, 234)")
                    Globals.theTrack = None
                    Globals.curveEditButton.setEnabled(False)
                    Globals.curveEditTable_tool.setEnabled(False)
                    Globals.OutlierEliminator_tool.setEnabled(False)
                    Globals.sign_isClickedOutlierEliminator = False
                    Globals.OutlierEliminator_tool.setChecked(Globals.sign_isClickedOutlierEliminator)
                    for track in Globals.tracks:
                        for child_widget in track[1].children():
                            if isinstance(child_widget, CustomPlotWidget):
                                child_widget.getPlotItem().setMouseEnabled(x=False,
                                                                           y=not Globals.sign_isClickedOutlierEliminator)

    def showEvent_Table(self):
        pass

    def showEvent_Curve(self, event):
        InformationShow.showEvent_Curve(self, event)

    def showMessageBox_newWindow(self):  # 点击帮助按钮显示
        InformationShow.showMessageBox_newWindow(self)

    def closeEvent(self, event):    # 重写窗口的关闭事件
        InformationShow.closeEvent(self, event)

    def retrunDepth(self):
        return TableFunction.getDepth(self)

    def returnCurve(self):
        return TableFunction.getCurveData(self)



if __name__ == '__main__':
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    window = Window()
    window.show()

    app.exec_()
