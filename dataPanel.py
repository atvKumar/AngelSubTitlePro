from PySide2.QtWidgets import QTableWidget, QMenu, QAction, QTableWidgetItem
from PySide2.QtCore import Slot, Signal
from timecode import TimeCode


class subTitleTable(QTableWidget):
    row_deleted = Signal()
    row_added = Signal()
    def __init__(self, parent=None):
        QTableWidget.__init__(self, 0, 3)
        self.setHorizontalHeaderLabels(['In TimeCode', 'Out TimeCode', 'Subtitle'])
        self.horizontalHeader().setStretchLastSection(True)
        self.setShowGrid(True)
        self.setMinimumWidth(500)
        self.delRowAction = QAction("Delete Row", self)
        self.delRowAction.triggered.connect(self.delete_row)
        self.splitRowAction = QAction("Split Row", self)
        self.splitRowAction.triggered.connect(self.split_row)
    
    def contextMenuEvent(self, event):
        # print("Right Clicked!", event)
        menu = QMenu(self)
        menu.addAction(self.delRowAction)
        menu.addAction(self.splitRowAction)
        menu.exec_(event.globalPos())
    
    def delete_row(self):
        current_sel = self.selectionModel().selectedRows()
        # print(current_sel[0].row(), total_num_rows)
        for each_row in sorted(set(row.row() for row in current_sel)):
            print(f"Deleting Row Number{each_row+1}")
            self.removeCellWidget(each_row, 0)
            self.removeCellWidget(each_row, 1)
            self.removeCellWidget(each_row, 2)
            self.removeRow(each_row)
            self.row_deleted.emit()
    
    def split_row(self):
        current_sel = self.selectionModel().selectedRows()[0].row()
        currIn = self.item(current_sel, 0).text()
        currOut = self.item(current_sel, 1).text()
        text = self.item(current_sel, 2).text()
        self.insertRow(current_sel+1)
        aIn = TimeCode(currIn)
        aOut = TimeCode(currOut)
        bIn = aIn + (aOut - aIn) / 2
        self.setItem(current_sel, 1, QTableWidgetItem(bIn.timecode, 1))
        self.setItem(current_sel+1, 0, QTableWidgetItem(bIn.timecode, 1))
        self.setItem(current_sel+1, 1, QTableWidgetItem(currOut, 1))
        self.setItem(current_sel+1, 2, QTableWidgetItem(text, 1))
        self.row_added.emit()