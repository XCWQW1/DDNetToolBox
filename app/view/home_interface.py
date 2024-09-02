import datetime
import requests
from PyQt5.QtGui import QFont, QPainter, QColor, QPen

from app.globals import GlobalsVal
from app.config import cfg, base_path
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRect, QSize
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QSpacerItem, QSizePolicy, QLabel, \
    QStackedWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QFrame, QToolTip, QTableWidget
from qfluentwidgets import ImageLabel, CardWidget, SubtitleLabel, BodyLabel, HeaderCardWidget, InfoBar, InfoBarPosition, \
    CaptionLabel, FlowLayout, SingleDirectionScrollArea, ToolTipFilter, ToolTipPosition, Pivot, TableWidget, SmoothMode, \
    ComboBox, StrongBodyLabel, SearchLineEdit

from app.utils.network import ImageLoader


class TEEDataLoader(QThread):
    finished = pyqtSignal(dict)

    def __init__(self, name):
        super().__init__()
        self.name = name

    def run(self):
        try:
            response = requests.get('https://ddnet.org/players/?json2={}'.format(self.name))
            if response.json() == {}:
                self.finished.emit({"error": "NoData"})
            else:
                self.finished.emit(response.json())
        except:
            self.finished.emit({"error": "InternetError"})


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

        if 'error' in json_data:
            if json_data['error'] == "NoData":
                self.labels[1].setText(self.tr('全球排名：NO.查无此人\n'
                                               '游戏分数：查无此人 分\n'
                                               '游玩时长：查无此人 小时\n'
                                               '最后完成：查无此人\n'
                                               '入坑时间：查无此人'))
            else:
                self.labels[1].setText(self.tr('全球排名：NO.数据获取失败\n'
                                               '游戏分数：数据获取失败 分\n'
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


class CreateTitleContent(QFrame):
    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)

        self.title_label = StrongBodyLabel(title)
        self.content_label = CaptionLabel(content)

        self.vBoxLayout.addWidget(self.title_label)
        self.vBoxLayout.addWidget(self.content_label)


class MapStatus(QWidget):
    tee_data = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(200)

        self.vBoxLayout = QVBoxLayout(self)
        self.hBoxLayout = QHBoxLayout()

        self.table = TableWidget()
        self.pointsWidget = CreateTitleContent(self.tr("分数 (共 {} 点)").format('NaN'), self.tr("第 {} 名，共 {} 分").format('NaN', 'NaN'))
        self.mapsWidget = CreateTitleContent(self.tr("地图 (共 {} 张)").format('NaN'), self.tr("已完成 {} 张，剩余 {} 张未完成").format('NaN', 'NaN'))
        self.teamRankWidget = CreateTitleContent(self.tr("队伍排名"), "NaN")
        self.rankWidget = CreateTitleContent(self.tr("全球排名"), "NaN")

        self.table.scrollDelagate.verticalSmoothScroll.setSmoothMode(SmoothMode.NO_SMOOTH)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setBorderRadius(5)
        self.table.setWordWrap(False)
        self.table.setColumnCount(7)
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.verticalHeader().hide()
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.table.setHorizontalHeaderLabels([
            self.tr("地图"),
            self.tr("分数"),
            self.tr("队伍排名"),
            self.tr("全球排名"),
            self.tr("用时"),
            self.tr("通关次数"),
            self.tr("首次完成于")
        ])
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.hBoxLayout.addWidget(self.pointsWidget)
        self.hBoxLayout.addWidget(self.mapsWidget)
        self.hBoxLayout.addWidget(self.teamRankWidget)
        self.hBoxLayout.addWidget(self.rankWidget)
        self.vBoxLayout.addLayout(self.hBoxLayout)
        self.vBoxLayout.addWidget(self.table)

        self.tee_data.connect(self.__on_data_loader)

    def search(self, text=None):
        if text is None:
            for i in range(self.table.rowCount()):
                self.table.setRowHidden(i, False)
        else:
            for i in range(self.table.rowCount()):
                match = False
                for j in range(self.table.columnCount()):
                    item = self.table.item(i, j)
                    if text.lower() in item.text().lower():
                        match = True
                        break
                self.table.setRowHidden(i, not match)

    def __on_data_loader(self, data):
        map_count = len(data['maps'])

        self.table.setRowCount(0)

        self.pointsWidget.title_label.setText(self.tr("分数 (共 {} 点)").format(data['points']['total']))
        if data['points']['rank'] is None:
            self.pointsWidget.content_label.setText(self.tr("未排名"))
        else:
            self.pointsWidget.content_label.setText(self.tr("第 {} 名，共 {} 分").format(data['points'].get('rank', '0'), data['points'].get('points', '0')))

        self.mapsWidget.title_label.setText(self.tr("地图 (共 {} 张)").format(map_count))

        self.team_rank = data.get('team_rank', {}).get('rank', self.tr("未排名"))
        self.teamRankWidget.content_label.setText(self.tr("未排名") if self.team_rank is None else str(self.team_rank))

        self.rank_text = data.get('rank', {}).get('rank', self.tr("未排名"))
        self.rankWidget.content_label.setText(self.tr("未排名") if self.rank_text is None else str(self.rank_text))

        data = data['maps']
        finish_map = 0

        for map_name in data:
            current_row = self.table.rowCount()
            self.table.insertRow(current_row)

            first_finish = data[map_name].get('first_finish', None)
            if first_finish is not None:
                first_finish = datetime.datetime.fromtimestamp(first_finish)
                finish_map += 1
            else:
                first_finish = ''

            team_rank = data[map_name].get('team_rank', None)
            if team_rank is not None:
                team_rank = team_rank
            else:
                team_rank = ''

            finish_time = data[map_name].get('time', None)
            if finish_time is not None:
                finish_time = datetime.timedelta(seconds=int(finish_time))
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

        self.mapsWidget.content_label.setText(self.tr("已完成 {} 张，剩余 {} 张未完成").format(finish_map, map_count - finish_map))

class TEEInfo(QWidget):
    tee_data = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)
        self.hBoxLayout = QHBoxLayout()
        self.comboBox = ComboBox()
        self.stackedWidget = QStackedWidget()
        self.searchLine = SearchLineEdit()

        self.stackedWidget.setContentsMargins(0, 0, 0, 0)

        self.NoviceWidget = MapStatus()
        self.ModerateWidget = MapStatus()
        self.BrutalWidget = MapStatus()
        self.InsaneWidget = MapStatus()
        self.DummyWidget = MapStatus()
        self.DDmaXEasyWidget = MapStatus()
        self.DDmaXNextWidget = MapStatus()
        self.DDmaXProWidget = MapStatus()
        self.DDmaXNutWidget = MapStatus()
        self.OldschoolWidget = MapStatus()
        self.SoloWidget = MapStatus()
        self.RaceWidget = MapStatus()
        self.FunWidget = MapStatus()

        self.addSubInterface(self.NoviceWidget, self.tr("Novice 简单"))
        self.addSubInterface(self.ModerateWidget, self.tr("Moderate 中阶"))
        self.addSubInterface(self.BrutalWidget, self.tr("Brutal 高阶"))
        self.addSubInterface(self.InsaneWidget, self.tr("Insane 疯狂"))
        self.addSubInterface(self.DummyWidget, self.tr("Dummy 分身"))
        self.addSubInterface(self.DDmaXEasyWidget, self.tr("DDmaX.Easy 古典.简单"))
        self.addSubInterface(self.DDmaXNextWidget, self.tr("DDmaX.Next 古典.中阶"))
        self.addSubInterface(self.DDmaXProWidget, self.tr("DDmaX.Pro 古典.高阶"))
        self.addSubInterface(self.DDmaXNutWidget, self.tr("DDmaX.Nut 古典.坚果"))
        self.addSubInterface(self.OldschoolWidget, self.tr("Oldschool 传统"))
        self.addSubInterface(self.SoloWidget, self.tr("Solo 单人"))
        self.addSubInterface(self.RaceWidget, self.tr("Race 竞速"))
        self.addSubInterface(self.FunWidget, self.tr("Fun 娱乐"))

        self.stackedWidget.setCurrentWidget(self.NoviceWidget)
        self.comboBox.currentIndexChanged.connect(lambda k: self.stackedWidget.setCurrentIndex(k))
        self.searchLine.setPlaceholderText(self.tr("搜点什么..."))

        self.hBoxLayout.addWidget(self.comboBox)
        self.hBoxLayout.addWidget(self.searchLine)
        self.vBoxLayout.addLayout(self.hBoxLayout)
        self.vBoxLayout.addWidget(self.stackedWidget)

        self.tee_data.connect(self.__on_data_loader)
        self.searchLine.returnPressed.connect(self.searchLine.search)
        self.searchLine.searchSignal.connect(lambda text=None:self.stackedWidget.currentWidget().search(text))
        self.searchLine.clearSignal.connect(lambda text=None:self.stackedWidget.currentWidget().search(text))

    def addSubInterface(self, widget: QLabel, text):
        self.stackedWidget.addWidget(widget)
        self.comboBox.addItem(text)

    def __on_data_loader(self, data):
        if data == {} or not "types" in data:
            return

        self.NoviceWidget.tee_data.emit(data['types']['Novice'])
        self.ModerateWidget.tee_data.emit(data['types']['Moderate'])
        self.BrutalWidget.tee_data.emit(data['types']['Brutal'])
        self.InsaneWidget.tee_data.emit(data['types']['Insane'])
        self.DummyWidget.tee_data.emit(data['types']['Dummy'])
        self.DDmaXEasyWidget.tee_data.emit(data['types']['DDmaX.Easy'])
        self.DDmaXNextWidget.tee_data.emit(data['types']['DDmaX.Next'])
        self.DDmaXProWidget.tee_data.emit(data['types']['DDmaX.Pro'])
        self.DDmaXNutWidget.tee_data.emit(data['types']['DDmaX.Nut'])
        self.OldschoolWidget.tee_data.emit(data['types']['Oldschool'])
        self.SoloWidget.tee_data.emit(data['types']['Solo'])
        self.RaceWidget.tee_data.emit(data['types']['Race'])
        self.FunWidget.tee_data.emit(data['types']['Fun'])


