from pathlib import Path

from .lang_files import LangCache, LangKey
from .set_bonus import SetBonusCache
from .spell import SpellCache
from .stat_rules import StatRules
from .talent import TalentCache
from .deserializer import BinDeserializer

class State:
    def __init__(self, root_wad: Path, types: Path):
        self.root_wad = root_wad
        self.de = BinDeserializer(root_wad, types)
        self.cache = LangCache(self.de, "Locale/en-US")
        self.stat_rules = StatRules(
            self.de,
            "GameEffectData/CanonicalStatEffects.xml",
            "GameEffectRuleData"
        )
        self.bonuses = SetBonusCache()

        self.file_to_id = {}
        self.id_to_file = {}

        manifest = self.de.deserialize_from_path("TemplateManifest.xml")
        for entry in manifest["m_serializedTemplates"]:
            filename = entry["m_filename"].decode()
            tid = entry["m_id"]

            self.file_to_id[filename] = tid
            self.id_to_file[tid] = filename

        self.spells = SpellCache(self)
        self.talents = TalentCache(self)

    def add_spell(self, name: str) -> int:
        return self.spells.get(name)

    def translate_stat(self, obj: dict):
        return self.stat_rules.translate(self, obj)

    def add_set_bonus(self, template: int) -> int:
        return self.bonuses.add(self, template)

    def make_lang_key(self, obj: dict) -> LangKey:
        return LangKey(self.cache, obj)
    
    def get_lang_str(self, langkey: LangKey) -> str:
        return self.cache.lookup.get(langkey.id)
