# Anki imports
from aqt import mw
from aqt.qt import *
from aqt.switch import Switch
from aqt.utils import showInfo, tooltip

# Python imports
import json
from os import path

#Local imports
from ..constants import *

class SettingsTab(QWidget):

    close_signal = pyqtSignal()

    def __init__(self):
        QWidget.__init__(self)

        self.set_ui()

    def set_ui(self):
        self.layout = QHBoxLayout()
        self.layout_left = QBoxLayout(QBoxLayout.Direction.TopToBottom)
        self.layout_right = QBoxLayout(QBoxLayout.Direction.TopToBottom)

        self.heading_label = QLabel("<h1><u>Settings</u></h1>")
        self.layout_left.addWidget(self.heading_label)

        self.search_settings_header = QHBoxLayout()
        self.search_settings_label = QLabel("<h2>Search Settings</h2>")
        self.search_settings_header.addWidget(self.search_settings_label)
        self.strict = Switch(left_label = "Off  ", right_label = "  On")
        self.strict.setChecked(config["strict"])
        self.strict.clicked.connect(self.set_editable)
        self.search_settings_header.addWidget(self.strict)
        self.search_settings_header.addStretch()
        self.layout_right.addLayout(self.search_settings_header)

        self.set_collection()
        self.set_deck_options()
        self.set_deck_limit()
        self.set_note_type_box()
        self.set_field_name_box()
        self.set_card_options()
        self.set_editable()

        self.layout_left.addStretch()
        self.layout_right.addStretch()
        self.save_button_layout = QHBoxLayout()
        self.save_button_layout.addStretch()
        self.reset_defaults_button = QPushButton("Reset to Defaults")
        self.reset_defaults_button.clicked.connect(self.reset_to_defaults)
        self.save_button_layout.addWidget(self.reset_defaults_button)
        self.reset_defaults_button.setAutoDefault(False)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_and_close)
        self.save_button_layout.addWidget(self.save_button)
        self.save_button.setAutoDefault(False)
        self.layout_right.addLayout(self.save_button_layout)

        self.layout.addLayout(self.layout_left)
        self.layout.addLayout(self.layout_right)
        self.setLayout(self.layout)    

    def set_note_type_box(self):
        self.note_type_box_layout = QHBoxLayout()
        self.note_type_label = QLabel("<h3>Note Type:</h3>")
        self.note_type_box_layout.addWidget(self.note_type_label)
        self.note_type_box = QLineEdit(config["note_type"])
        self.note_type_box.returnPressed.connect(self.save_to_file)
        self.note_type_box_layout.addWidget(self.note_type_box)
        self.layout_right.addLayout(self.note_type_box_layout)
        self.note_type_explanation_label = QLabel("<p>Excludes all other note types. Must match exactly. To use multiple note types, use a <a href=\"https://regex101.com\">regular expression</a> beginning with `re:`</p>")
        self.note_type_explanation_label.setWordWrap(True)
        self.note_type_explanation_label.setOpenExternalLinks(True)
        self.layout_right.addWidget(self.note_type_explanation_label)

    def set_field_name_box(self):
        self.field_name_box_layout = QHBoxLayout()
        self.field_name_label = QLabel("<h3>Field Name:</h3>")
        self.field_name_box_layout.addWidget(self.field_name_label)
        self.field_name_box = QLineEdit(config["field_name"])
        self.field_name_box.returnPressed.connect(self.save_to_file)
        self.field_name_box_layout.addWidget(self.field_name_box)
        self.layout_right.addLayout(self.field_name_box_layout)
        self.field_name_explanation_label = QLabel("<p>Exclusive field search. Must match exactly. Can be combined with a note type or used alone. Accepts only one.</p>")
        self.field_name_explanation_label.setWordWrap(True)
        self.field_name_explanation_label.setOpenExternalLinks(True)
        self.layout_right.addWidget(self.field_name_explanation_label)

    def set_card_options(self):

        self.card_options_heading_label = QLabel("<h3>Card Defaults:</h3><p>These settings determine the default for the text selection page. If you are consistently changing them on that page, change them here.</p>")
        self.card_options_heading_label.setWordWrap(True)
        self.layout_right.addWidget(self.card_options_heading_label)

        self.card_1_switch_layout = QHBoxLayout()
        self.card_1_switch = Switch(radius = 7)
        self.card_1_switch.setChecked(config["select_card_1"])
        self.card_1_switch_layout.addWidget(self.card_1_switch)
        self.card_1_switch_label = QLabel(f"Greek to {config['language']}")
        self.card_1_switch_layout.addWidget(self.card_1_switch_label)
        self.card_1_switch_layout.addStretch()
        self.layout_right.addLayout(self.card_1_switch_layout)

        self.card_2_switch_layout = QHBoxLayout()
        self.card_2_switch = Switch(radius = 7)
        self.card_2_switch.setChecked(config["select_card_2"])
        self.card_2_switch_layout.addWidget(self.card_2_switch)
        self.card_2_switch_label = QLabel(f"{config['language']} to Greek")
        self.card_2_switch_layout.addWidget(self.card_2_switch_label)
        self.card_2_switch_layout.addStretch()
        self.layout_right.addLayout(self.card_2_switch_layout)

        self.card_3_switch = Switch(radius = 7)
        self.card_3_switch_layout = QHBoxLayout()
        self.card_3_switch.setChecked(config["select_card_3"])
        self.card_3_switch_layout.addWidget(self.card_3_switch)
        self.card_3_switch_label = QLabel("Additional Cards")
        self.card_3_switch_layout.addWidget(self.card_3_switch_label)
        self.card_3_switch_layout.addStretch()
        self.layout_right.addLayout(self.card_3_switch_layout)

        self.card_3_explanation = QLabel("<p>Some note types contain additional cards. These can be for noun genders, verb principle parts, case uses for prepositions, etc.</p>")
        self.card_3_explanation.setWordWrap(True)
        self.layout_right.addWidget(self.card_3_explanation)

    def set_collection(self):
        self.collection_label = QLabel("<h2>Collection:</h2>")
        self.layout_left.addWidget(self.collection_label)
        self.collection = QComboBox()
        self.collection.addItems(["New Testament", "Septuagint"])
        self.collection.setCurrentText(config["collection"])
        self.layout_left.addWidget(self.collection)


    def set_deck_options(self):
        self.deck_option_heading_label = QLabel("<h2>Deck Settings</h2><p>These settings are used when building the temporary deck.</p>")
        self.deck_option_heading_label.setWordWrap(True)
        self.layout_left.addWidget(self.deck_option_heading_label)

        self.parent_deck_label = QLabel("<h3>Parent Deck:</h3>")
        self.layout_left.addWidget(self.parent_deck_label)
        self.parent_deck = QLineEdit(f"{config['parent_deck']}")
        self.parent_deck.returnPressed.connect(self.save_to_file)
        self.layout_left.addWidget(self.parent_deck)
        self.parent_deck_explanation = QLabel("<p>Temporary decks will be placed into this deck. Seperate parent and child decks with `::`. Limit the number of daily cards by setting a new card limit to this parent deck. To include the name of the text, use `$book$`.</p>")
        self.parent_deck_explanation.setWordWrap(True)
        self.layout_left.addWidget(self.parent_deck_explanation)


    def set_deck_limit(self):

        self.deck_limit_label = QLabel("<h3>Deck Size Limit:</h3>")
        self.layout_left.addWidget(self.deck_limit_label)
        self.deck_limit_box_layout = QHBoxLayout()
        self.deck_limit = QLineEdit(f"{config['deck_size_limit']}")
        limits = QIntValidator(1,9999)
        self.deck_limit.setValidator(limits)
        self.deck_limit.returnPressed.connect(self.save_to_file)
        self.deck_limit_box_layout.addWidget(self.deck_limit)
        self.deck_limit_box_layout.addStretch()
        self.deck_limit.resize(self.deck_limit.height(), 100)
        self.layout_left.addLayout(self.deck_limit_box_layout)

        self.deck_limit_explainer = QLabel("<p>Set a size limit to temporary decks. Must be between 1 and 9999.</p>")
        self.deck_limit_explainer.setWordWrap(True)
        self.layout_left.addWidget(self.deck_limit_explainer)


    def set_editable(self):
        if self.strict.isChecked():
            self.note_type_box.setDisabled(False)
            self.field_name_box.setDisabled(False)
            self.note_type_box.setPlaceholderText("")
            self.field_name_box.setPlaceholderText("")

        else:
            self.note_type_box.setDisabled(True)
            self.field_name_box.setDisabled(True)
            if config["note_type"] == "":
                self.note_type_box.setPlaceholderText("Turn on to edit")
            if config["field_name"] == "":
                self.field_name_box.setPlaceholderText("Turn on to edit")


    def reset_to_defaults(self):
        with open(path.join(current_directory, "Settings/default_config.json"), "r+") as file:
            defaults = json.load(file)
        with open(path.join(current_directory, "user_files/config.json"), "w") as file:
            json.dump(defaults, file, indent=4)
        self.strict.setChecked(config["strict"])
        self.note_type_box.setText(config["note_type"])
        self.field_name_box.setText(config["field_name"])
        self.card_1_switch.setChecked(config["select_card_1"])
        self.card_2_switch.setChecked(config["select_card_2"])
        self.card_3_switch.setChecked(config["select_card_3"])
        self.parent_deck.setText(config["parent_deck"])
        self.deck_limit.setText(f"{config['deck_size_limit']}")
        self.collection.setCurrentText(config["collection"])
        self.set_editable()

    def save_to_file(self):

        settings = {}

        settings["parent_deck"] = self.parent_deck.text()
        settings["note_type"] = self.note_type_box.text()
        settings["field_name"] = self.field_name_box.text()
        settings["strict"] = self.strict.isChecked()
        settings["select_card_1"] = self.card_1_switch.isChecked()
        settings["select_card_2"] = self.card_2_switch.isChecked()
        settings["select_card_3"] = self.card_3_switch.isChecked()
        settings["deck_size_limit"] = self.deck_limit.text()
        settings["language"] = "English"
        settings["collection"] = self.collection.currentText()

        with open(path.join(current_directory, "user_files/config.json"), "w") as file:
            json.dump(settings, file, indent=4)


    @pyqtSlot()
    def save_and_close(self):
        self.save_to_file()
        
        self.close_signal.emit()
