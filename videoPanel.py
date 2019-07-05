from os import path
from urllib.parse import urlparse
from PySide2.QtWidgets import (QWidget, QLabel, QVBoxLayout, QPushButton, 
QHBoxLayout)
from PySide2.QtCore import Signal, Slot
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
        self.vlc_instance = vlc.Instance("-q")
        self.initUI()
    
    def initUI(self):
        # Main Layout
        mainlayout = QVBoxLayout()
        mainlayout.setContentsMargins(0, 0, 0, 0)
        mainlayout.setMargin(0)
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
        self.setLayout(mainlayout)
        self.show()
    
    @Slot(str)
    def loadVideoFile(self, videoFile):
        print(videoFile)
        t_media = self.vlc_instance.media_new(videoFile)
        self.mPlayer.set_media(t_media)
        self.mPlayer.video_set_aspect_ratio(b"16:9")
        self.mPlayer.play()
