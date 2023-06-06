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
    return len(req) == 3 and "m_magicSchool" in req


def _is_level_req(req: dict) -> bool:
    return len(req) == 5 and "m_operatorType" in req and "m_numericValue" in req


def parse_equip_reqs(reqs: dict) -> set:
    if not reqs.get("m_operator", "ROP_AND").endswith("ROP_AND"):
        raise RuntimeError(f"No ROP_AND for {reqs}")
    if reqs.get("m_applyNOT", False):
        raise RuntimeError(f"applyNOT for {reqs}")

    conds = set()

    for req in reqs.get("m_requirements", []):
        if _is_school_req(req):
            conds.add(SchoolRequirement(req.get("m_applyNOT", False), req["m_magicSchool"]))

        elif _is_level_req(req):
            school = req["m_magicSchool"]
            op = req["m_operatorType"]
            level = int(req["m_numericValue"])
            op_not = req.get("m_applyNOT", False)

            #if school != b"":
            #    conds.add(SchoolRequirement(op_not, school))
            
            if op.endswith("GREATER_THAN_EQ"):
                conds.add(LevelRequirement(level))
            else:
                raise RuntimeError("Unknown level cond!")

    return conds
