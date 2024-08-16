import os

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from qfluentwidgets import (OptionsSettingCard, ScrollArea, ExpandLayout, FluentIcon, SettingCardGroup, setTheme,
                            InfoBar, isDarkTheme, Theme, PushSettingCard, SwitchSettingCard, PrimaryPushSettingCard,
                            CaptionLabel, qconfig, CustomColorSettingCard, setThemeColor)
from PyQt5.QtWidgets import QWidget, QFileDialog
from app.config import cfg, base_path
from app.globals import GlobalsVal


class SettingInterface(ScrollArea):
    """ Setting interface """

    ddnetFolderChanged = pyqtSignal(list)

    def __init__(self, themeChane, parent=None):
        super().__init__(parent=parent)
        self.themeChane = themeChane

        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # DDNet
        self.DDNetGroup = SettingCardGroup(self.tr("DDNet"), self.scrollWidget)
        self.DDNetFolder = PushSettingCard(
            self.tr('更改目录'),
            FluentIcon.DOWNLOAD,
            self.tr("DDNet配置目录"),
            cfg.get(cfg.DDNetFolder),
            self.DDNetGroup
        )

        self.DDNetCheckUpdate = SwitchSettingCard(
            FluentIcon.UPDATE,
            self.tr("检测DDNet版本更新"),
            self.tr("在启动工具箱的时候检测DDNet客户端版本是否为最新"),
            configItem=cfg.DDNetCheckUpdate,
            parent=self.DDNetGroup
        )

        # personal
        self.personalGroup = SettingCardGroup(self.tr('个性化'), self.scrollWidget)
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FluentIcon.BRUSH,
            self.tr('应用主题'),
            self.tr("调整你的应用外观"),
            texts=[
                self.tr('浅色'), self.tr('深色'),
                self.tr('跟随系统设置')
            ],
            parent=self.personalGroup
        )

        self.themeColorCard = CustomColorSettingCard(
            cfg.themeColor,
            FluentIcon.PALETTE,
            self.tr('主题颜色'),
            self.tr('更改应用程序的主题颜色'),
            self.personalGroup
        )

        self.zoomCard = OptionsSettingCard(
            cfg.dpiScale,
            FluentIcon.ZOOM,
            self.tr("缩放大小"),
            self.tr("更改小部件和字体的大小"),
            texts=[
                "100%", "125%", "150%", "175%", "200%",
                self.tr("跟随系统默认")
            ],
            parent=self.personalGroup
        )

        self.otherGroup = SettingCardGroup(self.tr('其他'), self.scrollWidget)
        self.checkUpdate = PrimaryPushSettingCard(
            text="检查更新",
            icon=FluentIcon.INFO,
            title="关于",
            content=f"当前工具箱版本：{GlobalsVal.DDNetToolBoxVersion}，logo 由 燃斯(Realyn//UnU) 绘制"
        )
        self.checkUpdate.clicked.connect(self.__check_update)

        self.__initWidget()

    def __check_update(self):
        pass

    def __initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName("SettingInterface")

        self.__setQss()

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __setQss(self):
        """ set style sheet """
        self.scrollWidget.setObjectName('scrollWidget')

        theme = 'dark' if isDarkTheme() else 'light'
        with open(base_path + f'/resource/{theme}/setting_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __initLayout(self):
        self.DDNetGroup.addSettingCard(self.DDNetFolder)
        self.DDNetGroup.addSettingCard(self.DDNetCheckUpdate)
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.themeColorCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.otherGroup.addSettingCard(self.checkUpdate)

        self.expandLayout.addWidget(self.DDNetGroup)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.otherGroup)

    def __showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.success(
            self.tr('成功'),
            self.tr('重启以应用更改'),
            duration=1500,
            parent=self
        )

    def __onThemeChanged(self, theme: Theme):
        """ theme changed slot """
        self.themeChane.emit(theme)
        setTheme(theme)
        self.__setQss()

    def __onDDNetFolderChanged(self):
        for i in os.listdir(cfg.get(cfg.DDNetFolder)):
            if i == "settings_ddnet.cfg":
                with open(f'{cfg.get(cfg.DDNetFolder)}/settings_ddnet.cfg', encoding='utf-8') as f:
                    for i in f.read().split('\n'):
                        i = i.split(' ', 1)
                        if len(i) == 2:
                            GlobalsVal.ddnet_setting_config[i[0]] = i[1].strip('\'"')

    def __onDDNetFolderCardClicked(self):
        """ download folder card clicked slot """
        folder = QFileDialog.getExistingDirectory(
            self, self.tr("更改目录"), "./")
        if not folder or cfg.get(cfg.DDNetFolder) == folder:
            return

        cfg.set(cfg.DDNetFolder, folder)
        self.DDNetFolder.setContent(folder)

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        cfg.themeChanged.connect(self.__onThemeChanged)

        self.DDNetFolder.clicked.connect(self.__onDDNetFolderCardClicked)
        self.DDNetFolder.clicked.connect(self.__onDDNetFolderChanged)
        self.themeCard.optionChanged.connect(lambda ci: setTheme(cfg.get(ci)))
        self.themeColorCard.colorChanged.connect(setThemeColor)
