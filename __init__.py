# -*- coding: utf-8 -*-

"""
Anki Add-on: Greek Bible Vocabulary Finder

Updated November 7, 2023 by Andrew Kinnamon

Search your Anki collection for unlearned Greek words from the New Testament or Septuagint.

Copyright: (c) Andrew Kinnamon 2023 (https://github.com/andkinnamon)
License: GNU GPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
"""

from aqt import mw
from aqt.qt import *

from .textpicker import TextPicker

class MenuManager:
    def __init__(self):
        self.setupMenu()

    def showTextPicker(self) -> None:
        self.textpicker = TextPicker()
        self.textpicker.show()

    def setupMenu(self):
        self.action = QAction()
        self.action.setText(f"Greek Vocab Finder - beta")
        mw.form.menuTools.addAction(self.action)
        self.action.triggered.connect(self.showTextPicker)

menuManager = MenuManager()