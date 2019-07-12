import sys
from PySide2.QtGui import QKeySequence
from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (QWidget, QApplication, QMainWindow, QDockWidget, 
QSizePolicy, QTableWidget, QMenu, QAction, QTableWidgetItem, QShortcut)
from editPanel import subTitleEdit
from videoPanel import vlcPlayer
from dataPanel import subTitleList

__version__ = "alpha Pre-Release"
__major__ = 0
__minor__ = 1


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
        shortcut_open = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_O), self)
        shortcut_open.activated.connect(self.open_project)
        shortcut_save = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_S), self)
        shortcut_save.activated.connect(self.save_project)
        shortcut_export = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_E), self)
        shortcut_export.activated.connect(self.export_project)
        shortcut_import = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_I), self)
        shortcut_import.activated.connect(self.import_project)
        shortcut_setIn = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_BracketLeft), self)
        shortcut_setIn.activated.connect(self.set_intime)
        shortcut_setOut = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_BracketRight), self)
        shortcut_setOut.activated.connect(self.set_outtime)
        shortcut_insert = QShortcut(QKeySequence(Qt.CTRL + Qt.Key_Equal), self)
        shortcut_insert.activated.connect(self.insert_new_subtitle)
    
    def initUI(self):
        self.setMinimumSize(50, 70)
        self.setWindowTitle(f"Angel SubTitle Pro ({__version__})")
        self.sb = self.statusBar() 
        self.updateStatusBar(f"{__version__}.{__major__}.{__minor__}")
        self.noTitle1 = QWidget()
        self.noTitle2 = QWidget()
        self.noTitle3 = QWidget()
        self.dock1 = QDockWidget("Video Player", self)
        self.dock2 = QDockWidget("Subtitle Editing", self)
        self.dock3 = QDockWidget("Subtitle List", self)
        self.oldD1Title = self.dock1.titleBarWidget()
        self.oldD2Title = self.dock2.titleBarWidget()
        self.oldD3Title = self.dock2.titleBarWidget()
        self.dock1.setTitleBarWidget(self.noTitle1)
        self.dock2.setTitleBarWidget(self.noTitle2)
        self.dock3.setTitleBarWidget(self.noTitle3) 
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock1)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock2)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock3)
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
        self.dock1.setWidget(self.videoPanel)
    
    @Slot(str)
    def updateStatusBar(self, message):
        self.sb.showMessage(message)
    
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.addAction(self.actShowT)
        menu.addAction(self.actHideT)
        menu.exec_(event.globalPos())
    
    def showTitleBar(self):
        self.dock1.setTitleBarWidget(self.oldD1Title)
        self.dock2.setTitleBarWidget(self.oldD2Title)
        self.dock3.setTitleBarWidget(self.oldD3Title)
    
    def hideTitleBar(self):
        self.dock1.setTitleBarWidget(self.noTitle1)
        self.dock2.setTitleBarWidget(self.noTitle2)
        self.dock3.setTitleBarWidget(self.noTitle3)
        self.repaint()
    
    @Slot()
    def insert_new_subtitle(self):
        index = self.editPanel.no.value() - 1 # Starts at 1
        numRows = self.subTitleList.rowCount()
        # print(index, numRows)
        if index >= numRows:
            # print("Everything is ok, can Insert")
            self.subTitleList.setRowCount(index+1)
            # Insert Row Data
            self.subTitleList.setItem(numRows, 0, QTableWidgetItem(str(index+1)))
            self.subTitleList.setItem(numRows, 1, QTableWidgetItem(self.editPanel.tcIn.text()))
            self.subTitleList.setItem(numRows, 2, QTableWidgetItem(self.editPanel.tcOut.text()))
            self.subTitleList.setItem(numRows, 3, QTableWidgetItem(self.editPanel.tcDur.text()))
            self.subTitleList.setItem(numRows, 4, QTableWidgetItem(self.editPanel.subtitle.toPlainText()))
            self.editPanel.no.setValue(index+2) # Increment Number
            self.editPanel.subtitle.clear()
            self.editPanel.tcIn.setText(self.editPanel.tcOut.text())
            self.editPanel.tcOut.setText("00000000")
            self.editPanel.tcDur.setText("00000000")
    
    @Slot()
    def open_project(self):
        print("Opening project!")
    
    @Slot()
    def save_project(self):
        print("Saving project!")
    
    @Slot()
    def export_project(self):
        print("Exporting current project!")
    
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())