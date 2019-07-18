from PySide2.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QHBoxLayout, 
QLineEdit, QSpinBox, QTextEdit, QCompleter, QLabel, QFontComboBox, QComboBox, QSpacerItem, QCheckBox)
from PySide2.QtCore import Signal, Slot, QRegExp, Qt, SIGNAL
from PySide2.QtGui import QRegExpValidator, QTextCursor, QFont
from timecode import TimeCode
from language_utils import en_autocomplete_words
from time import sleep


class en_autocomplete(QCompleter):
    def __init__(self, parent=None):
        words = en_autocomplete_words()
        QCompleter.__init__(self, words, parent)


class CompletionTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super(CompletionTextEdit, self).__init__(parent)
        self.setMinimumWidth(400)
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
        # self.connect(self.completer, SIGNAL("activated(const QString&)"), self.insertCompletion)
        self.completer.activated.connect(self.insertCompletion)
    
    def removeCompleter(self):
        self.completer.activated.disconnect()
        self.completer = None

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
            self.completer.setWidget(self)
        QTextEdit.focusInEvent(self, event)

    def keyPressEvent(self, event):
        try:
            if self.completer and self.completer.popup().isVisible():
                if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab, Qt.Key_Backtab):
                    event.ignore()
                    return

            ## has ctrl-C been pressed??
            completion_shortcut = (event.modifiers() == Qt.ControlModifier and
                        event.key() == Qt.Key_C)
            if (not self.completer or not completion_shortcut):
                QTextEdit.keyPressEvent(self, event)

            ## ctrl or shift key on it's own??
            ctrlOrShift = event.modifiers() in (Qt.ControlModifier, Qt.ShiftModifier)

            eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-=" #end of word

            hasModifier = ((event.modifiers() != Qt.NoModifier) and not ctrlOrShift)

            completionPrefix = self.textUnderCursor()

            if (not completion_shortcut and (hasModifier or event.text() == "" or
            len(completionPrefix) < 3 or event.text()[-1] in eow )):
                self.completer.popup().hide()
                return

            if (completionPrefix != self.completer.completionPrefix()):
                self.completer.setCompletionPrefix(completionPrefix)
                popup = self.completer.popup()
                popup.setCurrentIndex(self.completer.completionModel().index(0,0))

            cr = self.cursorRect()
            cr.setWidth(self.completer.popup().sizeHintForColumn(0)
                + self.completer.popup().verticalScrollBar().sizeHint().width())
            self.completer.complete(cr) ## popup it up!
        except AttributeError:
            pass  # No Completer Defined (Later in GUI)


