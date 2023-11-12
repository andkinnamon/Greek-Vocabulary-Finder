
# Anki imports
from aqt.qt import *
from aqt.utils import showInfo, tooltip

# Python imports
import json
from os import path

#Local imports
from ..constants import *
from . import *

class HelpTab(QWidget):

    close_signal = pyqtSignal()

    def __init__(self):

        QWidget.__init__(self)

        self.layout = QVBoxLayout()

        self.text = QLabel("<h1>Come back later!</h1><p>Issues? Let me know <a href=\"https://github.com/andkinnamon/Greek-Vocabulary-Finder/issues\">here</a>!</p>")
        self.text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text.setOpenExternalLinks(True)

        self.layout.addWidget(self.text)

        self.button_box = QHBoxLayout()
        self.button_box.addStretch()
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.save_and_close)
        self.button_box.addWidget(self.close_button)
        self.layout.addLayout(self.button_box)
        self.setLayout(self.layout)

    def save_and_close(self):
        
        self.close_signal.emit()