from pathlib import Path
import os
import sqlite3
import sys
import time

from .db import build_db, build_deck_db
from .item import Item, is_item_template
from .mob import Mob, is_mob_template
from .pet import Pet, is_pet_template
from .fish import Fish, is_fish_template
from .deck import Deck, is_deck_template
from .statcap import StatCap
from .state import State
from .stat_rules import UnknownStat

ROOT = Path(__file__).parent.parent

ITEMS_DB = ROOT / "items.db"
DECKS_DB = ROOT / "decks.db"
ROOT_WAD = ROOT / "Root.wad"
DECK_ROOT_WAD = ROOT / "Deck_Root.wad"
TYPES = ROOT / "types.json"
DECK_TYPES = ROOT / "deck_types.json"
LOCALE = "Locale/English"
STAT_EFFECTS = "GameEffectData/CanonicalStatEffects.xml"
STAT_RULES = "GameEffectRuleData"
STAT_CAPS = "LevelScaledData.xml"
DECKS = "Decks"


def deserialize_files(state: State):
    items = []
    mobs = []
    pets = []
    fishs = []
    decks = []
    stat_caps = []

    stat_cap_obj = state.de.deserialize_from_path(STAT_CAPS)
    for stat_cap in stat_cap_obj["m_levelScaledInfoList"]:
        stat_caps.append(StatCap(stat_cap))

    for file in state.de.archive.iter_glob(f"{DECKS}/**/*.xml"):
        obj = state.de.deserialize_from_path(file)
                            
        if is_deck_template(obj):
            deck = Deck(state, obj)
            decks.append(deck)
                
    for file in state.de.archive.iter_glob("ObjectData/**/*.xml"):
        obj = state.de.deserialize_from_path(file)

        try:
            if is_item_template(obj):
                item = Item(state, obj)
                items.append(item)
        except (UnknownStat, KeyError, IndexError):
            pass

        if is_mob_template(obj):
            mob = Mob(state, obj)
            mobs.append(mob)

        if is_pet_template(obj):
            pet = Pet(state, obj)
            pets.append(pet)
            
        if is_fish_template(obj):
            fish = Fish(state, obj)
            fishs.append(fish)
        
        if is_deck_template(obj):
            deck = Deck(state, obj)
            decks.append(deck)

    return items, mobs, pets, fishs, decks, stat_caps


def deserialize_decks(state: State):
    decks = []
    
    for file in state.de.archive.iter_glob(f"{DECKS}/**/*.xml"):
        obj = state.de.deserialize_from_path(file)
                            
        if is_deck_template(obj):
            deck = Deck(state, obj)
            decks.append(deck)
    
    return decks

def main():
    start = time.time()
    deck_db = False
    if "-d" in sys.argv:
        deck_db = True
        
    if deck_db:
        state = State(DECK_ROOT_WAD, DECK_TYPES)
        decks = deserialize_decks(state)
        
        if DECKS_DB.exists():
            DECKS_DB.unlink()
        
        db = sqlite3.connect(str(DECKS_DB))
        build_deck_db(decks, db)
        db.close()
    
    else:
        state = State(ROOT_WAD, TYPES)
        items, mobs, pets, fish, decks, stat_caps = deserialize_files(state)

        if ITEMS_DB.exists():
            ITEMS_DB.unlink()

        db = sqlite3.connect(str(ITEMS_DB))
        build_db(state, items, mobs, pets, fish, decks, stat_caps, db)
        db.close()

    print(f"Success! Database written to {ITEMS_DB.absolute()} in {round(time.time() - start, 2)} seconds")


if __name__ == "__main__":
    main()
