import datetime
import requests

from app.globals import GlobalsVal
from app.config import cfg, base_path
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QSpacerItem, QSizePolicy, QLabel, \
    QStackedWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from qfluentwidgets import ImageLabel, CardWidget, SubtitleLabel, BodyLabel, HeaderCardWidget, InfoBar, InfoBarPosition, \
    CaptionLabel, FlowLayout, SingleDirectionScrollArea, ToolTipFilter, ToolTipPosition, Pivot, TableWidget, SmoothMode

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
            self.finished.emit([])
            return
        try:
            response = requests.get("https://update.ddnet.org/update.json").json()
            self.finished.emit(response)
        except:
            self.finished.emit([])


class TEECard(CardWidget):
    ref_status = True

    def __init__(self, name: str, tee_info_ready=None, parent=None):
        super().__init__(parent)
        self.tee_info_ready = tee_info_ready

        self.setToolTip(self.tr('单击刷新数据'))
        self.setToolTipDuration(1000)
        self.installEventFilter(ToolTipFilter(self, showDelay=300, position=ToolTipPosition.BOTTOM))

        self.name = name
        self.hBoxLayout = QHBoxLayout()
        self.vBoxLayout = QVBoxLayout()

        self.iconWidget = ImageLabel(base_path + '/resource/logo.png', self)
        self.iconWidget.scaledToHeight(120)

        self.setLayout(self.hBoxLayout)
        self.hBoxLayout.setContentsMargins(0, 15, 0, 0)

        self.hBoxLayout.addWidget(self.iconWidget, 0, Qt.AlignLeft)

        self.labels = [
            SubtitleLabel(name, self),
            BodyLabel(self.tr('全球排名：加载中...\n'
                              '游戏分数：加载中...\n'
                              '游玩时长：加载中...\n'
                              '最后完成：加载中...\n'
                              '入坑时间：加载中...'), self),
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

        self.clicked.connect(self.__on_clicked)

    def __on_clicked(self):
        if self.ref_status:
            return
        else:
            self.ref_status = True

        self.labels[1].setText(self.tr('全球排名：加载中...\n'
                                       '游戏分数：加载中...\n'
                                       '游玩时长：加载中...\n'
                                       '最后完成：加载中...\n'
                                       '入坑时间：加载中...'))

        self.image_loader = ImageLoader('https://xc.null.red:8043/api/ddnet/draw_player_skin?name={}'.format(self.name))
        self.image_loader.finished.connect(self.on_image_loaded)
        self.image_loader.start()

        self.data_loader = TEEDataLoader(self.name)
        self.data_loader.finished.connect(self.on_data_loaded)
        self.data_loader.start()

    def on_image_loaded(self, pixmap):
        self.iconWidget.setPixmap(pixmap)
        self.iconWidget.scaledToHeight(120)

    def on_data_loaded(self, json_data: dict):
        if self.tee_info_ready is not None:
            self.tee_info_ready.emit(json_data)

        if json_data == {}:
            self.labels[1].setText(self.tr('全球排名：NO.数据获取失败\n'
                                           '游戏分数：数据获取失败/数据获取失败 分\n'
                                           '游玩时长：数据获取失败 小时\n'
                                           '最后完成：数据获取失败\n'
                                           '入坑时间：数据获取失败'))
            return
        use_time = 0
        for time in json_data['activity']:
            use_time = use_time + time['hours_played']

        self.labels[1].setText(self.tr('全球排名：NO.{}\n'
                                       '游戏分数：{}/{} 分\n'
                                       '游玩时长：{} 小时\n'
                                       '最后完成：{}\n'
                                       '入坑时间：{}').format(json_data["points"]["rank"], json_data["points"]["points"],
                                                             json_data["points"]["total"], use_time,
                                                             json_data["last_finishes"][0]["map"],
                                                             datetime.datetime.fromtimestamp(json_data["first_finish"]["timestamp"])))

        self.ref_status = False


class MapStatus(QWidget):
    tee_data = pyqtSignal(dict)

    def __init__(self, map_level: str, parent=None):
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.addWidget(SubtitleLabel(map_level))

        self.table = TableWidget()
        self.table.scrollDelagate.verticalSmoothScroll.setSmoothMode(SmoothMode.NO_SMOOTH)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.setBorderRadius(5)
        self.table.setWordWrap(False)
        self.table.setColumnCount(7)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.verticalHeader().hide()
        self.table.setHorizontalHeaderLabels([
            self.tr("地图"),
            self.tr("分数"),
            self.tr("队伍排名"),
            self.tr("全球排名"),
            self.tr("用时"),
            self.tr("通关次数"),
            self.tr("首次完成于")
        ])

        self.vBoxLayout.addWidget(self.table)

        self.tee_data.connect(self.__on_data_loader)

    def __on_data_loader(self, data):
        for map_name in data:
            current_row = self.table.rowCount()
            self.table.insertRow(current_row)

            first_finish = data[map_name].get('first_finish', None)
            if first_finish is not None:
                first_finish = datetime.datetime.fromtimestamp(first_finish)
            else:
                first_finish = ''

            team_rank = data[map_name].get('team_rank', None)
            if team_rank is not None:
                team_rank = team_rank
            else:
                team_rank = ''

            finish_time = data[map_name].get('time', None)
            if finish_time is not None:
                finish_time = datetime.timedelta(seconds=finish_time)
            else:
                finish_time = ''

            add_item = [
                map_name,
                data[map_name].get('points', ''),
                team_rank,
                data[map_name].get('rank', ''),
                finish_time,
                data[map_name]['finishes'],
                first_finish
            ]

            for column, value in enumerate(add_item):
                item = QTableWidgetItem(str(value))
                self.table.setItem(current_row, column, item)


class TEEInfo(SingleDirectionScrollArea):
    tee_data = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)

        self.noviceWidget = MapStatus(self.tr("Novice"))

        self.vBoxLayout.addWidget(self.noviceWidget)

        self.tee_data.connect(self.__on_data_loader)

    def __on_data_loader(self, data):
        self.vBoxLayout.addWidget(SubtitleLabel(data['player']))
        self.noviceWidget.tee_data.emit(data['types']['Novice']['maps'])



