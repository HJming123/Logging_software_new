import sys
from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtGui import QPixmap, QPainter, QFont, QColor
from PyQt5.QtCore import Qt

def text_to_image(text):
    try:
        # 创建 QPixmap 并设置大小
        pixmap = QPixmap(150, 70)
        pixmap.fill(Qt.transparent)  # 填充透明背景
        # pixmap.fill(Qt.white)  # 填充白色背景

        # 创建 QPainter 对象，并在 QPixmap 上绘制文本
        print(len(text))
        painter = QPainter(pixmap)
        if len(text) <= 4:
            print('1')
            painter.setFont(QFont('Arial', 35))
        else:
            painter.setFont(QFont('Arial', 30))
        # if
        painter.drawText(pixmap.rect(), Qt.AlignCenter, text)
        painter.end()

        return pixmap
    except Exception as e:
        print(f"绘制图片时出现异常：{e}")
        return None


    # file_path = "images/"  # 替换为您想要保存的目录路径
    # file_name = file_path + f'{text.lower()}.png'
    # # 创建 QLabel 用于绘制文本
    # label = QLabel()
    # label.setFont(QFont('Arial', 26))  # 设置字体
    # label.setText(text)
    # label.adjustSize()  # 调整大小以适应文本
    #
    # # 设置 QLabel 的固定大小
    # label.setFixedSize(label.sizeHint())
    #
    # # 创建 QPixmap 并将 QLabel 绘制到 QPixmap 上
    # pixmap = QPixmap(label.size())
    # pixmap.fill(Qt.transparent)  # 使用透明背景
    # painter = QPainter(pixmap)
    # label.render(painter)
    #
    # # 保存 QPixmap 到文件
    # pixmap.save(file_name)
    # print('已完成绘制文字')


