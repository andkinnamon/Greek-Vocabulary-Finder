# Anki imports
from aqt import mw
from aqt.utils import showInfo, tooltip
from aqt.qt import *
from aqt.progress import *
from aqt.operations import QueryOp
from anki.consts import DYN_DUE
from anki import tags

# Python imports
import json
from os import path
import datetime

# Local imports
from .bible_lists import *
from .Settings.settings import Configuration
from .constants import *


# TextPicker window for choosing text and creating deck
class TextPicker(QDialog):
    def __init__(self):
        QDialog.__init__(self)

        self.set_ui()
    

    # Create Textpicker visual layout
    def set_ui(self):
        self.setFixedSize(550, 450)


        self.setWindowTitle("Select Text to Study")
        self.layout = QHBoxLayout()
        self.text_layout = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.table_layout = QVBoxLayout()
        self.buttonlayout = QHBoxLayout()

        # Choose a collection (New Testament default)
        self.collection_label = QLabel("<b>Select a collection of texts</b>")
        self.text_layout.addWidget(self.collection_label)

        self.collection = QComboBox()
        self.collection.addItems(["New Testament", "Septuagint"])
        self.collection.setCurrentText(config["collection"])
        self.collection.currentTextChanged.connect(self.update_book_table)
        self.text_layout.addWidget(self.collection)

        # Choose a book
        self.book_list_label = QLabel(f"<b>Select a {self.collection.currentText()} book</b>")
        self.text_layout.addWidget(self.book_list_label)


        self.book_table = QTableWidget(0,1)
        self.book_table.horizontalHeader().hide()
        self.book_table.verticalHeader().hide()
        self.book_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.book_table.itemSelectionChanged.connect(self.update_chapter_table)
        self.book_table.setColumnWidth(0, self.book_table.width())
        self.book_table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.text_layout.addWidget(self.book_table)


        # Choose a chapter from a table menu
        self.chapter_label = QLabel("<b>Select at least one chapter</b>")
        self.chapter_label.setToolTip("Click to select one at a time.<br>Click and drag to select multiple.<br>Use the button at the bottom to quickly select and deselect chapters.")
        self.table_layout.addWidget(self.chapter_label)

        self.chapter_table = QTableWidget(0, 1)
        self.chapter_table.verticalHeader().hide()
        self.chapter_table.horizontalHeader().hide()
        self.chapter_table.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.chapter_table.setColumnWidth(0, self.chapter_table.width())
        self.chapter_table.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.table_layout.addWidget(self.chapter_table)

        # Button to select all
        select_all_button = QPushButton("Select All")
        select_all_button.clicked.connect(self.select_all)
        self.buttonlayout.addWidget(select_all_button)

        # Button to clear selection
        select_none_button = QPushButton("Clear Selection")
        select_none_button.clicked.connect(self.select_none)
        self.buttonlayout.addWidget(select_none_button)

        self.table_layout.addLayout(self.buttonlayout)

        # Checkboxes for choosing card layouts
        self.checkBoxes = QHBoxLayout()

        self.card1checkbox = QCheckBox(f"Grk → {config['lang']}")
        self.card1checkbox.setChecked(config["select_card_1"])
        self.checkBoxes.addWidget(self.card1checkbox)

        self.card2checkbox = QCheckBox(f"{config['lang']} → Grk")
        self.card2checkbox.setChecked(config["select_card_2"])
        self.checkBoxes.addWidget(self.card2checkbox)

        self.card3checkbox = QCheckBox("Other cards")
        self.card3checkbox.setChecked(config["select_card_3"])
        self.card3checkbox.setStatusTip("Not available for all note types. Check with the creator of your notes. This will usually be gender cards for nouns and/or principles for verbs.")
        self.checkBoxes.addWidget(self.card3checkbox)
        self.text_layout.addLayout(self.checkBoxes)
           
        # Confirmation button
        self.confirmButton = QPushButton("Find Cards...")
        self.confirmButton.clicked.connect(self.readiness_check)
        self.text_layout.addWidget(self.confirmButton)

        # Settings Button
        self.bottom_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        self.bottom_layout.addWidget(self.cancel_button)
        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.show_settings)
        self.bottom_layout.addWidget(self.settings_button)
        self.text_layout.addLayout(self.bottom_layout)


        self.layout.addLayout(self.text_layout)
        self.layout.addLayout(self.table_layout)

        self.setLayout(self.layout)

        self.update_book_table()

    

    # Select all rows in the chapter table
    def select_all(self):
        self.chapter_table.selectAll()


    # Unselect all rows in the chapter table
    def select_none(self):
        self.chapter_table.clearSelection()


    # Repopulate the book list
    # Called when the collection is changed
    def update_book_table(self):
        self.book_list_label.setText(f"<b>Select a {self.collection.currentText()} book</b>")
        self.book_table.clearContents()
        self.chapter_table.clearContents()
        self.chapter_table.setRowCount(0)

        if self.collection.currentText() == "New Testament":
            self.book_table.setRowCount(len(NT_book_list))
            for index, book in enumerate(NT_book_list):
                item = QTableWidgetItem(book)
                self.book_table.setItem(index,0, item)
        
        if self.collection.currentText() == "Septuagint":
            self.book_table.setRowCount(len(LXX_book_list))
            for index, book in enumerate(LXX_book_list):
                item = QTableWidgetItem(book)
                self.book_table.setItem(index,0, item)


    # Repopulate the chapter list
    # Called when the book is changed
    def update_chapter_table(self):
        self.chapter_table.clearContents()
        self.chapter_table.setRowCount(0)

        try:
            self.selectedText = self.book_table.selectedItems()[0].text()

            file_path = self.get_file_path()
            with open(file_path, "r") as book_file:
            
                chapter_dict = json.load(book_file)

                chapter_list = []
                for chapter in chapter_dict:
                    chapter_list.append(chapter)

                self.chapter_table.setRowCount(len(chapter_list))
            
                for index, chapterNumber in enumerate(chapter_list):
                    item = QTableWidgetItem(chapterNumber)
                    item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                    self.chapter_table.setItem(index,0, item)
        except:
            pass
            


    # Check to make sure all components are prepared. Do not continue if failed.
    # Called by confirmation button in set_UI
    def readiness_check(self):
        if len(self.book_table.selectedItems()) == 0:   # Check for a book option.
            showInfo("No text selected")
        elif len(self.chapter_table.selectedItems()) == 0:
            showInfo("No chapters selected")
        elif not (self.card1checkbox.isChecked() or self.card2checkbox.isChecked() or self.card3checkbox.isChecked()):   # Make sure at least one card type is checked
            showInfo("At least one card type must be selected")
        else:
            self.cards_to_find = self.get_card_numbers()   # Create search string for selected cards
            self.find_cards_and_make_deck()   # Continue the operation


    def show_settings(self) -> None:
        self.settings = Configuration()
        self.settings.show()


    # Build a string to be added to the search query when building the deck
    # Called in readiness_check
    def get_card_numbers(self):
        one = self.card1checkbox.isChecked()
        two = self.card2checkbox.isChecked()
        three = self.card3checkbox.isChecked()

        if (one and not two and not three):              # Card 1 only
            return "card:1"
        if (not one and two and not three):              # Card 2 only
            return "card:2"
        if (one and two and not three):                  # Cards 1 and 2
            return "(card:1 OR card:2)"
        if (not one and not two and three):              # Cards 3+
            return "-(card:1 OR card:2)"
        if (one and not two and three):                  # Cards 1 and 3+
            return "-card:2"
        if (not one and two and three):                  # Cards 
            return "-card:1"
        if (one and two and three):                      # All Cards
            return ""


    # Called in readiness_check
    def find_cards_and_make_deck(self):

        # Extract data from json file. Used in get_word_list.
        file_path = self.get_file_path()
        book_file = open(file_path, "r")
        self.book_list = json.load(book_file)
        book_file.close()

        self.col = mw.col

        self.wordsToFind = self.get_word_list()

        chapter_range = self.format_range(self.chapter_numbers)

        self.selectedText += " " + chapter_range

        tooltip(f"Searching for {len(self.wordsToFind)} words...")

        self.total = len(self.wordsToFind)

        # Run a background operation for searching the collection
        query_op = QueryOp(parent = self, op = lambda dummy: self.find_words(dummy), success = lambda dummy: self.success(dummy))
        query_op.with_backend_progress(self.update_progress).run_in_background()


    # Called in find_cards_and_make_deck
    def get_word_list(self) -> dict:
        chapters = [chap.text() for chap in self.chapter_table.selectedItems()]
        self.chapter_numbers = []
        book_list = self.book_list
        self.selectedText = self.book_table.selectedItems()[0].text()
        wordsToFind = {}
        self.ignored_words = []
        n = 0

        with open(path.join(current_directory, "user_files/ignore.json"), "r+") as file:
            ignore_list = json.load(file)
        with open(path.join(current_directory, "user_files/corrections.json"), "r+") as file:
            corrections = json.load(file)
        with open(path.join(current_directory, "auto_corrections.json"), "r+") as file:
            auto_corrections = json.load(file)
            for correction in auto_corrections:
                corrections[correction] = auto_corrections[correction]["replacement"]
        
        for chapter in chapters:
            chapter_number = int(chapter.replace(f"{self.selectedText} ", ""))
            self.chapter_numbers.append(chapter_number)
            for word in book_list[chapter]:
                for char in forbidden_characters:
                    word = word.replace(char, "")
                if word in ignore_list:
                    if word not in self.ignored_words:
                        self.ignored_words.append(word)
                    continue
                correction = corrections.get(word)
                if correction is not None and correction != "":
                    word = correction
                if word not in wordsToFind:
                    n += 1
                    wordsToFind[word] = {"order": n, "freq": 1}
                else:
                    wordsToFind[word]["freq"] += 1
        
        self.numWordsToFind = len(wordsToFind)

        return wordsToFind
    
    def format_range(self, int_list):
    
        ranges = []
        start = int_list[0]
        end = int_list[0]

        for num in int_list[1:]:
            if num == end + 1:
                end = num
            else:
                if start == end:
                    ranges.append(str(start).zfill(len(str(int_list[-1]))))
                else:
                    ranges.append(f"{start:0{len(str(int_list[-1]))}}-{end:0{len(str(int_list[-1]))}}")
                start = end = num

        if start == end:
            ranges.append(str(start).zfill(len(str(int_list[-1]))))
        else:
            ranges.append(f"{start:0{len(str(int_list[-1]))}}-{end:0{len(str(int_list[-1]))}}")

        return ", ".join(ranges)


    # Get the storage file path for the selected text
    # Called in update_chapter_list to populate the chapter list
    # Called in get_word_list
    def get_file_path(self):
        current_book = self.selectedText

        if self.collection.currentText() == "New Testament":
            book_number = NT_book_list.index(current_book) + 1
        if self.collection.currentText() == "Septuagint":
            book_number = LXX_book_list.index(current_book) + 1

        file_path = path.join(current_directory, f"Texts/{self.collection.currentText()} Files", f"{str(book_number).zfill(2)} {current_book}.json")

        return file_path
    

    # Background operation to search the collection
    # Called by query_op in find_cards_and_make_deck.
    def find_words(self, dummy):
        self.idList = []
        self.missingWords = []
        self.found_count = 0
        self.count = 0

        for word in self.wordsToFind:
            self.show_search_warning = False
            self.search_query_num = 0
            query = f"\"re:^{word}([ ,]|\\W)\"" # Default search
            if config['strict'] == True:    # Narrow search using strict settings
                field = config['field_name']
                note_type = config['note_type']
                if field and not note_type:
                    query = f"\"{field}:re:^{word}([ ,]|\\W)\""
                elif not field and note_type:
                    query = f"\"note:{note_type}\" \"re:^{word}([ ,]|\\W)\""
                elif field and note_type:
                    query = f"\"note:{note_type}\" \"{field}:re:^{word}([ ,]|\\W)\""
                else:
                    self.show_search_warning = True
                
            ids = self.col.findNotes(query)
            
            for note_id in ids:
                if note_id not in self.idList:
                    self.idList.append(note_id)
                card_ids = self.col.findCards(f"nid:{note_id} {self.cards_to_find} -deck:filtered")
                
                # Reposition the cards to appear in order within text
                self.col.sched.reposition_new_cards(
                    card_ids=card_ids,
                    starting_from=self.wordsToFind[word]["order"],
                    step_size=0,
                    randomize=False,
                    shift_existing=False
                )

            if len(ids) == 0:
                self.missingWords.append(word)
            else:
                self.found_count += 1
            self.count += 1

        self.numMissingWords = len(self.missingWords)

        if self.numMissingWords:
            self.log_missing_words()   # 

    # Keep a record of words that are not found
    # Called at the end of find_words
    def log_missing_words(self) -> None:
        with open(path.join(path.dirname(path.abspath(__file__)), "user_files/missing.json"), "r") as log_file:
            log = json.load(log_file)
            date = datetime.datetime.now().strftime("%b %d, %Y")
            for word in self.missingWords:
                if word not in log:
                    log[word] = {"text": self.selectedText, "date": date}
        with open(path.join(path.dirname(path.abspath(__file__)), "user_files/missing.json"), "w") as log_file:
            json.dump(log, log_file, ensure_ascii=False, indent=4)


    # Update the progress bar
    # Called by query_op in find_cards_and_make_deck
    def update_progress(self, progress, update):
        update.label = f"{self.count}/{self.numWordsToFind}"
        update.value = self.count
        update.max = self.numWordsToFind
        

    # Called by query_op in find_cards_and_make_deck on completion
    def success(self, dummy):

        self.create_deck()

        self.hide()   # Close window

        mw.reset()

    
    # Called in success
    def create_deck(self):
    
        self.tag_name = f"make-temp-deck-for-{self.selectedText.replace(' ', '-')}-Greek"

        self.col.tags.bulkAdd(self.idList, self.tag_name)

        deck_name = ""

        # If parent deck spcified in the add-on confguration, add it to the name of the temporary deck.
        parent_deck = config["parent_deck"]
        if parent_deck:
            parent_deck = parent_deck.replace("$book$", self.book_table.selectedItems()[0].text())
            deck_name = parent_deck + "::"

        deck_name += f"{self.selectedText}"

        searchQuery = f"tag:{self.tag_name} is:new {self.cards_to_find}"

        # Make deck
        did = self.col.decks.new_filtered(deck_name)
        deck = self.col.decks.get(did)
        
        card_limit = config["deck_size_limit"]
        if card_limit == "":
            card_limit = 9999
        deck["terms"] = [[searchQuery, card_limit, DYN_DUE]]
        self.col.decks.save(deck)
        self.col.sched.rebuildDyn(did)

        # Delete tag from collection
        tags_manager = tags.TagManager(self.col)
        tags_manager.remove(self.tag_name)

        count = self.col.decks.card_count(dids=did, include_subdecks=False)

        if self.show_search_warning:
            showInfo("<p>Default search settings used.</p><p>Check search settings.</p>")
            
        textToAdd = "<p>No missing words</p>"
        if self.numMissingWords != 0:
            textToAdd = f"<p>Missing words: {self.numMissingWords}. Check the settings for more info.</p>"
        if len(self.ignored_words) > 0:
            textToAdd += f"<p>Ignored {len(self.ignored_words)}.</p>"
        if not config['strict']:
            textToAdd += "<p>If you receive extraneous words,<br>try changing the settings to search<br>for a specific note type and/or field.</p>"

        if count == 0:
            showInfo("All words learned, filtered, or ignored")
            self.col.decks.remove([did])
            tooltip(f"Deck deleted: {self.selectedText}")
        else:
            showInfo(f"<div style=\"width:20em\"><p>Deck created: {self.selectedText}.</p><p>Words found: {self.found_count}{textToAdd}</p></div>")


