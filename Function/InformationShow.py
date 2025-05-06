from PyQt5.QtGui import QIcon
from qfluentwidgets import InfoBar, InfoBarPosition, MessageBox
from PyQt5.QtCore import Qt

# 所有的消息弹窗以及窗口弹窗

def showInformation_Waitting(parent, text: str, position):
    # print('正在导入数据...')
    waittingInfor = InfoBar.new(
        icon=QIcon("images/waitting.png"),
        title="稍等",
        content=text,
        orient=Qt.Horizontal,
        isClosable=True,
        position=position,
        duration=-1,
        parent=parent
    )
    # parent.waittingInfor.setCustomBackgroundColor()
    waittingInfor.show()

    return waittingInfor

def showInformation_Success(parent, text: str, position):
    # convenient class mothod
    InfoBar.success(
        title='恭喜',
        content=text,
        orient=Qt.Horizontal,
        isClosable=True,
        position=position,
        # position='Custom',   # NOTE: use custom info bar manager
        duration=2000,
        parent=parent
    )


def showInformation_Error(parent, text, position):
    InfoBar.error(
        title='遗憾',
        content=text,
        orient=Qt.Horizontal,
        isClosable=True,
        position=position,
        duration=2000,  # won't disappear automatically
        parent=parent
    )

def showMessageBox_newWindow(self):
    w = MessageBox(
        '非常抱歉🥰',
        '该模块用来新建一个窗口，由于该项目尚未完成，该模块还未进行开发',
        self
    )
    w.yesButton.setText('尽情期待')
    w.cancelButton.setText('尽情期待')

    if w.exec():
        pass
        # QDesktopServices.openUrl(QUrl("https://afdian.net/a/zhiyiYo"))

def showEvent_Curve(self, event):
    w = MessageBox(
        '非常抱歉🥰',
        '该模块用来提示该软件应该怎样使用，由于该项目尚未完成，该模块还未进行开发',
        self
    )
    w.yesButton.setText('尽情期待')
    w.cancelButton.setText('尽情期待')

    if w.exec():
       pass

def closeEvent(self, event):
    try:
        w = MessageBox(
            '提示',
            '你要关闭该窗口么？',
            self
        )
        w.yesButton.setText('是的')
        w.cancelButton.setText('不是')
        # w.setFixedSize(200,150)
        if w.exec():
            event.accept()
        else:
            event.ignore()
    except Exception as e:
        pass
