import sys, os
import xml.etree.ElementTree as xmlET
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (QWidget, QApplication, QMainWindow, QDockWidget, 
QSizePolicy, QLabel, QMenu, QAction, QTableWidgetItem, QShortcut, QFileDialog)
from editPanel import subTitleEdit
from videoPanel import vlcPlayer
from dataPanel import subTitleTable
from waveformPanel import waveform
from timecode import TimeCode
from os.path import splitext, abspath, join, exists
from copy import deepcopy
from urllib.parse import urlparse
from tempfile import NamedTemporaryFile


__major__ = 2
__minor__ = 0
__version__ = f"Beta {__major__}.{__minor__}"


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.re_editing = False
        self.initUI()
        self.setup_shortcuts()
        self._tmp = NamedTemporaryFile(suffix=".srt", delete=False)
        self.tmp = self._tmp.name
        self.importing = False
    
    def initUI(self):
        self.setMinimumSize(50, 70)
        self.setWindowTitle(f"Angel SubTitle Pro ({__version__})")
        self.sb = self.statusBar() 
        self.updateStatusBar(__version__)
        # Dockable Widgets -----------------------------------------------------------
        # self.dock1 = QDockWidget("Video Player", self) # Coverted to Central Widget
        self.dock2 = QDockWidget("Text Editing View", self)
        self.dock3 = QDockWidget("Table View", self)
        self.dock4 = QDockWidget("Waveform View", self)
        # Title Widgets    -----------------------------------------------------------
        # self.oldD1Title = self.dock1.titleBarWidget()  # Dock1
        self.oldD2Title = self.dock2.titleBarWidget()
        self.oldD3Title = self.dock3.titleBarWidget()
        self.oldD4Title = self.dock4.titleBarWidget()
        # self.noTitle1 = QWidget()  # Dock1
        self.noTitle2 = QWidget()
        self.noTitle3 = QWidget()
        self.noTitle4 = QWidget()
        # self.dock1.setTitleBarWidget(self.noTitle1)  # Dock1
        self.dock2.setTitleBarWidget(self.noTitle2)
        self.dock3.setTitleBarWidget(self.noTitle3)
        self.dock4.setTitleBarWidget(self.noTitle4)
        # Dockable Areas
        self.dock2.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.dock3.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.dock4.setAllowedAreas(Qt.AllDockWidgetAreas)
        # Adding Dockable Widgets ----------------------------------------------------
        # self.addDockWidget(Qt.RightDockWidgetArea, self.dock1)  # Video Player Panel
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock3)  # Subtitle Table Panel
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock2)  # Subtitle Editing Panel
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock4)  # Waveform Panel
        self.tabifyDockWidget(self.dock3, self.dock4)
        self.dock3.raise_()
        # Panel Instances ------------------------------------------------------------
        self.videoPanel = vlcPlayer()
        self.editPanel = subTitleEdit()
        self.subTablePanel = subTitleTable()
        self.setCentralWidget(self.videoPanel)
        self.waveFormPanel = waveform(self)
        # self.dock1.setWidget(self.videoPanel)
        self.dock2.setWidget(self.editPanel)
        self.dock3.setWidget(self.subTablePanel)
        # self.dock4.setWidget(QLabel("Under Construction"))
        self.dock4.setWidget(self.waveFormPanel)
        # Right Click Actions --------------------------------------------------------
        self.actShowT = QAction("Show TitleBar", self)
        self.actShowT.triggered.connect(self.showTitleBar)
        self.actHideT = QAction("Hide TitleBar", self)
        self.actHideT.triggered.connect(self.hideTitleBar)
        # Signals & Slot Connections
        self.videoPanel.message.connect(self.updateStatusBar)
        self.subTablePanel.verticalHeader().sectionDoubleClicked.connect(self.edit_row)
        self.subTablePanel.row_deleted.connect(self.row_deleted_update)
        self.subTablePanel.row_added.connect(self.row_added_update)
        self.waveFormPanel.file_loaded.connect(self.updateStatusBar)
        self.waveFormPanel.selectionCtrl.sigRegionChangeFinished.connect(self.processWaveformSelection)
        
        # Final Cleanup before show
        self.editPanel.subtitle.setFocus()
    
    def isVideoParsed(self):
        return self.videoPanel.fileParsed
    
    def getVideoFilePath(self):
        if self.isVideoParsed():
            return self.videoPanel.currVideoFile
        else:
            return None
    
    def setup_shortcuts(self):
        shortcut_open = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_O), self)
        shortcut_open.activated.connect(self.open_project)
        shortcut_save = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_S), self)
        shortcut_save.activated.connect(self.save_project)
        shortcut_export = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_E), self)
        shortcut_export.activated.connect(self.export_project)
        shortcut_import = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_I), self)
        shortcut_import.activated.connect(self.import_project)
        # Subtitle Editing Shortcuts
        shortcut_setIn = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_BracketLeft), self)
        shortcut_setIn.activated.connect(self.set_intime)
        shortcut_setOut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_BracketRight), self)
        shortcut_setOut.activated.connect(self.set_outtime)
        shortcut_insert = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Equal), self)
        shortcut_insert.activated.connect(self.insert_new_subtitle)
        # Video Player ShortCuts
        shortcut_rewind = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_J), self)
        shortcut_rewind.activated.connect(self.videoPanel.rewind)
        shortcut_play_pause = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_K), self)
        shortcut_play_pause.activated.connect(self.videoPanel.play_pause)
        shortcut_forward = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_L), self)
        shortcut_forward.activated.connect(self.videoPanel.fastforward)
        shortcut_nf = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Slash), self)
        shortcut_nf.activated.connect(self.videoPanel.nextFrame)
        shortcut_pf = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Comma), self)
        shortcut_pf.activated.connect(self.videoPanel.previousFrame)
        shortcut_loadV = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_P), self)
        shortcut_loadV.activated.connect(self.videoPanel.load_video)
        shortcut_safezone = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_T), self)
        shortcut_safezone.activated.connect(self.videoPanel.set_overlay_safezone)
    
    @Slot(str)
    def updateStatusBar(self, message):
        self.sb.showMessage(message)
    
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.addAction(self.actShowT)
        menu.addAction(self.actHideT)
        menu.exec_(event.globalPos())
    
    def showTitleBar(self):
        # self.dock1.setTitleBarWidget(self.oldD1Title)
        self.dock2.setTitleBarWidget(self.oldD2Title)
        self.dock3.setTitleBarWidget(self.oldD3Title)
        self.dock4.setTitleBarWidget(self.oldD4Title)
    
    def hideTitleBar(self):
        # self.dock1.setTitleBarWidget(self.noTitle1)
        self.dock2.setTitleBarWidget(self.noTitle2)
        self.dock3.setTitleBarWidget(self.noTitle3)
        self.dock4.setTitleBarWidget(self.noTitle4)
        self.repaint()
    
    @Slot()
    def insert_new_subtitle(self):
        index = self.editPanel.no.value() - 1 # Starts at 1
        numRows = self.subTablePanel.rowCount()
        tcIn = QTableWidgetItem(self.editPanel.tcIn.text())
        tcOut = QTableWidgetItem(self.editPanel.tcOut.text())
        sub = QTableWidgetItem(self.editPanel.subtitle.toPlainText())
        if not self.re_editing:
            # print(index, numRows)
            if index >= numRows:
                # print("Everything is ok, can Insert")
                self.subTablePanel.setRowCount(index+1)
                # Insert Row Data
                self.subTablePanel.setItem(numRows, 0, tcIn)
                self.subTablePanel.setItem(numRows, 1, tcOut)
                self.subTablePanel.setItem(numRows, 2, sub)
                self.editPanel.no.setValue(index+2) # Increment Number
                self.editPanel.tcIn.setText(tcOut.text())
        else:
            self.subTablePanel.setItem(index, 0, tcIn)
            self.subTablePanel.setItem(index, 1, tcOut)
            self.subTablePanel.setItem(index, 2, sub)
            self.editPanel.subtitle.clear()
            self.editPanel.no.setValue(numRows+1)
            self.editPanel.tcIn.setText(self.subTablePanel.item(numRows-1, 1).text())
            self.re_editing = False
        self.editPanel.subtitle.clear()
        self.editPanel.tcOut.setText("00000000")
        self.editPanel.tcDur.setText("00000000")
        if not self.importing:
            self.setup_temp_subtitles()
    
    def setup_temp_subtitles(self):
        self.saveSrt(self.tmp)
        print("Temp_File:", self.tmp)
        if self.videoPanel.fileParsed:
            self.videoPanel.set_subtitle_file(self.tmp)
    
    @Slot()
    def open_project(self):
        # print("Opening project!")
        file_dialog = QFileDialog(self, "Open Project")
        file_dialog.setNameFilter("AngelSubTitle Project Files (*.asp)")
        file_dialog.setDefaultSuffix("asp")
        selected_file, valid = file_dialog.getOpenFileName()
        if valid:
            filename, ext = splitext(selected_file)
            if ext == ".asp":
                project = xmlET.parse(selected_file)
                video_root = project.find("./video")
                subtitle_root = project.find("./subtitle")
                self.videoPanel.loadVideoFile(video_root.text)
                self.clear_table()
                self.editPanel.no.setValue(1)
                for i, sub in enumerate(subtitle_root.findall("./en/sub")):
                    inTime, outTime, data = list(sub)
                    # print(i, inTime.text, outTime.text, data.text)
                    self.editPanel.tcIn.setText(inTime.text)
                    self.editPanel.tcOut.setText(outTime.text)
                    self.editPanel.subtitle.setText(data.text)
                    self.insert_new_subtitle()
                videofile, videoext = splitext(video_root.text)
                if not exists(f"{videofile}.srt"):
                    self.setup_temp_subtitles()
            else:
                self.updateStatusBar("Please select a valid Project File!")
            
    def clear_table(self):
        for i in range(self.subTablePanel.rowCount()):
                # print("removing, row", i)
                self.subTablePanel.removeCellWidget(i, 0)
                self.subTablePanel.removeCellWidget(i, 1)
                self.subTablePanel.removeCellWidget(i, 2)
        self.subTablePanel.setRowCount(0)
    
    @Slot()
    def row_deleted_update(self):
        self.editPanel.no.setValue(self.editPanel.no.value()-1)
    
    @Slot()
    def row_added_update(self):
        self.editPanel.no.setValue(self.editPanel.no.value()+1)
    
    @Slot()
    def save_project(self):
        # print("Saving project!")
        file_dialog = QFileDialog(self, "Save as")
        file_dialog.setNameFilter("AngelSubTitle Project Files (*.asp)")
        file_dialog.setDefaultSuffix("asp")
        selected_file, valid = file_dialog.getSaveFileName()
        if valid:
            filename, ext = splitext(selected_file)
            if ext != ".asp":
                # print(join(filename+".asp"))
                selected_file = f"{filename}.asp"
            project = xmlET.Element("Angel_Subtitle_Pro_Project")
            project.text = __version__
            video_root = xmlET.SubElement(project, "video")
            video_root.text = self.videoPanel.currVideoFile
            subtitle_root = xmlET.SubElement(project, "subtitle")
            sub_en = xmlET.SubElement(subtitle_root, "en")
            sub_en.text = "English"
            for i in range(self.subTablePanel.rowCount()):
                curRow = xmlET.SubElement(sub_en, "sub")
                tcIn = xmlET.SubElement(curRow, "intime")
                tcIn.text = self.subTablePanel.item(i, 0).text()
                tcOut = xmlET.SubElement(curRow, "outtime")
                tcOut.text = self.subTablePanel.item(i, 1).text()
                sub = xmlET.SubElement(curRow, "data")
                sub.text = self.subTablePanel.item(i, 2).text()
            with open(selected_file, 'w', encoding='utf-8') as fp:
                fp.write(xmlET.tostring(project,  encoding="unicode",  method="xml"))
            self.updateStatusBar(f"File saved {selected_file}")

    
    @Slot()
    def export_project(self):  # Testing SubRip (SRT)
        # print("Exporting current project!")
        file_dialog = QFileDialog(self, "Save as")
        selected_file, valid = file_dialog.getSaveFileName()
        if valid:
            fileName, ext = splitext(selected_file)
            if ext == ".txt":
                self.saveAvidTxt(selected_file)
            elif ext == ".srt":
                self.saveSrt(selected_file)
            self.updateStatusBar(f"{selected_file} Exported!")
    
    def saveAvidTxt(self, filename):
        with open(filename, 'w', encoding='utf-8') as fp:
            fp.write("<begin subtitles>\n\n")
            for i in range(self.subTablePanel.rowCount()):
                tcIn = self.subTablePanel.item(i, 0).text()
                tcOut = self.subTablePanel.item(i, 1).text()
                sub = self.subTablePanel.item(i, 2).text()
                fp.write(f"{tcIn} {tcOut}\n")
                fp.write(f"{sub}\n")
                fp.write("\n")
            fp.write("<end subtitles>")
    
    def saveSrt(self, filename):
        with open(filename, 'w', encoding='utf-8') as fp:
            for i in range(self.subTablePanel.rowCount()):
                fp.write(f"{i+1}\n")
                tcIn = TimeCode(self.subTablePanel.item(i, 0).text())
                tcOut = TimeCode(self.subTablePanel.item(i, 1).text())
                sub = self.subTablePanel.item(i, 2).text()
                fp.write(f"{tcIn.get_mstc()} --> {tcOut.get_mstc()}\n")
                fp.write(f"{sub}\n")
                fp.write("\n")

    @Slot()
    def import_project(self):
        file_dialog = QFileDialog(self, "Import File")
        selected_file, valid = file_dialog.getOpenFileName()
        if valid:
            self.importing = True
            # print(f"Importing {selected_file}")
            fileName, ext = splitext(selected_file)
            if ext == ".xml":
                self.clear_table()
                self.editPanel.no.setValue(1)
                project = xmlET.parse(selected_file)
                # print(project.findall('.//generatoritem'))
                for card in project.findall('.//generatoritem'):
                    tcIn = TimeCode()
                    tcOut = TimeCode()
                    tcIn.setFrames(int(card[5].text))
                    tcOut.setFrames(int(card[6].text))
                    # print(tcIn.timecode, tcOut.timecode, card[10][6][2].text)
                    try:
                        sub = deepcopy(card[10][6][2].text)  # Standard FCP Outline Text
                    except IndexError:
                        sub = deepcopy(card[13][6][2].text)  # Texte avec bordure
                    self.editPanel.tcIn.setText(tcIn.timecode)
                    self.editPanel.tcOut.setText(tcOut.timecode)
                    self.editPanel.subtitle.setText(sub)
                    self.insert_new_subtitle()
                videofile = project.find(".//media/video/track/clipitem/file/pathurl")
                p = urlparse(videofile.text)
                finalPath = abspath(join(p.netloc, p.path))
                if exists(finalPath):
                    # print(f"Loading {finalPath}")
                    self.videoPanel.loadVideoFile(finalPath)
                else:
                    # print(f"File not found {finalPath}")
                    self.updateStatusBar(f"File not found {finalPath}")
                videofile, videoext = splitext(finalPath)
                if not exists(f"{videofile}.srt"):
                    self.setup_temp_subtitles()
            self.importing = False
            self.saveSrt(self.tmp)
    
    @Slot()
    def set_intime(self):
        if not self.videoPanel.isPlaying and self.videoPanel.fileParsed:
            self.editPanel.tcIn.setText(self.videoPanel.currPos.timecode)
    
    @Slot()
    def set_outtime(self):
        if not self.videoPanel.isPlaying and self.videoPanel.fileParsed:
            self.editPanel.tcOut.setText(self.videoPanel.currPos.timecode)
            self.editPanel.calculate_duration()
    
    @Slot()
    def edit_row(self, row_number):
        self.editPanel.no.setValue(row_number+1)
        self.editPanel.tcIn.setText(self.subTablePanel.item(row_number, 0).text())
        self.editPanel.tcOut.setText(self.subTablePanel.item(row_number, 1).text())
        self.editPanel.calculate_duration()
        self.editPanel.subtitle.clear()
        self.editPanel.subtitle.setText(self.subTablePanel.item(row_number, 2).text())
        self.editPanel.clearStyles()
        self.re_editing = True
    
    def map(self, value, low1, high1, low2, high2):  # Value Remap function
        return low2 + (value - low1) * (high2 - low2) / (high1 - low1)

    def processWaveformSelection(self):
        try:
            wavIn, wavOut = self.waveFormPanel.selectionCtrl.getRegion()
            total_audio_frames = self.waveFormPanel.getTotalAudioFrames()
            total_video_frames = self.videoPanel.video_duration.frames
            x = self.map(int(wavIn), 0, total_audio_frames/100, 0, total_video_frames)  # Because audio filtering
            y = self.map(int(wavOut), 0, total_audio_frames/100, 0, total_video_frames)  # of 100 in wavformPanel.py Line 83
            selIn = TimeCode()
            selIn.setFrames(int(x))
            selOut = TimeCode()
            selOut.setFrames(int(y))
            # print("Selected ->", wavIn, wavOut, "->", x, y, "->",selIn, selOut, "->", selIn.frames, selOut.frames)
            self.editPanel.tcIn.setText(selIn.timecode)
            self.editPanel.tcOut.setText(selOut.timecode)
            self.editPanel.calculate_duration()
        except AttributeError:
            print("please make sure you have a video and audio file loaded!")

    def closeEvent(self, event):
        # print("closing now!")
        self._tmp.close()
        os.unlink(self._tmp.name)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())