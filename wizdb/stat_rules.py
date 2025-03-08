from pathlib import Path
from struct import pack as pk

from katsuba.op import * # type: ignore

from .utils import fnv_1a
from .deserializer import BinDeserializer

class UnknownStat(Exception):
    pass

def _bitpack_float(value: float) -> int:
    encoded = pk("<f", value)
    return int.from_bytes(encoded, "little")

class Stat:
    def __init__(self, kind: int):
        self.kind = kind


class StatStat(Stat):
    def __init__(self, category: str, value: int):
        super().__init__(1)

        self.category = fnv_1a(category)
        self.value = value

    def __repr__(self):
        return f"{self.category}={self.value}"


class PipStat(Stat):
    def __init__(self, pips: int, power_pips: int):
        super().__init__(2)

        self.pips = pips
        self.power_pips = power_pips

    @classmethod
    def extract(cls, obj: dict):
        return cls(obj["m_pipsGiven"], obj["m_powerPipsGiven"])


class SpellStat(Stat):
    def __init__(self, state, spell: int, count: int):
        super().__init__(3)

        self.spell = spell
        self.count = count

    @classmethod
    def extract(cls, state, obj: dict):
        if spell := state.add_spell(obj["m_spellName"].decode()):
            return cls(state, spell, obj["m_numSpells"])
        else:
            return None


class MayCastStat(Stat):
    def __init__(self, state, spell: int, desc: bytes):
        super().__init__(4)

        self.spell = spell
        self.desc_key = state.make_lang_key({"m_displayName": desc})

    @classmethod
    def extract(cls, state, obj: dict):
        trigger_desc = obj["m_triggerDescription"]
        if trigger_desc is None:
            return None

        if spell := state.add_spell(trigger_desc["m_displaySpellName"].decode()):
            return cls(state, spell, trigger_desc["m_description"])
        else:
            return None


class SpeedStat(Stat):
    def __init__(self, multiplier: int):
        super().__init__(5)

        self.multiplier = multiplier

    @classmethod
    def extract(cls, obj: dict):
        return cls(obj["m_speedMultiplier"])


class MultiPassengerStat(Stat):
    def __init__(self, count: int):
        super().__init__(6)

        self.count = count

    @classmethod
    def extract(cls, obj: dict):
        return cls(obj["m_numSeats"])


class StatRules:
    def __init__(self, de: BinDeserializer, canonical: Path, rule_dir: Path):
        self.tables = {}

        for file in de.archive.iter_glob(f"{rule_dir}/*.xml"):
            obj = de.deserialize_from_path(file)
            self.tables[obj["m_tableName"].decode()] = obj

        self.canonical_effects = de.deserialize_from_path(canonical)

    def _translate_stat(self, name: str, idx: int) -> Stat:
        for template in self.canonical_effects["m_effectTemplates"]:
            if template["m_effectName"].decode() == name:
                category = template["m_effectCategory"].decode()
                table = template["m_statTableName"].decode()
                flat = "Flat" in name

                if table == '':
                    value = 1.0

                else:
                    
                    #if template.has_key("m_primaryStat1"):

                    #else:
                        table = self.tables[table]
                        value = table["m_statVector"][idx]

                if any(i in category for i in ("Damage", "Piercing", "Accuracy", "PowerPips", "Healing", "ReduceDamage", "StunResistance", "FishingLuck")) and not flat:
                    value *= 100
    
                return StatStat(name, round(value))

        raise UnknownStat

    def translate(self, state, obj: dict) -> Stat:
        name = obj["m_effectName"].decode()

        if name == "StartingPips":
            return PipStat.extract(obj)
        elif name == "ProvideSpell":
            return SpellStat.extract(state, obj)
        elif name == "ProvideCombatTrigger":
            return MayCastStat.extract(state, obj)
        elif name == "SpeedBuff":
            return SpeedStat.extract(obj)
        elif name in ("ShieldBuff", "Transformation", "BlackhawkFireJewelEffect01", "BlackhawkIceJewelEffect01", "BlackhawkStormJewelEffect01", "BlackhawkBalanceJewelEffect01", "BlackhawkDeathJewelEffect01", "BlackhawkLifeJewelEffect01", "BlackhawkMythJewelEffect01", "BlackhawkAllSchoolsJewelEffect01", "MorganthJewelEffect", "MeaninglessDOT", "HitpointBuff", "TwentyPercentPowerPips", "SixtyPercentPowerPips", "ProvideFourFireElves", "ProvideNineWandFire1", "ProvideNineWandIce1", "ProvideNineWandStorm1", "ProvideNineWandMyth1", "PostCombatEffect", "PostCombatEffect2", "ProvideSpell", "Invisible", "NonPersistentInvisible", "NonPersistentInvisibleToAll", "StartingPips", "CombatSpeed", "RecallHome", "CantGoHome", "CantTransfer", "RideState", "CantPlayPVP"):
            # TODO: Chances are we may actually need to handle some of this.
            return None
        else:
            return self._translate_stat(name, obj["m_lookupIndex"])
