# Anki imports
from aqt.qt import *
from aqt.utils import showInfo, tooltip

# Python imports
import json
from os import path

#Local imports
from ..constants import *
from . import *


class MissingTab(QWidget):

    close_signal = pyqtSignal()

    def __init__(self):
        QWidget.__init__(self)

        self.set_ui()

    
    def set_ui(self):
        self.layout = QHBoxLayout()

        self.text_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.table_layout = QVBoxLayout()

        self.explanation_label = QLabel("<h1><u>Missing Words</u></h1><p>These words were <i>not found</i> in your collection.</p><p>The Text and Date are from the earliest deck you attempted to make.</p><br>")
        self.explanation_label.setWordWrap(True)
        self.text_layout.addWidget(self.explanation_label)
        
        self.ignore_button = QPushButton("Add selection to Ignore")
        self.ignore_button.setAutoDefault(False)
        self.ignore_button.clicked.connect(self.add_to_ignore)
        self.text_layout.addWidget(self.ignore_button)

        self.corrections_button = QPushButton("Add selection to Corrections")
        self.corrections_button.setAutoDefault(False)
        self.corrections_button.clicked.connect(self.add_to_corrections)
        self.text_layout.addWidget(self.corrections_button)

        self.ignore_explanation_label = QLabel("Words that are added to Ignore will be removed from this list. This is recommended for <b>names</b> and <b>words you already know</b> and do not want to study. <i>Incorrect forms</i> should be added to the Corrections list.")
        self.ignore_explanation_label.setWordWrap(True)
        self.text_layout.addWidget(self.ignore_explanation_label)

        self.text_layout.addStretch()

        self.caution_label = QLabel("Use with caution! Cannot be undone.")
        self.text_layout.addWidget(self.caution_label)

        self.erase_button = QPushButton("Erase Full List")
        self.erase_button.setAutoDefault(False)
        self.erase_button.clicked.connect(self.erase_missing_list)
        self.text_layout.addWidget(self.erase_button)
        
        self.table = QTableWidget(0, 3, self)
        self.table.setFixedWidth(325)
        self.table.setColumnWidth(0, round(self.table.width()/3))
        self.table.setColumnWidth(1, round(self.table.width()/3)+10)
        self.table.setColumnWidth(2, round(self.table.width()/3)-25)
        self.table.setHorizontalHeaderLabels(["Word", "Text", "Date"])
        self.table.verticalHeader().hide()
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.initialize_table()
        self.table.sortItems(0, Qt.SortOrder.AscendingOrder)
        self.table_layout.addWidget(self.table)

        self.search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.returnPressed.connect(self.search_table)
        self.search_bar.setPlaceholderText("Search...")
        self.search_layout.addWidget(self.search_bar)

        self.save_button = QPushButton("Save")
        self.save_button.setAutoDefault(False)
        self.save_button.clicked.connect(self.save_and_close)
        self.search_layout.addWidget(self.save_button)
        self.save_button.setAutoDefault(False)
        self.table_layout.addLayout(self.search_layout)

        self.layout.addLayout(self.text_layout)
        self.layout.addLayout(self.table_layout)
        self.setLayout(self.layout)

    def initialize_table(self):
        self.table.clearContents()
        self.table.setRowCount(0)

        with open(path.join(current_directory, "user_files/missing.json"), "r+") as file:
            error_dict = json.load(file)

        self.table.setRowCount(len(error_dict))

        for index, (word, info) in enumerate(error_dict.items()):
            word_item = QTableWidgetItem(word)
            text_item = QTableWidgetItem(info["text"])
            date_item = QTableWidgetItem(info["date"])

            word_item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
            text_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            date_item.setFlags(Qt.ItemFlag.ItemIsEnabled)

            self.table.setItem(index, 0, word_item)
            self.table.setItem(index, 1, text_item)
            self.table.setItem(index, 2, date_item)
    
    def add_to_ignore(self):
        with open(path.join(current_directory, "user_files/ignore.json"), "r") as file:
            ignore = json.load(file)

        for item in self.table.selectedItems():
            word = item.text()
            if word not in ignore:
                 ignore.append(word)

        with open(path.join(current_directory, "user_files/ignore.json"), "w+") as file:
            json.dump(ignore, file, ensure_ascii=False, indent=4)

        tooltip("Added to Ignore!")

        while len(self.table.selectedItems()) > 0:
            item = self.table.selectedItems()[0]
            row = self.table.row(item)
            self.table.removeRow(row)
        
        self.save_to_file()
        self.initialize_table()

    def add_to_corrections(self):
        with open(path.join(current_directory, "user_files/corrections.json"), "r") as file:
            corrections = json.load(file)

        show_error = False
        for item in self.table.selectedItems():
            word = item.text()
            if word not in corrections:
                corrections[word] = ""
            else:
                item.setSelected(False)
                show_error = True

        with open(path.join(current_directory, "user_files/corrections.json"), "w+") as file:
            json.dump(corrections, file, ensure_ascii=False, indent=4)

        if show_error:
            tooltip("Highlighted words are already in Corrections")
        else:
            tooltip("Added to Corrections!")
        
        while len(self.table.selectedItems()) > 0:
            item = self.table.selectedItems()[0]
            row = self.table.row(item)
            self.table.removeRow(row)
        
        self.save_to_file()
        self.initialize_table()

        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            word = item.text()
            if word in corrections:
                item.setSelected(True)


    def search_table(self):
        query = self.search_bar.text()
        if query == "":
            tooltip("Enter a word to perform a search")
        else:
            found = False
            for row in range(self.table.rowCount()):
                if found == False:
                    item = self.table.item(row,0)
                    if item.text() == query:
                        self.table.scrollToItem(item, QAbstractItemView.ScrollHint.PositionAtTop)
                        item.setSelected(True)
                        found = True
                        break
            if found == False:
                tooltip("No results!")
        self.search_bar.clear()

    def erase_missing_list(self):
        self.table.clearContents()
        self.table.setRowCount(0)

        with open(path.join(current_directory, "user_files/log.json"), "w") as file:
            log = {}
            json.dump(log, file, indent=4)

    def save_to_file(self):
        missing_dict = {}

        for row in range(self.table.rowCount()):
            word = self.table.item(row, 0).text()
            text = self.table.item(row, 1).text()
            date = self.table.item(row, 2).text()

            missing_dict[word] = {"text": text, "date": date}

        with open(path.join(current_directory, "user_files/missing.json"), "w") as file:
            json.dump(missing_dict, file, ensure_ascii=False, indent=4)

    @pyqtSlot()
    def save_and_close(self):
        self.save_to_file()
        
        self.close_signal.emit()
