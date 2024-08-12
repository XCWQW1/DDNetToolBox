from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QTableWidgetItem, QVBoxLayout, QHeaderView, QStackedWidget, QLabel
from qfluentwidgets import TableWidget, CommandBar, Action, FluentIcon, InfoBar, InfoBarPosition, MessageBox, Pivot, \
    TitleLabel

from app.config import cfg
from app.globals import GlobalsVal


class ResourceDownloadInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ResourceDownloadInterface")

        self.pivot = Pivot(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(TitleLabel('材质下载', self))

        self.DDNetSkinsInterface = QLabel('皮肤', self)
        self.DDNetGameSkinsInterface = QLabel('贴图', self)
        self.DDNetEmoticonsInterface = QLabel('表情', self)
        self.DDNetCursorsInterface = QLabel('光标', self)
        self.DDNetParticlesInterface = QLabel('粒子', self)
        self.DDNetEntitiesInterface = QLabel('实体层', self)
        self.DDNetFontsInterface = QLabel('字体', self)

        self.addSubInterface(self.DDNetSkinsInterface, 'DDNetSkinsInterface', '皮肤')
        self.addSubInterface(self.DDNetGameSkinsInterface, 'DDNetGameSkinsInterface', '贴图')
        self.addSubInterface(self.DDNetEmoticonsInterface, 'DDNetEmoticonsInterface', '表情')
        self.addSubInterface(self.DDNetCursorsInterface, 'DDNetCursorsInterface', '光标')
        self.addSubInterface(self.DDNetParticlesInterface, 'DDNetParticlesInterface', '粒子')
        self.addSubInterface(self.DDNetEntitiesInterface, 'DDNetEntitiesInterface', '实体层')
        self.addSubInterface(self.DDNetFontsInterface, 'DDNetFontsInterface', '字体')

        self.vBoxLayout.addWidget(self.pivot, 0, Qt.AlignLeft)
        self.vBoxLayout.addWidget(self.stackedWidget)

        self.stackedWidget.setCurrentWidget(self.DDNetSkinsInterface)
        self.pivot.setCurrentItem(self.DDNetSkinsInterface.objectName())
        self.pivot.currentItemChanged.connect(
            lambda k: self.stackedWidget.setCurrentWidget(self.findChild(QWidget, k)))

    def addSubInterface(self, widget: QLabel, objectName, text):
        widget.setObjectName(objectName)
        widget.setAlignment(Qt.AlignCenter)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(routeKey=objectName, text=text)