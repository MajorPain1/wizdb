from .state import State
from .utils import SCHOOLS


def is_mob_template(obj: dict) -> bool:
    try:
        name = obj["m_displayName"]
        aggro_sound = obj["m_aggroSound"]
    except KeyError:
        return False

    behaviors = obj["m_behaviors"]
    has_duel = False
    for behavior in behaviors:
        if behavior == None:
            continue

        if behavior["m_behaviorName"] == b'DuelistBehavior':
            has_duel = True


    return has_duel and name


mob_titles = {0: "Easy", 1: "Normal", 2: "Elite", 3: "Boss", 4: "Minion"}

MONSTROLOGY_EXTRACTS = [
    b"Undead",          # No Prefix
    b"Gobbler",         # No Prefix
    b"MONST_Manders",
    b"MONST_Spiders",
    b"MONST_Colossus",
    b"MONST_Cyclops",
    b"MONST_Golems",
    b"MONST_Draconians",
    b"Treant",          # No Prefix
    b"MONST_Imps",
    b"Pig",             # No Prefix
    b"MONST_Elephant",  # Not Plural like the rest
    b"Wyrm",            # No Prefix
    b"MONST_Dinos",
    b"MONST_Birds",     # Extract Parrot
    b"MONST_Insects",
    b"PolarBear",       # No Prefix
]

class Mob:
    def __init__(self, state: State, obj: dict):
        self.template_id = obj["m_templateID"]
        self.name = state.make_lang_key(obj)
        self.real_name = obj["m_objectName"]
        self.image = obj["m_sIcon"].split(b"/")[-1]
        adj = obj["m_adjectiveList"]


        self.adjectives = 0
        for idx, entry in enumerate(MONSTROLOGY_EXTRACTS):
            if entry in adj:
                self.adjectives |= (1 << idx)

        behaviors = obj["m_behaviors"]
        effect_behavior = None
        equipment_behavior = None
        mobdeckbehavior = None
        for behavior in behaviors:
            if behavior == None:
                continue
            
            match behavior["m_behaviorName"]:
                case b'NPCBehavior':
                    effect_behavior = behavior

                case b'WizardEquipmentBehavior':
                    equipment_behavior = behavior
                
                case b"MobDeckBehavior":
                    mobdeckbehavior = behavior

        self.title = mob_titles[effect_behavior["m_mobTitle"]]
        self.stunnable = effect_behavior["m_bossMob"]
        self.intelligence = round(effect_behavior["m_fIntelligence"], 5)
        self.selfishFactor = round(effect_behavior["m_fSelfishFactor"], 5)
        self.aggressiveFactor = effect_behavior["m_nAggressiveFactor"]
        self.rank = effect_behavior["m_nLevel"]
        self.hitpoints = effect_behavior["m_nStartingHealth"]
        self.primarySchool = SCHOOLS.index(effect_behavior["m_schoolOfFocus"])
        self.secondarySchool = SCHOOLS.index(effect_behavior["m_secondarySchoolOfFocus"])

        self.max_shadow = effect_behavior["m_maxShadowPips"]
        self.has_cheats = effect_behavior["m_triggerList"] != b''

        self.items = equipment_behavior["m_itemList"]
        
        spell_list = mobdeckbehavior["m_spellList"]
        spell_dict = {}
        for spell in spell_list:
            if spell in spell_dict.keys():
                spell_dict[spell] += 1
            else:
                spell_dict[spell] = 1
                
        self.spells = spell_dict

        self.stats = []
        for effect in effect_behavior["m_baseEffects"]:
            if stat := state.translate_stat(effect):
                self.stats.append(stat)


    def __repr__(self):
        return ", ".join([repr(s) for s in self.stats])
