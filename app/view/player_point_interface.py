import datetime

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy, QStackedWidget, QLabel
from qfluentwidgets import CardWidget, ToolTipFilter, ToolTipPosition, SubtitleLabel, BodyLabel, ProgressRing, \
    SearchLineEdit, ImageLabel, HeaderCardWidget, Pivot, SingleDirectionScrollArea
from sspicon import SECPKG_ATTR_NATIVE_NAMES

from app.utils.points_rank import points_rank
from app.view.home_interface import TEEDataLoader, TEEInfo, TEEInfoList


class ByteLimitedSearchLineEdit(SearchLineEdit):
    def __init__(self, max_bytes, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_bytes = max_bytes
        self.textChanged.connect(self.limit_text)

    def limit_text(self):
        text = self.text()
        while len(text.encode('utf-8')) > self.max_bytes:
            text = text[:-1]
        self.setText(text)


class TEERankCard(CardWidget):
    ref_status = True

    def __init__(self, tee_info_ready=None, parent=None):
        super().__init__(parent)
        self.setMaximumSize(16777215, 180)
        self.tee_info_ready = tee_info_ready

        self.setToolTip(self.tr('单击刷新数据'))
        self.setToolTipDuration(1000)
        self.installEventFilter(ToolTipFilter(self, showDelay=300, position=ToolTipPosition.BOTTOM))

        self.name = "NaN"
        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()
        self.teeRankRing = ProgressRing()
        self.labels = [
            SubtitleLabel(self.name, self),
            BodyLabel(self.tr('全球排名：NaN\n'
                              '游戏分数：NaN\n'
                              '游玩时长：NaN\n'
                              '最后完成：NaN\n'
                              '入坑时间：NaN'), self),
        ]

        self.teeRankRing.setTextVisible(True)
        self.teeRankRing.setFormat("NaN")
        self.teeRankRing.setFont(QFont(None, 35))
        self.teeRankRing.setStrokeWidth(10)
        self.hBoxLayout.setContentsMargins(15, 15, 15, 15)

        self.hBoxLayout.addLayout(self.vBoxLayout)
        for label in self.labels:
            self.vBoxLayout.addWidget(label, 0, Qt.AlignLeft | Qt.AlignTop)
        self.hBoxLayout.addWidget(self.teeRankRing)

        self.clicked.connect(self.__on_clicked)

    def on_data(self, name):
        self.name = name
        self.labels[0].setText(name)
        self.ref_status = False
        self.__on_clicked()


    def __on_clicked(self):
        if self.ref_status:
            return
        else:
            self.ref_status = True

        self.teeRankRing.setRange(0, 100)
        self.teeRankRing.setValue(0)
        self.teeRankRing.setFormat("NaN")
        self.tee_info_ready.emit({"player": self.name})
        self.labels[1].setText(self.tr('全球排名：加载中...\n'
                                       '游戏分数：加载中...\n'
                                       '游玩时长：加载中...\n'
                                       '最后完成：加载中...\n'
                                       '入坑时间：加载中...'))

        # self.image_loader = ImageLoader('https://xc.null.red:8043/api/ddnet/draw_player_skin?name={}'.format(self.name))
        # self.image_loader.finished.connect(self.on_image_loaded)
        # self.image_loader.start()

        self.data_loader = TEEDataLoader(self.name)
        self.data_loader.finished.connect(self.on_data_loaded)
        self.data_loader.start()

    def on_image_loaded(self, pixmap):
        self.iconWidget.setPixmap(pixmap)
        self.iconWidget.scaledToHeight(120)

    def on_data_loaded(self, json_data: dict):
        if self.tee_info_ready is not None:
            json_data['player'] = self.name
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
            self.ref_status = False
            return
        use_time = 0
        for time in json_data['activity']:
            use_time = use_time + time['hours_played']

        self.teeRankRing.setRange(0, json_data["points"]["total"])
        self.teeRankRing.setValue(json_data["points"]["points"])
        self.teeRankRing.setFormat(points_rank(json_data["points"]["points"], json_data["points"]["total"], use_time, json_data["points"]["rank"]))
        self.labels[1].setText(self.tr('全球排名：NO.{}\n'
                                       '游戏分数：{}/{} 分\n'
                                       '游玩时长：{} 小时\n'
                                       '最后完成：{}\n'
                                       '入坑时间：{}').format(json_data["points"]["rank"], json_data["points"]["points"],
                                                             json_data["points"]["total"], use_time,
                                                             json_data["last_finishes"][0]["map"],
                                                             datetime.datetime.fromtimestamp(json_data["first_finish"]["timestamp"])))

        self.ref_status = False


class PlayerPointInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName('PlayerPointInterface')

        self.vBoxLayout = QVBoxLayout(self)
        self.teeinfolist = TEEInfoList(on_data=True)
        self.searchHBoxLayout = QHBoxLayout()
        self.teeHBoxLayout = QHBoxLayout()
        self.teeRankCard = TEERankCard(self.teeinfolist.title_player_name)
        self.searchLine = ByteLimitedSearchLineEdit(15)
        self.compareTeeRankCard = TEERankCard(self.teeinfolist.title_dummy_name)
        self.compareSearchLine = ByteLimitedSearchLineEdit(15)

        self.searchLine.setPlaceholderText(self.tr("填写要查询的玩家名称"))
        self.searchLine.setMaxLength(15)
        self.compareSearchLine.setPlaceholderText(self.tr("填写要比较的玩家名称"))

        self.searchHBoxLayout.addWidget(self.searchLine)
        self.searchHBoxLayout.addWidget(self.compareSearchLine)
        self.teeHBoxLayout.addWidget(self.teeRankCard, 0, Qt.AlignTop)
        self.teeHBoxLayout.addWidget(self.compareTeeRankCard, 0, Qt.AlignTop)
        self.vBoxLayout.addLayout(self.searchHBoxLayout)
        self.vBoxLayout.addLayout(self.teeHBoxLayout)
        self.vBoxLayout.addWidget(self.teeinfolist)

        self.searchLine.returnPressed.connect(self.searchLine.search)
        self.searchLine.searchSignal.connect(self.teeRankCard.on_data)
        self.compareSearchLine.returnPressed.connect(self.compareSearchLine.search)
        self.compareSearchLine.searchSignal.connect(self.compareTeeRankCard.on_data)