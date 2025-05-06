from PyQt5.QtGui import QPixmap, QLinearGradient, QPainter, QBrush, QCursor,  QColor
from PyQt5.QtCore import Qt

# +形状的鼠标
def createCrossCursor():
    size = 15
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)  # 设置背景为透明

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    # 创建画刷
    brush = QBrush(Qt.black)
    painter.setBrush(brush)

    pen = painter.pen()
    pen.setColor(QColor(Qt.black))
    pen.setWidth(2)
    painter.setPen(pen)

    # 绘制十字形状
    painter.drawLine(size // 2, 0, size // 2, size)
    painter.drawLine(0, size // 2, size, size // 2)

    painter.end()

    return QCursor(pixmap, size // 2, size // 2)



# ×形状的鼠标
def createXCursor():
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
