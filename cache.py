
from aqt.utils import showInfo
from aqt.qt import *
from aqt.operations import QueryOp
from aqt import gui_hooks

class Cache:
    def __init__(self):
        gui_hooks.main_window_did_init.append(self.run)

    def backgroundCache(self, dummy):
        if not self.config['note_type']:
            showInfo("Note type cannot be empty while caching.<br><br>Add a note type to the configuration file.")
        else:
            self.createCache()

    def run(self):
        self.config = mw.addonManager.getConfig(__name__)
        self.cache = self.config["cache"]
        self.col = mw.col

        if self.cache:
            cache_op = QueryOp(parent=mw, op=lambda dummy: self.backgroundCache(dummy), success = lambda dummy: self.success(dummy))
            cache_op.run_in_background()

    def createCache(self):

        notes = self.col.findNotes(f"\"note:{self.config['note_type']}\"")

        vocab_dict = {}

        for noteid in notes:
            note = self.col.getNote(noteid)
            greek_vocab = note[self.config["field_name"]].encode('utf-8').decode('utf-8')
            vocab_dict[greek_vocab] = noteid

        with open(Path.join(Path.dirname(Path.abspath(__file__)), "cache.json"), "w+", encoding='utf-8') as cache_file:
            json.dump(vocab_dict, cache_file, indent=4, ensure_ascii=False)

        del notes
        del vocab_dict

    def success(self, dummy) -> None:
        error_log("Greek Vocab Cached #1")