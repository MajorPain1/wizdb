SCHOOLS = [
    b"",
    b"All",
    b"Fire",
    b"Ice",
    b"Storm",
    b"Myth",
    b"Life",
    b"Death",
    b"Balance",
    b"Star",
    b"Sun",
    b"Moon",
    b"Gardening",
    b"Shadow",
    b"Fishing",
    b"Cantrips",
    b"CastleMagic",
    b"WhirlyBurly",
]


SPELL_TYPES = [
    b"",
    b"Heal",
    b"Damage",
    b"Charm",
    b"Ward",
    b"Aura",
    b"Global",
    b"AOE",
    b"Steal",
    b"Manipulation",
    b"Enchantment",
    b"Polymorph",
    b"Curse",
    b"Jinx",
    b"Mutate",
    b"Cloak",
    b"Shadow",
    b"Shadow_Creature",
    b"Shadow_Self",
    b"AuraNegative"
]

GARDENING_TYPES = [
    "enum GardenSpellTemplate::GardenSpellType::GS_Growing",
    "enum GardenSpellTemplate::GardenSpellType::GS_InsectFighting",
    "enum GardenSpellTemplate::GardenSpellType::GS_SoilPreparation",
    "enum GardenSpellTemplate::GardenSpellType::GS_PlantUtility",
    "enum GardenSpellTemplate::GardenSpellType::GS_PlantProtection",
]

FISHING_TYPES = [
    "enum FishingSpellTemplate::FishingSpellType::FS_Catching",
    "enum FishingSpellTemplate::FishingSpellType::FS_Utility",
]

CANTRIP_TYPES = [
    "enum CantripsSpellTemplate::CantripsSpellType::CS_Incantation",
    "enum CantripsSpellTemplate::CantripsSpellType::CS_Beneficial",
    "enum CantripsSpellTemplate::CantripsSpellType::CS_Sigil",
    "enum CantripsSpellTemplate::CantripsSpellType::CS_Teleportation",
    "enum CantripsSpellTemplate::CantripsSpellType::CS_Ritual",
]



def convert_rarity(obj: dict) -> int:
    rarity = obj.get("m_rarity", "r::RT_UNKNOWN").split("::")[1]
    if rarity == "RT_COMMON":
        return 0
    elif rarity == "RT_UNCOMMON":
        return 1
    elif rarity == "RT_RARE":
        return 2
    elif rarity == "RT_ULTRARARE":
        return 3
    elif rarity == "RT_EPIC":
        return 4
    else:
        return -1


def fnv_1a(data) -> int:
    if isinstance(data, str):
        data = data.encode()

    state = 0xCBF2_9CE4_8422_2325
    for b in data:
        state ^= b
        state *= 0x0000_0100_0000_01B3
        state &= 0xFFFF_FFFF_FFFF_FFFF
    return state >> 1
