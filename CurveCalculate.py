import math
import sys
import time

import mysql
from PyQt5.QtGui import QRegularExpressionValidator, QColor, QFont, QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QHBoxLayout, QGroupBox, QLineEdit, QFrame, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, QRegularExpression, QThread, pyqtSignal, QEvent
from qfluentwidgets import SplitFluentWindow, CardWidget, StrongBodyLabel, LineEdit, InfoBar, InfoBarPosition, \
    InfoBarIcon, SimpleCardWidget, CaptionLabel
from qfluentwidgets import FluentIcon as FIF
import pyqtgraph as pg
import numpy as np

import Globals
from ui import curveCalculate, curve
from Function import DataBaseConnection, CurveFunction, CurveEditFunction, InformationShow


class CurveCalculateMainWindow(SplitFluentWindow):
    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        self.setGeometry(300, 50, 650, 600)
        self.setFixedSize(650, 600)
        self.curveCalcluateInterface = CurveCalcluate('CurveEdit Interface', self)
        self.navigationInterface.hide()
        self.addSubInterface(self.curveCalcluateInterface, FIF.ADD, '曲线编辑')


class CurveCalcluate(CardWidget):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        # 设置ObjectName
        self.setObjectName(text.replace(' ', '-'))
        self.setupUi()
        # 保存最近点的索引
        self.nearest_idx = None
        Globals.curveCalcluateCradWidget = self


    def setupUi(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(11, 40, 11, 11)
        self.setLayout(main_layout)

        subComponent = SubComponent()
        # 从ui文件中获取公式区域
        formulaWidget = subComponent.formulaWidget
        formulaWidget.setParent(self)
        # 左上角按钮
        self.applyButton = subComponent.applyButton
        self.applyButton.setIcon(QIcon("images/apply_red.png"))
        self.applyButton.setToolTip('保存')
        self.applyButton.setEnabled(False)
        # self.applyButton.clicked.connect(self.applyInfor)
        self.applyButton.clicked.connect(self.applyButton_clicked)
        # 表达式下拉选项框
        self.expressionComboBox = subComponent.expressionComboBox
        self.expressionComboBox.setPlaceholderText('请选择一个表达式')
        expressions = ['y=a+x₁', 'y=a-x₁', 'y=a*x₁+b', 'y=a/x₁+b', 'y=a*x₁²+bx₁+c',
                      'y=a*ln(x₁)+b', 'y=a*log₂(x₁)+b', 'y=a*x₁*x₂+b', 'y=a*x₁/x₂',
                      'y=a*x₁+b*x₂+c', 'y=a*x₁²+b*x₂²+c', 'y=a*exp(b*x₁)+c']
        self.expressionComboBox.addItems(expressions)
        self.expressionComboBox.setCurrentIndex(-1)

        self.expressionComboBox.currentTextChanged.connect(lambda :self.expressionComboBoxChange(curvePlot))
        # a,b,c
        # self.aLineEdit = subComponent.aLineEdit
        # self.bLineEdit = subComponent.bLineEdit
        # self.cLineEdit = subComponent.cLineEdit
        self.aLineEdit = ABCLineEdit('a', formulaWidget)
        self.bLineEdit = ABCLineEdit('b', formulaWidget)
        self.cLineEdit = ABCLineEdit('c', formulaWidget)
        self.aLineEdit.setEnabled(False)
        self.bLineEdit.setEnabled(False)
        self.cLineEdit.setEnabled(False)
        self.aLineEdit.setPlaceholderText('a值')
        self.bLineEdit.setPlaceholderText('b值')
        self.cLineEdit.setPlaceholderText('c值')
        self.aLineEdit.setGeometry(40, 140, 71, 33)
        self.bLineEdit.setGeometry(120, 140, 71, 33)
        self.cLineEdit.setGeometry(200, 140, 71, 33)
        self.aLineEdit.textChanged.connect(lambda :self.LineEditChanged(curvePlot))
        self.bLineEdit.textChanged.connect(lambda :self.LineEditChanged(curvePlot))
        self.cLineEdit.textChanged.connect(lambda :self.LineEditChanged(curvePlot))

        # 曲线X1、X2下拉框
        self.X1ComboBox = subComponent.X1ComboBox
        self.X2ComboBox = subComponent.X2ComboBox
        self.X1ComboBox.setEnabled(False)
        self.X2ComboBox.setEnabled(False)
        self.X1ComboBox.setPlaceholderText('请选择x₁曲线')
        self.X2ComboBox.setPlaceholderText('请选择x₂曲线')
        curves = self.getCurve()
        self.X1ComboBox.addItems(curves)
        self.X2ComboBox.addItems(curves)
        self.X1ComboBox.setCurrentIndex(-1)
        self.X2ComboBox.setCurrentIndex(-1)
        self.X1ComboBox.currentTextChanged.connect(lambda :self.X1X2ComboBoxChanged(curvePlot))
        self.X2ComboBox.currentTextChanged.connect(lambda :self.X1X2ComboBoxChanged(curvePlot))

        # 输出曲线名称
        self.outputNameLinEdit = ABCLineEdit('outputName', formulaWidget)
        self.outputNameLinEdit.setGeometry(60, 410, 191, 33)
        self.outputNameLinEdit.setEnabled(False)
        self.outputNameLinEdit.setPlaceholderText('输出曲线名称')
        self.outputNameLinEdit.textChanged.connect(lambda: self.LineEditChanged(curvePlot))
        # 创建正则表达式验证器
        regex = QRegularExpression(r'^[a-zA-Z][a-zA-Z0-9_]{0,63}$')
        validator = QRegularExpressionValidator(regex)
        self.outputNameLinEdit.setValidator(validator)

        # 错误信息标签
        # a,b,c
        self.mistakeA = subComponent.mistakeA
        self.mistakeB = subComponent.mistakeB
        self.mistakeC = subComponent.mistakeC
        self.mistakeA.setStyleSheet('font-size: 10px; color: red;')
        self.mistakeB.setStyleSheet('font-size: 10px; color: red;')
        self.mistakeC.setStyleSheet('font-size: 10px; color: red;')
        Globals.mistakeA = self.mistakeA
        Globals.mistakeB = self.mistakeB
        Globals.mistakeC = self.mistakeC
        # outputName
        self.mistakeOutputName = subComponent.mistake2
        self.mistakeOutputName.setStyleSheet('font-size: 10px; color: red;')
        Globals.mistakeOutputName = self.mistakeOutputName
        # calculateButton
        self.mistakeCalculateButton = subComponent.mistake3
        self.mistakeCalculateButton.setText('')
        self.mistakeCalculateButton.setStyleSheet('font-size: 10px; color: red;')

        # 计算按钮
        self.calculateButton = subComponent.calculateButton
        self.calculateButton.setEnabled(False)
        self.calculateButton.clicked.connect(self.calculateButton_clicked)
        self.calculateButton.setToolTip('快捷键:Enter')

        # 预览按钮
        self.previewButton = subComponent.previewButton
        self.previewButton.setEnabled(False)
        self.sign_previewButton = False
        self.previewButton.clicked.connect(lambda :self.preview(curvePlot, curvePlotTop))
        main_layout.addWidget(formulaWidget)

        # 进度条
        self.progressBar = subComponent.ProgressBar

        # 曲线预览
        curvePlotGroupBox = QGroupBox('曲线预览', self)
        curvePlotGroupBox.setGeometry(375, 0, 310, 600)
        main_layout.addWidget(curvePlotGroupBox)

        # 曲线道顶层
        curvePlotTop = CurveTrackTop(curvePlotGroupBox)
        curvePlotTop.setParent(curvePlotGroupBox)
        curvePlotTop.setGeometry(0, 20, 310, 71)
        self.curveNameLabel = curvePlotTop.findChild(StrongBodyLabel, 'curveName')
        self.fillTheXRangeGroupBox(curvePlotTop.findChild(QGroupBox, 'theXRangeGroupBox'))
        # curvePlotTop.findChild(StrongBodyLabel, 'curveName').setText(self.curveName)

        # 曲线道
        curvePlot = pg.PlotWidget(curvePlotGroupBox)
        # curvePlotGroupBox_layout.addWidget(curvePlot)
        curvePlot.setParent(curvePlotGroupBox)
        curvePlot.setGeometry(0, 71 + 20, 310, 509)
        curvePlot.setStyleSheet("border: 1px solid rgb(180, 180, 180)")
        curvePlot.setBackground('w')  # 设置背景颜色
        curvePlot.getPlotItem().setMouseEnabled(x=False, y=True)  # 只允许上下鼠标拖动，不允许左右鼠标拖动
        curvePlot.invertY(True)  # 逆置纵坐标，从上到下：由小到大
        curvePlot.hideAxis("left")  # 隐藏y轴
        curvePlot.hideAxis("bottom")  # 隐藏x轴
        curvePlot.setLimits(yMin=-1000, yMax=5000)



        # 设置网格线
        self.addGridLines(curvePlot)

    def LineEditChanged(self, curvePlot):
        self.previewButton.setEnabled(False)
        self.previewButton.setChecked(False)
        self.sign_previewButton = False
        self.applyButton.setEnabled(False)
        self.theXMin_label.setVisible(False)
        self.theXMax_label.setVisible(False)
        self.theXRange_line.setVisible(False)

        self.progressBar.setValue(0)

        self.curveNameLabel.setText('曲线名称')
        curvePlot.clear()
        try:
            if hasattr(curvePlot, 'proxy'):
                curvePlot.proxy.deleteLater()
        except Exception as e:
            print('已被删除')
        self.addGridLines(curvePlot)

    def X1X2ComboBoxChanged(self, curvePlot):
        self.previewButton.setEnabled(False)
        self.previewButton.setChecked(False)
        self.sign_previewButton = False
        self.applyButton.setEnabled(False)
        self.theXMin_label.setVisible(False)
        self.theXMax_label.setVisible(False)
        self.theXRange_line.setVisible(False)

        self.progressBar.setValue(0)

        self.curveNameLabel.setText('曲线名称')
        curvePlot.clear()
        try:
            if hasattr(curvePlot, 'proxy'):
                curvePlot.proxy.deleteLater()
        except Exception as e:
            print('已被删除')
        self.addGridLines(curvePlot)

    def expressionComboBoxChange(self, curvePlot):
        self.aLineEdit.setEnabled(False)
        self.bLineEdit.setEnabled(False)
        self.cLineEdit.setEnabled(False)
        self.X1ComboBox.setEnabled(False)
        self.X2ComboBox.setEnabled(False)
        self.previewButton.setEnabled(False)
        self.previewButton.setChecked(False)
        self.sign_previewButton = False
        self.applyButton.setEnabled(False)
        self.mistakeA.setText('')
        self.mistakeB.setText('')
        self.mistakeC.setText('')
        self.mistakeOutputName.setText('')
        self.mistakeCalculateButton.setText('')
        self.progressBar.setValue(0)


        self.theXMin_label.setVisible(False)
        self.theXMax_label.setVisible(False)
        self.theXRange_line.setVisible(False)

        self.curveNameLabel.setText('曲线名称')
        curvePlot.clear()
        try:
            if hasattr(curvePlot, 'proxy'):
                curvePlot.proxy.deleteLater()
        except Exception as e:
            print('已被删除')
        self.addGridLines(curvePlot)

        self.expression = self.expressionComboBox.currentText()
        if self.expression == 'y=a+x₁':
            print('1')
            self.aLineEdit.setEnabled(True)
            self.X1ComboBox.setEnabled(True)
            self.outputNameLinEdit.setEnabled(True)
            self.calculateButton.setEnabled(True)
            pass
        elif self.expression == 'y=a-x₁':
            self.aLineEdit.setEnabled(True)
            self.X1ComboBox.setEnabled(True)
            self.outputNameLinEdit.setEnabled(True)
            self.calculateButton.setEnabled(True)
            pass
        elif self.expression == 'y=a*x₁+b':
            self.aLineEdit.setEnabled(True)
            self.bLineEdit.setEnabled(True)
            self.X1ComboBox.setEnabled(True)
            self.outputNameLinEdit.setEnabled(True)
            self.calculateButton.setEnabled(True)
            pass
        elif self.expression == 'y=a/x₁+b':
            self.aLineEdit.setEnabled(True)
            self.bLineEdit.setEnabled(True)
            self.X1ComboBox.setEnabled(True)
            self.outputNameLinEdit.setEnabled(True)
            self.calculateButton.setEnabled(True)
            pass
        elif self.expression == 'y=a*x₁²+bx₁+c':
            self.aLineEdit.setEnabled(True)
            self.bLineEdit.setEnabled(True)
            self.cLineEdit.setEnabled(True)
            self.X1ComboBox.setEnabled(True)
            self.X1ComboBox.setEnabled(True)
            self.outputNameLinEdit.setEnabled(True)
            self.calculateButton.setEnabled(True)
            pass
        elif self.expression == 'y=a*ln(x₁)+b':
            self.aLineEdit.setEnabled(True)
            self.bLineEdit.setEnabled(True)
            self.X1ComboBox.setEnabled(True)
            self.outputNameLinEdit.setEnabled(True)
            self.calculateButton.setEnabled(True)
            pass
        elif self.expression == 'y=a*log₂(x₁)+b':
            self.aLineEdit.setEnabled(True)
            self.bLineEdit.setEnabled(True)
            self.X1ComboBox.setEnabled(True)
            self.outputNameLinEdit.setEnabled(True)
            self.calculateButton.setEnabled(True)
            pass
        elif self.expression == 'y=a*x₁*x₂+b':
            self.aLineEdit.setEnabled(True)
            self.bLineEdit.setEnabled(True)
            self.X1ComboBox.setEnabled(True)
            self.X2ComboBox.setEnabled(True)
            self.outputNameLinEdit.setEnabled(True)
            self.calculateButton.setEnabled(True)
            pass
        elif self.expression == 'y=a*x₁/x₂':
            self.aLineEdit.setEnabled(True)
            self.X1ComboBox.setEnabled(True)
            self.X2ComboBox.setEnabled(True)
            self.outputNameLinEdit.setEnabled(True)
            self.calculateButton.setEnabled(True)
            pass
        elif self.expression == 'y=a*x₁+b*x₂+c':
            self.aLineEdit.setEnabled(True)
            self.bLineEdit.setEnabled(True)
            self.cLineEdit.setEnabled(True)
            self.X1ComboBox.setEnabled(True)
            self.X2ComboBox.setEnabled(True)
            self.outputNameLinEdit.setEnabled(True)
            self.calculateButton.setEnabled(True)
            pass
        elif self.expression == 'y=a*x₁²+b*x₂²+c':
            self.aLineEdit.setEnabled(True)
            self.bLineEdit.setEnabled(True)
            self.cLineEdit.setEnabled(True)
            self.X1ComboBox.setEnabled(True)
            self.X2ComboBox.setEnabled(True)
            self.outputNameLinEdit.setEnabled(True)
            self.calculateButton.setEnabled(True)
            pass
        elif self.expression == 'y=a*exp(b*x₁)+c':
            self.aLineEdit.setEnabled(True)
            self.bLineEdit.setEnabled(True)
            self.cLineEdit.setEnabled(True)
            self.X1ComboBox.setEnabled(True)
            self.outputNameLinEdit.setEnabled(True)
            self.calculateButton.setEnabled(True)
            pass

    def calculateButton_clicked(self):
        Globals.sign_isCalculateFinished = False
        self.calculate()
        if Globals.sign_isCalculateFinished:
            InformationShow.showInformation_Success(self, '计算完成', InfoBarPosition.TOP_LEFT)
        else:
            InformationShow.showInformation_Error(self, '计算发生错误', InfoBarPosition.TOP_LEFT)

    def calculate(self):
        self.result_list = []
        self.mistakeCalculateButton.setText('')
        # 获取曲线X1、X2
        X1_curve_name = self.X1ComboBox.currentText()
        X2_curve_name = self.X2ComboBox.currentText()
        print(f'X1={X1_curve_name}')
        print(f'X2={X2_curve_name}')
        # 获取两个曲线X1,X2的值
        if X1_curve_name != '':
            X1_curve_data = np.squeeze(np.array(self.getCurveData(X1_curve_name)))
        if X2_curve_name != '':
            X2_curve_data = np.squeeze(np.array(self.getCurveData(X2_curve_name)))

        if self.expression == 'y=a+x₁':
            try:
                self.outputName = self.outputNameLinEdit.text()
                if not self.outputName:
                    raise Exception('Output name cannot be empty.')
                a = float(self.aLineEdit.text())
                print(f'a={a}')
                for X1 in X1_curve_data:
                    if X1 != -99999.000:
                        print(X1)
                        result = X1+ a
                    else:
                        result = -99999.000
                    self.result_list.append(result)
                Globals.sign_isCalculateFinished = True
            except Exception as e:
                Globals.sign_isCalculateFinished = False
                self.mistakeCalculateButton.setText('请核实你的输入')
                if self.outputNameLinEdit.text() == '':
                    self.mistakeOutputName.setText('必填项！')
                if self.aLineEdit.text() == '':
                    Globals.mistakeA.setText('必填项！')
                else:
                    try:
                        float_value = float(self.aLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeA.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeA.setText('请输入有效值！')

        elif self.expression == 'y=a-x₁':
            try:
                self.outputName = self.outputNameLinEdit.text()
                if not self.outputName:
                    raise Exception('Output name cannot be empty.')
                a = float(self.aLineEdit.text())
                for X1 in X1_curve_data:
                    if X1 != -99999.000:
                        result = a - X1
                    else:
                        result = -99999.000
                    self.result_list.append(result)
                Globals.sign_isCalculateFinished = True
            except Exception as e:
                Globals.sign_isCalculateFinished = False
                self.mistakeCalculateButton.setText('请核实你的输入')
                if self.outputNameLinEdit.text() == '':
                    self.mistakeOutputName.setText('必填项！')
                if self.aLineEdit.text() == '':
                    Globals.mistakeA.setText('必填项！')
                else:
                    try:
                        float_value = float(self.aLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeA.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeA.setText('请输入有效值！')
        elif self.expression == 'y=a*x₁+b':
            try:
                self.outputName = self.outputNameLinEdit.text()
                if not self.outputName:
                    raise Exception('Output name cannot be empty.')
                a = float(self.aLineEdit.text())
                b = float(self.bLineEdit.text())
                for X1 in X1_curve_data:
                    if X1 != -99999.000:
                        result = a * X1 +b
                    else:
                        result = -99999.000
                    self.result_list.append(result)
                Globals.sign_isCalculateFinished = True
            except Exception as e:
                Globals.sign_isCalculateFinished = False
                self.mistakeCalculateButton.setText('请核实你的输入')
                if self.outputNameLinEdit.text() == '':
                    self.mistakeOutputName.setText('必填项！')
                if self.aLineEdit.text() == '':
                    Globals.mistakeA.setText('必填项！')
                else:
                    try:
                        float_value = float(self.aLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeA.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeA.setText('请输入有效值！')
                if self.bLineEdit.text() == '':
                    Globals.mistakeA.setText('必填项！')
                else:
                    try:
                        float_value = float(self.bLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeA.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeA.setText('请输入有效值！')
        elif self.expression == 'y=a/x₁+b':
            try:
                self.outputName = self.outputNameLinEdit.text()
                if not self.outputName:
                    raise Exception('Output name cannot be empty.')
                a = float(self.aLineEdit.text())
                b = float(self.bLineEdit.text())
                for X1 in X1_curve_data:
                    if X1 != -99999.000 and X1 != 0:
                        result = a / X1 + b
                    else:
                        result = -99999.000
                    self.result_list.append(result)
                Globals.sign_isCalculateFinished = True
            except Exception as e:
                Globals.sign_isCalculateFinished = False
                self.mistakeCalculateButton.setText('请核实你的输入')
                if self.outputNameLinEdit.text() == '':
                    self.mistakeOutputName.setText('必填项！')
                if self.aLineEdit.text() == '':
                    Globals.mistakeA.setText('必填项！')
                else:
                    try:
                        float_value = float(self.aLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeA.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeA.setText('请输入有效值！')
                if self.bLineEdit.text() == '':
                    Globals.mistakeB.setText('必填项！')
                else:
                    try:
                        float_value = float(self.bLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeB.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeB.setText('请输入有效值！')
        elif self.expression == 'y=a*x₁²+bx₁+c':
            try:
                self.outputName = self.outputNameLinEdit.text()
                if not self.outputName:
                    raise Exception('Output name cannot be empty.')
                a = float(self.aLineEdit.text())
                b = float(self.bLineEdit.text())
                c = float(self.cLineEdit.text())
                for X1 in X1_curve_data:
                    if X1 != -99999.000:
                        result = a * (X1**2) + b * X1 + c
                    else:
                        result = -99999.000
                    self.result_list.append(result)
                Globals.sign_isCalculateFinished = True
            except Exception as e:
                Globals.sign_isCalculateFinished = False
                self.mistakeCalculateButton.setText('请核实你的输入')
                if self.outputNameLinEdit.text() == '':
                    self.mistakeOutputName.setText('必填项！')
                if self.aLineEdit.text() == '':
                    Globals.mistakeA.setText('必填项！')
                else:
                    try:
                        float_value = float(self.aLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeA.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeA.setText('请输入有效值！')
                if self.bLineEdit.text() == '':
                    Globals.mistakeB.setText('必填项！')
                else:
                    try:
                        float_value = float(self.bLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeB.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeB.setText('请输入有效值！')
                if self.cLineEdit.text() == '':
                    Globals.mistakeC.setText('必填项！')
                else:
                    try:
                        float_value = float(self.cLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeC.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeC.setText('请输入有效值！')
        elif self.expression == 'y=a*ln(x₁)+b':
            try:
                self.outputName = self.outputNameLinEdit.text()
                if not self.outputName:
                    raise Exception('Output name cannot be empty.')
                a = float(self.aLineEdit.text())
                b = float(self.bLineEdit.text())
                for X1 in X1_curve_data:
                    if X1 != -99999.000 and X1 > 0:
                        result = a / math.log(X1) + b
                    else:
                        result = -99999.000
                    self.result_list.append(result)
                Globals.sign_isCalculateFinished = True
            except Exception as e:
                Globals.sign_isCalculateFinished = False
                self.mistakeCalculateButton.setText('请核实你的输入')
                if self.outputNameLinEdit.text() == '':
                    self.mistakeOutputName.setText('必填项！')
                if self.aLineEdit.text() == '':
                    Globals.mistakeA.setText('必填项！')
                else:
                    try:
                        float_value = float(self.aLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeA.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeA.setText('请输入有效值！')
                if self.bLineEdit.text() == '':
                    Globals.mistakeB.setText('必填项！')
                else:
                    try:
                        float_value = float(self.bLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeB.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeB.setText('请输入有效值！')
                print(e)
        elif self.expression == 'y=a*log₂(x₁)+b':
            try:
                self.outputName = self.outputNameLinEdit.text()
                if not self.outputName:
                    raise Exception('Output name cannot be empty.')
                a = float(self.aLineEdit.text())
                b = float(self.bLineEdit.text())
                for X1 in X1_curve_data:
                    if X1 != -99999.000 and X1 > 0:
                        result = a / math.log2(X1) + b
                    else:
                        result = -99999.000
                    self.result_list.append(result)
                Globals.sign_isCalculateFinished = True
            except Exception as e:
                Globals.sign_isCalculateFinished = False
                self.mistakeCalculateButton.setText('请核实你的输入')
                if self.outputNameLinEdit.text() == '':
                    self.mistakeOutputName.setText('必填项！')
                if self.aLineEdit.text() == '':
                    Globals.mistakeA.setText('必填项！')
                else:
                    try:
                        float_value = float(self.aLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeA.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeA.setText('请输入有效值！')
                if self.bLineEdit.text() == '':
                    Globals.mistakeB.setText('必填项！')
                else:
                    try:
                        float_value = float(self.bLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeB.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeB.setText('请输入有效值！')
                print(e)
        elif self.expression == 'y=a*x₁*x₂+b':
            try:
                self.outputName = self.outputNameLinEdit.text()
                if not self.outputName:
                    raise Exception('Output name cannot be empty.')
                a = float(self.aLineEdit.text())
                b = float(self.bLineEdit.text())
                for X1, X2 in zip(X1_curve_data, X2_curve_data):
                    if X1 != -99999.000 and X2 != -99999.000:
                        result = a * X1 * X2 + b
                    else:
                        result = -99999.000
                    self.result_list.append(result)
                Globals.sign_isCalculateFinished = True
            except Exception as e:
                Globals.sign_isCalculateFinished = False
                self.mistakeCalculateButton.setText('请核实你的输入')
                if self.outputNameLinEdit.text() == '':
                    self.mistakeOutputName.setText('必填项！')
                if self.aLineEdit.text() == '':
                    Globals.mistakeA.setText('必填项！')
                else:
                    try:
                        float_value = float(self.aLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeA.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeA.setText('请输入有效值！')
                if self.bLineEdit.text() == '':
                    Globals.mistakeB.setText('必填项！')
                else:
                    try:
                        float_value = float(self.bLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeB.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeB.setText('请输入有效值！')
        elif self.expression == 'y=a*x₁/x₂':
            try:
                self.outputName = self.outputNameLinEdit.text()
                if not self.outputName:
                    raise Exception('Output name cannot be empty.')
                a = float(self.aLineEdit.text())
                for X1, X2 in zip(X1_curve_data, X2_curve_data):
                    if X1 != -99999.000 and X2 != -99999.000 and X2 != 0:
                        result = a * X1 / X2
                    else:
                        result = -99999.000
                    self.result_list.append(result)
                Globals.sign_isCalculateFinished = True
            except Exception as e:
                Globals.sign_isCalculateFinished = False
                self.mistakeCalculateButton.setText('请核实你的输入')
                if self.outputNameLinEdit.text() == '':
                    self.mistakeOutputName.setText('必填项！')
                if self.aLineEdit.text() == '':
                    Globals.mistakeA.setText('必填项！')
                else:
                    try:
                        float_value = float(self.aLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeA.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeA.setText('请输入有效值！')
        elif self.expression == 'y=a*x₁+b*x₂+c':
            try:
                self.outputName = self.outputNameLinEdit.text()
                if not self.outputName:
                    raise Exception('Output name cannot be empty.')
                a = float(self.aLineEdit.text())
                b = float(self.bLineEdit.text())
                c = float(self.cLineEdit.text())
                for X1, X2 in zip(X1_curve_data, X2_curve_data):
                    if X1 != -99999.000 and X2 != -99999.000:
                        result = a * X1 + b * X2 + c
                    else:
                        result = -99999.000
                    self.result_list.append(result)
                Globals.sign_isCalculateFinished = True
            except Exception as e:
                Globals.sign_isCalculateFinished = False
                self.mistakeCalculateButton.setText('请核实你的输入')
                if self.outputNameLinEdit.text() == '':
                    self.mistakeOutputName.setText('必填项！')
                if self.aLineEdit.text() == '':
                    Globals.mistakeA.setText('必填项！')
                else:
                    try:
                        float_value = float(self.aLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeA.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeA.setText('请输入有效值！')
                if self.bLineEdit.text() == '':
                    Globals.mistakeB.setText('必填项！')
                else:
                    try:
                        float_value = float(self.bLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeB.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeB.setText('请输入有效值！')
                if self.cLineEdit.text() == '':
                    Globals.mistakeC.setText('必填项！')
                else:
                    try:
                        float_value = float(self.cLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeC.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeC.setText('请输入有效值！')
        elif self.expression == 'y=a*x₁²+b*x₂²+c':
            try:
                self.outputName = self.outputNameLinEdit.text()
                if not self.outputName:
                    raise Exception('Output name cannot be empty.')
                a = float(self.aLineEdit.text())
                b = float(self.bLineEdit.text())
                c = float(self.cLineEdit.text())
                for X1, X2 in zip(X1_curve_data, X2_curve_data):
                    if X1 != -99999.000 and X2 != -99999.000:
                        result = a * (X1**2) + b * (X2**2) + c
                    else:
                        result = -99999.000
                    self.result_list.append(result)
                Globals.sign_isCalculateFinished = True
            except Exception as e:
                Globals.sign_isCalculateFinished = False
                self.mistakeCalculateButton.setText('请核实你的输入')
                if self.outputNameLinEdit.text() == '':
                    self.mistakeOutputName.setText('必填项！')
                if self.aLineEdit.text() == '':
                    Globals.mistakeA.setText('必填项！')
                else:
                    try:
                        float_value = float(self.aLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeA.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeA.setText('请输入有效值！')
                if self.bLineEdit.text() == '':
                    Globals.mistakeB.setText('必填项！')
                else:
                    try:
                        float_value = float(self.bLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeB.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeB.setText('请输入有效值！')
                if self.cLineEdit.text() == '':
                    Globals.mistakeC.setText('必填项！')
                else:
                    try:
                        float_value = float(self.cLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeC.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeC.setText('请输入有效值！')
        elif self.expression == 'y=a*exp(b*x₁)+c':
            try:
                self.outputName = self.outputNameLinEdit.text()
                if not self.outputName:
                    raise Exception('Output name cannot be empty.')
                a = float(self.aLineEdit.text())
                b = float(self.bLineEdit.text())
                c = float(self.cLineEdit.text())
                for X1 in X1_curve_data:
                    if X1 != -99999.000:
                        result = a * math.exp(b * X1) + c
                    else:
                        result = -99999.000
                    self.result_list.append(result)
                Globals.sign_isCalculateFinished = True
            except Exception as e:
                Globals.sign_isCalculateFinished = False
                self.mistakeCalculateButton.setText('请核实你的输入')
                if self.outputNameLinEdit.text() == '':
                    self.mistakeOutputName.setText('必填项！')
                if self.aLineEdit.text() == '':
                    Globals.mistakeA.setText('必填项！')
                else:
                    try:
                        float_value = float(self.aLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeA.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeA.setText('请输入有效值！')
                if self.bLineEdit.text() == '':
                    Globals.mistakeB.setText('必填项！')
                else:
                    try:
                        float_value = float(self.bLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeB.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeB.setText('请输入有效值！')
                if self.cLineEdit.text() == '':
                    Globals.mistakeC.setText('必填项！')
                else:
                    try:
                        float_value = float(self.cLineEdit.text())  # 尝试将输入文本转换为浮点数
                        Globals.mistakeC.setText('')  # 转换成功则清除提示信息
                    except ValueError:  # 转换失败则提示错误
                        Globals.mistakeC.setText('请输入有效值！')
                print(e)

        if len(self.result_list) != 0 and not Globals.sign_isDuplicationOfName and not Globals.sign_isCompliance:
            self.previewButton.setEnabled(True)
            self.applyButton.setEnabled(True)
            print(f'result_list:{self.result_list}')

    # 得到已有的曲线名称
    def getCurvesName(self):
            connection = DataBaseConnection.connect_to_database_test()
            try:
                cursor = connection.cursor()
                try:
                    curves_name = []
                    cursor.execute(f"PRAGMA table_info({Globals.theOpenedWellName})")
                    # cursor.execute(f"SHOW COLUMNS FROM {Globals.theOpenedWellName}")
                    columns = cursor.fetchall()
                    print(f'columns:{columns}')
                    headers = [column[1] for column in columns]

                    for header in headers:
                        if header != 'id' and header != 'depth':
                            curves_name.append(header)

                    return curves_name
                except Exception as e:
                    print(f'曲线计算——获得曲线名错误:{e}')
                finally:
                    cursor.close()
            finally:
                connection.close()




    # 预览
    def preview(self, curvePlot, curvePlotTop):
        self.sign_previewButton = not self.sign_previewButton
        self.labelX = 0 # 用来标识“记录当前深度标签”的横向位置
        if self.sign_previewButton:
            self.curveNameLabel.setText(self.outputName)
            curve_plot_data = np.squeeze(np.array(self.result_list))
            filtered_curve_data = np.where(curve_plot_data == -99999.000, np.nan, curve_plot_data)

            # 真实的最大值和最小值-->>曲线值
            curve_data_min = np.nanmin(filtered_curve_data) if not np.isnan(np.nanmin(filtered_curve_data)) else 0
            curve_data_max = np.nanmax(filtered_curve_data) if not np.isnan(np.nanmax(filtered_curve_data)) else 1


            # floor(最小值)和ceil(最大值)-->>曲线值
            curve_data_min_floor = np.floor(curve_data_min)
            curve_data_max_ceil = np.ceil(curve_data_max)


            depth = np.squeeze(np.array(self.getDepth()))
            depth_min = np.floor(np.min(depth))
            depth_max = np.ceil(np.max(depth))

            # 绘图-->>计算出来的曲线图
            self.plotCurve = curvePlot.plot(filtered_curve_data, depth, pen=pg.mkPen(color=(135, 206, 250), width=1))  # 绘图
            if curve_data_max_ceil - curve_data_min_floor <= 2:
                curvePlot.setXRange(curve_data_min, curve_data_min)
                print(f"曲线计算：curve_data_min:{curve_data_min}")
                print(f"曲线计算：curve_data_max:{curve_data_max}")
                curvePlot.setXRange(curve_data_min, curve_data_max)
                curvePlot.setYRange(depth_min, depth_max)
                self.labelX = curve_data_min
            else:
                print(f"曲线计算：curve_data_min_floor:{curve_data_min_floor}")
                print(f"曲线计算：curve_data_max_ceil:{curve_data_max_ceil}")
                curvePlot.setXRange(curve_data_min_floor, curve_data_max_ceil)
                curvePlot.setYRange(depth_min, depth_max)
                self.labelX = curve_data_min_floor

            self.theXMin_label.setText(f"{curve_data_min_floor}")
            self.theXMax_label.setText(f"{curve_data_max_ceil}")
            # 添加显示深度的标签
            self.addLabelToDepthTrack(curvePlot)

            # 创建一个透明的白色填充色
            transparent_white = pg.QtGui.QColor(255, 255, 255, 0)
            # 创建散点图对象并设置边框颜色为红色，填充色为透明的白色
            self.scatter = pg.ScatterPlotItem(size=8, pen=pg.mkPen(color='r'), brush=transparent_white)
            self.scatter.setData([0], [0])
            curvePlot.addItem(self.scatter)

            # 添加水平线
            self.addHorizontalLine(curvePlot)
            # 添加垂直线
            self.addVerticalLine(curvePlotTop, curvePlot)

            self.theXMin_label.setVisible(True)
            self.theXMax_label.setVisible(True)
            self.theXRange_line.setVisible(True)
        else:
            self.theXMin_label.setVisible(False)
            self.theXMax_label.setVisible(False)
            self.theXRange_line.setVisible(False)

            self.curveNameLabel.setText('曲线名称')
            curvePlot.clear()
            curvePlot.proxy.deleteLater()
            self.addGridLines(curvePlot)

    # 创建一个自定义的多线程类，用来导入计算的得到的新曲线
    class DataImportThread(QThread):
        # 自定义信号，用于向主线程发送信息-->>当前进度的值，更新progressBar
        progress_updated = pyqtSignal(float)
        # 自定义信号，用于向主线程发送信息-->>是否成功完成新曲线的导入
        infor_signal = pyqtSignal(bool)
        def __init__(self, superior):
            super().__init__()
            self.superior = superior
            self.outputName = superior.outputName
            self.result_list = superior.result_list
            self.waittingInfor = superior.waittingInfor

        def run(self):
            self.task_progress = 0
            step_len = 80/len(self.result_list)

            connection = DataBaseConnection.connect_to_database_test()
            try:
                cursor = connection.cursor()
                try:
                    # 在表格中添加新列
                    cursor.execute(f"ALTER TABLE {Globals.theOpenedWellName} ADD COLUMN {self.outputName} FLOAT")
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
                    self.task_progress = 20
                    self.progress_updated.emit(self.task_progress)
                    connection.commit()
                    print('曲线数量+1')

                    # 更新新列的数据，将Null更新为计算后得到的数据
                    for idx, curve_data in enumerate(self.result_list, start=1):
                        self.task_progress += step_len
                        cursor.execute(
                            f"UPDATE {Globals.theOpenedWellName} SET {self.outputName} = ? WHERE id = ?",
                            (curve_data, idx))  # 使用 id 来更新每行数据
                        self.progress_updated.emit(self.task_progress)
                    connection.commit()
                    print("成功向新列中插入数据")
                    self.infor_signal.emit(True)
                except Exception as e:
                    # 回滚事务
                    connection.rollback()
                    self.infor_signal.emit(False)
                    print(f'添加计算得到的新曲线失败：{e}')
                finally:
                    cursor.close()
            finally:
                connection.close()

    def applyButton_clicked(self):
        # 信息提示-->>正在导入新曲线
        self.waittingInfor = InformationShow.showInformation_Waitting(self, f"正在添加{self.outputName}曲线", InfoBarPosition.TOP_LEFT)
        # 创建子线程(数据导入)
        self.dataImportThread = self.DataImportThread(self)
        self.dataImportThread.progress_updated.connect(self.setProgressBarValue)
        self.dataImportThread.infor_signal.connect(self.control_inforShow)
        self.dataImportThread.start()

    # 更新进度栏
    def setProgressBarValue(self, taskprogress):
        self.progressBar.setValue(int(taskprogress))

    # 提示信息-->>用来显示是否完成新曲线的导入
    def control_inforShow(self, sign_IsCurveCalculateImport):
        self.waittingInfor.close()
        if sign_IsCurveCalculateImport:
            InformationShow.showInformation_Success(self, f'成功添加{self.outputName}曲线',InfoBarPosition.TOP_LEFT)
        else:
            InformationShow.showInformation_Error(self, f'添加{self.outputName}失败', InfoBarPosition.TOP_LEFT)

    def mousePressEvent(self, event):
        # print('执行了')
        self.aLineEdit.clearFocus()
        self.bLineEdit.clearFocus()
        self.cLineEdit.clearFocus()
        self.outputNameLinEdit.clearFocus()

    def getDepth(self):
        connection = DataBaseConnection.connect_to_database_test()
        cursor = connection.cursor()

        cursor.execute(f'SELECT depth FROM {Globals.theOpenedWellName}')
        # cursor.execute(f'SELECT depth FROM x12')

        depth = cursor.fetchall()

        cursor.close()
        connection.close()

        return depth

    def getCurveData(self, curve_name):
        connection = DataBaseConnection.connect_to_database_test()
        cursor = connection.cursor()

        cursor.execute(f'SELECT {curve_name} FROM {Globals.theOpenedWellName}')
        # cursor.execute(f'SELECT {curve_name} FROM x12')

        curve_data = cursor.fetchall()

        cursor.close()
        connection.close()

        return curve_data

    def getCurve(self):
        curve = []
        headers = self.getTableHeaders()
        for header in headers:
            if header !='id' and header !='depth':
                curve.append(header)
        return curve

    def getTableHeaders(self):
        connection = DataBaseConnection.connect_to_database_test()
        cursor = connection.cursor()
        cursor.execute(f"PRAGMA table_info({Globals.theOpenedWellName})")
        # cursor.execute(f"SHOW COLUMNS FROM X12")
        columns = cursor.fetchall()
        column_names = [column[1] for column in columns]
        cursor.close()
        connection.close()
        return column_names

    def fillTheXRangeGroupBox(self, theXRangeGroupBox):
        theXRangeGroupBox_layout = QHBoxLayout(theXRangeGroupBox)
        theXRangeGroupBox.setLayout(theXRangeGroupBox_layout)

        self.theXRange_line = QFrame(theXRangeGroupBox)
        self.theXRange_line.setFrameShape(QFrame.HLine)  # 设置为水平线
        self.theXRange_line.setFrameShadow(QFrame.Sunken)
        self.theXRange_line.setFixedWidth(200)  # 设置水平线的长度
        self.theXRange_line.setLineWidth(5)  # 设置水平线的粗细

        self.theXRange_line.setStyleSheet("background-color: black;")

        self.theXMin_label = StrongBodyLabel(theXRangeGroupBox)
        self.theXMin_label.setParent(theXRangeGroupBox)
        self.theXMax_label = StrongBodyLabel(theXRangeGroupBox)
        self.theXMax_label.setParent(theXRangeGroupBox)

        theXRangeGroupBox_layout.addStretch()
        theXRangeGroupBox_layout.addWidget(self.theXMin_label)
        theXRangeGroupBox_layout.addStretch()
        theXRangeGroupBox_layout.addWidget(self.theXRange_line)
        theXRangeGroupBox_layout.addStretch()
        theXRangeGroupBox_layout.addWidget(self.theXMax_label)
        theXRangeGroupBox_layout.addStretch()

        self.theXRange_line.setVisible(False)
        self.theXMin_label.setVisible(False)
        self.theXMax_label.setVisible(False)

        return self.theXMin_label, self.theXMax_label

    # 添加网格线
    def addGridLines(self, plotWidget):
        grid = pg.GridItem()
        plotWidget.addItem(grid)
        grid.setPen(pg.mkPen('k', width=0))

    # 向深度道中添加标签，该标签用于显示当前深度
    def addLabelToDepthTrack(self, plotWidget):
        plotWidget.label = pg.TextItem(text='', color=(0, 0, 0), anchor=(0, 0.5))
        plotWidget.addItem(plotWidget.label)
        plotWidget.proxy = pg.SignalProxy(plotWidget.scene().sigMouseMoved, rateLimit=50,
                                          slot=lambda evt: self.mouseMoved_horizontal(plotWidget, evt))

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
                plotWidget.label.setPos(self.labelX, mousePoint_y.y())
            # 更新 curveNameLabel 的内容：曲线值的大小
            plotWidgetTop.findChild(StrongBodyLabel, 'curveName').setText(
                f'{self.outputName}: {mousePoint_x.x():.6f}')

            # 设置scatter的值
            distances_y = np.sqrt((np.array(self.plotCurve.yData) - y) ** 2)
            min_distance_idx = np.argmin(distances_y)  # 获取索引
            if min_distance_idx != self.nearest_idx:
                nearest_x = self.plotCurve.xData[min_distance_idx]
                nearest_y = self.plotCurve.yData[min_distance_idx]
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


class SubComponent(QMainWindow, curveCalculate.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

class TrackSubComponent(QMainWindow, curve.Ui_Frame):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

class ABCLineEdit(LineEdit):
    def __init__(self, text, parent = None):
        super().__init__(parent)
        self.sign = text

    def focusOutEvent(self, event):
        super().focusOutEvent(event)  # 调用父类的focusInEvent方法
        input_text = self.text().strip()
        if self.sign == 'a':
            if input_text == '':
                Globals.mistakeA.setText('必填项！')
            else:
                try:
                    float_value = float(input_text)  # 尝试将输入文本转换为浮点数
                    Globals.mistakeA.setText('')  # 转换成功则清除提示信息
                except ValueError:  # 转换失败则提示错误
                    Globals.mistakeA.setText('请输入有效值！')

        elif self.sign == 'b':
            if input_text == '':
                Globals.mistakeB.setText('必填项！')
            else:
                try:
                    float_value = float(input_text)  # 尝试将输入文本转换为浮点数
                    Globals.mistakeB.setText('')  # 转换成功则清除提示信息
                except ValueError:  # 转换失败则提示错误
                    Globals.mistakeB.setText('请输入有效值！')

        elif self.sign == 'c':
            if input_text == '':
                Globals.mistakeC.setText('必填项！')
            else:
                try:
                    float_value = float(input_text)  # 尝试将输入文本转换为浮点数
                    Globals.mistakeC.setText('')  # 转换成功则清除提示信息
                except ValueError:  # 转换失败则提示错误
                    Globals.mistakeC.setText('请输入有效值！')
        elif self.sign == 'outputName':
            self.inforWidget.close()
            if input_text == '':
                Globals.mistakeOutputName.setText('必填项！')
            else:
                Globals.sign_isDuplicationOfName = False
                Globals.sign_isCompliance = False
                curves_name = self.getCurvesName()
                for curve_name in curves_name:
                    if input_text == curve_name:
                        Globals.sign_isDuplicationOfName = True
                        break
                if Globals.sign_isDuplicationOfName:
                    Globals.mistakeOutputName.setText('曲线名已存在！')
                elif input_text[0].isdigit():
                    Globals.mistakeOutputName.setText('第一个字符不允许为数字')
                    Globals.sign_isCompliance = True
                else:
                    Globals.mistakeOutputName.setText('')



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
            self.inforWidget.setGeometry(245, 418, 210, 100)
            self.inforWidget.show()
            font = QFont("Arial Rounded MT", 8)
            self.inforLabel.setFont(font)

        if self.sign == 'outputName':
            createInfoInfoBar(Globals.curveCalcluateCradWidget)


    def getCurvesName(self):
        connection = DataBaseConnection.connect_to_database_test()
        try:
            cursor = connection.cursor()
            try:
                curves_name = []
                cursor.execute(f"PRAGMA table_info({Globals.theOpenedWellName})")
                # cursor.execute(f"SHOW COLUMNS FROM {Globals.theOpenedWellName}")
                columns = cursor.fetchall()
                print(f'columns:{columns}')
                headers = [column[1] for column in columns]

                for header in headers:
                    if header != 'id' and header != 'depth':
                        curves_name.append(header)

                return curves_name
            except Exception as e:
                print(f'曲线计算——获得曲线名错误:{e}')
            finally:
                cursor.close()
        finally:
            connection.close()

class CurveTrackTop(CardWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        # self.clicked = pyqtSignal(CardWidget)
        self.initUi()
        self.sign_theTitleNameIsChanged = False

    def initUi(self):
        curveSubComponent = TrackSubComponent()
        curveFrame_width = 325

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
    CurveCalcluate_window = CurveCalculateMainWindow()
    CurveCalcluate_window.show()
    sys.exit(app.exec_())