class subTitleEdit(QWidget):
    def __init__(self):
        super(subTitleEdit, self).__init__()
        self.rx = QRegExp("(^(?:(:?[0-1][0-9]|[0-2][0-3]):)(?:[0-5][0-9]:){2}(?:[0-2][0-9])$)")
        self.language_choice = 1  # 1 English, 2 Tamil, 3 Hindi
        self.initUI()

    def initUI(self):
        # Master Layout
        mainlayout = QVBoxLayout()
        mainlayout.setContentsMargins(0, 0, 0, 0)
        mainlayout.setMargin(3)
        mainlayout.setSpacing(0)
        mainlayout.setStretch(0, 0)
        # Top Layout (In Out Duration)
        subLayout = QHBoxLayout()
        subLayout.setContentsMargins(0, 0, 0, 0)
        subLayout.setMargin(2)
        subLayout.setSpacing(5)
        # Top Layout Controls
        self.no = QSpinBox()
        self.no.setMinimum(1)
        self.no.setMaximum(9999)  # < Memory Concerns Lower
        self.tcIn = QLineEdit()
        self.tcOut = QLineEdit()
        self.tcDur = QLineEdit()
        index_lbl = QLabel("No:")
        intc_lbl = QLabel("In:")
        outtc_lbl = QLabel("Out:")
        durtc_lbl = QLabel("Duration:")
        # Add to Layout
        subLayout.addWidget(index_lbl)
        subLayout.addWidget(self.no)
        subLayout.addWidget(intc_lbl)
        subLayout.addWidget(self.tcIn)
        subLayout.addWidget(outtc_lbl)
        subLayout.addWidget(self.tcOut)
        subLayout.addWidget(durtc_lbl)
        subLayout.addWidget(self.tcDur)
        # Add to Main
        mainlayout.addLayout(subLayout)
        # Add Next Line Controls
        second_line_layout = QHBoxLayout()
        font = QFont("Helvetica", 13)
        self.font_family = QFontComboBox()
        self.font_family.setMaximumWidth(180)
        self.font_family.setCurrentFont(font)
        second_line_layout.addWidget(self.font_family)
        self.font_family.currentTextChanged.connect(self.set_font)
        self.font_size = QComboBox()
        self.font_size.addItems(["9", "10", "11", "12", "13", "14", "18", "24", "36", "48", "64"])
        self.font_size.setCurrentText("13")
        self.font_size.setMaximumWidth(80)
        self.font_size.currentIndexChanged.connect(self.set_font)
        second_line_layout.addWidget(self.font_size)
        bold = QPushButton("B")
        bold.clicked.connect(self.bold)
        italic = QPushButton("I")
        italic.clicked.connect(self.italic)
        underline = QPushButton("U")
        underline.clicked.connect(self.underline)
        second_line_layout.addWidget(bold)
        second_line_layout.addWidget(italic)
        second_line_layout.addWidget(underline)
        # ------------------------------------------
        language = QComboBox()
        language.addItems(["English", "Tamil", "Hindi"])
        language.currentIndexChanged.connect(self.setup_language)
        language.setDisabled(True)  # Disabled
        spellCheck = QPushButton("Spell Check")
        spellCheck.setDisabled(True)  # Disabled
        autocomplete = QCheckBox("AutoCmp")
        autocomplete.toggled.connect(self.setup_autocomplete)
        second_line_layout.addWidget(language)
        second_line_layout.addWidget(spellCheck)
        second_line_layout.addWidget(autocomplete)
        second_line_layout.addStretch(1)
        mainlayout.addLayout(second_line_layout)
        # txtSubTitle = QTextEdit()
        self.subtitle = CompletionTextEdit()
        # print(self.subtitle.font())
        # completer = DictionaryCompleter()
        # self.subtitle.setCompleter(completer)
        # self.subtitle.setMaximumHeight(100)
        mainlayout.addWidget(self.subtitle)
        # Setup TimeCode LineEdit Controls
        self.setup_linedt_tc(self.tcIn)
        self.setup_linedt_tc(self.tcOut)
        self.setup_linedt_tc(self.tcDur)
        self.tcOut.editingFinished.connect(self.calculate_duration)
        # Layout Operations
        self.setLayout(mainlayout)
        self.setTabOrder(self.tcDur, self.subtitle)
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

    @Slot()
    def set_font(self):
        self.subtitle.setCurrentFont(QFont(self.font_family.currentText(), int(self.font_size.currentText())))
    
    @Slot()
    def bold(self):
        if self.subtitle.fontWeight() == QFont.Bold:
            self.subtitle.setFontWeight(QFont.Normal)
        else:
            self.subtitle.setFontWeight(QFont.Bold)
    
    @Slot()
    def italic(self):
        state = self.subtitle.fontItalic()
        self.subtitle.setFontItalic(not state)
    
    @Slot()
    def underline(self):
        state = self.subtitle.fontUnderline()
        self.subtitle.setFontUnderline(not state)
    
    def clearStyles(self):
        bold = self.subtitle.fontWeight() == QFont.Bold
        italic = self.subtitle.fontItalic()
        underline = self.subtitle.fontUnderline()
        if bold:
            self.subtitle.setFontWeight(QFont.Normal)
        if italic:
            self.subtitle.setFontItalic(False)
        if underline:
            self.subtitle.setFontUnderline(False)

    @Slot()
    def setup_language(self, event):
        event += 1
        self.language_choice = event
        if self.language_choice == 1:  # Tamil
            self.subtitle.setText("You have chosen English")
        elif self.language_choice == 2:  # Tamil
            self.subtitle.setText("You have chosen Tamil")
        elif self.language_choice == 3:  # Hindi
            self.subtitle.setText("You have chosen Hindi")

    @Slot()
    def setup_autocomplete(self, event):
        if self.language_choice == 1 and event == True:
            completer = en_autocomplete()
            self.subtitle.setCompleter(completer)
        elif self.language_choice == 1 and event == False:
            self.subtitle.removeCompleter()