import requests
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap


class ImageLoader(QThread):
    finished = pyqtSignal(QPixmap)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            response = requests.get(url=self.url)
            image_data = response.content

            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
        except:
            pixmap = QPixmap()
        self.finished.emit(pixmap)


class JsonLoader(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            response = requests.get(url=self.url).json()
        except:
            response = {}

        self.finished.emit(response)
