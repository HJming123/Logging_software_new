from qfluentwidgets import InfoBarPosition

import Globals
from Function import InformationShow


def handleOpenWellButtonClicked(self):
    # 在这里执行打开文件按钮点击后的逻辑
    # print("Open well button clicked!")
    self.getData.import_las_file()  # 导入las井文件数据
    try:
        if self.getData.sign_whetherTheWellFileIsOpened:
            InformationShow.showInformation_Success(self, f"{Globals.theOpenedWellName}.las文件已成功导入数据库！", InfoBarPosition.TOP_RIGHT)
            self.getData.sign_whetherTheWellFileIsOpened = False
        else:
            InformationShow.showInformation_Error(self, f".las文件导入失败！", InfoBarPosition.TOP_RIGHT)
    except Exception as e:
        print(e)
    # self.tableInterface.sign = True
    self.sign_iftheDatatoDatabase = True
    self.fenYeChaXun()

def handleOpenWellButtonClicked1(self):
    pass