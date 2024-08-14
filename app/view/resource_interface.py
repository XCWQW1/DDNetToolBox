import os
from functools import partial

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFontMetrics
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QLabel
from qfluentwidgets import CommandBar, Action, FluentIcon, InfoBar, InfoBarPosition, Pivot, \
    TitleLabel, CardWidget, ImageLabel, CaptionLabel, FlowLayout, SingleDirectionScrollArea

from app.config import cfg
from app.utils.draw_tee import draw_tee


class ResourceCard(CardWidget):
    def __init__(self, file, card_type, parent=None):
        super().__init__(parent)

        self.setFixedSize(135, 120)

        if card_type == "skins":
            self.iconWidget = ImageLabel(draw_tee(file), self)
            self.iconWidget.scaledToHeight(128)
        else:
            self.iconWidget = ImageLabel(file, self)
            self.iconWidget.scaledToHeight(68)

        self.label = CaptionLabel(self)
        self.label.setText(self.get_elided_text(self.label, os.path.basename(file)[:-4]))

        self.hBoxLayout = QVBoxLayout(self)
        self.hBoxLayout.addWidget(self.iconWidget, Qt.AlignCenter | Qt.AlignTop)
        self.hBoxLayout.addWidget(self.label, 0, Qt.AlignCenter)

    def get_elided_text(self, label, text):
        # 省略文本
        metrics = QFontMetrics(label.font())
        available_width = label.width()

        elided_text = metrics.elidedText(text, Qt.ElideRight, available_width)
        return elided_text


class ResourceList(SingleDirectionScrollArea):
    refresh_resource = pyqtSignal()
    card_list = []

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

        for i in os.listdir(self.file_path):
            card = ResourceCard(f"{self.file_path}/{i}", self.list_type)
            self.card_list.append(card)
            self.fBoxLayout.addWidget(card)

        self.refresh_resource.connect(self.__refresh)

    def __refresh(self):
        for i in self.card_list:
            self.fBoxLayout.removeWidget(i)

        for i in os.listdir(self.file_path):
            card = ResourceCard(f"{self.file_path}/{i}", self.list_type)
            self.card_list.append(card)
            self.fBoxLayout.addWidget(card)


class ResourceInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ResourceInterface")

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
        self.TeedataCursorsInterface = ResourceList('cursor', self)  # gui_cursor.png
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
        # widget.setAlignment(Qt.AlignCenter)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(routeKey=objectName, text=text)

    def addButton(self, icon, text):
        action = Action(icon, text, self)
        action.triggered.connect(partial(self.Button_clicked, text))
        self.commandBar.addAction(action)

    def Button_clicked(self, text):
        if text == "刷新":
            self.TeedataSkinsInterface.refresh_resource.emit()
            self.TeedataGameSkinsInterface.refresh_resource.emit()
            self.TeedataEmoticonsInterface.refresh_resource.emit()
            self.TeedataCursorsInterface.refresh_resource.emit()
            self.TeedataParticlesInterface.refresh_resource.emit()
            self.TeedataEntitiesInterface.refresh_resource.emit()

            InfoBar.success(
                title='成功',
                content="已重新加载本地资源",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=2000,
                parent=self
            )
