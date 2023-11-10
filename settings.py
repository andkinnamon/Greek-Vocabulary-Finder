# Anki imports
from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo, tooltip

# Python imports
import json


class Configuration(QDialog):
    def __init__(self):
        QDialog.__init__(self)

        self.config = mw.addonManager.getConfig(__name__)

        self.set_ui()



    def set_ui(self):
        self.setFixedSize(600, 400)

        self.setWindowTitle("Greek Vocabulary Finder Settings")
        self.layout = QVBoxLayout(self)
        
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.settings_tab = QWidget()
        self.ignore_tab = QWidget()
        self.corrections_tab = QWidget()
        self.tabs.resize(300,200)
        
        # Add tabs
        self.tabs.addTab(self.settings_tab, "Settings")
        self.tabs.addTab(self.ignore_tab, "Ignore")
        self.tabs.addTab(self.corrections_tab, "Corrections")
        
        # Settings tab
        self.settings_tab.layout = QVBoxLayout(self)
        self.label1 = QLabel("Under Construction<br><br>This will be where the general settings belong")
        self.settings_tab.layout.addWidget(self.label1)
        self.settings_tab.setLayout(self.settings_tab.layout)

        # Ignore tab
        self.ignore_tab.layout = QVBoxLayout(self)
        self.label2 = QLabel("Under Construction!<br><br>This will be where the user can add words to ignore in the search")
        self.ignore_tab.layout.addWidget(self.label2)
        self.ignore_tab.setLayout(self.ignore_tab.layout)

        # Corrections tab
        self.corrections_tab.layout = QVBoxLayout(self)
        self.pushButton1 = QLabel("Under Construction!<br><br>This will be where the user can add corrections to the search")
        self.corrections_tab.layout.addWidget(self.pushButton1)
        self.corrections_tab.setLayout(self.corrections_tab.layout)

        
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.setLayout(self.layout)