class TEEInfoList(HeaderCardWidget):
    title_player_name = pyqtSignal(dict)
    title_dummy_name = pyqtSignal(dict)

    def __init__(self, on_data: bool=False, parent=None):
        super().__init__(parent)
        self.viewLayout.setContentsMargins(0, 0, 0, 0)

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

        if on_data:
            self.addSubInterface(self.homePlayerInterface, 'homePlayerInterface', "NaN")
            self.addSubInterface(self.homeDummyInterface, 'homeDummyInterface', "NaN")
        else:
            self.addSubInterface(self.homePlayerInterface, 'homePlayerInterface', self.tr('本体'))
            self.addSubInterface(self.homeDummyInterface, 'homeDummyInterface', self.tr('分身'))

        self.stackedWidget.setCurrentWidget(self.homePlayerInterface)
        self.headerLabel.setCurrentItem(self.homePlayerInterface.objectName())
        self.headerLabel.currentItemChanged.connect(lambda k: self.stackedWidget.setCurrentWidget(self.findChild(QWidget, k)))
        self.vBoxLayout.addWidget(self.stackedWidget)

        self.title_player_name.connect(self.__changePlayerTitle)
        self.title_dummy_name.connect(self.__changeDummyTitle)

    def __changePlayerTitle(self, data):
        self.headerLabel.items['homePlayerInterface'].setText(data['player'])
        self.homePlayerInterface.tee_data.emit(data)

    def __changeDummyTitle(self, data):
        self.headerLabel.items['homeDummyInterface'].setText(data['player'])
        self.homeDummyInterface.tee_data.emit(data)

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