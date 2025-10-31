import os
from itertools import repeat

from .jewels import JewelSockets
from .requirements import parse_equip_reqs
from .state import State
from .stat_rules import MultiPassengerStat
from .utils import convert_rarity, SCHOOLS
from .spell import SpellCache

ADJECTIVES = (
    b"FLAG_NoAuction",
    b"FLAG_CrownsOnly",
    b"FLAG_NoGift",
    b"FLAG_InstantEffect",
    b"FLAG_NoCombat",
    b"FLAG_NoDrops",
    b"FLAG_NoDye",
    b"FLAG_NoHatchmaking",
    b"FLAG_NoPVP",
    b"FLAG_NoSell",
    b"FLAG_NoShatter",
    b"FLAG_NoTrade",
    b"FLAG_PVPOnly",
    b"FLAG_ArenaPointsOnly",
    b"FLAG_BlueArenaPointsOnly"
)

def make_string_id(string: str) -> int:
        """
        Credit: PeechezNCreem
        Feed this function a talent to get a hash value which can then be used to get talent order
        Ex: make_string_id("Talent-Accuracy-All01")
        """
        result = 0
        def sign_extend(value: int) -> int:
            return (value & 0x7FFFFFFF) - (value & 0x80000000)
        
        for index, value in enumerate(string):
            value -= 32
            shift = 5 * index % 32

            result ^= sign_extend(value << shift)
            if shift > 24:
                result ^= sign_extend(value >> (32 - shift))

        return abs(result) & 0xFFFFFFFF


def is_pet_template(obj: dict) -> bool:
    try:
        adjectives = obj["m_adjectiveList"]
        name = obj["m_displayName"]
    except KeyError:
        return False

    behaviors = obj["m_behaviors"]
    has_pet_behaviors = False
    has_20_talents = False
    for behavior in behaviors:
        if behavior == None:
            continue

        if behavior["m_behaviorName"] == b'PetItemBehavior':
            has_pet_behaviors = True

        if "m_talents" in behavior and len(behavior["m_talents"]) + len(behavior["m_derbyTalents"]) == 20:
            has_20_talents = True

    return b"Pet" in adjectives and has_pet_behaviors and name and has_20_talents


def translate_talents(state: State, talents: list):

    formatted_talents = []
    for talent in talents:
        talent_name: str = talent.decode().replace("Talent-ArmorPiercing-01", "Talent-ArmorPiercing-All01").replace("Talent-ArmorPiercing-02", "Talent-ArmorPiercing-All02")
        path = f"TalentData/{talent_name}.xml"
        if not path in state.de.archive:
            path = f"TalentData/PetPowers/{talent.decode()}.xml"

        obj = state.de.deserialize_from_path(path)
        name = state.make_lang_key(obj)

        formatted_talents.append((make_string_id(talent), name))

        

    return formatted_talents




class Pet:
    def __init__(self, state: State, obj: dict):
        self.template_id = obj["m_templateID"]
        self.name = state.make_lang_key(obj)
        self.school = SCHOOLS.index(obj["m_school"])
        
        if self.name.id is None:
            self.name.id = state.cache.add_entry(obj["m_objectName"], obj["m_objectName"].decode())
        self.real_name = obj["m_objectName"]
        self.set_bonus_id = state.add_set_bonus(obj["m_itemSetBonusTemplateID"])
        self.rarity = obj["m_rarity"]

        adj = obj["m_adjectiveList"]
        self.adjectives = 0
        for idx, entry in enumerate(ADJECTIVES):
            if entry in adj:
                self.adjectives |= (1 << (16 + idx))

        self.strength = 0
        self.intellect = 0
        self.agility = 0
        self.will = 0
        self.power = 0
        raw_derby = []
        raw_talents = []
        self.wow_factor = 0
        self.cards = []
        self.exclusive = 0
        self.egg_name = None
        for behavior in obj["m_behaviors"]:
            
            name = behavior["m_behaviorName"]

            if name == b"PetItemBehavior":
                for stat in behavior["m_maxStats"]:
                    match stat["m_name"]:
                        case b"Strength":
                            self.strength = stat["m_value"]
                        case b"Intellect":
                            self.intellect = stat["m_value"]
                        case b"Agility":
                            self.agility = stat["m_value"]
                        case b"Will":
                            self.will = stat["m_value"]
                        case b"Power":
                            self.power = stat["m_value"]

                for level in behavior["m_Levels"]:
                    if level["m_level"] == 7:
                        num_cards = level["m_powerCardCount"]
                        if num_cards != 0:
                            self.cards.append(level["m_powerCardName"])

                            if level["m_powerCardName2"] != b'':
                                self.cards.append(level["m_powerCardName2"])
                            if level["m_powerCardName3"] != b'':
                                self.cards.append(level["m_powerCardName3"])
                        
                        if num_cards > 0:
                            self.cards = [x for item in self.cards for x in repeat(item, num_cards)]

                
                raw_derby = behavior["m_derbyTalents"]
                raw_talents = behavior["m_talents"]
                self.wow_factor = int(behavior["m_wowFactor"])
                self.exclusive = int(behavior["m_exclusivePet"])
                self.egg_name = state.cache.find_entry(behavior["m_eggName"])

        self.talents = translate_talents(state, raw_talents)
        self.derby = translate_talents(state, raw_derby)

                


    def __repr__(self):
        return ", ".join([repr(s) for s in self.talents])
