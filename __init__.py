from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, tooltip

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