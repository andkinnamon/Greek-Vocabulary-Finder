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

# TextPicker dialog for choosing text and creating deck
class TextPicker(QDialog):
    def __init__(self):
        QDialog.__init__(self)

        self.config = mw.addonManager.getConfig(__name__)

        self.n = 0

        self.set_UI()
    

    def set_UI(self):

        self.setWindowTitle("Select Text to Study")
        self.layout = QVBoxLayout()
        self.cardLayout = QHBoxLayout()

        self.collection_label = QLabel("Select a collection of texts")
        self.layout.addWidget(self.collection_label)

        self.collection = QComboBox()
        self.collection.addItems(["New Testament", "Septuagint"])
        self.layout.addWidget(self.collection)

        self.book_list_label = QLabel(f"Select a {self.collection.currentText()} book")
        self.layout.addWidget(self.book_list_label)

        self.book = QComboBox()
        self.book.addItem("")
        self.book.addItems(NT_book_list)
        self.layout.addWidget(self.book)
        self.collection.currentTextChanged.connect(self.update_book_list)

        self.chapter_label = QLabel("Select a chapter")
        self.layout.addWidget(self.chapter_label)

        self.chapterList = QComboBox()
        self.layout.addWidget(self.chapterList)
        self.book.currentTextChanged.connect(self.update_chapter_list)

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

        self.confirmButton = QPushButton("Find Cards")
        self.confirmButton.clicked.connect(self.readiness_check)
        self.layout.addWidget(self.confirmButton)

        self.layout.setContentsMargins(10, 20, 10, 30)

        self.setLayout(self.layout)

    def update_book_list(self):
        self.book.clear()

        self.book_list_label.setText(f"Select a {self.collection.currentText()} book")

        if self.collection.currentText() == "New Testament":
            self.book.addItem("")
            self.book.addItems(NT_book_list)
        
        if self.collection.currentText() == "Septuagint":
            self.book.addItem("")
            self.book.addItems(LXX_book_list)


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


    def readiness_check(self):
        if self.book.currentText() == "":
            showInfo("No text selected")
        elif not (self.card1checkbox.isChecked() or self.card2checkbox.isChecked() or self.card3checkbox.isChecked()):
            showInfo("At least one card type must be selected")
        else:
            self.get_card_numbers()
            self._find_cards_and_make_deck()


    def get_card_numbers(self):
        one = self.card1checkbox.isChecked()
        two = self.card2checkbox.isChecked()
        three = self.card3checkbox.isChecked()

        if (one and not two and not three):
            self.cards_to_find = "card:1"
        if (not one and two and not three):
            self.cards_to_find = "card:2"
        if (one and two and not three):
            self.cards_to_find = "(card:1 OR card:2)"
        if (not one and not two and three):
            self.cards_to_find = "-(card:1 OR card:2)"
        if (one and not two and three):
            self.cards_to_find = "-card:2"
        if (not one and two and three):
            self.cards_to_find = "-card:1"
        if (one and two and three):
            self.cards_to_find = ""


    def _find_cards_and_make_deck(self):
        self.selectedText = self.chapterList.currentText()

        file_path = self.getFilePath()
        book_file = open(file_path, "r")
        self.book_list = json.load(book_file)
        book_file.close()

        self.col = mw.col

        self.wordsToFind = self.get_word_list()

        showInfo(f"Searching for {len(self.wordsToFind)} words...")

        self.total = len(self.wordsToFind)

        query_op = QueryOp(parent = self, op = lambda dummy: self.find_words(dummy), success = lambda dummy: self.success(dummy))
        #query_op.with_progress()
        query_op.with_backend_progress(self.update_progress).run_in_background()
        #query_op.with_progress().run_in_background()


    def get_word_list(self) -> dict:
        text = self.selectedText
        book_list = self.book_list
        if text == "Whole Book":
            self.selectedText = self.book.currentText()
            wordsToFind = {}
            n = 0
            for chapter in book_list:
                for word in book_list[chapter]:
                    if word not in wordsToFind:
                        n += 1
                        wordsToFind[word] = {"order": n, "freq":1}
                    else:
                        wordsToFind[word]["freq"] += 1
        else:
            wordsToFind = book_list[text]

        
        self.numWordsToFind = len(wordsToFind)

        return wordsToFind


    def getFilePath(self):
        current_book = self.book.currentText()

        if self.collection.currentText() == "New Testament":
            book_number = NT_book_list.index(current_book) + 1
        if self.collection.currentText() == "Septuagint":
            book_number = LXX_book_list.index(current_book) + 1
    
        self.chapterList.addItem("Whole Book")

        file_path = path.join(current_directory, f"{self.collection.currentText()} Files", f"{str(book_number).zfill(2)} {current_book}.json")

        return file_path
    

    def find_words(self, dummy):
        self.idList = []
        self.missingWords = []
        self.found_count = 0

        for word in self.wordsToFind:
            query = f"\"{self.config['field_name']}:re:^{word}$\""
            ids = self.col.findNotes(query)
            for note_id in ids:
                if note_id not in self.idList:
                    self.idList.append(note_id)
                card_ids = self.col.findCards(f"nid:{note_id} {self.cards_to_find}")
                
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
            self.n += 1

            #update = ProgressUpdate(label = f"{self.n}/{self.numWordsToFind}", value = self.n, max = self.numWordsToFind)
            #self.update_progress()

        self.numMissingWords = len(self.missingWords)

        if self.numMissingWords:
            self.log_missing_words()


    def log_missing_words(self) -> None:
        with open(path.join(path.dirname(path.abspath(__file__)), "log.log"), "a") as log:
            log.write("="*50)
            log.write(f"\n\n{datetime.datetime.now()}\n\nAttempted to create {self.selectedText} deck. Missing words:\n\n")
            for word in self.missingWords:
                log.write(word)
                log.write("\n")
            log.write("\n")


    def update_progress(self, progress, update):
        update.label = f"{self.n}/{self.numWordsToFind}"
        update.value = self.n
        update.max = self.numWordsToFind
        


    def success(self, dummy):

        textToAdd = "<br><br>No missing words"
        if self.numMissingWords != 0:
            textToAdd = f"<br><br>Missing words: {self.numMissingWords}. See <a href=\"file:///{current_directory}\\log.log\">log</a>."

        self._create_deck()
        
        showInfo(f"Deck created: {self.selectedText}. Words found: {self.found_count}{textToAdd}")

        self.reset()

        self.hide()

        mw.reset()

    
    def _create_deck(self):
    
        self.tag_name = "add-this-tag-to-cards-to-make-temp-deck"

        self.col.tags.bulkAdd(self.idList, self.tag_name)

        deckName = ""

        parent_deck = self.config["parent_deck"]
        if parent_deck:
            deckName += parent_deck + "::"

        deckName += f"{self.selectedText}"

        searchQuery = f"tag:{self.tag_name} is:new {self.cards_to_find}"

        did = self.col.decks.new_filtered(deckName)
        deck = self.col.decks.get(did)
        deck["terms"] = [[searchQuery, self.config["deck_size_limit"], DYN_DUE]]
        self.col.decks.save(deck)
        self.col.sched.rebuildDyn(did)
        #mw.progress.finish()


    def _delete_tag(self):
        tags_manager = tags.TagManager(self.col)
        tags_manager.remove(self.tag_name)

    def reset(self):
        self._delete_tag()

        self.book = None
        self.book_list = None
        self.missingWords = None
        self.cards_to_find = None
