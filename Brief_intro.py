from PyQt5.QtWidgets import QFrame, QHBoxLayout


class Brief_intro(QFrame):   # 定义了一个自定义的小部件类 Widget，继承自 QFrame。用于显示界面中的一些基本信息，如应用程序名称、图标等。

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        # self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        # setFont(self.label, 24)
        # self.label.setAlignment(Qt.AlignCenter)
        # self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
        self.setObjectName(text.replace(' ', '-'))