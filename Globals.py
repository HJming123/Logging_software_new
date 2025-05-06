import numpy as np

from Function import CurveEditFunction

# 被打开井的井名
theOpenedWellName = None
# 被打开井的id
theOpenedWellId = None

# 用来判断是否已经导入文件
sign_whetherTheWellFileIsOpened = False
# 用来判断是否数据库内已有相同的井
sign_hasSameWellName = False

# 执行标志，是否已经执行了分层函数，若执行了则为True， 若未执行则为False
# 主要目的：控制鼠标形状
sign_addLayeredLine = False

# 用来判断添加分层窗口是否点击了确定按钮
Sign_WhetherAddLayerIsOk = False

# 分层线的数量

# 控制分层线是否可移动
sign_LayerLineIsMovable = False

# 分页查询的标志，用来对分页查询进行控制
current_page = 1    # 记录当前页码
page_size = 50     # 记录每一页的行数
total_pages = 0     # 记录总共有多少页

# 当鼠标为➕时，鼠标点击的位置对应在PlotWidget中的数值
theMousePressXPos = 0   # X坐标
theMousePressYPos = 0   # Y坐标------------> 用来记录分层功能中，水平分层线要添加的位置

# 包含所有曲道
tracks = []

# 包含所有的分层线，里面包含分层线对象，和分层线对应的名称标签
layerLines = []

# 是否删除分层线标志
sign_deleteLayerLine = False

# 鼠标点击位置是否在curveTrackTop里面
sign_clicked_inside_curveTrackTop = False

# 用来存储当前要操作的曲道
theTrack = None

# 用来存储当前要操作的曲道名称
theTrackName = ''

# 判断曲线道是否已经选择了曲线
sign_theTitleNameIsChanged = False

# 用来存储曲线计算按钮
curveEditButton = None
# 曲线表格编辑快捷按钮
curveEditTable_tool = None
# 曲线异常值剔除快捷按钮
OutlierEliminator_tool = None
# 曲线异常值剔除是否开始
sign_isClickedOutlierEliminator = False

# # 用来存储测深列表
# depth = np.squeeze(np.array(CurveEditFunction.getDepth(cursor)))

# 错误信息提示框
mistakeA = None
mistakeB = None
mistakeC = None
mistakeOutputName = None

# 当前井曲线的数量
curveNum = 0
layerNum = 0

# 在添加新计算的曲线时，用来判断是否已有同名的曲线存在
sign_isDuplicationOfName = False
# 在添加新计算的曲线时， 用来判断该曲线名是否合规
sign_isCompliance = False

# 深度
depth_min = 0
depth_max = 0

# 曲线异常值剔除的框架
deleteOutlierWidget = None

# 曲线计算的框架
curveCalcluateCradWidget = None

# 计算得到的曲线是否成功导入数据库
sign_IsCurveCalculateImport = False
# 曲线计算是否完成
sign_isCalculateFinished = False

xmistake_L = None
ymistake_L = None
xmistake_R = None
ymistake_R = None
mistake3 = None

# 矩形框
rectItem = None
