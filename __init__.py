from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, tooltip

from .UI import TextPicker

current_version = "0.4.2"

class MenuManager:
    def __init__(self):
        self.setupMenu()

    def showTextPicker(self) -> None:
        self.textpicker = TextPicker()
        self.textpicker.show()

    def setupMenu(self):
        self.action = QAction()
        self.action.setText(f"Greek Vocabulary")
        mw.form.menuTools.addAction(self.action)
        self.action.triggered.connect(self.showTextPicker)

menuManager = MenuManager()

config = mw.addonManager.getConfig(__name__)