import datetime
import requests

from PyQt5.QtGui import QPixmap
from app.globals import GlobalsVal
from app.config import cfg, base_path
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QSpacerItem, QSizePolicy
from qfluentwidgets import ImageLabel, CardWidget, SubtitleLabel, BodyLabel, HeaderCardWidget, InfoBar, InfoBarPosition, CaptionLabel, FlowLayout, SingleDirectionScrollArea, setFont

from app.utils.network import ImageLoader


class TEEDataLoader(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, name):
        super().__init__()
        self.name = name

    def run(self):
        try:
            response = requests.get('https://ddnet.org/players/?json2={}'.format(self.name))
            self.finished.emit(response.json())
        except:
            self.finished.emit({})


class CheckUpdate(QThread):
    finished = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        if GlobalsVal.ddnet_info is None:
            self.finished.emit({})
            return
        try:
            response = requests.get("https://update.ddnet.org/update.json").json()
            self.finished.emit(response)
        except:
            self.finished.emit([])


class TEECard(CardWidget):
    def __init__(self, name: str, parent=None):
        super().__init__(parent)
        self.hBoxLayout = QHBoxLayout()
        self.vBoxLayout = QVBoxLayout()

        self.iconWidget = ImageLabel(base_path + '/resource/logo.png', self)
        self.iconWidget.scaledToHeight(120)

        self.setLayout(self.hBoxLayout)
        self.hBoxLayout.setContentsMargins(0, 15, 0, 0)

        self.hBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignLeft)

        self.labels = [
            SubtitleLabel(name, self),
            BodyLabel('全球排名：加载中...\n'
                      '游戏分数：加载中...\n'
                      '游玩时长：加载中...\n'
                      '最后完成：加载中...\n'
                      '入坑时间：加载中...', self),
        ]

        for label in self.labels:
            self.vBoxLayout.addWidget(label, 0, Qt.AlignLeft | Qt.AlignTop)

        self.spacer = QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.vBoxLayout.addItem(self.spacer)

        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.image_loader = ImageLoader('https://xc.null.red:8043/api/ddnet/draw_player_skin?name={}'.format(name))
        self.image_loader.finished.connect(self.on_image_loaded)
        self.image_loader.start()

        self.data_loader = TEEDataLoader(name)
        self.data_loader.finished.connect(self.on_data_loaded)
        self.data_loader.start()

    def on_image_loaded(self, pixmap):
        self.iconWidget.setPixmap(pixmap)
        self.iconWidget.scaledToHeight(120)

    def on_data_loaded(self, json_data: dict):
        if json_data == {}:
            self.labels[1].setText(f'全球排名：NO.数据获取失败\n'
                                   f'游戏分数：数据获取失败/数据获取失败 分\n'
                                   f'游玩时长：数据获取失败 小时\n'
                                   f'最后完成：数据获取失败\n'
                                   f'入坑时间：数据获取失败')
            return
        use_time = 0
        for time in json_data['activity']:
            use_time = use_time + time['hours_played']

        self.labels[1].setText(f'全球排名：NO.{json_data["points"]["rank"]}\n'
                               f'游戏分数：{json_data["points"]["points"]}/{json_data["points"]["total"]} 分\n'
                               f'游玩时长：{use_time} 小时\n'
                               f'最后完成：{json_data["last_finishes"][0]["map"]}\n'
                               f'入坑时间：{datetime.datetime.fromtimestamp(json_data["first_finish"]["timestamp"])}')


class FriendCard(CardWidget):
    tee_image_size = 50

    def __init__(self, name, parent=None):
        super().__init__(parent)
        if type(name) == list:
            name = name[0]

        self.setFixedSize(168, 50)

        self.iconWidget = ImageLabel(base_path + '/resource/logo.png', self)
        self.iconWidget.scaledToHeight(self.tee_image_size)
        self.label = CaptionLabel(name, self)

        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.setContentsMargins(0, 11, 6, 2)
        self.hBoxLayout.addWidget(self.iconWidget)
        self.hBoxLayout.addWidget(self.label, 0, Qt.AlignBottom | Qt.AlignRight)

        self.image_loader = ImageLoader('https://xc.null.red:8043/api/ddnet/draw_player_skin?name={}'.format(name))
        self.image_loader.finished.connect(self.on_image_loaded)
        self.image_loader.start()

    def on_image_loaded(self, pixmap):
        self.iconWidget.setPixmap(pixmap)
        self.iconWidget.scaledToHeight(self.tee_image_size)


class FriendList(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle('好友列表')

        self.containerWidget = QWidget()
        self.fBoxLayout = FlowLayout(self.containerWidget)

        self.batch_size = 1
        self.current_index = 0
        try:
            self.friend_list = GlobalsVal.ddnet_setting_config['add_friend']
            QTimer.singleShot(0, self.load_friend)
        except:
            self.label = SubtitleLabel("没有获取到任何数据 T-T", self)
            self.hBoxLayout = QHBoxLayout()

            setFont(self.label, 24)
            self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)
            self.viewLayout.addLayout(self.hBoxLayout)
            return

        self.scrollArea = SingleDirectionScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.containerWidget)
        self.scrollArea.enableTransparentBackground()

        self.viewLayout.addWidget(self.scrollArea)
        self.viewLayout.setContentsMargins(11, 11, 11, 11)

    def load_friend(self):
        end_index = min(self.current_index + self.batch_size, len(self.friend_list))
        for i in range(self.current_index, end_index):
            self.fBoxLayout.addWidget(FriendCard(self.friend_list[i]))
        self.current_index = end_index

        if self.current_index < len(self.friend_list):
            QTimer.singleShot(0, self.load_friend)


class HomeInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("HomeInterface")

        self.vBoxLayout = QVBoxLayout(self)
        self.hBoxLayout = QHBoxLayout()

        self.vBoxLayout.addLayout(self.hBoxLayout, Qt.AlignTop)

        try:
            self.TEECARD(GlobalsVal.ddnet_setting_config["player_name"], GlobalsVal.ddnet_setting_config["dummy_name"])
        except:
            self.TEECARD("nameless tee", "[D] nameless te")

        self.vBoxLayout.addWidget(FriendList(), Qt.AlignCenter)

        if cfg.get(cfg.DDNetCheckUpdate):
            self.check_update = CheckUpdate()
            self.check_update.finished.connect(self.on_check_update_loaded)
            self.check_update.start()

    def on_check_update_loaded(self, json_data: list):
        if json_data == []:
            InfoBar.warning(
                title='DDNet 版本检测',
                content="无法连接到DDNet官网",
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=-1,
                parent=self
            )
            return
        if GlobalsVal.ddnet_info['version'] != json_data[0]["version"]:
            InfoBar.warning(
                title='DDNet 版本检测',
                content="您当前的DDNet版本为 {} 最新版本为 {} 请及时更新".format(GlobalsVal.ddnet_info['version'], json_data[0]["version"]),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=-1,
                parent=self
            )

    def TEECARD(self, player_name: str, dummy_name: str):
        for i in reversed(range(self.hBoxLayout.count())):
            widget = self.hBoxLayout.itemAt(i).widget()
            self.hBoxLayout.removeWidget(widget)
            widget.deleteLater()

        self.hBoxLayout.addWidget(TEECard(player_name), alignment=Qt.AlignTop)
        self.hBoxLayout.addWidget(TEECard(dummy_name), alignment=Qt.AlignTop)
