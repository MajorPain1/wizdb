from enum import Enum
from typing import Iterator

from katsuba.op import * # type: ignore

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

DISPOSITION = [
    "enum SpellEffect::kHangingDisposition::kBoth",
    "enum SpellEffect::kHangingDisposition::kBeneficial",
    "enum SpellEffect::kHangingDisposition::kHarmful",
]

def op_to_dict(type_list: TypeList, v):
    if isinstance(v, LazyObject):
        lazy_dict = {k: op_to_dict(type_list, e) for k, e in v.items(type_list)}
        lazy_dict["$__type"] = type_list.name_for(v.type_hash)
        return lazy_dict
    
    elif isinstance(v, LazyList):
        return [op_to_dict(type_list, e) for e in v]
    
    elif isinstance(v, Vec3):
        return f"(x={v.x}, y={v.y}, z={v.z})"
    
    elif isinstance(v, Quaternion):
        return f"(z={v.x}, y={v.y=}, z={v.z}, w={v.w})"
    
    elif isinstance(v, Matrix):
        return f"[{v.i}, {v.j}, {v.k}]"
    
    elif isinstance(v, Euler):
        return f"(pitch={v.pitch}, yaw={v.yaw}, roll={v.roll})"
    
    elif isinstance(v, PointInt) or isinstance(v, PointFloat):
        return f"(x={v.x}, y={v.y})"
    
    elif isinstance(v, SizeInt):
        return f"({v.width}, {v.height})"
    
    elif isinstance(v, RectInt) or isinstance(v, RectFloat):
        return f"(left={v.left}, top={v.top}, right={v.right}, bottom={v.bottom})"
    
    elif isinstance(v, Color):
        return f"(r={v.r}, g={v.g}, b={v.b}, a={v.a})"
    
    return v

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

def iter_lazyobject_keys(types: TypeList, obj: LazyObject):
    iterd_lazyobject = []
    for item in obj.items(types):
        iterd_lazyobject.append(item[0])
    
    return iterd_lazyobject

