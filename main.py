import json
import os
import re
import sys

from PyQt5.QtCore import Qt, QLocale, pyqtSignal
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import (NavigationItemPosition, FluentWindow,
                            FluentTranslator, qconfig, Theme, setThemeColor)
from qfluentwidgets import FluentIcon as FIF

from app.config import cfg, base_path
from app.globals import GlobalsVal
from app.view.cfg_interface import CFGInterface
from app.view.home_interface import HomeInterface
from app.view.resource_download_interface import ResourceDownloadInterface
from app.view.resource_interface import ResourceInterface
from app.view.server_list_preview_interface import ServerListPreviewInterface
from app.view.setting_interface import SettingInterface
from app.view.server_list_interface import ServerListInterface


class MainWindow(FluentWindow):
    """ 主界面 """
    themeChane = pyqtSignal(Theme)
    def __init__(self):
        super().__init__()

        file_list = cfg.get(cfg.DDNetFolder)
        for i in os.listdir(file_list):
            if i == "settings_ddnet.cfg":
                with open(f'{file_list}/settings_ddnet.cfg', encoding='utf-8') as f:
                    lines = f.read().strip().split('\n')
                    for line in lines:
                        if line.strip():
                            parts = re.split(r'\s+', line, maxsplit=1)
                            if len(parts) == 2:
                                key, value = parts
                                if ',' in value:
                                    value = [v.strip(' "') for v in re.split(r',', value)]
                                else:
                                    value = self.remove_quotes(value)

                                if key in GlobalsVal.ddnet_setting_config:
                                    if not isinstance(GlobalsVal.ddnet_setting_config[key], list):
                                        GlobalsVal.ddnet_setting_config[key] = [GlobalsVal.ddnet_setting_config[key]]
                                    else:
                                        GlobalsVal.ddnet_setting_config[key].append(value)
                                else:
                                    if type(value) != str:
                                        GlobalsVal.ddnet_setting_config[key] = [value]
                                    else:
                                        GlobalsVal.ddnet_setting_config[key] = value
            if i == "ddnet-info.json":
                with open(f'{file_list}/ddnet-info.json', encoding='utf-8') as f:
                    GlobalsVal.ddnet_info = json.loads(f.read())
            if i == "ddnet-serverlist-urls.cfg":
                GlobalsVal.server_list_file = True

        if not os.path.exists(f"{os.getcwd()}/app/config"):
            if not "player_name" in GlobalsVal.ddnet_setting_config:
                return
            if GlobalsVal.ddnet_setting_config["player_name"] == "Realyn//UnU":
                cfg.set(cfg.themeColor, QColor("#af251a"))

        # 创建子界面
        self.homeInterface = HomeInterface(self)
        self.CFGInterface = CFGInterface()
        self.ResourceInterface = ResourceInterface()
        # self.ResourceDownloadInterface = ResourceDownloadInterface()
        self.ServerListMirrorInterface = ServerListInterface()
        self.ServerListPreviewInterface = ServerListPreviewInterface()

        self.settingInterface = SettingInterface(self.themeChane)

        self.initNavigation()
        self.initWindow()

        self.themeChane.connect(self.__theme_change)

    @staticmethod
    def remove_quotes(text):
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        if '" "' in text:
            text = re.split(r'" "', text)
        return text

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '首页')
        self.addSubInterface(self.CFGInterface, FIF.APPLICATION, 'CFG管理')
        self.addSubInterface(self.ResourceInterface, FIF.EMOJI_TAB_SYMBOLS, '材质管理')
        self.addSubInterface(self.ServerListMirrorInterface, FIF.LIBRARY, '服务器列表管理')
        # self.addSubInterface(self.ServerListPreviewInterface, FIF.LIBRARY, '服务器列表预览')
        # self.addSubInterface(self.ResourceDownloadInterface, FIF.DOWNLOAD, '材质下载')

        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(820, 600)
        theme = cfg.get(cfg.themeMode)
        theme = qconfig.theme if theme == Theme.AUTO else theme
        self.setWindowIcon(QIcon(base_path + f'/resource/{theme.value.lower()}/logo.svg'))
        self.setWindowTitle('DDNetToolBox')

        # 关闭win11的云母特效，他会导致窗口卡顿
        self.setMicaEffectEnabled(False)

    def __theme_change(self, theme: Theme):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        self.setWindowIcon(QIcon(base_path + f'/resource/{theme.value.lower()}/logo.svg'))


if __name__ == '__main__':
    # 启用DPI
    if cfg.get(cfg.dpiScale) == "Auto":
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    else:
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    translator = FluentTranslator(QLocale(QLocale.Chinese, QLocale.China))
    app.installTranslator(translator)
    w = MainWindow()
    w.show()
    app.exec_()
