from .jewels import JewelSockets
from .requirements import parse_equip_reqs
from .state import State
from .stat_rules import MultiPassengerStat
from .utils import convert_rarity, SCHOOLS

ITEM_ADJECTIVES = (b"Hat", b"Robe", b"Shoes", b"Weapon", b"Athame", b"Amulet", b"Ring", b"Deck", b"Jewel", b"Mount")
META_ADJECTIVES = (
    b"PetJewel",
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


def is_item_template(obj: dict) -> bool:
    name = obj.get("m_displayName", b"")
    adjectives = obj.get("m_adjectiveList", [])

    return not name.startswith(b"ItemTestStrings") and obj.get("m_itemSetBonusTemplateID") is not None and any(a in adjectives for a in ITEM_ADJECTIVES)



class Item:
    def __init__(self, state: State, obj: dict):
        self.template_id = obj["m_templateID"]
        self.name = state.make_lang_key(obj)
        if self.name.id is None:
            self.name.id = state.cache.add_entry(obj["m_objectName"], obj["m_objectName"].decode())
        self.real_name = obj["m_objectName"]
        self.set_bonus_id = state.add_set_bonus(obj["m_itemSetBonusTemplateID"])
        self.rarity = convert_rarity(obj)

        reqs = obj["m_equipRequirements"] or {}
        self.equip_reqs = parse_equip_reqs(reqs)

        self.jewel_sockets = JewelSockets()

        adj = obj["m_adjectiveList"]
        self.adjectives = 0
        for idx, entry in enumerate(ITEM_ADJECTIVES):
            if entry in adj:
                self.adjectives |= (1 << idx)

        for idx, entry in enumerate(META_ADJECTIVES):
            if entry in adj:
                self.adjectives |= (1 << (16 + idx))

        self.min_pet_level = 0
        self.pet_talents = []

        self.max_spells = 0
        self.max_copies = 0
        self.max_school_copies = 0
        self.deck_school = 0
        self.max_tcs = 0
        self.archmastery_points = 0.

        self.stats = []

        for behavior in obj["m_behaviors"]:
            if behavior == None:
                continue
            
            name = behavior["m_behaviorName"]

            if name == b"JewelSocketBehavior":
                for idx, socket in enumerate(behavior["m_jewelSockets"]):
                    self.jewel_sockets.add_socket(idx, socket)

            elif name == b"PetJewelBehavior":
                self.min_pet_level = behavior["m_minPetLevel"]
                self.pet_talents = [state.talents.get(t.decode()) for t in behavior["m_petTalentName"]]

            elif name == b"BasicDeckBehavior":
                self.max_spells = behavior["m_maxSpells"]
                self.max_copies = behavior["m_genericMaxInstances"]
                self.max_school_copies = behavior["m_schoolMaxInstances"]
                self.deck_school = SCHOOLS.index(behavior["m_primarySchoolName"].replace(b"None", b"").replace(b"All", b"").replace(b"Generic", b""))
                self.max_tcs = behavior["m_maxTreasureCards"]
                self.archmastery_points = behavior["m_maxArchmasteryPoints"]

            elif name == b"MountItemBehavior":
                self.stats.append(MultiPassengerStat.extract(behavior))



        for effect in obj["m_equipEffects"]:
            if stat := state.translate_stat(effect):
                self.stats.append(stat)

    def __repr__(self):
        return ", ".join([repr(s) for s in self.stats])
