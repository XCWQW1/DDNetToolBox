import os
import shutil
import threading
from functools import partial

from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt5.QtGui import QFontMetrics, QPainter, QBrush, QPainterPath
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QLabel, QFileDialog, QPushButton, QHBoxLayout
from qfluentwidgets import CommandBar, Action, FluentIcon, InfoBar, InfoBarPosition, Pivot, TitleLabel, CardWidget, \
    ImageLabel, CaptionLabel, FlowLayout, SingleDirectionScrollArea, MessageBoxBase, SubtitleLabel, MessageBox, \
    RadioButton, TogglePushButton, ToolTipFilter, ToolTipPosition, PrimaryPushButton, setFont

from app.config import cfg
from app.globals import GlobalsVal
from app.utils.draw_tee import draw_tee


select_list = {
    "skins": {},
    "game": {},
    "emoticons": {},
    "cursor": {},
    "particles": {},
    "entities": {}
}
button_select = None


class FileSelectMessageBox(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_files = None
        self.titleLabel = SubtitleLabel('选择文件')
        self.label = QLabel("拖拽文件到此处或点击选择文件", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("QLabel { border: 2px dashed #aaa; }")

        self.setAcceptDrops(True)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.label)

        self.label.setMinimumWidth(300)
        self.label.setMinimumHeight(100)

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
        files, _ = QFileDialog.getOpenFileNames(self, "选择文件", "", "All Files (*)",
                                                options=options)

        if files:
            self.selected_files = files
            self.label.setText("\n".join(files))

    def get_selected_files(self):
        return self.selected_files


class ResourceCard(CardWidget):
    selected = False

    def __init__(self, file, card_type, parent=None):
        super().__init__(parent)
        global button_select

        self.card_type = card_type
        self.file = file
        self.setFixedSize(135, 120)

        if self.card_type == "skins":
            self.iconWidget = ImageLabel(draw_tee(self.file), self)
            self.iconWidget.scaledToHeight(110)
        else:
            self.iconWidget = ImageLabel(self.file, self)
            if self.card_type == "entities":
                self.iconWidget.scaledToHeight(100)
            else:
                self.iconWidget.scaledToHeight(60)

        self.label = CaptionLabel(self)
        self.label.setText(self.get_elided_text(self.label, os.path.basename(self.file)[:-4]))
        self.label.setToolTip(os.path.basename(self.file)[:-4])
        self.label.setToolTipDuration(1000)
        self.label.installEventFilter(ToolTipFilter(self.label, showDelay=300, position=ToolTipPosition.BOTTOM))

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignCenter)

        if self.card_type == "cursor":
            self.button = TogglePushButton("启用", self)
            self.button.clicked.connect(self.__button_clicked)
            self.vBoxLayout.addWidget(self.button, 0, Qt.AlignCenter)

            self.select_cursor = cfg.get(cfg.DDNetAssetsCursor)
            if self.select_cursor is not None:
                if file == self.select_cursor:
                    self.button.setText('禁用')
                    button_select = self.button

        self.vBoxLayout.addWidget(self.label, 0, Qt.AlignCenter)

        self.clicked.connect(self.__on_clicked)

    def __button_clicked(self, checked):  # gui_cursor.png
        global button_select
        if button_select is not None and button_select != self.button:
            button_select.setChecked(False)
            button_select.setText('启用')

        ddnet_folder = GlobalsVal.ddnet_folder

        if checked:
            self.button.setText('禁用')
            button_select = self.button
            cfg.set(cfg.DDNetCheckUpdate, self.file)

            shutil.copy(self.file, f"{ddnet_folder}/gui_cursor.png")
        else:
            self.button.setText('启用')
            os.remove(f"{ddnet_folder}/gui_cursor.png")

    def __on_clicked(self):
        self.set_selected(not self.selected)

    def set_selected(self, selected):
        self.selected = selected
        if self.selected:
            select_list[self.card_type][self.file] = self
        else:
            del select_list[self.card_type][self.file]
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.selected:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)

            rect = self.rect()
            path = QPainterPath()
            path.addRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), 5, 5)

            painter.setBrush(QBrush(cfg.get(cfg.themeColor)))
            painter.setPen(Qt.NoPen)
            painter.drawPath(path)

    def get_elided_text(self, label, text):
        # 省略文本
        metrics = QFontMetrics(label.font())
        available_width = label.width()

        elided_text = metrics.elidedText(text, Qt.ElideRight, available_width)
        return elided_text


