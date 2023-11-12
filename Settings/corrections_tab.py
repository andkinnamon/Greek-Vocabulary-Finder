# Anki imports
from aqt import mw
from aqt.qt import *
from aqt.switch import Switch
from aqt.utils import showInfo, tooltip

# Python imports
import json
from os import path

#Local imports
from ..constants import *
from . import *


class CorrectionsTab(QWidget):

    close_signal = pyqtSignal()

    def __init__(self):
        QWidget.__init__(self)

        self.set_ui()

    def set_ui(self):
        self.layout = QHBoxLayout(self)
        self.text_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.table_layout = QVBoxLayout()

        self.label = QLabel("<h1><u>Corrections</u></h1><p>Add corrections pairs to this table to help the search engine find the correct forms of words.</p><p>Greyed out words are added automatically and cannot be edited.</p>")
        self.label.setWordWrap(True)
        self.text_layout.addWidget(self.label)
        
        self.incorrect_label = QLabel("<b>Incorrect form:</b>")
        self.text_layout.addWidget(self.incorrect_label)
        
        self.incorrect_box = QLineEdit()
        self.text_layout.addWidget(self.incorrect_box)

        self.replacement_label = QLabel("<b>Replacement form:</b>")
        self.text_layout.addWidget(self.replacement_label)

        self.replacement_box = QLineEdit()
        self.replacement_box.returnPressed.connect(self.add_to_table)
        self.text_layout.addWidget(self.replacement_box)

        self.add_button = QPushButton("Add to list")
        self.add_button.clicked.connect(self.add_to_table)
        self.add_button.setAutoDefault(False)
        self.text_layout.addWidget(self.add_button)

        self.word_box_label = QLabel("<p>Press Enter or click the button</p><p>Words without a replacement will be treated regularly. Use this as a reminder to find a correct form, if one exists.</p>")
        self.word_box_label.setWordWrap(True)
        self.text_layout.addWidget(self.word_box_label)

        self.text_layout.addStretch()

        self.select_unpaired_button = QPushButton("Select Empty")
        self.select_unpaired_button.clicked.connect(self.select_unpaired)
        self.select_unpaired_button.setAutoDefault(False)
        self.text_layout.addWidget(self.select_unpaired_button)

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected)
        self.delete_button.setAutoDefault(False)
        self.text_layout.addWidget(self.delete_button)

        self.table = QTableWidget(0, 2, self)
        self.table.setHorizontalHeaderLabels(["Incorrect", "Replacement"])
        self.table.verticalHeader().hide()
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.table.setFixedWidth(325)
        self.table.setColumnWidth(0, round(self.table.width()/2))
        self.table.setColumnWidth(1, round(self.table.width()/2))
        self.initialize_table()
        self.table_layout.addWidget(self.table)

        #self.table.cellChanged.connect(self.empty_check)

        self.search_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.returnPressed.connect(self.search_table)
        self.search_bar.setPlaceholderText("Search...")
        self.search_layout.addWidget(self.search_bar)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_and_close)
        self.save_button.setAutoDefault(False)
        self.search_layout.addWidget(self.save_button)
        self.save_button.setAutoDefault(False)
        self.table_layout.addLayout(self.search_layout)
        
        self.layout.addLayout(self.text_layout)
        self.layout.addLayout(self.table_layout)
        self.setLayout(self.layout)

    def initialize_table(self):
        with open(path.join(current_directory, "user_files/corrections.json"), "r+") as file:
            corrections_dict = json.load(file)
        
        for word in corrections_dict:
            corrections_dict[word] = {"replacement": corrections_dict[word], "display": True}

        with open(path.join(current_directory, "auto_corrections.json"), "r+") as file:
            self.auto_corrections_dict = json.load(file)
            corrections_dict.update(self.auto_corrections_dict)

        self.table.setRowCount(len(corrections_dict))
        
        for index, (word, info) in enumerate(corrections_dict.items()):
            if info["display"] == False:
                continue
            word_item = QTableWidgetItem(word)
            replace_item = QTableWidgetItem(info["replacement"])

            if word in self.auto_corrections_dict:
                word_item.setFlags(Qt.ItemFlag.ItemIsSelectable)
                replace_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            else:
                replace_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable)

            self.table.setItem(index, 0, word_item)
            self.table.setItem(index, 1, replace_item)
        
        self.table.sortItems(0, Qt.SortOrder.AscendingOrder)

    def empty_check(self, row, column):
        main_item = self.table.item(row, column).text()
        pair_item = self.table.item(row, column ^ 1)
        pair = pair_item.text if pair_item is not None else ""
        if (main_item == "" and pair == ""):
            self.table.removeRow(row)
        if (main_item == "" and pair != "") or (main_item != "" and pair == "" and pair_item is not None):
            tooltip("Enter a full pair")

    def add_to_table(self):
      incorrect = self.incorrect_box.text()
      replacement = self.replacement_box.text()
      if (incorrect != "" and replacement != ""):
            new_incorrect_item = QTableWidgetItem(incorrect)
            new_replacement_item = QTableWidgetItem(replacement)
            self.table.setRowCount(self.table.rowCount() + 1)

            self.table.setItem(self.table.rowCount() - 1, 0, new_incorrect_item)
            self.table.setItem(self.table.rowCount() - 1, 1, new_replacement_item)

            self.table.sortItems(0, Qt.SortOrder.AscendingOrder)
            self.table.scrollToItem(new_incorrect_item, QAbstractItemView.ScrollHint.PositionAtTop)

            self.incorrect_box.clear()
            self.replacement_box.clear()
    
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

    def save_to_file(self):
        correction_dict = {}

        for row in range(self.table.rowCount()):
            incorrect_item = self.table.item(row, 0)
            if incorrect_item is None:
                continue
            incorrect = incorrect_item.text()
            if incorrect in self.auto_corrections_dict:
                continue
            replacement = self.table.item(row, 1).text()
            correction_dict[incorrect] = replacement
        
        if correction_dict != {}:
            with open(path.join(current_directory, "user_files/corrections.json"), "w") as file:
                json.dump(correction_dict, file, ensure_ascii=False, indent=4)

    def select_unpaired(self):
        for row in range(self.table.rowCount()):
            replace = self.table.item(row,1).text()
            if replace == "":
                self.table.item(row,0).setSelected(True)

    def delete_selected(self):

        while len(self.table.selectedItems()) > 0:
            item = self.table.selectedItems()[0]
            row = self.table.row(item)
            self.table.removeRow(row)

        correction_dict = {}

        for row in range(self.table.rowCount()):
            word = self.table.item(row, 0).text()
            replace = self.table.item(row, 1).text()

            correction_dict[word] = replace

        with open(path.join(current_directory, "user_files/corrections.json"), "w") as file:
            json.dump(correction_dict, file, ensure_ascii=False, indent=4)
        
        self.initialize_table()

    @pyqtSlot()
    def save_and_close(self):

        self.save_to_file()
        self.close_signal.emit()
