from pathlib import Path
import os
import sqlite3

from kobold_py import KoboldError
from kobold_py import op as kobold

from .db import build_db
from .item import Item, is_item_template
from .mob import Mob, is_mob_template
from .state import State
from .stat_rules import UnknownStat

ROOT = Path(__file__).parent.parent

ITEMS_DB = ROOT / "items.db"
ROOT_WAD = ROOT / "Root"
TYPES = ROOT / "types.json"
LOCALE = ROOT_WAD / "Locale" / "English"
STAT_EFFECTS = ROOT_WAD / "GameEffectData" / "CanonicalStatEffects.xml"
STAT_RULES = ROOT_WAD / "GameEffectRuleData"


def read_item_template(de: kobold.BinaryDeserializer, file: Path) -> dict:
    try:
        obj = de.deserialize_from_path(file)
    except KoboldError:
        return None

    if not is_item_template(obj):
        return None

    return obj

def read_mob_template(de: kobold.BinaryDeserializer, file: Path) -> dict:
    try:
        obj = de.deserialize_from_path(file)
    except KoboldError:
        return None

    if not is_mob_template(obj):
        return None

    return obj


def deserialize_files(state: State):
    items = []
    mobs = []
    for root, dirs, files in os.walk((ROOT_WAD / "ObjectData")):
        for file in files:
            if file.endswith('.xml'):
                path = Path(os.path.join(root, file))
                #print(path)
                try:
                    if obj := read_item_template(state.de, path):
                        item = Item(state, obj)
                        items.append(item)

                    elif obj := read_mob_template(state.de, path):
                        mob = Mob(state, obj)
                        mobs.append(mob)
                except (UnknownStat, KeyError, IndexError):
                    print(path)

    return items, mobs




def main():
    state = State(ROOT_WAD, TYPES)
    items, mobs = deserialize_files(state)

    if ITEMS_DB.exists():
        ITEMS_DB.unlink()

    db = sqlite3.connect(str(ITEMS_DB))
    build_db(state, items, mobs, db)
    db.close()

    print(f"Success! Database written to {ITEMS_DB.absolute()}")


if __name__ == "__main__":
    main()