class ResourceList(SingleDirectionScrollArea):
    refresh_resource = pyqtSignal()

    def __init__(self, list_type, parent=None):
        super().__init__(parent)
        self.list_type = list_type
        if self.list_type == "cursor" and not os.path.exists(f"{os.getcwd()}/app/ddnet_assets/cursor"):
            os.mkdir(f"{os.getcwd()}/app/ddnet_assets")
            os.mkdir(f"{os.getcwd()}/app/ddnet_assets/cursor")

        if self.list_type == "skins":
            self.file_path = f"{GlobalsVal.ddnet_folder}/{self.list_type}"
        elif self.list_type == "cursor":
            self.file_path = f"{os.getcwd()}/app/ddnet_assets/cursor"
        else:
            self.file_path = f"{GlobalsVal.ddnet_folder}/assets/{self.list_type}"

        self.containerWidget = QWidget()
        self.containerWidget.setStyleSheet("background: transparent;")
        self.fBoxLayout = FlowLayout(self.containerWidget)
        self.setContentsMargins(11, 11, 11, 11)

        self.setWidgetResizable(True)
        self.enableTransparentBackground()
        self.setWidget(self.containerWidget)

        self.file_list = os.listdir(self.file_path)
        self.batch_size = 1
        self.current_index = 0

        QTimer.singleShot(0, self.load_next_batch)

        self.refresh_resource.connect(self.__refresh)

    def load_next_batch(self):
        end_index = min(self.current_index + self.batch_size, len(self.file_list))
        for i in range(self.current_index, end_index):
            self.fBoxLayout.addWidget(ResourceCard(f"{self.file_path}/{self.file_list[i]}", self.list_type))
        self.current_index = end_index

        if self.current_index < len(self.file_list):
            QTimer.singleShot(0, self.load_next_batch)

    def __refresh(self):
        for i in reversed(range(self.fBoxLayout.count())):
            widget = self.fBoxLayout.itemAt(i).widget()
            if widget:
                self.fBoxLayout.removeWidget(widget)
                widget.deleteLater()

        self.file_list = os.listdir(self.file_path)
        self.current_index = 0

        QTimer.singleShot(0, self.load_next_batch)


class ResourceInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ResourceInterface")

        if os.path.abspath(GlobalsVal.ddnet_folder) == os.path.abspath(os.getcwd()):
            self.label = SubtitleLabel("我们的程序无法自动找到DDNet配置目录\n请手动到设置中指定DDNet配置目录", self)
            self.hBoxLayout = QHBoxLayout(self)

            setFont(self.label, 24)
            self.label.setAlignment(Qt.AlignCenter)
            self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
            return

        self.pivot = Pivot(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(TitleLabel('材质管理', self))

        self.commandBar = CommandBar(self)
        self.commandBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.addButton(FluentIcon.ADD, '添加'),
        self.addButton(FluentIcon.DELETE, '删除'),
        self.addButton(FluentIcon.SYNC, '刷新'),

        self.TeedataSkinsInterface = ResourceList('skins', self)
        self.TeedataGameSkinsInterface = ResourceList('game', self)
        self.TeedataEmoticonsInterface = ResourceList('emoticons', self)
        self.TeedataCursorsInterface = ResourceList('cursor', self)
        self.TeedataParticlesInterface = ResourceList('particles', self)
        self.TeedataEntitiesInterface = ResourceList('entities', self)

        self.addSubInterface(self.TeedataSkinsInterface, 'TeedataSkinsInterface', '皮肤')
        self.addSubInterface(self.TeedataGameSkinsInterface, 'TeedataGameSkinsInterface', '贴图')
        self.addSubInterface(self.TeedataEmoticonsInterface, 'TeedataEmoticonsInterface', '表情')
        self.addSubInterface(self.TeedataCursorsInterface, 'TeedataCursorsInterface', '光标')
        self.addSubInterface(self.TeedataParticlesInterface, 'TeedataParticlesInterface', '粒子')
        self.addSubInterface(self.TeedataEntitiesInterface, 'TeedataEntitiesInterface', '实体层')

        self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignLeft)
        self.vBoxLayout.addWidget(self.commandBar)
        self.vBoxLayout.addWidget(self.stackedWidget)

        self.stackedWidget.setCurrentWidget(self.TeedataSkinsInterface)
        self.pivot.setCurrentItem(self.TeedataSkinsInterface.objectName())
        self.pivot.currentItemChanged.connect(
            lambda k: self.stackedWidget.setCurrentWidget(self.findChild(QWidget, k)))

    def addSubInterface(self, widget: QLabel, objectName, text):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(routeKey=objectName, text=text)

    def addButton(self, icon, text):
        action = Action(icon, text, self)
        action.triggered.connect(partial(self.Button_clicked, text))
        self.commandBar.addAction(action)

    def Button_clicked(self, text):
        global button_select
        current_item = self.pivot.currentItem().text()

        if text == "添加":
            w = FileSelectMessageBox(self)
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
                        if i.split("/")[-1] in [file for file in os.listdir(self.get_resource_url(current_item))]:
                            cover += 1

                        try:
                            shutil.copy(i, self.get_resource_url(current_item))
                        except Exception as e:
                            InfoBar.error(
                                title='错误',
                                content=f"文件 {i} 复制失败\n原因：{e}",
                                orient=Qt.Horizontal,
                                isClosable=True,
                                position=InfoBarPosition.BOTTOM_RIGHT,
                                duration=-1,
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
            selected_items = select_list[self.get_resource_pivot_type(current_item)]
            if not selected_items:
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

            delete_file = ""
            for i in selected_items:
                delete_file += f"{i}\n"

            w = MessageBox("警告", f"此操作将会从磁盘中永久删除下列文件，不可恢复：\n{delete_file}", self)
            delete = 0
            if w.exec():
                for i in selected_items:
                    try:
                        os.remove(i)
                        delete += 1
                    except:
                        pass

                select_list[self.get_resource_pivot_type(current_item)] = {}

                InfoBar.warning(
                    title='成功',
                    content=f"共删除 {delete} 个文件，{len(selected_items) - delete} 个文件删除失败",
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=2000,
                    parent=self
                )

                self.Button_clicked("刷新")

        elif text == "刷新":
            button_select = None
            self.get_resource_pivot(current_item).refresh_resource.emit()
            select_list[self.get_resource_pivot_type(current_item)] = {}

            InfoBar.success(
                title='成功',
                content="已重新加载本地资源",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=2000,
                parent=self
            )

    def get_resource_pivot(self, text):
        if text == "皮肤":
            return self.TeedataSkinsInterface
        elif text == "贴图":
            return self.TeedataGameSkinsInterface
        elif text == "表情":
            return self.TeedataEmoticonsInterface
        elif text == "光标":
            return self.TeedataCursorsInterface
        elif text == "粒子":
            return self.TeedataParticlesInterface
        elif text == "实体层":
            return self.TeedataEntitiesInterface

    @staticmethod
    def get_resource_pivot_type(text):
        if text == "皮肤":
            text = "skins"
        elif text == "贴图":
            text = "game"
        elif text == "表情":
            text = "emoticons"
        elif text == "光标":
            text = "cursor"
        elif text == "粒子":
            text = "particles"
        elif text == "实体层":
            text = "entities"

        return text

    @staticmethod
    def get_resource_url(text):
        if text == "皮肤":
            text = "skins"
        elif text == "贴图":
            text = "game"
        elif text == "表情":
            text = "emoticons"
        elif text == "光标":
            text = "cursor"
        elif text == "粒子":
            text = "particles"
        elif text == "实体层":
            text = "entities"

        if text == "cursor" and not os.path.exists(f"{os.getcwd()}/app/ddnet_assets/cursor"):
            os.mkdir(f"{os.getcwd()}/app/ddnet_assets")
            os.mkdir(f"{os.getcwd()}/app/ddnet_assets/cursor")

        if text == "skins":
            file_path = f"{GlobalsVal.ddnet_folder}/{text}"
        elif text == "cursor":
            file_path = f"{os.getcwd()}/app/ddnet_assets/cursor"
        else:
            file_path = f"{GlobalsVal.ddnet_folder}/assets/{text}"

        return file_path
