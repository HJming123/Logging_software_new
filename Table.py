# import PyQt5.QtWidgets as qw
from PyQt5.QtWidgets import QWidget, QHBoxLayout, \
    QVBoxLayout
from qfluentwidgets import TableWidget, PrimaryPushButton, MessageBox


class Table(QWidget):

    def __init__(self, text: str, parent = None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(' ', '-'))
        # setTheme(Theme.DARK)
        self.setupUi()
        self.sign = False
        # self.import_to_table()


    def CheckHaveData(self):
        if self.tableInterface.sign:
            # self.setupUi()
            pass
        else:
            w = MessageBox(
                '提示🥰',
                '你还未导入数据',
                self
            )
            w.yesButton.setText('现在导入')
            w.cancelButton.setText('稍后导入')

            if w.exec():
                pass


    def setupUi(self):
        self.vBoxLayout = QVBoxLayout(self)
        self.tableView = TableWidget(self)

        # select row on right-click
        # self.tableView.setSelectRightClickedRow(True)

        # enable border
        self.tableView.setBorderVisible(True)
        self.tableView.setBorderRadius(8)

        self.tableView.setWordWrap(False)   # 设置表格试图的文本换行行为属性为禁用状态

        self.tableView.verticalHeader().hide()      # 隐藏表格视图中的垂直表头
        # self.tableView.setHorizontalHeaderLabels(['Title', 'Artist', 'Album', 'Year', 'Duration'])
        # self.tableView.resizeColumnsToContents()    # 自动调整表格视图中列的宽度，使列的内容适应列的宽度。
        # self.tableView.horizontalHeader().setSectionResizeMode(qw.QHeaderView.Stretch)
        self.tableView.setSortingEnabled(False)

        # 设置表格为只读模式
        self.tableView.setEditTriggers(TableWidget.NoEditTriggers)
        self.setStyleSheet("Demo{background: rgb(255, 255, 255)} ")
        self.vBoxLayout.setContentsMargins(50, 30, 50, 30)
        self.vBoxLayout.addWidget(self.tableView)
        self.resize(735, 760)

        self.prev_button = PrimaryPushButton('前一页', self)
        # self.prev_button = QPushButton("Previous")
        # self.prev_button.clicked.connect(self.load_previous_page)

        self.next_button = PrimaryPushButton('下一页', self)
        # self.next_button = QPushButton("Next")
        # self.next_button.clicked.connect(self.load_next_page)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.prev_button)
        self.hBoxLayout.addWidget(self.next_button)

        self.vBoxLayout.addLayout(self.hBoxLayout)


