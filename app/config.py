# coding:utf-8
import os
import sys

from qfluentwidgets import (qconfig, QConfig, ConfigItem, FolderListValidator, Theme, OptionsConfigItem,
                            OptionsValidator, EnumSerializer, FolderValidator, BoolValidator)
from app.util.config_directory import get_ddnet_directory


base_path = os.path.dirname(__file__)


class Config(QConfig):
    themeMode = OptionsConfigItem("QFluentWidgets", "ThemeMode", Theme.AUTO, OptionsValidator(Theme),
                                  EnumSerializer(Theme))
    DDNetFolder = ConfigItem("DDNet", "DDNetFolder", get_ddnet_directory(), FolderValidator())
    DDNetCheckUpdate = ConfigItem("DDNet", "DDNetCheckUpdate", True, BoolValidator())


cfg = Config()
qconfig.load(base_path + '/config/config.json', cfg)
