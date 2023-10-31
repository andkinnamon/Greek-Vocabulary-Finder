from aqt import mw
from aqt.utils import showInfo, tooltip
from aqt.qt import *
from aqt.operations import QueryOp
from aqt import gui_hooks

class Cache:
    def __init__(self):
        gui_hooks.main_window_did_init.append(self.run)

    def backgroundCache(self, dummy):
        if not self.config['note_type']:
            showInfo("Note type cannot be empty while caching.<br><br>Go to Tools->Addons->Greek Vocab Finder->Configure<br>Add a note type or set 'cache' to False.")
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

        query = f"\"note:{self.config['note_type']}\""

        notes = self.col.findNotes(query)
        cards = self.col.findCards(query)

        vocab_dict = {}
        
        tooltip("Creating Greek vocab cache")

        for noteid in notes:
            note = self.col.getNote(noteid)
            greek_vocab = note[self.config["field_name"]].encode('utf-8').decode('utf-8')
            vocab_dict[greek_vocab] = {}
            vocab_dict[greek_vocab]["noteid"] = noteid
            vocab_dict[greek_vocab]["cardid"] = []

            showInfo("Note IDs cached")

        for cardid in cards:
            card = self.col.getCard(cardid)
            greek_vocab = card[self.config["field_name"]].encode('utf-8').decode('utf-8')
            vocab_dict[greek_vocab]["cardid"].append(cardid)

            showInfo("Card IDs cached")

        with open(Path.join(Path.dirname(Path.abspath(__file__)), "cache.json"), "w+", encoding='utf-8') as cache_file:
            json.dump(vocab_dict, cache_file, indent=4, ensure_ascii=False)

        del notes
        del cards
        del vocab_dict

    def success(self, dummy) -> None:
        tooltip("Greek vocab cached")