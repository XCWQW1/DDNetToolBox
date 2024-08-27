import os
import sys

from app.config import cfg
from PyQt5.QtCore import Qt, QTranslator
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import FluentTranslator

from app.view.main_interface import MainWindow

if __name__ == '__main__':
    # 初始化目录
    if not os.path.exists(f"{os.getcwd()}/app"):
        os.mkdir(f"{os.getcwd()}/app")

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
    Translator.load(locale, "DDNetToolBox", ".", "app/resource/i18n")

    app.installTranslator(fluentTranslator)
    app.installTranslator(Translator)

    w = MainWindow()

    # 崩溃回溯
    sys.excepthook = w.show_crash_message

    w.show()
    sys.exit(app.exec_())
