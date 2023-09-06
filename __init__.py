from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *
from aqt.operations import QueryOp
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

    def _main(self):
        op = QueryOp(
        parent=mw,
        op=lambda 
    ):

        # if with_progress() is not called, no progress window will be shown.
        # note: QueryOp.with_progress() was broken until Anki 2.1.50
        op.with_progress().run_in_background()

    def _find_cards_and_make_deck(self):
        self.selectedText = self.chapterList.currentText()

        file_path = self.getFilePath()
        book_file = open(file_path, "r")
        self.book_list = json.load(book_file)
        book_file.close()

        wordsToFind = self.get_word_list()

        col = mw.col

        showInfo(f"Searching for {len(wordsToFind)} words...")
        
        idList, missingWords = self.find_words()

        textToAdd = "<br><br>No missing words"
        if len(missingWords) != 0:
            textToAdd = f"<br><br>Missing words: {len(missingWords)}. Check log for details."

        showInfo(f"Notes found: {n}{textToAdd}")

        tag_name = "add-this-tag-to-cards-to-make-temp-deck"

        col.tags.bulkAdd(idList, tag_name)

        deckName = f"New Greek Vocab - {selectedText}"
        deckId = int(datetime.datetime.now().timestamp()) % 10**9

        searchQuery = f"tag:{tag_name} is:new card:1"

        did = col.decks.new_filtered(deckName)
        deck = col.decks.get(did)
        deck["terms"] = [[searchQuery, 1000, DYN_DUE]]
        col.decks.save(deck)
        col.sched.rebuildDyn(did)
        mw.progress.finish()

        closeTextPicker()
        
        mw.reset()

        showInfo(f"Deck created: {selectedText}")


    def get_word_list(self, text=self.selectedText,book_list=self.book_list) -> dict:
        if text == "Whole Book":
            text = self.book.currentText()
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
            wordsToFind = book_list[selectedText]

        return wordsToFind


    def getFilePath(self):
        current_book = self.book.currentText()
        book_number = NT_book_list.index(current_book) + 1
    
        self.chapterList.clear()
        self.chapterList.addItem("Whole Book")

        current_directory = Path.dirname(Path.abspath(__file__))
        file_path = Path.join(current_directory, "NT", f"{str(book_number).zfill(2)} {current_book}.json")

        return file_path
    

    def find_words(self, col):
        idList = []
        missingWords = []
        for word in wordsToFind:
            ids = col.findNotes(f"\"Dictionary Entry:re:^{word}\\b\" -\"NT Frequency:\"")
            for id in ids:
                if id not in idList:
                    n += 1
                    idList.append(id)
            if len(ids) == 0:
                missingWords.append(word)

        self.log_missing_words(missingWords)


    def log_missing_words(self, missingWords) -> None:
        with open(Path.join(Path.dirname(Path.abspath(__file__)), "log.log"), "a") as log:
            log.write("="*50)
            log.write(f"\n\n{datetime.datetime.now()}\n\nAttempted to create {self.selectedText} deck. Missing words:\n\n")
            for word in missingWords:
                log.write(word)
                log.write("\n")
            log.write("\n")
    

    def closeTextPicker() -> None:
        # Beta code: Do not trust
        textpicker.hide()


    def showProgressBar() -> None:
        # Fill this in later
        dummy = "This is dummy text"


textpicker = TextPicker()

def showTextPicker() -> None:
    textpicker.show()


action = QAction()
action.setText("Greek Vocabulary")
mw.form.menuTools.addAction(action)
action.triggered.connect(showTextPicker)