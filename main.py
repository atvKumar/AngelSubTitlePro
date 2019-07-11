import sys
# from PySide2 import QtGui
from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (QWidget, QApplication, QMainWindow, QDockWidget, 
QSizePolicy, QTableWidget, QMenu, QAction, QTableWidgetItem)
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
        self.editPanel.subtitle.insert_subtitle.connect(self.insert_subtitle)
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
    def insert_subtitle(self):
        rollNum = self.editPanel.no.value()
        # print("Inserting Subtitle", x)
        self.subTitleList.setRowCount(rollNum)
        for col in range(0, 5):
            self.subTitleList.setItem(rollNum-1, col, QTableWidgetItem("XXX"))
        self.editPanel.no.setValue(rollNum+1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())