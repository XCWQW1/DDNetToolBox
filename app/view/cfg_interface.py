from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidgetItem, QVBoxLayout, QHeaderView
from qfluentwidgets import TableWidget, CommandBar, Action, FluentIcon, InfoBar, InfoBarPosition, MessageBox, TitleLabel

from app.config import cfg
from app.globals import GlobalsVal


class CFGInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("CFGInterface")

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(TitleLabel('CFG管理', self))
        self.setLayout(self.vBoxLayout)

        self.commandBar = CommandBar()
        self.commandBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.addButton(FluentIcon.ADD, '添加'),
        self.addButton(FluentIcon.DELETE, '删除'),
        self.addButton(FluentIcon.SYNC, '刷新'),

        self.table = TableWidget(self)
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(5)
        self.table.setWordWrap(False)
        self.table.setColumnCount(1)

        server_list = GlobalsVal.ddnet_cfg_list
        self.table.setRowCount(len(server_list))

        for i, server_link in enumerate(server_list, start=0):
            self.table.setItem(i, 0, QTableWidgetItem(server_link))

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().hide()

        self.vBoxLayout.addWidget(self.commandBar)
        self.vBoxLayout.addWidget(self.table)

    def addButton(self, icon, text):
        action = Action(icon, text, self)
        action.triggered.connect(partial(self.Button_clicked, text))
        self.commandBar.addAction(action)

    def Button_clicked(self, text):
        print(text)
