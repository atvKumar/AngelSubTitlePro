from PySide2.QtWidgets import QWidget, QVBoxLayout, QPushButton #,QHBoxLayout
from PySide2.QtCore import Signal, Slot

class subTitleEdit(QWidget):
    btn1Clicked = Signal()
    btn2Clicked = Signal()
    btn3Clicked = Signal()
    def __init__(self):
        super(subTitleEdit, self).__init__()
        self.initUI()
    
    def initUI(self):
        mainlayout = QVBoxLayout()
        mainlayout.setContentsMargins(0, 0, 0, 0)
        mainlayout.setMargin(0)
        mainlayout.setSpacing(0)
        btn1 = QPushButton("Button1")
        btn2 = QPushButton("Button2")
        btn3 = QPushButton("Button3")
        mainlayout.addWidget(btn1)
        mainlayout.addWidget(btn2)
        mainlayout.addWidget(btn3)
        btn1.clicked.connect(self._btn1Slot)
        btn2.clicked.connect(self._btn2Slot)
        btn3.clicked.connect(self._btn3Slot)
        self.setLayout(mainlayout)
        self.show()
    
    @Slot()
    def _btn1Slot(self):
        self.btn1Clicked.emit()
    
    @Slot()
    def _btn2Slot(self):
        self.btn2Clicked.emit()

    @Slot()
    def _btn3Slot(self):
        self.btn3Clicked.emit()