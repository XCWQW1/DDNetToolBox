import os

from qfluentwidgets import (qconfig, QConfig, ConfigItem, Theme, OptionsConfigItem,
                            OptionsValidator, EnumSerializer, FolderValidator, BoolValidator, ColorConfigItem)

from app.utils.config_directory import get_ddnet_directory

base_path = os.path.dirname(__file__)

class Config(QConfig):
    themeMode = OptionsConfigItem("个性化", "ThemeMode", Theme.AUTO, OptionsValidator(Theme),
                                  EnumSerializer(Theme))
    dpiScale = OptionsConfigItem(
        "个性化", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True)
    themeColor = ColorConfigItem("个性化", "ThemeColor", "#009faa")
    DDNetFolder = ConfigItem("DDNet", "DDNetFolder", get_ddnet_directory(), FolderValidator())
    DDNetCheckUpdate = ConfigItem("DDNet", "DDNetCheckUpdate", True, BoolValidator())
    DDNetAssetsCursor = ConfigItem("DDNet", "DDNetAssetsCursor", None)


cfg = Config()
qconfig.load(os.getcwd() + '/app/config/config.json', cfg)
