import sys
# from PySide2 import QtGui
from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import (QApplication, QMainWindow, 
QDockWidget, QSizePolicy)
from editPanel import subTitleEdit

__version__ = "alpha Pre-Release"
__major__ = 0
__minor__ = 1


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.initUI()
    
    def initUI(self):
        self.setMinimumSize(480, 640)
        self.setWindowTitle(f"Angel SubTitle Pro ({__version__})")
        self.sb = self.statusBar() 
        self.updateStatusBar(f"{__version__}.{__major__}.{__minor__}")
        dock1 = QDockWidget("Video Player", self)
        dock2 = QDockWidget("Subtitle Editing", self)
        dock3 = QDockWidget("Subtitle List", self)
        self.addDockWidget(Qt.RightDockWidgetArea, dock1)
        self.addDockWidget(Qt.RightDockWidgetArea, dock2)
        self.addDockWidget(Qt.RightDockWidgetArea, dock3)
        dock2.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # Custom widget editPanel.py |> subTitleEdit
        self.subTitlePanel = subTitleEdit()
        dock2.setWidget(self.subTitlePanel)
        # Connecting custom widget Signals to Slots
        self.subTitlePanel.btn1Clicked.connect(self.printMsg1)
        self.subTitlePanel.btn2Clicked.connect(self.printMsg2)
        self.subTitlePanel.btn3Clicked.connect(self.printMsg3)

    def updateStatusBar(self, message):
        self.sb.showMessage(message)
    
    @Slot()
    def printMsg1(self):
        print("Button1 Pressed!")

    @Slot()
    def printMsg2(self):
        print("Button2 Pressed!")

    @Slot()
    def printMsg3(self):
        print("Button3 Pressed!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())