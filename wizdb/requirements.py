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
        
        
class SecondarySchoolRequirement(EquipRequirement):
    def __init__(self, op_not: bool, school: bytes):
        super().__init__(3)
        self.school = SCHOOLS.index(school) | (op_not << 31)


def parse_equip_reqs(reqs: dict, types: TypeList) -> set:
    conds = set()

    if "m_requirements" in reqs:
        for req in reqs["m_requirements"]:
            req_class = types.name_for(req.type_hash)
            if req_class == "class ReqSchoolOfFocus":
                applyNOT = req["m_applyNOT"]
                conds.add(SchoolRequirement(applyNOT, req["m_magicSchool"]))
            
            elif req_class == "class ReqHasSecondarySchool":
                applyNOT = req["m_applyNOT"]
                conds.add(SecondarySchoolRequirement(applyNOT, req["m_secondarySchool"]))

            elif req_class == "class ReqMagicLevel":
                op = req["m_operatorType"]
                level = int(req["m_numericValue"])
                
                if op == 3: # Greater Than or EQ
                    conds.add(LevelRequirement(level))
                else:
                    raise RuntimeError("Unknown level cond!")

    return conds
