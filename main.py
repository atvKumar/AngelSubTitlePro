import sys
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (QWidget, QApplication, QMainWindow, QDockWidget, 
QSizePolicy, QTableWidget, QMenu, QAction, QTableWidgetItem, QShortcut, QFileDialog)
from editPanel import subTitleEdit
from videoPanel import vlcPlayer
from dataPanel import subTitleList
from timecode import TimeCode
from os.path import splitext

__version__ = "alpha Pre-Release"
__major__ = 0
__minor__ = 1


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
        self.setup_shortcuts()
    
    def initUI(self):
        self.setMinimumSize(50, 70)
        self.setWindowTitle(f"Angel SubTitle Pro ({__version__})")
        self.sb = self.statusBar() 
        self.updateStatusBar(f"{__version__}.{__major__}.{__minor__}")
        self.noTitle1 = QWidget()
        self.noTitle2 = QWidget()
        self.noTitle3 = QWidget()
        # self.dock1 = QDockWidget("Video Player", self)
        self.dock2 = QDockWidget("Subtitle Editing", self)
        self.dock3 = QDockWidget("Subtitle List", self)
        # self.oldD1Title = self.dock1.titleBarWidget()
        self.oldD2Title = self.dock2.titleBarWidget()
        self.oldD3Title = self.dock2.titleBarWidget()
        # self.dock1.setTitleBarWidget(self.noTitle1)
        self.dock2.setTitleBarWidget(self.noTitle2)
        self.dock3.setTitleBarWidget(self.noTitle3)
        self.dock2.setAllowedAreas(Qt.AllDockWidgetAreas)
        self.dock3.setAllowedAreas(Qt.AllDockWidgetAreas)
        # self.addDockWidget(Qt.RightDockWidgetArea, self.dock1)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dock3)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock2)
        # Custom widget editPanel.py |> subTitleEdit
        self.editPanel = subTitleEdit()
        self.dock2.setWidget(self.editPanel)
        # Custom widget dataPanel.py |> subTitleList
        self.subTitleList = subTitleList()
        self.dock3.setWidget(self.subTitleList)
        self.actShowT = QAction("Show TitleBar", self)
        self.actShowT.triggered.connect(self.showTitleBar)
        self.actHideT = QAction("Hide TitleBar", self)
        self.actHideT.triggered.connect(self.hideTitleBar)
        # VLC Player
        self.videoPanel = vlcPlayer()
        self.videoPanel.message.connect(self.updateStatusBar)
        # self.dock1.setWidget(self.videoPanel)
        self.setCentralWidget(self.videoPanel)
        self.editPanel.subtitle.setFocus()
        self.subTitleList.verticalHeader().sectionDoubleClicked.connect(self.edit_row)
        self.re_editing = False
    
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
    
    def hideTitleBar(self):
        # self.dock1.setTitleBarWidget(self.noTitle1)
        self.dock2.setTitleBarWidget(self.noTitle2)
        self.dock3.setTitleBarWidget(self.noTitle3)
        self.repaint()
    
    @Slot()
    def insert_new_subtitle(self):
        index = self.editPanel.no.value() - 1 # Starts at 1
        numRows = self.subTitleList.rowCount()
        tcIn = QTableWidgetItem(self.editPanel.tcIn.text())
        tcOut = QTableWidgetItem(self.editPanel.tcOut.text())
        sub = QTableWidgetItem(self.editPanel.subtitle.toPlainText())
        if not self.re_editing:
            # print(index, numRows)
            if index >= numRows:
                # print("Everything is ok, can Insert")
                self.subTitleList.setRowCount(index+1)
                # Insert Row Data
                self.subTitleList.setItem(numRows, 0, tcIn)
                self.subTitleList.setItem(numRows, 1, tcOut)
                self.subTitleList.setItem(numRows, 2, sub)
                self.editPanel.no.setValue(index+2) # Increment Number
                self.editPanel.tcIn.setText(tcOut.text())
        else:
            self.subTitleList.setItem(index, 0, tcIn)
            self.subTitleList.setItem(index, 1, tcOut)
            self.subTitleList.setItem(index, 2, sub)
            self.editPanel.subtitle.clear()
            self.editPanel.no.setValue(numRows+1)
            self.editPanel.tcIn.setText(self.subTitleList.item(numRows-1, 1).text())
            self.re_editing = False
        self.editPanel.subtitle.clear()
        self.editPanel.tcOut.setText("00000000")
        self.editPanel.tcDur.setText("00000000")
    
    @Slot()
    def open_project(self):
        print("Opening project!")
        # self.videoPanel.set_overlay_image()
    
    @Slot()
    def save_project(self):
        print("Saving project!")
    
    @Slot()
    def export_project(self):  # Testing SubRip (SRT)
        print("Exporting current project!")
        file_dialog = QFileDialog(self, "Save as")
        selected_file, valid = file_dialog.getSaveFileName()
        if valid:
            fileName, ext = splitext(selected_file)
            if ext == ".txt":
                with open(selected_file, 'w', encoding='utf-8') as fp:
                    fp.write("<begin subtitles>\n\n")
                    for i in range(self.subTitleList.rowCount()):
                        tcIn = self.subTitleList.item(i, 0).text()
                        tcOut = self.subTitleList.item(i, 1).text()
                        sub = self.subTitleList.item(i, 2).text()
                        fp.write(f"{tcIn} {tcOut}\n")
                        fp.write(f"{sub}\n")
                        fp.write("\n")
                    fp.write("<end subtitles>")
            elif ext == ".srt":
                with open(selected_file, 'w', encoding='utf-8') as fp:
                    for i in range(self.subTitleList.rowCount()):
                        fp.write(f"{i+1}\n")
                        tcIn = TimeCode(self.subTitleList.item(i, 0).text())
                        tcOut = TimeCode(self.subTitleList.item(i, 1).text())
                        sub = self.subTitleList.item(i, 2).text()
                        fp.write(f"{tcIn.get_mstc()} --> {tcOut.get_mstc()}\n")
                        fp.write(f"{sub}\n")
                        fp.write("\n")

    @Slot()
    def import_project(self):
        print("Importing File!")
    
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
        self.editPanel.tcIn.setText(self.subTitleList.item(row_number, 0).text())
        self.editPanel.tcOut.setText(self.subTitleList.item(row_number, 1).text())
        self.editPanel.calculate_duration()
        self.editPanel.subtitle.clear()
        self.editPanel.subtitle.setText(self.subTitleList.item(row_number, 2).text())
        self.re_editing = True

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())