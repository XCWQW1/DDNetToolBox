import os
import shutil
from functools import partial

from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFontMetrics, QPainter, QBrush, QPainterPath, QPixmap
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QLabel, QFileDialog, QHBoxLayout
from qfluentwidgets import CommandBar, Action, FluentIcon, InfoBar, InfoBarPosition, Pivot, TitleLabel, CardWidget, \
    ImageLabel, CaptionLabel, FlowLayout, SingleDirectionScrollArea, MessageBoxBase, SubtitleLabel, MessageBox, \
    SearchLineEdit, TogglePushButton, ToolTipFilter, ToolTipPosition

from app.config import cfg, base_path
from app.utils.draw_tee import draw_tee
from app.utils.network import JsonLoader, ImageLoader

select_list = {
    "skins": {},
    "game": {},
    "emoticons": {},
    "cursor": {},
    "particles": {},
    "entities": {}
}
button_select = None
tee_data_url = "https://teedata.net/_next/data/4C1xLtC88u-Pu26aBBoiA"


class ResourceCard(CardWidget):
    selected = False

    def __init__(self, data, card_type, parent=None):
        super().__init__(parent)
        global button_select

        self.card_type = card_type
        self.data = data
        self.setFixedSize(135, 120)

        if self.card_type == "skins":
            self.image_load = ImageLoader(f"https://teedata.net/api/skin/render/name/{data['name']}?emotion=default_eye")
            self.iconWidget = ImageLabel(base_path + '/resource/logo.png', self)
            self.iconWidget.scaledToHeight(110)
        else:
            self.image_load = ImageLoader(f"https://teedata.net/databasev2{data['file_path']}")
            self.iconWidget = ImageLabel(base_path + '/resource/logo.png', self)
            if self.card_type == "entities":
                self.iconWidget.scaledToHeight(100)
            else:
                self.iconWidget.scaledToHeight(60)

        self.image_load.finished.connect(self.__on_image_load)
        self.image_load.start()

        self.label = CaptionLabel(self)
        self.label.setText(self.get_elided_text(self.label, self.data['name']))
        self.label.setToolTip(self.data['name'])
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

    def __on_image_load(self, pixmap: QPixmap):
        if self.card_type == "skins":
            self.iconWidget.setPixmap(pixmap)
            self.iconWidget.scaledToHeight(110)
        else:
            self.iconWidget.setPixmap(pixmap)
            if self.card_type == "entities":
                self.iconWidget.scaledToHeight(100)
            else:
                self.iconWidget.scaledToHeight(60)

    def __button_clicked(self, checked):  # gui_cursor.png
        global button_select
        if button_select is not None and button_select != self.button:
            button_select.setChecked(False)
            button_select.setText('启用')

        ddnet_folder = cfg.get(cfg.DDNetFolder)

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
    data_ready = pyqtSignal(list)
    batch_size = 1
    current_index = 0

    def __init__(self, list_type, parent=None):
        super().__init__(parent)
        self.list_type = list_type
        if self.list_type == "cursor" and not os.path.exists(f"{os.getcwd()}/app/ddnet_assets/cursor"):
            os.mkdir(f"{os.getcwd()}/app/ddnet_assets")
            os.mkdir(f"{os.getcwd()}/app/ddnet_assets/cursor")

        if self.list_type == "skins":
            self.file_path = f"{cfg.get(cfg.DDNetFolder)}/{self.list_type}"
        elif self.list_type == "cursor":
            self.file_path = f"{os.getcwd()}/app/ddnet_assets/cursor"
        else:
            self.file_path = f"{cfg.get(cfg.DDNetFolder)}/assets/{self.list_type}"

        self.containerWidget = QWidget()
        self.containerWidget.setStyleSheet("background: transparent;")
        self.fBoxLayout = FlowLayout(self.containerWidget)
        self.setContentsMargins(11, 11, 11, 11)

        self.setWidgetResizable(True)
        self.enableTransparentBackground()
        self.setWidget(self.containerWidget)

        self.refresh_resource.connect(self.__refresh)
        self.data_ready.connect(self.__data_ready)

    def load_next_batch(self):
        end_index = min(self.current_index + self.batch_size, len(self.teedata_list))
        for i in range(self.current_index, end_index):
            self.fBoxLayout.addWidget(ResourceCard(self.teedata_list[i], self.list_type))
        self.current_index = end_index

        if self.current_index < len(self.teedata_list):
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

    def __data_ready(self, data):
        self.teedata_list = data

        QTimer.singleShot(0, self.load_next_batch)
        # print(data)


class ResourceDownloadInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ResourceDownloadInterface")

        self.pivot = Pivot(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)

        self.hBoxLayout = QHBoxLayout()
        self.hBoxLayout.addWidget(TitleLabel('材质下载', self))
        self.hBoxLayout.addWidget(CaptionLabel("数据取自 teedata.net"), 0, Qt.AlignRight | Qt.AlignTop)

        self.search_edit = SearchLineEdit()
        self.search_edit.setPlaceholderText('搜点什么...')

        self.commandBar = CommandBar(self)
        self.commandBar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.addButton(FluentIcon.DOWNLOAD, '下载'),
        self.addButton(FluentIcon.SYNC, '刷新'),

        self.TeedataSkinsInterface = ResourceList('skins', self)
        self.TeedataGameSkinsInterface = ResourceList('game', self)
        self.TeedataEmoticonsInterface = ResourceList('emoticons', self)
        self.TeedataCursorsInterface = ResourceList('cursor', self)  # gui_cursor.png
        self.TeedataParticlesInterface = ResourceList('particles', self)
        self.TeedataEntitiesInterface = ResourceList('entities', self)

        self.addSubInterface(self.TeedataSkinsInterface, 'TeedataSkinsInterface', '皮肤')
        self.addSubInterface(self.TeedataGameSkinsInterface, 'TeedataGameSkinsInterface', '贴图')
        self.addSubInterface(self.TeedataEmoticonsInterface, 'TeedataEmoticonsInterface', '表情')
        self.addSubInterface(self.TeedataCursorsInterface, 'TeedataCursorsInterface', '光标')
        self.addSubInterface(self.TeedataParticlesInterface, 'TeedataParticlesInterface', '粒子')
        self.addSubInterface(self.TeedataEntitiesInterface, 'TeedataEntitiesInterface', '实体层')

        self.headBoxLayout = QHBoxLayout()
        self.headBoxLayout.addWidget(self.pivot, 0, Qt.AlignLeft)
        self.headBoxLayout.addWidget(self.commandBar)

        self.vBoxLayout.addLayout(self.hBoxLayout)
        self.vBoxLayout.addWidget(self.search_edit)
        self.vBoxLayout.addLayout(self.headBoxLayout)
        self.vBoxLayout.addWidget(self.stackedWidget)

        self.stackedWidget.setCurrentWidget(self.TeedataSkinsInterface)
        self.pivot.setCurrentItem(self.TeedataSkinsInterface.objectName())
        self.pivot.currentItemChanged.connect(lambda k: self.stackedWidget.setCurrentWidget(self.findChild(QWidget, k)))

        self.teedata_index = JsonLoader(f"{tee_data_url}/index.json")
        self.teedata_index.finished.connect(self.__teedata_index_finished)
        self.teedata_index.start()

    def __teedata_index_finished(self, data):
        data = data['pageProps']
        self.TeedataSkinsInterface.data_ready.emit(data['skinTrending']['items'])
        self.TeedataGameSkinsInterface.data_ready.emit(data['gameskinTrending']['items'])
        self.TeedataEmoticonsInterface.data_ready.emit(data['emoticonTrending']['items'])
        self.TeedataCursorsInterface.data_ready.emit(data['cursorTrending']['items'])
        self.TeedataParticlesInterface.data_ready.emit(data['particleTrending']['items'])
        self.TeedataEntitiesInterface.data_ready.emit(data['entityTrending']['items'])

    def addSubInterface(self, widget: QLabel, objectName, text):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(routeKey=objectName, text=text)

    def addButton(self, icon, text):
        action = Action(icon, text, self)
        action.triggered.connect(partial(self.Button_clicked, text))
        self.commandBar.addAction(action)

    def Button_clicked(self, text):
        current_item = self.pivot.currentItem().text()

        if text == "下载":
            pass
        elif text == "刷新":
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
            file_path = f"{cfg.get(cfg.DDNetFolder)}/{text}"
        elif text == "cursor":
            file_path = f"{os.getcwd()}/app/ddnet_assets/cursor"
        else:
            file_path = f"{cfg.get(cfg.DDNetFolder)}/assets/{text}"

        return file_path
