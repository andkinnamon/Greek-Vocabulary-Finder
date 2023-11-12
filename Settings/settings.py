# Anki imports
from aqt.qt import *

#Local imports
from .settings_tab import SettingsTab
from .ignore_tab import IgnoreTab
from .corrections_tab import CorrectionsTab
from .missing_tab import MissingTab
from .help_tab import HelpTab


class Configuration(QDialog):
    def __init__(self):
        QDialog.__init__(self)

        self.set_ui()

        self.finished.connect(self.update_tabs)

        self.await_close()


    def set_ui(self):
        self.setFixedSize(600, 500)

        self.setWindowTitle("Greek Vocabulary Finder Settings")
        self.layout = QVBoxLayout(self)
        
        # Initialize tab screen
        self.tabs = QTabWidget()
        self.settings_tab = SettingsTab()
        self.ignore_tab = IgnoreTab()
        self.corrections_tab = CorrectionsTab()
        self.missing_tab = MissingTab()
        self.help_tab = HelpTab()
        self.tabs.resize(325,200)
        
        # Add tabs
        self.tabs.addTab(self.settings_tab, "Settings")
        self.tabs.addTab(self.ignore_tab, "Ignore")
        self.tabs.addTab(self.corrections_tab, "Corrections")
        self.tabs.addTab(self.missing_tab, "Missing")
        self.tabs.addTab(self.help_tab, "Help")

        self.tabs.tabBarClicked.connect(self.update_tabs)
        
        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def update_tabs(self):

        self.settings_tab.save_to_file()
        self.ignore_tab.initialize_table()
        self.ignore_tab.save_to_file()
        self.corrections_tab.initialize_table()
        self.corrections_tab.save_to_file()
        self.missing_tab.initialize_table()
        self.missing_tab.save_to_file()

    def await_close(self):
        self.settings_tab.close_signal.connect(self.close)
        self.ignore_tab.close_signal.connect(self.close)
        self.corrections_tab.close_signal.connect(self.close)
        self.missing_tab.close_signal.connect(self.close)
        self.help_tab.close_signal.connect(self.close)

