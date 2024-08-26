import os
from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidgetItem, QVBoxLayout, QHeaderView, QLabel
from qfluentwidgets import TableWidget, CommandBar, Action, FluentIcon, InfoBar, InfoBarPosition, MessageBox, \
    TitleLabel, SubtitleLabel, setFont

from app.config import cfg
from app.globals import GlobalsVal


class ServerListInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("ServerListInterface")

        if os.path.abspath(GlobalsVal.ddnet_folder) == os.path.abspath(os.getcwd()):
            self.label = SubtitleLabel("我们的程序无法自动找到DDNet配置目录\n请手动到设置中指定DDNet配置目录", self)
            self.hBoxLayout = QHBoxLayout(self)

            setFont(self.label, 24)
            self.label.setAlignment(Qt.AlignCenter)
            self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
            return

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(TitleLabel('服务器列表管理', self))
        self.setLayout(self.vBoxLayout)

        self.commandBar = CommandBar()
        self.commandBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.addButton(FluentIcon.ADD, '添加'),
        self.addButton(FluentIcon.DELETE, '删除'),
        self.addButton(FluentIcon.SAVE, '保存'),
        self.addButton(FluentIcon.SYNC, '刷新'),
        self.addButton(FluentIcon.UPDATE, '重置'),
        self.addButton(FluentIcon.SPEED_HIGH, '一键加速'),

        self.table = TableWidget(self)
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(5)
        self.table.setWordWrap(False)
        self.table.setColumnCount(1)

        server_list = self.get_server_list()
        self.table.setRowCount(len(server_list))

        for i, server_link in enumerate(server_list, start=0):
            self.table.setItem(i, 0, QTableWidgetItem(server_link))

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().hide()

        self.vBoxLayout.addWidget(self.commandBar)
        self.vBoxLayout.addWidget(self.table)

    def get_server_list(self):
        if GlobalsVal.server_list_file:
            with open(f'{GlobalsVal.ddnet_folder}/ddnet-serverlist-urls.cfg', encoding='utf-8') as f:
                return f.read().split('\n')
        else:
            return ['https://master1.ddnet.org/ddnet/15/servers.json', 'https://master2.ddnet.org/ddnet/15/servers.json', 'https://master3.ddnet.org/ddnet/15/servers.json', 'https://master4.ddnet.org/ddnet/15/servers.json']

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
            if selected_items == []:
                InfoBar.warning(
                    title='警告',
                    content="您没有选择任何东西",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=2000,
                    parent=self
                )
                return

            for item in selected_items:
                self.table.removeRow(item.row())
        elif text == "保存":
            save_txt = ""
            for i in range(self.table.rowCount()):
                selected_items = self.table.item(i, 0).text()
                if selected_items == "":
                    w = MessageBox("警告", "检测到空行，是否删除", self)
                    if w.exec():
                        InfoBar.success(
                            title='成功',
                            content="已剔除当前空行",
                            orient=Qt.Horizontal,
                            isClosable=True,
                            position=InfoBarPosition.BOTTOM_RIGHT,
                            duration=2000,
                            parent=self
                        )
                        continue
                    else:
                        InfoBar.warning(
                            title='警告',
                            content="已保留当前空行",
                            orient=Qt.Horizontal,
                            isClosable=True,
                            position=InfoBarPosition.BOTTOM_RIGHT,
                            duration=2000,
                            parent=self
                        )
                save_txt += f"{selected_items}\n"

            save_txt = save_txt.rstrip('\n')

            if save_txt == "":
                w = MessageBox("警告", "列表内容为空，是否继续写入", self)
                if not w.exec():
                    return

            with open(f'{GlobalsVal.ddnet_folder}/ddnet-serverlist-urls.cfg', 'w', encoding='utf-8') as f:
                f.write(save_txt)

            InfoBar.success(
                title='成功',
                content="服务器列表已保存",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=2000,
                parent=self
            )
            self.Button_clicked('刷新')
        elif text == "刷新":
            self.table.clear()
            self.table.setRowCount(0)
            self.table.clearSelection()

            server_list = self.get_server_list()
            self.table.setRowCount(len(server_list))

            for i, server_link in enumerate(server_list, start=0):
                self.table.setItem(i, 0, QTableWidgetItem(server_link))

            InfoBar.success(
                title='成功',
                content="已重新加载本地资源",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=2000,
                parent=self
            )
        elif text == "重置":
            w = MessageBox("警告", "该操作将会覆盖本地文件中的所有内容", self)
            if w.exec():
                with open(f'{GlobalsVal.ddnet_folder}/ddnet-serverlist-urls.cfg', 'w', encoding='utf-8') as f:
                    f.write('https://master1.ddnet.org/ddnet/15/servers.json\nhttps://master2.ddnet.org/ddnet/15/servers.json\nhttps://master3.ddnet.org/ddnet/15/servers.json\nhttps://master4.ddnet.org/ddnet/15/servers.json')

                self.Button_clicked('刷新')

                InfoBar.success(
                    title='成功',
                    content="已重置服务器列表",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=2000,
                    parent=self
                )
        elif text == "一键加速":
            w = MessageBox("警告", "该操作将会覆盖本地文件中的所有内容", self)
            if w.exec():
                with open(f'{GlobalsVal.ddnet_folder}/ddnet-serverlist-urls.cfg', 'w', encoding='utf-8') as f:
                    f.write('https://master1.ddnet.org/ddnet/15/servers.json\nhttps://master2.ddnet.org/ddnet/15/servers.json\nhttps://master3.ddnet.org/ddnet/15/servers.json\nhttps://master4.ddnet.org/ddnet/15/servers.json\nhttps://xc.null.red:8043/api/ddnet/get_ddnet_server_list\nhttps://midnight-1312303898.cos.ap-nanjing.myqcloud.com/server-list.json')

                self.Button_clicked('刷新')

                InfoBar.success(
                    title='成功',
                    content="已加速服务器列表，重启游戏应用加速",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=2000,
                    parent=self
                )