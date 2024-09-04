import json
import os
import re

from PyQt5.QtCore import pyqtSignal, QTimer, Qt
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import QWidget, QHBoxLayout

from qfluentwidgets import Theme, qconfig, NavigationItemPosition, FluentWindow, SubtitleLabel, setFont, InfoBar, \
    InfoBarPosition

from app.config import cfg, base_path, config_path
from app.globals import GlobalsVal

from qfluentwidgets import FluentIcon as FIF


class DDNetFolderCrash(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.label = SubtitleLabel(self.tr("我们的程序无法自动找到DDNet配置目录\n请手动到设置中指定DDNet配置目录"),
                                   self)
        self.hBoxLayout = QHBoxLayout(self)

        setFont(self.label, 24)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)


class MainWindow(FluentWindow):
    """ 主界面 """
    themeChane = pyqtSignal(Theme)
    def __init__(self):
        super().__init__()

        self.file_list = GlobalsVal.ddnet_folder

        # 加载配置文件
        self.load_config_files()

        # 延迟初始化子界面
        self.homeInterface = None
        self.PlayerPointInterface = None
        self.CFGInterface = None
        self.ResourceInterface = None
        self.ServerListMirrorInterface = None
        self.ServerListPreviewInterface = None
        self.settingInterface = None

        self.initWindow()
        self.initNavigation()
        self.themeChane.connect(self.__theme_change)


    def load_config_files(self):
        """加载配置文件"""
        if all(elem in os.listdir(self.file_list) for elem in ['assets', 'ddnet-info.json', 'settings_ddnet.cfg']):
            GlobalsVal.ddnet_folder_status = True
        else:
            InfoBar.warning(
                title=self.tr('警告'),
                content=self.tr("DDNet配置文件目录配置错误，部分功能将被禁用\n请于设置中修改后重启本程序\n请勿设置为DDNet游戏目录"),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=-1,
                parent=GlobalsVal.main_window
            )

        settings_file = os.path.join(self.file_list, "settings_ddnet.cfg")
        if os.path.isfile(settings_file):
            self.load_settings_ddnet_cfg(settings_file)

        json_file = os.path.join(self.file_list, "ddnet-info.json")
        if os.path.isfile(json_file):
            with open(json_file, encoding='utf-8') as f:
                GlobalsVal.ddnet_info = json.loads(f.read())

        server_list_file = os.path.join(self.file_list, "ddnet-serverlist-urls.cfg")
        GlobalsVal.server_list_file = os.path.isfile(server_list_file)

        if not os.path.isfile(f"{config_path}/app/config/config.json"):
            if "player_name" in GlobalsVal.ddnet_setting_config:
                if GlobalsVal.ddnet_setting_config["player_name"] == "Realyn//UnU":
                    cfg.set(cfg.themeColor, QColor("#af251a"))

    def load_settings_ddnet_cfg(self, file_path):
        """加载并解析 settings_ddnet.cfg 文件"""
        with open(file_path, encoding='utf-8') as f:
            lines = f.read().strip().split('\n')
            for line in lines:
                if line.strip():
                    parts = re.split(r'\s+', line, maxsplit=1)
                    if len(parts) == 2:
                        key, value = parts
                        value = self.parse_value(value)

                        if key in GlobalsVal.ddnet_setting_config:
                            if not isinstance(GlobalsVal.ddnet_setting_config[key], list):
                                GlobalsVal.ddnet_setting_config[key] = [GlobalsVal.ddnet_setting_config[key]]
                            GlobalsVal.ddnet_setting_config[key].append(value)
                        else:
                            GlobalsVal.ddnet_setting_config[key] = value

    @staticmethod
    def parse_value(value):
        """解析配置文件中的值"""
        if ',' in value:
            return [v.strip(' "') for v in re.split(r',', value)]
        return MainWindow.remove_quotes(value)

    @staticmethod
    def remove_quotes(text):
        """替换一些文本方便解析"""
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        if '" "' in text:
            return re.split(r'" "', text)
        return text

    def initNavigation(self):
        """初始化子页面"""
        self.addSubInterface(self.get_home_interface(), FIF.HOME, self.tr('首页'))
        self.addSubInterface(self.get_player_point_interface(), FIF.SEARCH, self.tr('玩家分数查询'))
        self.addSubInterface(self.get_CFG_interface(), FIF.APPLICATION, self.tr('CFG管理'))
        self.addSubInterface(self.get_resource_interface(), FIF.EMOJI_TAB_SYMBOLS, self.tr('材质管理'))
        self.addSubInterface(self.get_server_list_mirror_interface(), FIF.LIBRARY, self.tr('服务器列表管理'))
        # self.addSubInterface(self.ServerListPreviewInterface, FIF.LIBRARY, self.tr('服务器列表预览'))
        # self.addSubInterface(self.ResourceDownloadInterface, FIF.DOWNLOAD, self.tr('材质下载'))

        self.addSubInterface(self.get_setting_interface(), FIF.SETTING, self.tr('设置'), NavigationItemPosition.BOTTOM)

    def get_home_interface(self):
        if self.homeInterface is None:
            from app.view.home_interface import HomeInterface
            self.homeInterface = HomeInterface()
        return self.homeInterface

    def get_player_point_interface(self):
        if self.PlayerPointInterface is None:
            from app.view.player_point_interface import PlayerPointInterface
            self.PlayerPointInterface = PlayerPointInterface()
        return self.PlayerPointInterface

    def get_CFG_interface(self):
        if self.CFGInterface is None:
            from app.view.cfg_interface import CFGInterface
            self.CFGInterface = CFGInterface()
        return self.CFGInterface

    def get_resource_interface(self):
        if self.ResourceInterface is None:
            from app.view.resource_interface import ResourceInterface
            self.ResourceInterface = ResourceInterface()
        return self.ResourceInterface

    def get_server_list_mirror_interface(self):
        if self.ServerListMirrorInterface is None:
            from app.view.server_list_interface import ServerListInterface
            self.ServerListMirrorInterface = ServerListInterface()
        return self.ServerListMirrorInterface

    def get_setting_interface(self):
        if self.settingInterface is None:
            from app.view.setting_interface import SettingInterface
            self.settingInterface = SettingInterface(self.themeChane)
        return self.settingInterface

    def initWindow(self):
        self.resize(820, 600)
        theme = cfg.get(cfg.themeMode)
        theme = qconfig.theme if theme == Theme.AUTO else theme
        self.setWindowIcon(QIcon(base_path + f'/resource/{theme.value.lower()}/logo.svg'))
        self.setWindowTitle('DDNetToolBox')
        self.setMicaEffectEnabled(False)  # 关闭win11的云母特效

    def __theme_change(self, theme: Theme):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        self.setWindowIcon(QIcon(base_path + f'/resource/{theme.value.lower()}/logo.svg'))
