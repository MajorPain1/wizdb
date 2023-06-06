from kobold_py import KoboldError
from struct import pack as pk
from typing import List

from .utils import SCHOOLS, SPELL_TYPES, GARDENING_TYPES, CANTRIP_TYPES, FISHING_TYPES

def find_effects(d, effects, damage_types, num_rounds):
    dictionaries_to_search = []
    for k, v in d.items():
        if not "m_effectList" in d and not "m_elements" in d and not "m_outputEffect" in d:
            match k:
                case "m_effectParam":
                    effects.append(v)
                case "m_sDamageType":
                    try:
                        damage_types.append(SCHOOLS.index(v))
                    except ValueError:
                        damage_types.append(0)

                case "m_numRounds":
                    num_rounds.append(v)

        match v:
            case dict():
                dictionaries_to_search.append(v)
            case list():
                if k == "m_elements":
                    dictionaries_to_search.append(v[0])
                else:
                    for item in v:
                        if isinstance(item, dict):
                            dictionaries_to_search.append(item)

    for dictionary in dictionaries_to_search:
        find_effects(dictionary, effects, damage_types, num_rounds)

def remove_duplicates(lst):
    seen = {}
    result = []
    
    for element in list(lst):
        if element not in seen:
            seen[element] = True
            result.append(element)
    
    return result


class Spell:
    def __init__(self, template_id: int, state, obj: dict):
        self.template = template_id
        self.name = state.make_lang_key(obj)
        if self.name.id is None:
            self.name.id = state.cache.add_entry(obj["m_name"], obj["m_name"].decode())
        self.real_name = obj["m_name"]
        self.image = obj["m_imageName"].decode()
        self.accuracy = obj["m_accuracy"]

        if "m_energyCost" in obj:
            self.energy = obj["m_energyCost"]
        else:
            self.energy = 0

        school = obj["m_sMagicSchoolName"]
        self.description = state.make_lang_key({"m_displayName": obj["m_description"]})
        if school == b"Gardening":
            self.type_name = GARDENING_TYPES.index(obj["m_gardenSpellType"])
        elif school == b"Fishing":
            self.type_name = FISHING_TYPES.index(obj["m_fishingSpellType"])
        elif school == b"Cantrips":
            self.type_name = CANTRIP_TYPES.index(obj["m_cantripsSpellType"])
        else:
            self.type_name = SPELL_TYPES.index(obj["m_sTypeName"])
        
        self.school = SCHOOLS.index(school)

        rank = obj["m_spellRank"]
        self.rank = rank["m_spellRank"]
        self.x_pips = rank["m_xPipSpell"]
        self.shadow_pips = rank["m_shadowPips"]
        
        self.fire_pips = rank["m_firePips"]
        self.ice_pips = rank["m_icePips"]
        self.storm_pips = rank["m_stormPips"]
        self.myth_pips = rank["m_mythPips"]
        self.life_pips = rank["m_lifePips"]
        self.death_pips = rank["m_deathPips"]
        self.balance_pips = rank["m_balancePips"]

        raw_effects = []
        raw_damage_types = []
        raw_num_rounds = []
        find_effects(obj, raw_effects, raw_damage_types, raw_num_rounds)

        self.effect_params= raw_effects
        self.damage_types = raw_damage_types
        self.num_rounds = raw_num_rounds




class SpellCache:
    def __init__(self, state):
        self.cache = {}
        self.name_to_id = {}

        for file, template in state.file_to_id.items():
            if not file.startswith("Spells/"):
                continue
            
            try:
                value = state.de.deserialize_from_path((state.root_wad / file))
            except KoboldError as Err:
                print(Err)
                continue

            spell = Spell(template, state, value)
            self.cache[template] = spell
            self.name_to_id[value["m_name"].decode()] = template

    def get(self, name: str) -> int:
        if tid := self.name_to_id.get(name):
            return tid
        else:
            return None
