import os
import sys
import traceback

from qfluentwidgets import FluentTranslator

from app.config import cfg, base_path, config_path
from PyQt5.QtCore import Qt, QTranslator
from PyQt5.QtWidgets import QApplication, QWidget, QDialog, QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton

from app.view.main_interface import MainWindow


class CrashApp(QWidget):
    def __init__(self, exc_type, exc_value, exc_traceback):
        super().__init__()

        error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(error_message)

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


def init_window():
    # 初始化目录
    if not os.path.exists(config_path):
        os.makedirs(os.path.join(config_path, "app"), exist_ok=True)

    # 启用DPI
    dpi_scale = cfg.get(cfg.dpiScale)
    if dpi_scale == "Auto":
        QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    else:
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        os.environ["QT_SCALE_FACTOR"] = str(dpi_scale)

    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    # app.setQuitOnLastWindowClosed(False)

    locale = cfg.get(cfg.language).value

    fluentTranslator = FluentTranslator(locale)
    Translator = QTranslator()
    CrashTranslator = QTranslator()

    Translator.load(locale, "DDNetToolBox.view", ".", base_path)
    CrashTranslator.load(locale, "DDNetToolBox.main", ".", base_path)

    app.installTranslator(fluentTranslator)
    app.installTranslator(Translator)
    app.installTranslator(CrashTranslator)

    w = MainWindow()

    w.show()
    app.exec_()


if __name__ == '__main__':
    # 崩溃回溯
    sys.excepthook = CrashApp
    sys.exit(init_window())
