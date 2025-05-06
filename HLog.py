import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from MyMainWindow import Window

QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

app = QApplication(sys.argv)

window = Window()
window.show()

app.exec_()