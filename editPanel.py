from PySide2.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QHBoxLayout, 
QLineEdit, QSpinBox, QTextEdit, QCompleter)
from PySide2.QtCore import Signal, Slot, QRegExp, Qt, SIGNAL
from PySide2.QtGui import QRegExpValidator, QTextCursor
from timecode import TimeCode
from en_dictionary_filtered import get_filtered_words


class DictionaryCompleter(QCompleter):
    def __init__(self, parent=None):
        words = get_filtered_words()
        QCompleter.__init__(self, words, parent)


class CompletionTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super(CompletionTextEdit, self).__init__(parent)
        self.setMinimumWidth(400)
        # self.setPlainText(STARTTEXT)
        self.completer = None
        self.moveCursor(QTextCursor.End)

    def setCompleter(self, completer):
        if self.completer:
            self.disconnect(self.completer, 0, self, 0)
        if not completer:
            return

        completer.setWidget(self)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer = completer
        self.connect(self.completer, SIGNAL("activated(const QString&)"), self.insertCompletion)

    def insertCompletion(self, completion):
        tc = self.textCursor()
        extra = (len(completion) - len(self.completer.completionPrefix()))
        tc.movePosition(QTextCursor.Left)
        tc.movePosition(QTextCursor.EndOfWord)
        tc.insertText(completion[-extra::])
        self.setTextCursor(tc)

    def textUnderCursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def focusInEvent(self, event):
        if self.completer:
            self.completer.setWidget(self);
        QTextEdit.focusInEvent(self, event)

    def keyPressEvent(self, event):
        if self.completer and self.completer.popup().isVisible():
            if event.key() in (
            Qt.Key_Enter,
            Qt.Key_Return,
            Qt.Key_Escape,
            Qt.Key_Tab,
            Qt.Key_Backtab):
                event.ignore()
                return

        ## has ctrl-E been pressed??
        isShortcut = (event.modifiers() == Qt.ControlModifier and
                      event.key() == Qt.Key_E)
        if (not self.completer or not isShortcut):
            QTextEdit.keyPressEvent(self, event)

        ## ctrl or shift key on it's own??
        ctrlOrShift = event.modifiers() in (Qt.ControlModifier, Qt.ShiftModifier)
        # if ctrlOrShift and event == "":
        #     # ctrl or shift key on it's own
        #     print("Pressed CTRL OR SHIFT")
        #     return

        eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-=" #end of word

        hasModifier = ((event.modifiers() != Qt.NoModifier) and
                        not ctrlOrShift)

        completionPrefix = self.textUnderCursor()

        if (not isShortcut and (hasModifier or event.text() == "" or
        len(completionPrefix) < 3 or
        event.text()[-1] in eow )):
            self.completer.popup().hide()
            return

        if (completionPrefix != self.completer.completionPrefix()):
            self.completer.setCompletionPrefix(completionPrefix)
            popup = self.completer.popup()
            popup.setCurrentIndex(
                self.completer.completionModel().index(0,0))

        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0)
            + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr) ## popup it up!


class subTitleEdit(QWidget):
    def __init__(self):
        super(subTitleEdit, self).__init__()
        self.rx = QRegExp("(^(?:(:?[0-1][0-9]|[0-2][0-3]):)(?:[0-5][0-9]:){2}(?:[0-2][0-9])$)")
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
        self.no = QSpinBox()
        self.no.setMinimum(1)
        self.no.setMaximum(9999)  # < Memory Concerns Lower
        self.tcIn = QLineEdit()
        self.tcOut = QLineEdit()
        self.tcDur = QLineEdit()
        # Add to Layout
        subLayout.addWidget(self.no)
        subLayout.addWidget(self.tcIn)
        subLayout.addWidget(self.tcOut)
        subLayout.addWidget(self.tcDur)
        # Add to Main
        mainlayout.addLayout(subLayout)
        # Add Next Line Controls
        # txtSubTitle = QTextEdit()
        txtSubTitle = CompletionTextEdit()
        completer = DictionaryCompleter()
        txtSubTitle.setCompleter(completer)
        txtSubTitle.setMaximumHeight(100)
        mainlayout.addWidget(txtSubTitle)
        # Setup TimeCode LineEdit Controls
        self.setup_linedt_tc(self.tcIn)
        self.setup_linedt_tc(self.tcOut)
        self.setup_linedt_tc(self.tcDur)
        self.tcOut.editingFinished.connect(self.calculate_duration)
        # Layout Operations
        self.setLayout(mainlayout)
        self.show()
    
    def setup_linedt_tc(self, ctrl):
        ctrl.setDragEnabled(True)
        ctrl.setInputMask("99:99:99:99")
        ctrl.setText("00000000")
        ctrl.setCursorPosition(0)
        ctrl.setValidator(QRegExpValidator(self.rx))
    
    def calculate_duration(self):
        tcIn = TimeCode(self.tcIn.text())
        tcOut = TimeCode(self.tcOut.text())
        if tcOut.frames > tcIn.frames:
            Dur = tcOut - tcIn
            self.tcDur.setText(Dur.timecode)
        else:
            print("Error, Out should be larger than In!")