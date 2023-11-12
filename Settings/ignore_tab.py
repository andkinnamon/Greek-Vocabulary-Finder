# Anki imports
from aqt.qt import *
from aqt.utils import showInfo, tooltip

# Python imports
import json
from os import path

#Local imports
from ..constants import *
from . import *


class IgnoreTab(QWidget):

    close_signal = pyqtSignal()

    def __init__(self):
        QWidget.__init__(self)

        self.set_ui()

    
    def set_ui(self):
        self.layout = QHBoxLayout()
        self.text_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.table_layout = QVBoxLayout()

        self.explanation_label = QLabel("<h1><u>Ignore</u></h1><p>Add words to ignore when performing searches.</p><p>Words card be added manually here or selected from Missing.</p>")
        self.explanation_label.setWordWrap(True)
        self.text_layout.addWidget(self.explanation_label)

        self.add_word_box = QLineEdit()
        self.add_word_box.returnPressed.connect(self.add_to_table)
        self.text_layout.addWidget(self.add_word_box)

        self.add_button = QPushButton("Add to list")
        self.add_button.clicked.connect(self.add_to_table)
        self.add_button.setAutoDefault(False)
        self.text_layout.addWidget(self.add_button)

        self.word_box_label = QLabel("<p>Press Enter or click the button</p><br><p>Use this for <b>names</b> and <b>words you already know</b>.</p><p><i>Do not add incorrect forms</i> (e.g. deponent verbs) to this list. Add those to Corrections.</p>")
        self.word_box_label.setWordWrap(True)
        self.text_layout.addWidget(self.word_box_label)

        self.text_layout.addStretch()

        self.delete_button = QPushButton("Delete Selected")
        self.delete_button.clicked.connect(self.delete_selected)
        self.delete_button.setAutoDefault(False)
        self.text_layout.addWidget(self.delete_button)

        self.table = QTableWidget(0, 1, self)
        self.table.setFixedWidth(325)
        self.table.setColumnWidth(0, round(self.table.width()/2))
        self.table.verticalHeader().hide()
        self.table.horizontalHeader().hide()
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.table_layout.addWidget(self.table)

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
        
        self.initialize_table()
        self.table.cellChanged.connect(self.empty_check)

        self.layout.addLayout(self.text_layout)
        self.layout.addLayout(self.table_layout)
        self.setLayout(self.layout)


    def initialize_table(self):
        self.table.clearContents()
        self.table.setRowCount(0)

        with open(path.join(current_directory, "user_files/ignore.json"), "r") as file:
            self.ignore_list = json.load(file)

        self.table.setRowCount(len(self.ignore_list))

        for index, word in enumerate(self.ignore_list):

            item = QTableWidgetItem(word)

            self.table.setItem(index, 0, item)

        self.table.setRowCount(self.table.rowCount() + 1)

        self.table.sortItems(0, Qt.SortOrder.AscendingOrder)


    def add_to_table(self):
        if self.add_word_box.text() != "":
            new_item = QTableWidgetItem(self.add_word_box.text())
            self.table.setItem(self.table.rowCount() - 1, 0, new_item)

            self.table.sortItems(0, Qt.SortOrder.AscendingOrder)
            self.table.scrollToItem(new_item, QAbstractItemView.ScrollHint.PositionAtTop)

            self.table.setRowCount(self.table.rowCount() + 1)

            self.add_word_box.clear()
    
    def delete_selected(self):

        while len(self.table.selectedItems()) > 0:
            item = self.table.selectedItems()[0]
            row = self.table.row(item)
            self.table.removeRow(row)

        ignore = []

        for row in range(self.table.rowCount() - 1):
            word = self.table.item(row, 0).text()

            ignore.append(word)

        with open(path.join(current_directory, "user_files/ignore.json"), "w") as file:
            json.dump(ignore, file, ensure_ascii=False, indent=4)
        
        self.initialize_table()

    def search_table(self):
        query = self.search_bar.text()
        if query == "":
            tooltip("Enter a word to perform a search")
        else:
            found = False
            for row in range(self.table.rowCount()):
                if found == False:
                    item = self.table.item(row,0)
                    if item == None:
                        break
                    if item.text() == query:
                        self.table.scrollToItem(item, QAbstractItemView.ScrollHint.PositionAtTop)
                        item.setSelected(True)
                        found = True
                        break
            if found == False:
                tooltip("No results!")
        self.search_bar.clear()

    
    def empty_check(self, row, column):
        item = self.table.item(row, column)
        if item.text() == "":
            self.table.removeRow(row)


    def save_to_file(self):
        word_list = []
        for row in range(self.table.rowCount() - 1):
            word_list.append(self.table.item(row, 0).text())
        file_path = path.join(current_directory, "user_files/ignore.json")
        file = open(file_path, "w")
        json.dump(word_list, file, ensure_ascii=False, indent=4)
        file.close()

    @pyqtSlot()
    def save_and_close(self):

        self.save_to_file()
        self.close_signal.emit()
