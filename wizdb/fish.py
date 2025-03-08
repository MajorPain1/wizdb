from .state import State
from .utils import SCHOOLS


def is_fish_template(obj: dict) -> bool:
    try:
        name = obj["m_displayName"]
    except KeyError:
        return False

    behaviors = obj["m_behaviors"]
    has_fish_behaviors = False
    for behavior in behaviors:
        if behavior == None:
            continue

        if behavior["m_behaviorName"] == b'FishBehavior':
            has_fish_behaviors = True


    return has_fish_behaviors

class Fish:
    def __init__(self, state: State, obj: dict):
        self.template_id = obj["m_templateID"]
        self.name = state.make_lang_key(obj)
        
        if self.name.id is None:
            self.name.id = state.cache.add_entry(obj["m_objectName"], obj["m_objectName"].decode())
        self.real_name = obj["m_objectName"]
        
        behaviors = obj["m_behaviors"]
        fish_behavior = None
        for behavior in behaviors:
            if behavior == None:
                continue
            
            match behavior["m_behaviorName"]:
                case b'FishBehavior':
                    fish_behavior = behavior
        
        self.school = SCHOOLS.index(fish_behavior["m_schoolName"])
        self.rank = fish_behavior["m_rank"]
        self.base_length = round(fish_behavior["m_baseLength"], 3)
        self.min_size = round(fish_behavior["m_minimumSize"], 3)
        self.max_size = round(fish_behavior["m_maximumSize"], 3)
        self.speed = round(fish_behavior["m_speed"], 3)
        self.bite_seconds = round(fish_behavior["m_biteSeconds"], 3)
        self.initial_bite_chance = round(fish_behavior["m_initialBiteChance"], 3)
        self.incremental_bite_chance = round(fish_behavior["m_incrementalBiteChance"], 3)
        self.is_sentinel = fish_behavior["m_isPredator"]


    def __repr__(self):
        return ", ".join([repr(s) for s in self.talents])
