from .utils import SCHOOLS, iter_lazyobject_keys

from katsuba.op import LazyObject, TypeList # type: ignore

class EquipRequirement:
    def __init__(self, id: int):
        self.id = id

    def __hash__(self) -> int:
        return self.id


class LevelRequirement(EquipRequirement):
    def __init__(self, level: int):
        super().__init__(1)
        self.level = level


class SchoolRequirement(EquipRequirement):
    def __init__(self, op_not: bool, school: bytes):
        super().__init__(2)
        self.school = SCHOOLS.index(school) | (op_not << 31)


def _is_school_req(req: LazyObject) -> bool:
    return len(req) == 3


def _is_level_req(req: LazyObject) -> bool:
    return len(req) == 5


def parse_equip_reqs(reqs: dict) -> set:
    conds = set()

    if "m_requirements" in reqs:
        for req in reqs["m_requirements"]:
            if _is_school_req(req):
                applyNOT = req["m_applyNOT"]
                conds.add(SchoolRequirement(applyNOT, req["m_magicSchool"]))

            elif _is_level_req(req):
                op = req["m_operatorType"]
                level = int(req["m_numericValue"])
                
                if op == 3: # Greater Than or EQ
                    conds.add(LevelRequirement(level))
                else:
                    raise RuntimeError("Unknown level cond!")

    return conds