class TEEInfoList(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.headerLabel.deleteLater()
        self.headerLabel = Pivot(self)
        self.headerLabel.setStyleSheet("font-size: 15px;")

        self.containerWidget = QWidget()
        self.vBoxLayout = QVBoxLayout(self.containerWidget)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.scrollArea = SingleDirectionScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.containerWidget)
        self.scrollArea.enableTransparentBackground()

        self.viewLayout.addWidget(self.scrollArea)

        self.stackedWidget = QStackedWidget(self)
        self.stackedWidget.setContentsMargins(0, 0, 0, 0)

        self.homePlayerInterface = TEEInfo(self)
        self.homeDummyInterface = TEEInfo(self)

        self.addSubInterface(self.homePlayerInterface, 'homePlayerInterface', '本体')
        self.addSubInterface(self.homeDummyInterface, 'homeDummyInterface', '分身')

        self.stackedWidget.setCurrentWidget(self.homePlayerInterface)
        self.headerLabel.setCurrentItem(self.homePlayerInterface.objectName())
        self.headerLabel.currentItemChanged.connect(lambda k: self.stackedWidget.setCurrentWidget(self.findChild(QWidget, k)))
        self.vBoxLayout.addWidget(self.stackedWidget)

    def addSubInterface(self, widget: QLabel, objectName, text):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.headerLabel.addItem(routeKey=objectName, text=text)


class HomeInterface(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setObjectName("HomeInterface")

        self.vBoxLayout = QVBoxLayout(self)
        self.hBoxLayout = QHBoxLayout()

        self.teeinfolist = TEEInfoList()

        # Add Layout&widget
        self.vBoxLayout.addLayout(self.hBoxLayout, Qt.AlignTop)
        self.TEECARD(GlobalsVal.ddnet_setting_config.get("player_name", "nameless tee"),
                     GlobalsVal.ddnet_setting_config.get("dummy_name", "[D] nameless te"))
        self.vBoxLayout.addWidget(self.teeinfolist, Qt.AlignCenter)

        if cfg.get(cfg.DDNetCheckUpdate):
            self.check_update = CheckUpdate()
            self.check_update.finished.connect(self.on_check_update_loaded)
            self.check_update.start()

    def on_check_update_loaded(self, json_data: list):
        if json_data == []:
            InfoBar.warning(
                title=self.tr('DDNet 版本检测'),
                content=self.tr("无法连接到DDNet官网"),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.BOTTOM_RIGHT,
                duration=-1,
                parent=self
            )
            return
        if GlobalsVal.ddnet_info['version'] != json_data[0]["version"]:
            InfoBar.warning(
                title=self.tr('DDNet 版本检测'),
                content=self.tr("您当前的DDNet版本为 {} 最新版本为 {} 请及时更新").format(
                    GlobalsVal.ddnet_info['version'], json_data[0]["version"]),
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
        self.hBoxLayout.addWidget(TEECard(player_name, self.teeinfolist.homePlayerInterface.tee_data), alignment=Qt.AlignTop)
        self.hBoxLayout.addWidget(TEECard(dummy_name, self.teeinfolist.homeDummyInterface.tee_data), alignment=Qt.AlignTop)
