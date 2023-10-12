from aqt import mw
from aqt.qt import *
from anki import tags

from .UI import TextPicker
from .cache import Cache

import datetime

current_version = "0.3.0"

forbidden_characters = ['(', ')']

def error_log(text) -> None:
    with open("C:\\Users\\drkin\\Desktop\\Errors.txt", "a+") as file:
        file.write(f"{datetime.datetime.now()} {text}\n")

def _run():

    def showTextPicker() -> None:
        textpicker.show()

    action = QAction()
    action.setText(f"Greek Vocabulary ({current_version})")
    mw.form.menuTools.addAction(action)
    action.triggered.connect(showTextPicker)
    mw.reset()
        
    error_log("Menu created")

    textpicker = TextPicker()

    error_log("Textpicker Created")

    new_cache = Cache()

    error_log("Greek Vocab Cached #1")

_run()