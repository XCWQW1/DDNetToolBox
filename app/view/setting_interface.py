import os
import platform
import subprocess

from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices
from qfluentwidgets import (OptionsSettingCard, ScrollArea, ExpandLayout, FluentIcon, SettingCardGroup, setTheme,
                            InfoBar, isDarkTheme, Theme, PushSettingCard, SwitchSettingCard, PrimaryPushSettingCard,
                            CaptionLabel, qconfig, CustomColorSettingCard, setThemeColor, InfoBarPosition,
                            ComboBoxSettingCard, PushButton, PrimaryPushButton, InfoBarIcon)
from PyQt5.QtWidgets import QWidget, QFileDialog, QPushButton, QHBoxLayout
from app.config import cfg, base_path, config_path
from app.globals import GlobalsVal
from app.utils.config_directory import get_ddnet_directory
from app.utils.network import JsonLoader


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
        self.DDNetFolderButton = QPushButton(self.tr('自动寻找'), self.DDNetFolder)
        self.DDNetFolder.hBoxLayout.addWidget(self.DDNetFolderButton, 0, Qt.AlignRight)
        self.DDNetFolder.hBoxLayout.addSpacing(16)

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

        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FluentIcon.LANGUAGE,
            self.tr('语言'),
            self.tr('更改首选语言'),
            texts=['简体中文', 'English', self.tr('跟随系统默认')],
            parent=self.personalGroup
        )

        self.otherGroup = SettingCardGroup(self.tr('其他'), self.scrollWidget)
        self.checkUpdate = PrimaryPushSettingCard(
            text=self.tr("检查更新"),
            icon=FluentIcon.INFO,
            title=self.tr("关于"),
            content=self.tr("当前工具箱版本：{}，logo 由 燃斯(Realyn//UnU) 绘制").format(GlobalsVal.DDNetToolBoxVersion)
        )
        self.checkUpdate.clicked.connect(self.__check_update)

        self.openConfigFolder = PrimaryPushSettingCard(
            text=self.tr("打开目录"),
            icon=FluentIcon.FOLDER,
            title=self.tr("工具箱配置目录"),
            content=self.tr("打开工具箱配置文件所在目录")
        )
        self.openConfigFolder.clicked.connect(lambda: self.open_folder(config_path))

        self.__initWidget()

    @staticmethod
    def open_folder(directory_path):
        if platform.system() == "Windows":
            os.startfile(directory_path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", directory_path])
        else:
            subprocess.run(["xdg-open", directory_path])


    def __check_update(self, data=None, on_load: bool=False):
        if data is not None:
            self.checkUpdate.button.setEnabled(True)
            if data == {}:
                InfoBar.error(
                    title=self.tr('检查更新'),
                    content=self.tr("无法访问到github"),
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=-1,
                    parent=GlobalsVal.main_window
                )
                return

            if GlobalsVal.DDNetToolBoxVersion != data['tag_name']:
                self.updateInfoBar = InfoBar(
                    icon=InfoBarIcon.WARNING,
                    title=self.tr('检查更新'),
                    content=self.tr("您当前的DDNetToolBox版本为 {} 最新版本为 {}").format(GlobalsVal.DDNetToolBoxVersion, data['tag_name']),
                    orient=Qt.HorPattern,
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=-1,
                    parent=GlobalsVal.main_window
                )
                self.updateButton = PushButton('现在更新')
                self.closeButton = PushButton('以后再说')
                self.updateLayout = QHBoxLayout()

                self.updateButton.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(data['html_url'])))
                self.closeButton.clicked.connect(lambda: self.updateInfoBar.close())

                self.updateLayout.addWidget(self.updateButton)
                self.updateLayout.addWidget(self.closeButton)
                self.updateInfoBar.widgetLayout.addLayout(self.updateLayout)
                self.updateInfoBar.show()
            else:
                InfoBar.success(
                    title=self.tr('检查更新'),
                    content=self.tr("您的DDNetToolBox为最新版"),
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.BOTTOM_RIGHT,
                    duration=2000,
                    parent=GlobalsVal.main_window
                )
            return

        if not on_load:
            self.checkUpdate.button.setEnabled(False)
            InfoBar.info(
                title=self.tr('检查更新'),
                content=self.tr("正在检查更新中..."),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=2000,
                parent=GlobalsVal.main_window
            )

        self.latest_release = JsonLoader('https://api.github.com/repos/XCWQW1/DDNetToolBox/releases/latest')
        self.latest_release.finished.connect(self.__check_update)
        self.latest_release.start()

    def __initWidget(self):
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName("SettingInterface")

        self.__setQss()
        self.__check_update(on_load=True)

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
        self.personalGroup.addSettingCard(self.languageCard)
        self.otherGroup.addSettingCard(self.checkUpdate)
        self.otherGroup.addSettingCard(self.openConfigFolder)

        self.expandLayout.addWidget(self.DDNetGroup)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.otherGroup)

    def __showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.success(
            self.tr('成功'),
            self.tr('重启以应用更改'),
            duration=1500,
            position=InfoBarPosition.BOTTOM_RIGHT,
            parent=GlobalsVal.main_window
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
        self.__showRestartTooltip()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        cfg.themeChanged.connect(self.__onThemeChanged)

        self.DDNetFolderButton.clicked.connect(self.__FindDDNetFolder)
        self.DDNetFolder.clicked.connect(self.__onDDNetFolderCardClicked)
        self.DDNetFolder.clicked.connect(self.__onDDNetFolderChanged)
        self.themeCard.optionChanged.connect(lambda ci: setTheme(cfg.get(ci)))
        self.themeColorCard.colorChanged.connect(setThemeColor)


    def __FindDDNetFolder(self):
        folder = get_ddnet_directory()
        if folder != "./":
            cfg.set(cfg.DDNetFolder, folder)
            self.DDNetFolder.contentLabel.setText(folder)
            InfoBar.success(
                self.tr('成功'),
                self.tr('识别到的DDNet配置文件夹为：{}').format(folder),
                duration=1500,
                parent=self,
                position=InfoBarPosition.BOTTOM_RIGHT,
            )
            self.__showRestartTooltip()
        else:
            InfoBar.error(
                self.tr('错误'),
                self.tr('没有找到DDNet配置文件夹'),
                duration=1500,
                position=InfoBarPosition.BOTTOM_RIGHT,
                parent=self
            )
