import json
import os
import re
import sys
import traceback

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QHBoxLayout, QPushButton, QApplication
from qfluentwidgets import Theme, qconfig, NavigationItemPosition, FluentWindow

from app.config import cfg, base_path
from app.globals import GlobalsVal
from app.view.cfg_interface import CFGInterface
from app.view.home_interface import HomeInterface
from app.view.resource_interface import ResourceInterface
from app.view.server_list_interface import ServerListInterface
from app.view.server_list_preview_interface import ServerListPreviewInterface
from app.view.setting_interface import SettingInterface

from qfluentwidgets import FluentIcon as FIF


class MainWindow(FluentWindow):
    """ 主界面 """
    themeChane = pyqtSignal(Theme)
    def __init__(self):
        super().__init__()

        file_list = GlobalsVal.ddnet_folder
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

        if not os.path.isfile(f"{os.getcwd()}/app/config/config.json"):
            if "player_name" in GlobalsVal.ddnet_setting_config:
                if GlobalsVal.ddnet_setting_config["player_name"] == "Realyn//UnU":
                    cfg.set(cfg.themeColor, QColor("#af251a"))

        # 创建子界面
        self.homeInterface = HomeInterface()
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
        self.addSubInterface(self.homeInterface, FIF.HOME, self.tr('首页'))
        self.addSubInterface(self.CFGInterface, FIF.APPLICATION, self.tr('CFG管理'))
        self.addSubInterface(self.ResourceInterface, FIF.EMOJI_TAB_SYMBOLS, self.tr('材质管理'))
        self.addSubInterface(self.ServerListMirrorInterface, FIF.LIBRARY, self.tr('服务器列表管理'))
        # self.addSubInterface(self.ServerListPreviewInterface, FIF.LIBRARY, self.tr('服务器列表预览'))
        # self.addSubInterface(self.ResourceDownloadInterface, FIF.DOWNLOAD, self.tr('材质下载'))

        self.addSubInterface(self.settingInterface, FIF.SETTING, self.tr('设置'), NavigationItemPosition.BOTTOM)

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

    def show_crash_message(self, exc_type, exc_value, exc_traceback):
        error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))

        dialog = QDialog()
        dialog.setWindowTitle(self.tr("程序崩溃"))

        layout = QVBoxLayout(dialog)

        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setText(error_message)
        layout.addWidget(text_edit)

        button_layout = QHBoxLayout()

        copy_button = QPushButton(self.tr("复制日志"))
        copy_button.clicked.connect(lambda: QApplication.clipboard().setText(error_message))
        button_layout.addWidget(copy_button)

        ok_button = QPushButton(self.tr("确定并关闭"))
        ok_button.clicked.connect(dialog.accept)
        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)
        dialog.exec_()
        sys.exit(1)
