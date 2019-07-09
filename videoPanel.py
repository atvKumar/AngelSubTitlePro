from os import path
from urllib.parse import urlparse
from math import floor
from time import sleep
from PySide2.QtWidgets import (QWidget, QLabel, QVBoxLayout, QPushButton, 
QHBoxLayout, QSlider)
from PySide2.QtCore import Signal, Slot, QSize, Qt
from PySide2.QtGui import QPixmap, QIcon
from vlc import EventType
from timecode import TimeCode
import vlc, sys


class video_frame(QLabel):
    fileDroped = Signal(str)
    def __init__(self):
        super(video_frame, self).__init__()
        self.setStyleSheet("QLabel {background: 'black';}")
        self.setMinimumSize(480, 360)
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, e):
        file_url = e.mimeData().text()
        p = urlparse(file_url)
        self.finalPath = path.abspath(path.join(p.netloc, p.path))
        if path.exists(self.finalPath):
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e):
        self.fileDroped.emit(self.finalPath)


class vlcPlayer(QWidget):
    def __init__(self):
        super(vlcPlayer, self).__init__()
        self.vlc_instance = vlc.Instance("-q") # '--verbose 2'.split()
        self.initUI()
    
    def initUI(self):
        # Main Layout
        mainlayout = QVBoxLayout()
        mainlayout.setContentsMargins(0, 0, 0, 0)
        mainlayout.setMargin(5)
        mainlayout.setSpacing(0)
        videoFrame = video_frame()
        mainlayout.addWidget(videoFrame)
        vframeID = videoFrame.winId()
        # Connect to Slot
        videoFrame.fileDroped.connect(self.loadVideoFile)
        self.mPlayer = self.vlc_instance.media_player_new()
        if sys.platform.startswith('linux'):  # linux
            self.mPlayer.set_xwindow(vframeID)
        elif sys.platform == "win32":  # windows
            self.mPlayer.set_hwnd(vframeID)
        elif sys.platform == "darwin":  # mac
            self.mPlayer.set_nsobject(vframeID)
        vctrl_layout = QHBoxLayout()
        # Previous Frame
        btn_pf = QPushButton()
        btn_pf.setFixedSize(QSize(32, 32))
        ico_pf = QIcon(QPixmap("icons/previous.png"))
        btn_pf.setIcon(ico_pf)
        btn_pf.clicked.connect(self.previousFrame)
        # Rewind
        btn_rewind = QPushButton()
        btn_rewind.setFixedSize(QSize(32, 32))
        ico_re = QIcon(QPixmap("icons/rewind.png"))
        btn_rewind.setIcon(ico_re)
        btn_rewind.clicked.connect(self.rewind)
        # Play
        btn_play = QPushButton()
        btn_play.setFixedSize(QSize(32, 32))
        ico_play = QIcon(QPixmap("icons/play-button.png"))
        btn_play.setIcon(ico_play)
        btn_play.clicked.connect(self.playVideo)
        # Pause
        btn_pause = QPushButton()
        btn_pause.setFixedSize(QSize(32, 32))
        ico_pause = QIcon(QPixmap("icons/pause-button.png"))
        btn_pause.setIcon(ico_pause)
        btn_pause.clicked.connect(self.pauseVideo)
        # Fast Forward
        btn_ff = QPushButton()
        btn_ff.setFixedSize(QSize(32, 32))
        ico_ff = QIcon(QPixmap("icons/fast-forward.png"))
        btn_ff.setIcon(ico_ff)
        btn_ff.clicked.connect(self.fastforward)
        # Next Frame
        btn_nf = QPushButton()
        btn_nf.setFixedSize(QSize(32, 32))
        ico_nf = QIcon(QPixmap("icons/next.png"))
        btn_nf.setIcon(ico_nf)
        btn_nf.clicked.connect(self.nextFrame)
        # Video Lenght Slider
        self.vlenght = QSlider(Qt.Orientation.Horizontal)
        self.vlenght.setMinimum(0)
        self.vlenght.setMaximum(1000)  # Rough
        # Duration
        self.tcPos = QLabel("00:00:00:00")
        self.tcPos.setMaximumHeight(20)
        self.tcPos.setStyleSheet("border: 1px solid black")
        vctrl_layout.addWidget(btn_pf)
        vctrl_layout.addWidget(btn_rewind)
        vctrl_layout.addWidget(btn_play)
        vctrl_layout.addWidget(btn_pause)
        vctrl_layout.addWidget(btn_ff)
        vctrl_layout.addWidget(btn_nf)
        vctrl_layout.addWidget(self.vlenght)
        # vctrl_layout.addWidget(tcIn)
        # vctrl_layout.addWidget(tcOut)
        vctrl_layout.addWidget(self.tcPos)
        mainlayout.addLayout(vctrl_layout, 1)
        self.setLayout(mainlayout)
        self.show()
        # Disabled until further notice
        # btn_nf.setDisabled(True)
        # btn_pf.setDisabled(True)
        btn_rewind.setDisabled(True)
    
    @Slot(str)
    def loadVideoFile(self, videoFile):
        # print("Video File:", videoFile)
        t_media = self.vlc_instance.media_new(videoFile)
        self.mPlayer.set_media(t_media)
        self.mPlayer.video_set_aspect_ratio(b"16:9")
        # self.mPlayer.play()
        t_media.parse() # Depreciated : Async parse_with_options()
        # print("Video Duration:", t_media.get_duration())
        self.dur = t_media.get_duration()/1000
        # print(dur, floor(self.dur))
        vidDur = TimeCode()
        vidDur.setSecs(self.dur)
        self.vlenght.setMaximum(floor(self.dur))
        self.tcPos.setText(vidDur.getTimeCode())
    
    def vlc_event_handle_timeChanged(self, event):
        if event.type == EventType.MediaPlayerTimeChanged:
            newPos = self.mPlayer.get_time()/1000
            newTC = TimeCode()
            newTC.setSecs(newPos)
            self.tcPos.setText(newTC.timecode)
            self.vlenght.setSliderPosition(floor(newPos))
    
    def playVideo(self):
        self.event_manager = self.mPlayer.event_manager()
        self.event_manager.event_attach(EventType.MediaPlayerTimeChanged, self.vlc_event_handle_timeChanged)
        if not self.mPlayer.is_playing():
            self.mPlayer.play()
        else:
            self.mPlayer.set_rate(1.0)
    
    def pauseVideo(self):
        if self.mPlayer.is_playing() and self.mPlayer.can_pause():
            self.mPlayer.pause()
            self.mPlayer.set_rate(1.0)
    
    def nextFrame(self):
        if not self.mPlayer.is_playing() and self.mPlayer.is_seekable() == 1:
            self.mPlayer.next_frame()
            tc = TimeCode()
            tc.setTimeCode(self.tcPos.text())
            tc += 1
            self.tcPos.setText(tc.timecode)
            self.tcPos.repaint()
            # assert self.tcDur.text() == tc.timecode

    def previousFrame(self):
        if not self.mPlayer.is_playing() and self.mPlayer.is_seekable() == 1:
            currPos = self.mPlayer.get_position()
            self.mPlayer.set_position(currPos - 0.001)  # Frames in Milliseconds
            newPos = self.mPlayer.get_time()/1000
            newTC = TimeCode()
            newTC.setSecs(newPos)
            self.tcPos.setText(newTC.timecode)
            self.tcPos.repaint()
    
    def fastforward(self):
        curPlayRate = self.mPlayer.get_rate()
        self.mPlayer.set_rate(curPlayRate * 2)
    
    def rewind(self):
        curPlayRate = self.mPlayer.get_rate()
        self.mPlayer.set_rate(curPlayRate / 2)
