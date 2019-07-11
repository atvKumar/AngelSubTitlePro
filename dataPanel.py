from PySide2.QtWidgets import QTableWidget

class subTitleList(QTableWidget):
    def __init__(self, parent=None):
        QTableWidget.__init__(self, 0, 5)
        self.setHorizontalHeaderLabels(['No', 'In TimeCode', 'Out TimeCode', 'Duration', 'Subtitle'])
        self.setColumnWidth(0, 50)  # 4Digits 9999
        self.horizontalHeader().setStretchLastSection(True)