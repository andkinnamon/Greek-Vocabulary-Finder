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


current_directory = path.dirname(path.abspath(__file__))

# TextPicker window for choosing text and creating deck
class TextPicker(QDialog):
    def __init__(self):
        QDialog.__init__(self)

        self.config = mw.addonManager.getConfig(__name__)   # Load add-on configuation settings

        self.set_UI()
    

    # Create Textpicker visual layout
    def set_UI(self):

        self.setWindowTitle("Select Text to Study")
        self.layout = QVBoxLayout()
        self.cardLayout = QHBoxLayout() # Sub-layout for card check boxes

        # Choose a collection (New Testament default)
        self.collection_label = QLabel("Select a collection of texts")
        self.layout.addWidget(self.collection_label)

        self.collection = QComboBox()
        self.collection.addItems(["New Testament", "Septuagint"])
        self.layout.addWidget(self.collection)

        # Choose a book
        self.book_list_label = QLabel(f"Select a {self.collection.currentText()} book")
        self.layout.addWidget(self.book_list_label)

        self.book = QComboBox()
        self.book.addItem("")
        self.book.addItems(NT_book_list)
        self.layout.addWidget(self.book)
        self.collection.currentTextChanged.connect(self.update_book_list)

        
        # Choose a chapter from a dropdown menu
        self.chapter_label = QLabel("Select a chapter")
        self.layout.addWidget(self.chapter_label)
        """
        self.chapterList = QComboBox()
        self.layout.addWidget(self.chapterList)
        self.book.currentTextChanged.connect(self.update_chapter_list)
        """

        self.chapterList = QTableWidget(0, 1, self)
        self.chapterList.verticalHeader().hide()
        self.chapterList.horizontalHeader().hide()
        self.layout.addWidget(self.chapterList)
        self.book.currentTextChanged.connect(self.update_chapter_table)


        # Checkboxes for choosing card layouts
        self.checkBoxes = QHBoxLayout()

        self.card1checkbox = QCheckBox("Grk → Eng")
        self.card1checkbox.setChecked(self.config["select_card_1"])
        self.checkBoxes.addWidget(self.card1checkbox)

        self.card2checkbox = QCheckBox("Eng → Grk")
        self.card2checkbox.setChecked(self.config["select_card_2"])
        self.checkBoxes.addWidget(self.card2checkbox)

        self.card3checkbox = QCheckBox("Other cards")
        self.card3checkbox.setChecked(self.config["select_cards_3+"])
        self.checkBoxes.addWidget(self.card3checkbox)
        
        self.layout.addLayout(self.checkBoxes)

        # Confirmation button
        self.confirmButton = QPushButton("Find Cards")
        self.confirmButton.clicked.connect(self.readiness_check)
        self.layout.addWidget(self.confirmButton)

        self.layout.setContentsMargins(10, 20, 10, 30)

        self.setLayout(self.layout)

    # Repopulate the book list
    # Called when the collection is changed
    def update_book_list(self):
        self.book.clear()

        self.book_list_label.setText(f"Select a {self.collection.currentText()} book")

        if self.collection.currentText() == "New Testament":
            self.book.addItem("")
            self.book.addItems(NT_book_list)
        
        if self.collection.currentText() == "Septuagint":
            self.book.addItem("")
            self.book.addItems(LXX_book_list)


    # Repopulate the chapter list
    # Called when the book is changed
    def update_chapter_list(self):
        self.chapterList.clear()
        
        # Collection changed -> Do nothing
        if self.book.currentText() == "":
            pass
        
        # Book changed -> Rebuild chapter list
        else:
            file_path = self.getFilePath()
            with open(file_path, "r") as book_file:
            
                chapter_list = json.load(book_file)
            
                for chapterNumber in chapter_list:
                    self.chapterList.addItem(chapterNumber)


    # Repopulate the chapter list
    # Called when the book is changed
    def update_chapter_table(self):
        self.chapterList.clearContents()
        
        # Collection changed -> Do nothing
        if self.book.currentText() == "":
            pass
        
        # Book changed -> Rebuild chapter list
        else:
            file_path = self.getFilePath()
            with open(file_path, "r") as book_file:
            
                chapter_dict = json.load(book_file)

                chapter_list = []
                for chapter in chapter_dict:
                    chapter_list.append(chapter)

                added_rows = 0

                self.chapterList.setRowCount(len(chapter_list))
            
                for chapterNumber in chapter_list:

                    item = QTableWidgetItem(chapterNumber)

                    item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                    #item.setCheckState(Qt.CheckState.Unchecked)

                    self.chapterList.setItem(1,added_rows-1, item)
                    added_rows += 1
            
            self.chapterList.resizeColumnsToContents()


    # Check to make sure all components are prepared. Do not continue if failed.
    # Called by confirmation button in set_UI
    def readiness_check(self):
        if self.book.currentText() == "":   # Check for a book option. No possibility of no chapter selected.
            showInfo("No text selected")
        elif not (self.card1checkbox.isChecked() or self.card2checkbox.isChecked() or self.card3checkbox.isChecked()):   # Make sure at least one card type is checked
            showInfo("At least one card type must be selected")
        else:
            self.cards_to_find = self.get_card_numbers()   # Create search string for selected cards
            self.find_cards_and_make_deck()   # Continue the operation


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
        self.selectedText = self.book.currentText()

        # Extract data from json file. Used in get_word_list.
        file_path = self.getFilePath()
        book_file = open(file_path, "r")
        self.book_list = json.load(book_file)
        book_file.close()

        self.col = mw.col

        self.wordsToFind = self.get_word_list()

        showInfo(f"Searching for {len(self.wordsToFind)} words...")

        self.total = len(self.wordsToFind)

        # Run a background operation for searching the collection
        query_op = QueryOp(parent = self, op = lambda dummy: self.find_words(dummy), success = lambda dummy: self.success(dummy))
        query_op.with_backend_progress(self.update_progress).run_in_background()


    # Called in find_cards_and_make_deck
    def get_word_list(self) -> dict:
        chapters = [chap.text() for chap in self.chapterList.selectedItems()]
        book_list = self.book_list
        self.selectedText = self.book.currentText()
        wordsToFind = {}
        n = 0
        for chapter in chapters:
            for word in book_list[chapter]:
                if word not in wordsToFind:
                    n += 1
                    wordsToFind[word] = {"order": n, "freq": 1}
                else:
                    wordsToFind[word]["freq"] += 1
        
        self.numWordsToFind = len(wordsToFind)

        return wordsToFind

    # Get the storage file path for the selected text
    # Called in update_chapter_list to populate the chapter list
    # Called in get_word_list
    def getFilePath(self):
        current_book = self.book.currentText()

        if self.collection.currentText() == "New Testament":
            book_number = NT_book_list.index(current_book) + 1
        if self.collection.currentText() == "Septuagint":
            book_number = LXX_book_list.index(current_book) + 1
    
        #self.chapterList.addItem("Whole Book")

        file_path = path.join(current_directory, f"{self.collection.currentText()} Files", f"{str(book_number).zfill(2)} {current_book}.json")

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
            if self.config['strict'] == True:    # Narrow search using strict settings
                field = self.config['field_name']
                note_type = self.config['note_type']
                if field and not note_type:
                    query = f"\"{field}:re:^{word}([ ,]|\\W)\""
                elif not field and note_type:
                    query = f"\"note:{note_type}\" \"re:^{word}([ ,]|\\W)\""
                elif field and note_type:
                    query = f"\"note:{note_type}\" \"{field}:re:^{word}([ ,]|\\W)\""
                else:
                    self.show_search_warning = True
                    query = f"\"re:^{word}([ ,]|\\W)\""
            else:                        # Broad search using only word
                query = f"\"re:^{word}([ ,]|\\W)\""

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
        with open(path.join(path.dirname(path.abspath(__file__)), "log.log"), "a") as log:
            log.write("="*50)
            log.write(f"\n\n{datetime.datetime.now()}\n\nAttempted to create {self.selectedText} deck. Missing words:\n\n")
            for word in self.missingWords:
                log.write(word)
                log.write("\n")
            log.write("\n")


    # Update the progress bar
    # Called by query_op in find_cards_and_make_deck
    def update_progress(self, progress, update):
        update.label = f"{self.count}/{self.numWordsToFind}"
        update.value = self.count
        update.max = self.numWordsToFind
        

    # Called by query_op in find_cards_and_make_deck on completion
    def success(self, dummy):

        if self.show_search_warning:
            showInfo("Default search settings used<br><br>Turn off Strict or add Field or Note Type requirements")
            
        textToAdd = "<br><br>No missing words"
        if self.numMissingWords != 0:
            textToAdd = f"<br><br>Missing words: {self.numMissingWords}. See <a href=\"file:///{current_directory}\\log.log\">log</a>."
        if not self.config['strict']:
            textToAdd += "<br><br>If you receive extraneous words, try changing the settings to search for a specific note type and/or field name and set strict to true<br><br>Tools→Add-ons→Config"

        self.create_deck()
        
        showInfo(f"Deck created: {self.selectedText}. Words found: {self.found_count}{textToAdd}")

        self.hide()   # Close window

        mw.reset()

    
    # Called in success
    def create_deck(self):
    
        self.tag_name = f"make-temp-deck-for-{self.selectedText.replace(' ', '-')}-Greek"

        self.col.tags.bulkAdd(self.idList, self.tag_name)

        deckName = ""

        # If parent deck spcified in the add-on confguration, add it to the name of the temporary deck.
        parent_deck = self.config["parent_deck"]
        if parent_deck:
            parent_deck.replace("&book&", self.selectedText)
            deckName += parent_deck + "::"

        deckName += f"{self.selectedText}"

        searchQuery = f"tag:{self.tag_name} is:new {self.cards_to_find}"

        # Make deck
        did = self.col.decks.new_filtered(deckName)
        deck = self.col.decks.get(did)
        deck["terms"] = [[searchQuery, self.config["deck_size_limit"], DYN_DUE]]
        self.col.decks.save(deck)
        self.col.sched.rebuildDyn(did)

        # Delete tag from collection
        tags_manager = tags.TagManager(self.col)
        tags_manager.remove(self.tag_name)

