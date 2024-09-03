import os
from enum import Enum

import platformdirs
from PyQt5.QtCore import QLocale
from qfluentwidgets import (qconfig, QConfig, ConfigItem, Theme, OptionsConfigItem,
                            OptionsValidator, EnumSerializer, FolderValidator, BoolValidator, ColorConfigItem,
                            ConfigSerializer)

from app.utils.config_directory import get_ddnet_directory

base_path = os.path.dirname(__file__)
config_path = platformdirs.user_config_dir(appname="DDNetToolBox", appauthor="XCWQW233")


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO



class Config(QConfig):
    themeMode = OptionsConfigItem("个性化", "ThemeMode", Theme.AUTO, OptionsValidator(Theme),
                                  EnumSerializer(Theme))
    dpiScale = OptionsConfigItem(
        "个性化", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    themeColor = ColorConfigItem("个性化", "ThemeColor", "#009faa")
    language = OptionsConfigItem("个性化", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True)
    DDNetFolder = ConfigItem("DDNet", "DDN1etFolder", get_ddnet_directory(), FolderValidator())
    DDNetCheckUpdate = ConfigItem("DDNet", "DDNetCheckUpdate", True, BoolValidator())
    DDNetAssetsCursor = ConfigItem("DDNet", "DDNetAssetsCursor", None)


cfg = Config()
qconfig.load(config_path + '/app/config/config.json', cfg)
