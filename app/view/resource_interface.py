from functools import partial

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidgetItem, QVBoxLayout, QHeaderView, QStackedWidget, QLabel
from qfluentwidgets import TableWidget, CommandBar, Action, FluentIcon, InfoBar, InfoBarPosition, MessageBox, Pivot, \
    TitleLabel

from app.config import cfg
from app.globals import GlobalsVal


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

        self.TeedataSkinsInterface = QLabel('皮肤', self)
        self.TeedataGameSkinsInterface = QLabel('贴图', self)
        self.TeedataEmoticonsInterface = QLabel('表情', self)
        self.TeedataCursorsInterface = QLabel('光标', self)
        self.TeedataParticlesInterface = QLabel('粒子', self)
        self.TeedataEntitiesInterface = QLabel('实体层', self)
        self.TeedataFontsInterface = QLabel('字体', self)

        self.addSubInterface(self.TeedataSkinsInterface, 'TeedataSkinsInterface', '皮肤')
        self.addSubInterface(self.TeedataGameSkinsInterface, 'TeedataGameSkinsInterface', '贴图')
        self.addSubInterface(self.TeedataEmoticonsInterface, 'TeedataEmoticonsInterface', '表情')
        self.addSubInterface(self.TeedataCursorsInterface, 'TeedataCursorsInterface', '光标')
        self.addSubInterface(self.TeedataParticlesInterface, 'TeedataParticlesInterface', '粒子')
        self.addSubInterface(self.TeedataEntitiesInterface, 'TeedataEntitiesInterface', '实体层')
        self.addSubInterface(self.TeedataFontsInterface, 'TeedataFontsInterface', '字体')

        self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignLeft)
        self.vBoxLayout.addWidget(self.commandBar)
        self.vBoxLayout.addWidget(self.stackedWidget)

        self.stackedWidget.setCurrentWidget(self.TeedataSkinsInterface)
        self.pivot.setCurrentItem(self.TeedataSkinsInterface.objectName())
        self.pivot.currentItemChanged.connect(
            lambda k: self.stackedWidget.setCurrentWidget(self.findChild(QWidget, k)))

    def addSubInterface(self, widget: QLabel, objectName, text):
        widget.setObjectName(objectName)
        widget.setAlignment(Qt.AlignCenter)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(routeKey=objectName, text=text)

    def addButton(self, icon, text):
        action = Action(icon, text, self)
        action.triggered.connect(partial(self.Button_clicked, text))
        self.commandBar.addAction(action)

    def Button_clicked(self, text):
        pass
