from aqt import mw
from aqt import progress as PROG
from aqt.utils import showInfo
from aqt.qt import *
from aqt.operations import QueryOp
from aqt.errors import show_exception
from anki import tags
from aqt import filtered_deck as filter
from anki.consts import DYN_DUE

from .bible_lists import *

import datetime
import json
from os import path as Path

class TextPicker(QDialog):
    def __init__(self):
        QDialog.__init__(self)

        self.config = mw.addonManager.getConfig(__name__)

        self.setWindowTitle("Select Text to Study")
        self.layout = QVBoxLayout()
        self.cardLayout = QHBoxLayout()

        self.label1 = QLabel("Select a New Testament book to study its vocabulary")
        self.layout.addWidget(self.label1)

        self.book = QComboBox()
        self.book.addItem("")
        self.book.addItems(NT_book_list)
        self.layout.addWidget(self.book)

        self.label2 = QLabel("Select a chapter")
        self.layout.addWidget(self.label2)

        self.chapterList = QComboBox()
        self.layout.addWidget(self.chapterList)
        self.book.currentTextChanged.connect(self.update_chapter_list)

        self.confirmButton = QPushButton("Find Cards")
        self.confirmButton.clicked.connect(self._find_cards_and_make_deck)
        self.layout.addWidget(self.confirmButton)

        self.layout.setContentsMargins(10, 20, 10, 30)

        self.setLayout(self.layout)


    def update_chapter_list(self):
        file_path = self.getFilePath()
        with open(file_path, "r") as book_file:
        
            chapter_list = json.load(book_file)
        
            for chapterNumber in chapter_list:
                self.chapterList.addItem(chapterNumber)


    def _find_cards_and_make_deck(self):
        self.selectedText = self.chapterList.currentText()

        file_path = self.getFilePath()
        book_file = open(file_path, "r")
        self.book_list = json.load(book_file)
        book_file.close()

        self.col = mw.col

        self.wordsToFind = self.get_word_list()

        #showInfo(f"Searching for {len(self.wordsToFind)} words...")

        self.found = 0
        self.total = len(self.wordsToFind)

        self.progress = PROG.ProgressManager(mw)
        self.progress.start()

        query_op = QueryOp(parent=self, op=self.find_words, success=self.success)
        #query_op.with_progress()
        query_op.with_backend_progress(self.update_progress).run_in_background()
        self.progress.finish()

        self._create_deck()
        
        showInfo(f"Deck created: {self.selectedText}")

        self._delete_tag()

        closeTextPicker()

        mw.reset()


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

        return wordsToFind


    def getFilePath(self):
        current_book = self.book.currentText()
        book_number = NT_book_list.index(current_book) + 1
    
        self.chapterList.clear()
        self.chapterList.addItem("Whole Book")

        current_directory = Path.dirname(Path.abspath(__file__))
        file_path = Path.join(current_directory, "NT", f"{str(book_number).zfill(2)} {current_book}.json")

        return file_path
    

    def find_words(self):
        self.idList = []
        self.missingWords = []
        self.n = 0

        notes = self.col.findNotes(f"\"note:\"")

        try:

            for word in self.wordsToFind:
                ids = self.col.findNotes(f"\"Dictionary Entry:re:^{word}$\" -\"NT Frequency:\"")
                for id in ids:
                    if id not in self.idList:
                        self.n += 1
                        self.idList.append(id)
                if len(ids) == 0:
                    self.missingWords.append(word)
                
                self.found += 1

                #self.progress.update(label=f"{self.found}/{self.total}", value=self.found, max=self.total)

                self.update_progress(self.progress, PROG.ProgressUpdate(label=f"{self.found}/{self.total}"),value=self.found, max=self.total)
        except exception:
            show_exception(parent=self._parent, exception=exception)

        if self.missingWords:
            self.log_missing_words()

        self.numMissingWords = len(self.missingWords)


    def log_missing_words(self) -> None:
        with open(Path.join(Path.dirname(Path.abspath(__file__)), "log.log"), "a") as log:
            log.write("="*50)
            log.write(f"\n\n{datetime.datetime.now()}\n\nAttempted to create {self.selectedText} deck. Missing words:\n\n")
            for word in self.missingWords:
                log.write(word)
                log.write("\n")
            log.write("\n")


    def update_progress(self, progress, update):
        progress = progress
        update = update
        #progress.update(label=update.label, value=update.value, max=update.max)

    

    def success(self):

        textToAdd = "<br><br>No missing words"
        if self.numMissingWords != 0:
            textToAdd = f"<br><br>Missing words: {self.numMissingWords}. Check log for details."

        showInfo(f"Words found: {self.n}{textToAdd}")

    
    def _create_deck(self):
    
        self.tag_name = "add-this-tag-to-cards-to-make-temp-deck"

        self.col.tags.bulkAdd(self.idList, self.tag_name)

        deckName = ""

        parent_deck = self.config["parent_deck"]
        if parent_deck:
            deckName += parent_deck + "::"

        deckName += f"{self.selectedText}"
        deckId = int(datetime.datetime.now().timestamp()) % 10**9

        searchQuery = f"tag:{self.tag_name} is:new card:1"

        did = self.col.decks.new_filtered(deckName)
        deck = self.col.decks.get(did)
        deck["terms"] = [[searchQuery, 1000, DYN_DUE]]
        self.col.decks.save(deck)
        self.col.sched.rebuildDyn(did)
        mw.progress.finish()

    def _delete_tag(self):
        tags_manager = tags.TagManager(self.col)

        tags_manager.remove(self.tag_name)
        # Add code
        dummy = "Filler text"


textpicker = TextPicker()

def showTextPicker() -> None:
    textpicker.show()

def closeTextPicker() -> None:
    # Beta code: Do not trust
    textpicker.hide()


action = QAction()
action.setText("Greek Vocabulary")
mw.form.menuTools.addAction(action)
action.triggered.connect(showTextPicker)