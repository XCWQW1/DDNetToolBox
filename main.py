import json
import os
import re
import sys

from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout
from qfluentwidgets import (NavigationItemPosition, setFont, SubtitleLabel, FluentWindow,
                            FluentTranslator)
from qfluentwidgets import FluentIcon as FIF

from app.config import cfg, base_path
from app.globals import GlobalsVal
from app.view.cfg_interface import CFGInterface
from app.view.home_interface import HomeInterface
from app.view.resource_download_interface import ResourceDownloadInterface
from app.view.resource_interface import ResourceInterface
from app.view.setting_interface import SettingInterface
from app.view.server_list_interface import ServerListInterface


class MainWindow(FluentWindow):
    """ 主界面 """
    def __init__(self):
        super().__init__()

        file_list = cfg.get(cfg.DDNetFolder)
        GlobalsVal.ddnet_cfg_list = [file for file in os.listdir(file_list) if file.endswith('.cfg')]
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

        # 创建子界面
        self.homeInterface = HomeInterface(self)
        self.CFGInterface = CFGInterface()
        self.ResourceInterface = ResourceInterface()
        self.ResourceDownloadInterface = ResourceDownloadInterface()
        self.ServerListMirrorInterface = ServerListInterface()

        self.settingInterface = SettingInterface()

        self.initNavigation()
        self.initWindow()

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
        self.addSubInterface(self.ServerListMirrorInterface, FIF.LIBRARY, '服务器列表管理')
        self.addSubInterface(self.ResourceDownloadInterface, FIF.DOWNLOAD, '材质下载')
        self.addSubInterface(self.ResourceInterface, FIF.EMOJI_TAB_SYMBOLS, '材质管理')

        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(820, 600)
        self.setWindowIcon(QIcon(base_path + '/resource/logo.svg'))
        self.setWindowTitle('DDNetToolBox')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    translator = FluentTranslator(QLocale(QLocale.Chinese, QLocale.China))
    app.installTranslator(translator)
    w = MainWindow()
    w.show()
    app.exec_()
