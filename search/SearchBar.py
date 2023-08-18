import os
import re

import pandas as pd
import qdarkstyle
from PyQt5.QtCore import Qt, QEvent, QSortFilterProxyModel, pyqtSignal
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QCompleter, QVBoxLayout, QWidget, QSizePolicy
from pypinyin import pinyin, Style


class SearchBar(QMainWindow):
    """
    搜索栏，用于搜索股票，板块，指数
    数据初始化数据类型为tuple数组，分别是[(股票代码,股票名称,代码归类)]
    列如：[('000001', '平安银行', '股票'),('BK1037', '消费电子', '板块'),('sh000852', '中证1000', '指数')]
    搜索完后，按上下键选中，按回车键选择
    """
    # 选择搜索结果后的回调
    select_item_signal = pyqtSignal(tuple)

    def __init__(self, parent=None):
        super().__init__()
        # 回调信号槽
        # 父窗口，用于显示搜索窗口的位置
        self.parent = parent
        self._init_view()
        self._init_listener()

    def _init_view(self):
        """
        初始化搜索栏工具条
        """
        self.setStyleSheet(qdarkstyle.load_stylesheet())

        self.setWindowTitle("键盘小精灵")
        # 隐藏标题栏中的最小化、最大化和帮助按钮
        self.setWindowFlags(self.windowFlags()
                            & ~Qt.WindowMinMaxButtonsHint
                            & ~Qt.WindowContextHelpButtonHint)

        # 设置无标题栏
        # self.setWindowFlags(Qt.FramelessWindowHint)
        # 设置搜索栏的宽高
        self.setGeometry(100, 100, 300, 50)

        self.search_combobox = ExtendedComboBox(self.select_item_signal, self)

        # 创建布局和容器
        layout = QVBoxLayout()
        widget = QWidget()

        # 将搜索控件添加到布局中,设置布局的外边距
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.search_combobox.setSizePolicy(size_policy)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.addWidget(self.search_combobox)
        widget.setLayout(layout)

        # 设置窗口的主部件
        self.setCentralWidget(widget)

    def _init_listener(self):
        """
        监听事件
        """
        self.select_item_signal.connect(self._on_select_item)

    def set_data(self, data: list):
        """
        数据是tuple类型数组,分别是(股票代码,股票名称,归类)
        列如：('000001', '平安银行', '股票')
        """
        self.search_combobox.set_data(data)

    def _on_select_item(self, item):
        """
        选择搜索结果后的回调
        """
        self.close()

    def mousePressEvent(self, evt):
        """
        隐藏标题栏 可拖动，需重写mousePressEvent，mouseMoveEvent
        """

        # 获取鼠标当前的坐标
        self.mouse_x = evt.globalX()
        self.mouse_y = evt.globalY()

        # 获取窗体当前坐标
        self.origin_x = self.x()
        self.origin_y = self.y()

    def mouseMoveEvent(self, evt):
        """
        鼠标移动事件，用于拖动窗体
        """

        # 计算鼠标移动的x，y位移
        move_x = evt.globalX() - self.mouse_x
        move_y = evt.globalY() - self.mouse_y

        # 计算窗体更新后的坐标：更新后的坐标 = 原本的坐标 + 鼠标的位移
        dest_x = self.origin_x + move_x
        dest_y = self.origin_y + move_y

        # 移动窗体
        self.move(dest_x, dest_y)

    def event(self, event):
        """
        事件监听，当窗口失去焦点时关闭窗口
        """
        if event.type() == QEvent.WindowDeactivate:
            self.close()
            return True
        if event.type() == QEvent.KeyPress:
            pass

        return super().event(event)

    def showEvent(self, event):
        """
        重写showEvent方法，当窗口显示时，
        如果 attach_window 不未空，显示在 attach_window 的左下方
        否则将窗口移动到鼠标位置
        """
        super().showEvent(event)
        if self.parent:
            # 获取 attach_window 的左下方的坐标
            pos = self.parent.pos()
            p_x = pos.x()
            p_y = pos.y()
            p_width = self.parent.width()
            p_height = self.parent.height()
            # 将窗口移动到 attach_window 的右下方
            x = p_x + p_width - self.width() - 10
            y = int(p_y + 0.4 * p_height)
            self.move(x, y)
        else:
            # 获取鼠标位置
            mouse_pos = QCursor.pos()
            # 将窗口移动到鼠标位置
            self.move(mouse_pos.x(), mouse_pos.y())

    def clear_text(self):
        """
        清空搜索框
        """
        self.search_combobox.clearEditText()

    def set_text(self, text):
        self.search_combobox.setEditText(text)


