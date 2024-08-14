# coding:utf-8
import os

from qfluentwidgets import (qconfig, QConfig, ConfigItem, Theme, OptionsConfigItem,
                            OptionsValidator, EnumSerializer, FolderValidator, BoolValidator)
from app.utils.config_directory import get_ddnet_directory

base_path = os.path.dirname(__file__)


class Config(QConfig):
    themeMode = OptionsConfigItem("MainWindow", "ThemeMode", Theme.AUTO, OptionsValidator(Theme),
                                  EnumSerializer(Theme))
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    DDNetFolder = ConfigItem("DDNet", "DDNetFolder", get_ddnet_directory(), FolderValidator())
    DDNetCheckUpdate = ConfigItem("DDNet", "DDNetCheckUpdate", True, BoolValidator())


cfg = Config()
qconfig.load(os.getcwd() + '/app/config/config.json', cfg)
