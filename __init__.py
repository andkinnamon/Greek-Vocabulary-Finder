from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, tooltip

from .UI import TextPicker
from .cache import Cache

current_version = "0.3.0"

class MenuManager:
    def __init__(self):
        self.setupMenu()

    def showTextPicker(self) -> None:
        self.textpicker = TextPicker()
        self.textpicker.show()

    def setupMenu(self):
        self.action = QAction()
        self.action.setText(f"Greek Vocabulary ({current_version})")
        mw.form.menuTools.addAction(self.action)
        self.action.triggered.connect(self.showTextPicker)

menuManager = MenuManager()

config = mw.addonManager.getConfig(__name__)

if config['cache'] == True:
    pass
    #new_cache = Cache()