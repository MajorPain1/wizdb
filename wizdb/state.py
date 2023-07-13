from pathlib import Path

from kobold_py import op as kobold

from .lang_files import LangCache, LangKey
from .set_bonus import SetBonusCache
from .spell import SpellCache
from .stat_rules import StatRules
from .talent import TalentCache


class BinDeserializer(kobold.BinaryDeserializer):
    @staticmethod
    def make(types_path: Path):
        opts = kobold.DeserializerOptions()
        opts.flags = 1
        opts.shallow = False
        opts.skip_unknown_types = True

        types = kobold.TypeList(types_path.read_text())

        return BinDeserializer(opts, types)


    def deserialize(self, data):
        if data.startswith(b"BINd"):
            data = data[4:]

        return super().deserialize(data)


class State:
    def __init__(self, root_wad: Path, types: Path):
        self.root_wad = root_wad
        self.de = BinDeserializer.make(types)
        self.cache = LangCache(root_wad / "Locale" / "English")
        self.stat_rules = StatRules(
            self.de,
            root_wad / "GameEffectData" / "CanonicalStatEffects.xml",
            root_wad / "GameEffectRuleData"
        )
        self.bonuses = SetBonusCache()

        self.file_to_id = {}
        self.id_to_file = {}

        manifest = self.de.deserialize((root_wad / "TemplateManifest.xml").read_bytes())
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
