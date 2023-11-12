# Anki imports
from aqt import mw

# Python imports
from os import path
import json

# Local path for the addon
current_directory = path.dirname(path.abspath(__file__))

def get_configurations():
    with open(path.join(current_directory, "user_files/config.json"), "r") as file:
        configurations = json.load(file)
        return configurations

# User configuration
class configurations():
    def __init__(self, func):
        self.func = func
        self.data = self.func()

    def __getattr__(self, attr):
        if attr == "__call__":
            return attr
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{attr}'")

    def __getitem__(self, key):
        self.data = self.func()

        if key == "lang":
            try:
                return language_abbreviations[self.data["language"]]
            except:
                return self.data["language"]
        else:
            return self.data[key]

config = configurations(get_configurations)

language_abbreviations = {
    'English': 'Eng',
    'Spanish': 'Spa',
    'Chinese': 'Chi',
    'Hindi': 'Hin',
    'Arabic': 'Ara',
    'Portuguese': 'Por',
    'Bengali': 'Ben',
    'Russian': 'Rus',
    'Urdu': 'Urd',
    'Indonesian': 'Ind',
    'French': 'Fra',
    'German': 'Deu',
    'Italian': 'Ita',
    'Dutch': 'Dut',
    'Castilian': 'Spa',
    'Castellano': 'Spa',
    'Turkish': 'Tur',
    'Persian': 'Per',
    'Thai': 'Tha',
    'Vietnamese': 'Vie',
    'Tamil': 'Tam',
    'Telugu': 'Tel',
    'Japanese': 'Jpn',
    'Korean': 'Kor',
    'Marathi': 'Mar',
    'Javanese': 'Jav',
    'Wu': 'Wuu',
    'Telugu': 'Tel',
    'Cantonese': 'Yue',
    'Urdu': 'Urd'
}

forbidden_characters = "()}{\\/!@#$%^&*"

def get_language():
    lang = config['language']

    try:
        language = language_abbreviations[lang]
    except:
        language = lang

    return language

class language():
    def __init__(self, func):
        self.func = func
        self.lang = self.func()

    def __getattr__(self, attr):
        if attr == "__call__":
            return attr
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{attr}'")

    
lang = language(get_language)
