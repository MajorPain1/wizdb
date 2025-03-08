from .utils import SCHOOLS


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


def _is_school_req(req: dict) -> bool:
    return len(req) == 4 and "m_magicSchool" in req


def _is_level_req(req: dict) -> bool:
    return len(req) == 6 and "m_operatorType" in req and "m_numericValue" in req


def parse_equip_reqs(reqs: dict) -> set:
    #if "m_operator" not in reqs or reqs["m_operator"] != 0:
        #raise RuntimeError(f"No ROP_AND for {reqs}")
    #if "m_applyNOT" in reqs and reqs["m_applyNOT"]:
        #raise RuntimeError(f"applyNOT for {reqs}")

    conds = set()

    if "m_requirements" in reqs:
        for req in reqs["m_requirements"]:
            if _is_school_req(req):
                applyNOT = req["m_applyNOT"]
                conds.add(SchoolRequirement(applyNOT, req["m_magicSchool"]))

            elif _is_level_req(req):
                school = req["m_magicSchool"]
                op = req["m_operatorType"]
                level = int(req["m_numericValue"])
                op_not = req.get("m_applyNOT", False)

                #if school != b"":
                #    conds.add(SchoolRequirement(op_not, school))
                
                if op == 3: # Greater Than or EQ
                    conds.add(LevelRequirement(level))
                else:
                    raise RuntimeError("Unknown level cond!")

    return conds
