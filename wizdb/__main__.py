from pathlib import Path
import os
import sqlite3

from kobold_py import KoboldError
from kobold_py import op as kobold

from .db import build_db
from .item import Item, is_item_template
from .mob import Mob, is_mob_template
from .pet import Pet, is_pet_template
from .statcap import StatCap
from .state import State
from .stat_rules import UnknownStat

ROOT = Path(__file__).parent.parent

ITEMS_DB = ROOT / "items.db"
ROOT_WAD = ROOT / "Root"
TYPES = ROOT / "types.json"
LOCALE = ROOT_WAD / "Locale" / "English"
STAT_EFFECTS = ROOT_WAD / "GameEffectData" / "CanonicalStatEffects.xml"
STAT_RULES = ROOT_WAD / "GameEffectRuleData"
STAT_CAPS = ROOT_WAD / "LevelScaledData.xml"


def deserialize_files(state: State):
    items = []
    mobs = []
    pets = []
    stat_caps = []

    stat_cap_obj = state.de.deserialize_from_path(STAT_CAPS)
    for stat_cap in stat_cap_obj["m_levelScaledInfoList"]:
        stat_caps.append(StatCap(stat_cap))


    for root, dirs, files in os.walk((ROOT_WAD / "ObjectData")):
        for file in files:
            if file.endswith('.xml'):
                    path = Path(os.path.join(root, file))
                    try:
                        obj = state.de.deserialize_from_path(path)
                    except KoboldError:
                        return None

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
                        

    return items, mobs, pets, stat_caps


def main():
    state = State(ROOT_WAD, TYPES)
    items, mobs, pets, stat_caps = deserialize_files(state)

    if ITEMS_DB.exists():
        ITEMS_DB.unlink()

    db = sqlite3.connect(str(ITEMS_DB))
    build_db(state, items, mobs, pets, stat_caps, db)
    db.close()

    print(f"Success! Database written to {ITEMS_DB.absolute()}")


if __name__ == "__main__":
    main()
