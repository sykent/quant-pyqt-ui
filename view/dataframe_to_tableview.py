import os

from qtpy import uic

from constants.appconstants import ui_dir_path
from viewmodel.pdviewmodel import PdTable


class DataframeToTableviewDemo:
    def __init__(self):
        # 表格
        self.model = PdTable(column=2)

        self._init_view()
        self._init_listener()
        self._init_data()

    pass

    def _init_view(self):
        self.ui = uic.loadUi(os.path.join(ui_dir_path, 'designer/tab_industry.ui'), self)
        pass

    def _init_data(self):
        pass

    def _init_listener(self):
        pass
