from functools import partial

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidgetItem, QVBoxLayout, QHeaderView
from qfluentwidgets import TableWidget, CommandBar, Action, FluentIcon


class ServerListInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("ServerListInterface")

        self.vBoxLayout = QVBoxLayout(self)
        self.setLayout(self.vBoxLayout)

        self.commandBar = CommandBar()

        self.addButton(FluentIcon.ADD, '添加'),
        self.addButton(FluentIcon.DELETE, '删除'),
        self.addButton(FluentIcon.SAVE, '保存'),

        self.table = TableWidget(self)

        # 启用边框并设置圆角
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)

        self.table.setWordWrap(False)
        self.table.setRowCount(3)
        self.table.setColumnCount(1)

        # 添加表格数据
        songInfos = [
            ['https://master1.ddnet.org/ddnet/15/servers.json'],
            ['https://master2.ddnet.org/ddnet/15/servers.json'],
            ['https://master4.ddnet.org/ddnet/15/servers.json'],
        ]

        for i, songInfo in enumerate(songInfos):
            self.table.setItem(i, 0, QTableWidgetItem(songInfo[0]))

        # 设置水平表头并隐藏垂直表头
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
        if text == "添加":
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)

            item = QTableWidgetItem("双击我进行编辑")
            self.table.setItem(row_position, 0, item)
        elif text == "删除":
            selected_items = self.table.selectedItems()
            for item in selected_items:
                self.table.removeRow(item.row())
            pass
        elif text == "保存":
            pass
