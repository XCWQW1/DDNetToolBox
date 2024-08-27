import os
import sys

from app.config import cfg, base_path, config_path
from PyQt5.QtCore import Qt, QTranslator
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator

from app.view.main_interface import MainWindow

if __name__ == '__main__':
    # 初始化目录
    if not os.path.exists(f"{config_path}"):
        os.mkdir(f"{config_path}")
        os.mkdir(f"{config_path}/app")

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

    locale = cfg.get(cfg.language).value
    fluentTranslator = FluentTranslator(locale)
    Translator = QTranslator()
    Translator.load(locale, "DDNetToolBox", ".", base_path + "/resource/i18n")

    app.installTranslator(fluentTranslator)
    app.installTranslator(Translator)

    w = MainWindow()

    # 崩溃回溯
    sys.excepthook = w.show_crash_message

    w.show()
    sys.exit(app.exec_())
