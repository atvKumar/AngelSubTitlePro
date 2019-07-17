from os import path
from urllib.parse import urlparse
from math import floor
from time import sleep
from PySide2.QtWidgets import (QWidget, QLabel, QVBoxLayout, QPushButton, 
QHBoxLayout, QSlider, QFileDialog)
from PySide2.QtCore import Signal, Slot, QSize, Qt, QTimer
from PySide2.QtGui import QPixmap, QIcon
from vlc import EventType, VideoMarqueeOption, VideoLogoOption, Position, str_to_bytes
from timecode import TimeCode
import vlc, sys

def resource_path(relative_path):
     if hasattr(sys, '_MEIPASS'):
         return path.join(sys._MEIPASS, relative_path)
     return path.join(path.abspath("."), relative_path)


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
    message = Signal(str)
    def __init__(self):
        super(vlcPlayer, self).__init__()
        self.vlc_instance = vlc.Instance("-q") # '--verbose 2'.split()
        self.mPlayer = self.vlc_instance.media_player_new()
        self.event_manager = self.mPlayer.event_manager()
        self.currVideoFile = ""
        self.fileParsed = False
        self.isPlaying = False
        self.isSeekable = False
        self.event_manager.event_attach(EventType.MediaPlayerTimeChanged, self.vlc_event_handle_timeChanged)
        self.event_manager.event_attach(EventType.MediaPlayerPlaying, self.vlc_event_handle_MediaPlaying)
        self.event_manager.event_attach(EventType.MediaPlayerPaused, self.vlc_event_handle_MediaPaused)
        self.event_manager.event_attach(EventType.MediaPlayerEndReached, self.vlc_event_handle_MediaEnded)
        self.timer = QTimer(self)
        self.safezone = False
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
        if sys.platform.startswith('linux'):  # linux
            self.mPlayer.set_xwindow(vframeID)
        elif sys.platform == "win32":  # windows
            self.mPlayer.set_hwnd(vframeID)
        elif sys.platform == "darwin":  # mac
            self.mPlayer.set_nsobject(vframeID)
        # Connect to Slot
        videoFrame.fileDroped.connect(self.loadVideoFile)
        vctrl_layout = QHBoxLayout()
        # Previous Frame
        btn_pf = QPushButton()
        btn_pf.setFixedSize(QSize(32, 32))
        ico_pf = QIcon(QPixmap(resource_path("icons/previous.png")))
        btn_pf.setIcon(ico_pf)
        btn_pf.clicked.connect(self.previousFrame)
        # Rewind
        btn_rewind = QPushButton()
        btn_rewind.setFixedSize(QSize(32, 32))
        ico_re = QIcon(QPixmap(resource_path("icons/rewind.png")))
        btn_rewind.setIcon(ico_re)
        btn_rewind.clicked.connect(self.rewind)
        # btn_rewind.release.connect(self.playVideo)
        btn_rewind.setAutoRepeat(True)
        btn_rewind.setAutoRepeatInterval(1000)
        btn_rewind.setAutoRepeatDelay(1000)
        # Play
        btn_play = QPushButton()
        btn_play.setFixedSize(QSize(32, 32))
        ico_play = QIcon(QPixmap(resource_path("icons/play-button.png"))) # "icons/play-button.png"
        btn_play.setIcon(ico_play)
        btn_play.clicked.connect(self.playVideo)
        # Pause
        btn_pause = QPushButton()
        btn_pause.setFixedSize(QSize(32, 32))
        ico_pause = QIcon(QPixmap(resource_path("icons/pause-button.png")))
        btn_pause.setIcon(ico_pause)
        btn_pause.clicked.connect(self.pauseVideo)
        # Fast Forward
        btn_ff = QPushButton()
        btn_ff.setFixedSize(QSize(32, 32))
        ico_ff = QIcon(QPixmap(resource_path("icons/fast-forward.png")))
        btn_ff.setIcon(ico_ff)
        btn_ff.clicked.connect(self.fastforward)
        # Next Frame
        btn_nf = QPushButton()
        btn_nf.setFixedSize(QSize(32, 32))
        ico_nf = QIcon(QPixmap(resource_path("icons/next.png")))
        btn_nf.setIcon(ico_nf)
        btn_nf.clicked.connect(self.nextFrame)
        # Video Lenght Slider
        self.video_slider = QSlider(Qt.Orientation.Horizontal)
        self.video_slider.setMinimum(0)
        self.video_slider.setMaximum(1000)  # Rough
        # self.video_slider.sliderPressed.connect(self.pauseVideo)
        self.video_slider.sliderMoved.connect(self.vslider_moved)
        self.video_slider.sliderReleased.connect(self.vslider_released)
        # self.video_slider.valueChanged.connect(self.sliderChanged)
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
        vctrl_layout.addWidget(self.video_slider)
        vctrl_layout.addWidget(self.tcPos)
        mainlayout.addLayout(vctrl_layout, 1)
        self.setLayout(mainlayout)
        self.show()
        self.timer.setInterval(200)
        self.timer.timeout.connect(self.vslider_posUpdate)
        # Disable Controls
        # btn_rewind.setDisabled(True)
    
    @Slot(str)
    def loadVideoFile(self, videoFile):
        self.fileParsed = False
        t_media = self.vlc_instance.media_new(videoFile)
        self.mPlayer.set_media(t_media)
        self.mPlayer.video_set_aspect_ratio(b"16:9")
        t_media.parse_with_options(1,0)
        sleep(1) # Time to parse video
        if t_media.get_parsed_status() == vlc.MediaParsedStatus().done:
            self.fileParsed = True
            self.currVideoFile = videoFile
            self.message.emit(f"{path.basename(videoFile)} Loaded!")
        self.dur = t_media.get_duration()/1000  # video duration in seconds
        self.video_duration = TimeCode()
        self.video_duration.setSecs(self.dur)
        # self.video_slider.setMaximum(floor(self.dur))
        self.tcPos.setText(self.video_duration.getTimeCode())
        # self.set_subtitle_file("/Users/promo3/Desktop/PHB0138.srt")

    def set_subtitle_file(self, filename)->bool:
        final_path = f"file://{filename}"  # https://github.com/caprica/vlcj/issues/497
        # 0 for subtitle 1 for audio vlc.MediaSlaveType(0)
        x = vlc.libvlc_media_player_add_slave(self.mPlayer, 0, str_to_bytes(final_path), True)
        if x == 0:
            return True
        else:
            return False
    
    def get_video_size(self):
        if self.fileParsed:
            return vlc.libvlc_video_get_size(self.mPlayer, 0)
    
    def getPosition(self):  # More accurate video position
        newPos = self.mPlayer.get_time()/1000
        self.currPos = TimeCode()
        self.currPos.setSecs(newPos)
        return newPos
    
    def vlc_event_handle_timeChanged(self, event): # MediaPlayerTimeChanged
        self.getPosition()
        self.tcPos.setText(self.currPos.timecode)
    
    def vlc_event_handle_MediaParsed(self, event): # vlc ParseChanged event never fires
        pass
    
    def vlc_event_handle_MediaPlaying(self, event): # MediaPlayerPlaying
        # Processing event.u causes Segmentation 11 errors
        self.isPlaying = True
        self.message.emit(f"Video Playing!")
    
    def vlc_event_handle_MediaPaused(self, event): # MediaPlayerPaused
        self.isPlaying = False
        self.message.emit(f"Video Paused!")
    
    def vlc_event_handle_MediaEnded(self, event): # MediaPlayerEndReached
        self.isPlaying = False
        self.isSeekable = False
        self.message.emit("Video End Reached!")

    def playVideo(self):
        if not self.isPlaying:
            self.mPlayer.play()
            self.timer.start()
            if self.isSeekable == False: # Check once
                if self.mPlayer.is_seekable() == 1:
                    self.isSeekable = True
            sleep(1)
        else:
            self.mPlayer.set_rate(1.0)

    @Slot()
    def pauseVideo(self):
        if self.isPlaying and self.mPlayer.can_pause():
            self.mPlayer.pause()
            self.timer.stop()
            self.mPlayer.set_rate(1.0)

    @Slot()
    def nextFrame(self):
        if not self.isPlaying and self.isSeekable:
            self.mPlayer.next_frame()
            tc = TimeCode()
            tc.setTimeCode(self.tcPos.text())
            tc += 1
            self.tcPos.setText(tc.timecode)
            self.tcPos.repaint()

    @Slot()
    def previousFrame(self):
        if not self.isPlaying and self.isSeekable:
            currPos = self.mPlayer.get_position()  # Not accurate
            self.mPlayer.set_position(currPos - 0.001)
            self.getPosition()
            self.tcPos.setText(self.currPos.timecode)
            self.tcPos.repaint()
    @Slot()
    def fastforward(self):
        curPlayRate = self.mPlayer.get_rate()
        self.mPlayer.set_rate(curPlayRate * 2)

    @Slot()
    def rewind(self):
        if self.isPlaying:
            self.pauseVideo()
        currPos = self.mPlayer.get_position()  # Not accurate
        # print("Seeking to ", currPos-0.1)
        self.mPlayer.set_position(currPos - 0.01)
        pos_msecs = self.getPosition()
        self.tcPos.setText(self.currPos.timecode)
        self.tcPos.repaint()
        self.video_slider.setSliderPosition(floor(pos_msecs))
    
    def vslider_moved(self, position):
        self.mPlayer.set_position(position/1000)
    
    def vslider_released(self):
        self.mPlayer.play()
    
    def vslider_posUpdate(self):
        self.video_slider.setSliderPosition(self.mPlayer.get_position()*1000)
        self.video_slider.repaint()

    @Slot()
    def play_pause(self):
        if self.fileParsed:
            if not self.isPlaying:
                self.mPlayer.play()
                self.timer.start()
                if self.isSeekable == False: # Check once
                    if self.mPlayer.is_seekable() == 1:
                        self.isSeekable = True
            else:
                self.mPlayer.pause()
                self.timer.stop()
            sleep(1)
            self.mPlayer.set_rate(1.0)
    
    @Slot()
    def load_video(self):
        file_dialog = QFileDialog(self, "Open Video File")
        selected_file = file_dialog.getOpenFileName()
        if selected_file:
            self.loadVideoFile(selected_file[0])
    
    def set_overlay_text(self, text):  # Timeout and Refresh options available
        self.mPlayer.video_set_marquee_int(VideoMarqueeOption.Enable, 1)
        self.mPlayer.video_set_marquee_int(VideoMarqueeOption.Size, 20)
        self.mPlayer.video_set_marquee_int(VideoMarqueeOption.Position, Position.Bottom+Position.Center)
        self.mPlayer.video_set_marquee_string(VideoMarqueeOption.Text, str_to_bytes(text))

    @Slot()
    def set_overlay_safezone(self):
        if not self.safezone:
            self.mPlayer.video_set_logo_int(VideoLogoOption.logo_enable, 1)
            self.mPlayer.video_set_logo_string(VideoLogoOption.logo_file, str_to_bytes(resource_path("icons/camera_safe_areas_646x360.png")))
            self.safezone = True
        else:
            self.mPlayer.video_set_logo_int(VideoLogoOption.logo_enable, 0)
            self.safezone = False