class ExtendedComboBox(QComboBox):
    """
    自定义QComboBox，添加筛选功能
    """

    def __init__(self, select_item_signal, parent=None):
        """
        select_item_signal 回调信号槽
        """
        self.select_item = select_item_signal
        # 外面传进来的数据
        self.data = None

        super(ExtendedComboBox, self).__init__(parent)
        # self.setFocusPolicy(Qt.StrongFocus)
        self.setEditable(True)

        # 添加筛选器模型来筛选匹配项
        self.pFilterModel = StockFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(Qt.CaseInsensitive)  # 大小写不敏感
        self.pFilterModel.setSourceModel(self.model())

        # 添加一个使用筛选器模型的QCompleter
        self.completer = QCompleter(self.pFilterModel, self)
        # 始终显示所有(过滤后的)补全结果
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)  # 不区分大小写
        self.setCompleter(self.completer)

        # Qcombobox编辑栏文本变化时对应的槽函数
        self.lineEdit().textEdited.connect(self.pFilterModel.setFilterFixedString)
        self.completer.activated.connect(self.on_completer_activated)
        self.lineEdit().setPlaceholderText("输入...")

    def set_data(self, data: list):
        """
        数据是tuple类型数组,分别是(股票代码,股票名称,归类)
        列如：('000001', '平安银行', '股票')
        """

        self.data = data

        # 转为字符串数组，固定宽度，右对齐最后一个字符串
        width = 30
        items = []
        for item in data:
            text = f"{item[1]} ({item[0]})"
            text = f'{text:<{width}}' + item[2]
            items.append(text)

        self.addItems(items)

        # 获取 filter
        filter_map = {}
        # 将中文转换为拼音
        for item in data:
            code = item[0]
            name = item[1]
            pinyin_list = pinyin(name, style=Style.NORMAL)

            # 获取拼音首字母
            pinyin_list = [py[0].lower() for py in pinyin_list]
            pinyin_str = ''.join([py[0] for py in pinyin_list])

            # 自身以及code
            pinyin_str = pinyin_str + name.lower() + code
            # 以 code 为key
            filter_map[code] = pinyin_str

        self.pFilterModel.setFilterMap(filter_map)

    def on_completer_activated(self, text):
        """
        当在Qcompleter列表选中候，下拉框项目列表选择相应的子项目，
        并触发相应的信号将选中的条目回调出去
        """

        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)
            # 选中自定义信号,回调出去
            text = self.itemText(index)
            # 获取括号的内容
            code = re.search(r'\((.*?)\)', text).group(1)
            data = self.data[index]
            self.select_item.emit(data)

    def setModel(self, model):
        """
        在模型更改时，更新过滤器和补全器的模型
        """

        super(ExtendedComboBox, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)

    def setModelColumn(self, column):
        """
        在模型列更改时，更新过滤器和补全器的模型列
        """

        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(ExtendedComboBox, self).setModelColumn(column)

    def keyPressEvent(self, e):
        """
        重写键盘事件，当按下回车键时，选中当前选项
        """
        if e.key() == Qt.Key_Enter & e.key() == Qt.Key_Return:
            text = self.currentText()
            index = self.findText(text, Qt.MatchExactly | Qt.MatchCaseSensitive)
            self.setCurrentIndex(index)
            self.hidePopup()
        elif e.key() == Qt.Key_Delete:
            # 按delete键时，清空编辑框
            self.clearEditText()

        super(ExtendedComboBox, self).keyPressEvent(e)


class StockFilterProxyModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        super(StockFilterProxyModel, self).__init__(parent)
        # code 对应的filter
        self.filter_map = None

    def setFilterMap(self, filter_map):
        self.filter_map = filter_map

    def filterAcceptsRow(self, source_row, source_parent):
        """
        重写filterAcceptsRow方法，当某一行包含筛选文本时，返回True，否则返回False
        中文拼音的首字母也会被匹配，例如：输入"zg"，"中国"也会被匹配
        自身中文也会被匹配，例如：输入"中国"，"中国"也会被匹配
        股票代码也会被匹配，例如：输入"000001"，"平安银行"也会被匹配
        """
        source_model = self.sourceModel()
        index = source_model.index(source_row, self.filterKeyColumn(), source_parent)
        item = source_model.data(index, Qt.DisplayRole)

        # 获取输入框的文本，去掉空格，转为小写
        text = self.filterRegExp().pattern().lower().replace(" ", "")
        if text == "":
            return False

        # 获取code
        left_index = item.find("(")
        right_index = item.find(")")
        if left_index != -1 and right_index != -1:
            code = item[left_index + 1: right_index]
        else:
            code = ""

        if self.filter_map is not None:
            pinyin_str = self.filter_map[code]
        else:
            pinyin_str = ""

        # 判断是否匹配
        condition = text in pinyin_str
        # print('item', item, 'pinyin_str', pinyin_str, 'condition', condition)

        # 判断是否匹配
        return condition


class MainWin(QMainWindow):
    """
    主窗口
    使用示例，工程按示例接入工程的主窗口即可
    """

    def __init__(self):
        super().__init__()
        self._init_view()
        self._init_listener()

    def _init_view(self):
        """
        初始化搜索栏工具条
        """
        self.setStyleSheet(qdarkstyle.load_stylesheet())
        self.setGeometry(100, 100, 1000, 600)

        # 在主题窗口初始化搜索栏
        self.search_bar = SearchBar(self)
        stock_data = self._stock_data()
        industry_data = self._industry_data()
        market_data = self._market_data()
        data = stock_data + industry_data + market_data
        self.search_bar.set_data(data)

    def keyPressEvent(self, e):
        """
        重写键盘事件
        """
        # 判断是字母和数字，弹起搜索栏
        if Qt.Key_A <= e.key() <= Qt.Key_Z \
                or Qt.Key_0 <= e.key() <= Qt.Key_9 \
                or Qt.Key_Space == e.key():
            self.show_search_bar(e.text())
            print(e.text())

        super(MainWin, self).keyPressEvent(e)

    def show_search_bar(self, text):
        """
        显示搜索栏,并搜索栏输入文本
        如果没有显示则显示，否则不处理
        """
        if not self.search_bar.isVisible():
            self.search_bar.set_text(text.strip())
            self.search_bar.show()

    def _stock_data(self) -> list:
        """
        获取股票数据，工程请用数据库或本地数据
        """
        # 获取网络股票代码和股票名
        # stock_df = ak.stock_info_a_code_name()
        # 获取该类所处的目录,
        stock_df = pd.read_csv(rf'{os.path.dirname(__file__)}\stock.csv', dtype={
            'code': str, 'name': str}, index_col=0)
        # 转为list
        stock_list = stock_df.values.tolist()
        stock_list = [(stock[0], stock[1], '股票') for stock in stock_list]
        return stock_list

    def _industry_data(self) -> list:
        """
        获取板块数据，工程请用数据库或本地数据
        """
        # 获取该类所处的目录,
        industry_df = pd.read_csv(rf'{os.path.dirname(__file__)}\industry.csv', dtype={
            'code': str, 'name': str}, index_col=0)
        # 转为list
        industry_list = industry_df.values.tolist()
        industry_list = [(industry[0], industry[1], '板块') for industry in industry_list]
        return industry_list

    def _market_data(self) -> list:
        """
        获取指数数据，工程请用数据库或本地数据
        """
        # 获取该类所处的目录,
        market_df = pd.read_csv(rf'{os.path.dirname(__file__)}\market.csv', dtype={
            'code': str, 'name': str}, index_col=0)
        # 转为list
        market_list = market_df.values.tolist()
        market_list = [(market[0], market[1], '指数') for market in market_list]
        return market_list

    def _init_listener(self):
        # 选择搜索结果后的回调
        self.search_bar.select_item_signal.connect(self._on_search_callback)
        pass

    def _on_search_callback(self, item):
        """
        选择搜索结果后的回调
        """
        print(item)

        code = item[0]
        name = item[1]
        item_type = item[2]
        if item_type == '股票':
            print(f'选中股票：代码：{code}，名称：{name}')
        elif item_type == '板块':
            print(f'选中板块：代码：{code}，名称：{name}')
        elif item_type == '指数':
            print(f'选中指数：代码：{code}，名称：{name}')


if __name__ == '__main__':
    app = QApplication([])
    # 设置样式表
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    mainWin = MainWin()
    mainWin.show()
    app.exec_()
