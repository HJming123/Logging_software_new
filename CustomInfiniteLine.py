import pyqtgraph as pg
from PyQt5.QtGui import QPixmap, QPainter, QLinearGradient, QBrush, QColor, QCursor
from PyQt5.QtCore import Qt, QTimer

import Globals


class CustomLayeredLine(pg.InfiniteLine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAcceptHoverEvents(True)
        self.hovering = False  # 初始时鼠标不在上面
        self.tolerance = 10  # 容差值，单位为像素
        self.custom_deleteCursor = self.createXCursor()

    # def hoverEvent(self, ev):
    #     if ev.enter:
    #         self.hovering = True
    #         # 在这里可以添加鼠标进入时的处理代码
    #         self.setCursor(self.custom_deleteCursor)
    #         print("鼠标进入")
    #     else:
    #         pos = ev.pos()
    #         if pos.x() < -self.tolerance or pos.x() > self.boundingRect().width() + self.tolerance \
    #                 or pos.y() < -self.tolerance or pos.y() > self.boundingRect().height() + self.tolerance:
    #             self.hovering = False
    #             # 在这里可以添加鼠标离开时的处理代码
    #             self.unsetCursor()
    #             print("鼠标离开")

    # 自定义×鼠标形状
    def createXCursor(self):
        size = 15
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)  # 设置背景为透明

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        # 创建渐变效果
        gradient = QLinearGradient(0, 0, size, size)
        gradient.setColorAt(0, QColor(Qt.white))
        gradient.setColorAt(1, QColor(Qt.black))

        # 创建画刷并应用渐变
        brush = QBrush(gradient)
        painter.setBrush(brush)

        pen = painter.pen()
        pen.setColor(QColor(Qt.black))
        pen.setWidth(2)
        painter.setPen(pen)

        # 绘制“X”形状
        painter.drawLine(0, 0, size, size)
        painter.drawLine(0, size, size, 0)

        painter.end()

        return QCursor(pixmap, size // 2, size // 2)

class CustomTextItem(pg.TextItem):
    def __init__(self, text, *args, **kwargs):
        super().__init__(text, *args, **kwargs)


import pyqtgraph as pg
from PyQt5.QtCore import Qt

