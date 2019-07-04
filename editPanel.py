from PySide2.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QHBoxLayout, 
QLineEdit, QSpinBox, QTextEdit)
from PySide2.QtCore import Signal, Slot

class subTitleEdit(QWidget):
    # btn1Clicked = Signal()
    # btn2Clicked = Signal()
    # btn3Clicked = Signal()
    def __init__(self):
        super(subTitleEdit, self).__init__()
        self.initUI()
    
    def initUI(self):
        # Master Layout
        mainlayout = QVBoxLayout()
        mainlayout.setContentsMargins(0, 0, 0, 0)
        mainlayout.setMargin(0)
        mainlayout.setSpacing(0)
        # Top Layout (In Out Duration)
        subLayout = QHBoxLayout()
        subLayout.setContentsMargins(0, 0, 0, 0)
        subLayout.setMargin(0)
        subLayout.setSpacing(0)
        # Top Layout Controls
        txtNo = QSpinBox()
        txtNo.setMinimum(1)
        txtNo.setMaximum(9999)  # < Memory Concerns Lower
        txtIn = QLineEdit()
        txtOut = QLineEdit()
        txtDur = QLineEdit()
        # Add to Layout
        subLayout.addWidget(txtNo)
        subLayout.addWidget(txtIn)
        subLayout.addWidget(txtOut)
        subLayout.addWidget(txtDur)
        # Add to Main
        mainlayout.addLayout(subLayout)
        # Add Next Line Controls
        txtSubTitle = QTextEdit()
        mainlayout.addWidget(txtSubTitle)
        # Layout Operations
        self.setLayout(mainlayout)
        self.show()
    
    # @Slot()
    # def _btn1Slot(self):
    #     self.btn1Clicked.emit()
    
    # @Slot()
    # def _btn2Slot(self):
    #     self.btn2Clicked.emit()

    # @Slot()
    # def _btn3Slot(self):
    #     self.btn3Clicked.emit()