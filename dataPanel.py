from PySide2.QtWidgets import QTableWidget
from PySide2.QtCore import Slot

class subTitleList(QTableWidget):
    def __init__(self, parent=None):
        QTableWidget.__init__(self, 0, 3)
        self.setHorizontalHeaderLabels(['In TimeCode', 'Out TimeCode', 'Subtitle'])
        # self.setColumnWidth(0, 50)  # 4Digits 9999
        self.horizontalHeader().setStretchLastSection(True)
        self.setShowGrid(True)
        self.setMinimumWidth(500)
        # self.verticalHeader().sectionDoubleClicked.connect(self.dblClicked)

    # @Slot()
    # def dblClicked(self, event):
    #     print("Double Clicked!", event)