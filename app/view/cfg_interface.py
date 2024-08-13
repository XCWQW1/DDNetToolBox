import os
import shutil
from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidgetItem, QVBoxLayout, QHeaderView, QLabel, QFileDialog
from qfluentwidgets import TableWidget, CommandBar, Action, FluentIcon, InfoBar, InfoBarPosition, MessageBox, \
    TitleLabel, MessageBoxBase, SubtitleLabel, Dialog

from app.config import cfg
from app.globals import GlobalsVal


class CFGSelectMessageBox(MessageBoxBase):
    """ Custom message box """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.selected_files = None
        self.titleLabel = SubtitleLabel('选择CFG文件')
        self.label = QLabel("拖拽文件到此处或点击选择文件", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("QLabel { border: 2px dashed #aaa; }")

        self.setAcceptDrops(True)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.label)

        # 设置对话框的最小宽度
        self.label.setMinimumWidth(300)
        self.label.setMinimumHeight(100)

        # 连接点击事件
        self.label.mousePressEvent = self.select_file

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = []
        for url in event.mimeData().urls():
            files.append(url.toLocalFile())

        self.selected_files = files
        self.label.setText("\n".join(files))

    def select_file(self, event):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        files, _ = QFileDialog.getOpenFileNames(self, "选择CFG文件", "", "CFG Files (*.cfg);;All Files (*)",
                                                options=options)

        if files:
            self.selected_files = files
            self.label.setText("\n".join(files))

    def get_selected_files(self):
        return self.selected_files


class CFGInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("CFGInterface")

        self.vBoxLayout = QVBoxLayout(self)
        self.commandBar = CommandBar(self)
        self.table = TableWidget(self)

        self.vBoxLayout.addWidget(TitleLabel('CFG管理', self))
        self.setLayout(self.vBoxLayout)

        self.commandBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.addButton(FluentIcon.ADD, '添加'),
        self.addButton(FluentIcon.DELETE, '删除'),
        # self.addButton(FluentIcon.ACCEPT, '启用'),
        # self.addButton(FluentIcon.CLOSE, '禁用'),
        self.addButton(FluentIcon.SYNC, '刷新'),

        self.table.setBorderVisible(True)
        self.table.setBorderRadius(5)
        self.table.setWordWrap(False)
        self.table.setColumnCount(2)

        cfg_list = [file for file in os.listdir(cfg.get(cfg.DDNetFolder)) if file.endswith('.cfg')]
        self.table.setRowCount(len(cfg_list))

        for i, server_link in enumerate(cfg_list, start=0):
            self.table.setItem(i, 0, QTableWidgetItem(server_link))
            """
            if server_link.endswith("disable.cfg"):
                self.table.setItem(i, 0, QTableWidgetItem(server_link))
                self.table.setItem(i, 1, QTableWidgetItem("禁用"))
            else:
                self.table.setItem(i, 0, QTableWidgetItem(server_link))
                self.table.setItem(i, 1, QTableWidgetItem("启用"))
            """

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
            w = CFGSelectMessageBox(self)
            if w.exec():
                files = w.get_selected_files()
                if files is None:
                    InfoBar.error(
                        title='错误',
                        content="您没有选择任何文件",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.BOTTOM_RIGHT,
                        duration=2000,
                        parent=self
                    )
                else:
                    errors = 0
                    cover = 0
                    for i in files:
                        if i.split("/")[-1] in [file for file in os.listdir(cfg.get(cfg.DDNetFolder)) if file.endswith('.cfg')]:
                            cover += 1

                        try:
                            shutil.copy(i, cfg.get(cfg.DDNetFolder))
                        except Exception as e:
                            InfoBar.warning(
                                title='警告',
                                content=f"文件 {i} 复制失败\n原因：{e}",
                                orient=Qt.Horizontal,
                                isClosable=True,
                                position=InfoBarPosition.BOTTOM_RIGHT,
                                duration=2000,
                                parent=self
                            )
                            errors += 1

                    InfoBar.success(
                        title='成功',
                        content=f"文件复制已完成\n共复制了 {len(files)} 个文件，{cover} 个文件被覆盖，{errors} 个文件失败",
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.BOTTOM_RIGHT,
                        duration=2000,
                        parent=self
                    )
                    self.Button_clicked("刷新")
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

            rows_to_delete = {}
            for i in selected_items:
                if i.text() in ["启用", "禁用"]:
                    continue
                rows_to_delete[i.row()] = i.text()

            delete_text = ""
            for i in list(set(i.text() for i in selected_items)):
                if i in ["启用", "禁用"]:
                    continue
                delete_text += f"{i}\n"

            w = MessageBox("警告", f"此操作将会从磁盘中永久删除下列文件，不可恢复：\n{delete_text}", self)
            delete = 0
            if w.exec():
                for i, a in enumerate(rows_to_delete):
                    self.table.removeRow(a)
                    os.remove(f"{cfg.get(cfg.DDNetFolder)}/{rows_to_delete[a]}")
                    delete += 1

            InfoBar.warning(
                title='成功',
                content=f"共删除 {delete} 个文件，{len(rows_to_delete) - delete} 个文件删除失败",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=2000,
                parent=self
            )

        elif text == "刷新":
            self.table.clear()
            self.table.setRowCount(0)
            self.table.clearSelection()

            cfg_list = [file for file in os.listdir(cfg.get(cfg.DDNetFolder)) if file.endswith('.cfg')]
            self.table.setRowCount(len(cfg_list))

            for i, server_link in enumerate(cfg_list, start=0):
                self.table.setItem(i, 0, QTableWidgetItem(server_link))
                """
                if server_link.endswith("disable.cfg"):
                    self.table.setItem(i, 0, QTableWidgetItem(server_link))
                    self.table.setItem(i, 1, QTableWidgetItem("禁用"))
                else:
                    self.table.setItem(i, 0, QTableWidgetItem(server_link))
                    self.table.setItem(i, 1, QTableWidgetItem("启用"))
                """

            InfoBar.success(
                title='成功',
                content="已重新加载本地内容",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=2000,
                parent=self
            )



