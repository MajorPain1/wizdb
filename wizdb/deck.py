from .state import State
from .utils import SCHOOLS

def is_deck_template(obj) -> bool:
    try:
        name = obj["m_name"]
        spellNameList = obj["m_spellNameList"]
    except KeyError:
        return False
    
    return name and spellNameList


class Deck:
    def __init__(self, state: State, obj: dict):
        self.name = obj["m_name"]
        spellNameList = obj["m_spellNameList"]
        
        spell_dict = {}
        for spell in spellNameList:
            if spell in spell_dict.keys():
                spell_dict[spell] += 1
            else:
                spell_dict[spell] = 1
                
        self.spells = spell_dict

    def __repr__(self):
        return repr(self.spells)
