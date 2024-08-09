# coding:utf-8
import json
import os
import sys

from PyQt5.QtCore import Qt, QLocale
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QFrame, QHBoxLayout
from qfluentwidgets import (NavigationItemPosition, setFont, SubtitleLabel, FluentWindow,
                            FluentTranslator)
from qfluentwidgets import FluentIcon as FIF

from app.config import cfg, base_path
from app.globals import GlobalsVal
from app.view.home_interface import HomeInterface
from app.view.setting_interface import SettingInterface
from app.view.server_list_interface import ServerListInterface


class Widget(QFrame):
    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.label = SubtitleLabel(text, self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)

        # 必须给子界面设置全局唯一的对象名
        self.setObjectName(text.replace(' ', '-'))


class MainWindow(FluentWindow):
    """ 主界面 """
    def __init__(self):
        super().__init__()

        file_list = cfg.get(cfg.DDNetFolder)
        for i in os.listdir(file_list):
            if i == "settings_ddnet.cfg":
                with open(f'{file_list}/settings_ddnet.cfg', encoding='utf-8') as f:
                    for a in f.read().split('\n'):
                        a = a.split(' ', 1)
                        if len(a) == 2:
                            a[1] = a[1].split(" ")
                            if len(a[1]) != 1:
                                GlobalsVal.ddnet_setting_config[a[0]] = a[1]
                            else:
                                GlobalsVal.ddnet_setting_config[a[0]] = a[1][0].strip('\'"')
            if i == "ddnet-info.json":
                with open(f'{file_list}/ddnet-info.json', encoding='utf-8') as f:
                    GlobalsVal.ddnet_info = json.loads(f.read())

        # 创建子界面
        self.homeInterface = HomeInterface()
        self.CFGInterface = Widget('没写', self)
        self.ServerListMirrorInterface = ServerListInterface()

        self.settingInterface = SettingInterface(self)

        self.initNavigation()
        self.initWindow()

    def initNavigation(self):
        self.addSubInterface(self.homeInterface, FIF.HOME, '首页')
        self.addSubInterface(self.CFGInterface, FIF.APPLICATION, 'CFG管理')
        self.addSubInterface(self.ServerListMirrorInterface, FIF.LIBRARY, '服务器列表管理')

        self.addSubInterface(self.settingInterface, FIF.SETTING, '设置', NavigationItemPosition.BOTTOM)

    def initWindow(self):
        self.resize(800, 600)
        self.setWindowIcon(QIcon(base_path + 'app/resource/logo.svg'))
        self.setWindowTitle('DDNetToolBox')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    translator = FluentTranslator(QLocale(QLocale.Chinese, QLocale.China))
    app.installTranslator(translator)
    w = MainWindow()
    w.show()
    app.exec_()
