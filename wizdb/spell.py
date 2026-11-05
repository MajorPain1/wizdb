from enum import Enum
from struct import pack as pk
from typing import List

from katsuba.utils import string_id # type: ignore
from katsuba.op import * # type: ignore

from .utils import SCHOOLS, SPELL_TYPES, GARDENING_TYPES, CANTRIP_TYPES, FISHING_TYPES, DISPOSITION, op_to_dict

class SpellEffects(Enum):
    invalid_spell_effect = 0
    damage = 1
    damage_no_crit = 2
    heal = 3
    heal_percent = 4
    steal_health = 5
    reduce_over_time = 6
    detonate_over_time = 7
    push_charm = 8
    steal_charm = 9
    push_ward = 10
    steal_ward = 11
    push_over_time = 12
    steal_over_time = 13
    remove_charm = 14
    remove_ward = 15
    remove_over_time = 16
    remove_aura = 17
    swap_all = 18
    swap_charm = 19
    swap_ward = 20
    swap_over_time = 21
    minion_rank_damage = 22
    modify_incoming_damage = 23
    maximum_incoming_damage = 24
    modify_incoming_heal = 25
    modify_incoming_damage_type = 26
    modify_incoming_armor_piercing = 27
    modify_outgoing_damage = 28
    modify_outgoing_heal = 29
    modify_outgoing_damage_type = 30
    modify_outgoing_armor_piercing = 31
    modify_outgoing_steal_health = 32
    modify_incoming_steal_health = 33
    bounce_next = 34
    bounce_previous = 35
    bounce_back = 36
    bounce_all = 37
    absorb_damage = 38
    absorb_heal = 39
    modify_accuracy = 40
    dispel = 41
    confusion = 42
    cloaked_charm = 43
    cloaked_ward = 44
    stun_resist = 45
    pip_conversion = 46
    crit_boost = 47
    crit_block = 48
    polymorph = 49
    delay_cast = 50
    modify_card_cloak = 51
    modify_card_damage = 52
    modify_card_heal = 53
    modify_card_accuracy = 54
    modify_card_mutation = 55
    modify_card_rank = 56
    modify_card_armor_piercing = 57
    modify_card_charm = 58
    modify_card_ward = 59
    modify_card_outgoing_damage = 60
    modify_card_outgoing_accuracy = 61
    modify_card_outgoing_heal = 62
    modify_card_outgoing_armor_piercing = 63
    modify_card_incoming_damage = 64
    modify_card_absorb_damage = 65
    summon_creature = 66
    teleport_player = 67
    stun = 68
    dampen = 69
    reshuffle = 70
    mind_control = 71
    modify_pips = 72
    modify_power_pips = 73
    modify_shadow_pips = 74
    modify_hate = 75
    damage_over_time = 76
    heal_over_time = 77
    modify_power_pip_chance = 78
    modify_rank = 79
    stun_block = 80
    reveal_cloak = 81
    instant_kill = 82
    after_life = 83
    deferred_damage = 84
    damage_per_total_pip_power = 85
    cloaked_ward_no_remove = 87
    add_combat_trigger_list = 88
    remove_combat_trigger_list = 89
    backlash_damage = 90
    modify_backlash = 91
    intercept = 92
    shadow_self = 93
    shadow_creature = 94
    modify_shadow_creature_level = 95
    select_shadow_creature_attack_target = 96
    shadow_decrement_turn = 97
    crit_boost_school_specific = 98
    spawn_creature = 99
    un_polymorph = 100
    power_pip_conversion = 101
    protect_card_beneficial = 102
    protect_card_harmful = 103
    protect_beneficial = 104
    protect_harmful = 105
    divide_damage = 106
    collect_essence = 107
    kill_creature = 108
    dispel_block = 109
    confusion_block = 110
    modify_pip_round_rate = 111
    clue = 112
    max_health_damage = 113
    set_heal_percent = 114
    untargetable = 115
    make_targetable = 116
    force_targetable = 117
    remove_stun_block = 118
    modify_incoming_heal_flat = 119
    modify_incoming_damage_flat = 120
    modify_outgoing_heal_flat = 121
    modify_outgoing_damage_flat = 122
    exit_combat = 123
    suspend_pips = 124
    resume_pips = 125
    auto_pass = 126
    stop_auto_pass = 127
    vanish = 128
    stop_vanish = 129
    max_health_heal = 130
    heal_by_ward = 131
    taunt = 132
    pacify = 133
    remove_target_restriction = 134
    convert_hanging_effect = 135
    add_spell_to_deck = 136
    add_spell_to_hand = 137
    modify_incoming_damage_over_time = 138
    modify_incoming_heal_over_time = 139
    modify_card_damage_by_rank = 140
    push_converted_charm = 141
    steal_converted_charm = 142
    push_converted_ward = 143
    steal_converted_ward = 144
    push_converted_over_time = 145
    steal_converted_over_time = 146
    remove_converted_charm = 147
    remove_converted_ward = 148
    remove_converted_over_time = 149
    modify_over_time_duration = 150
    modify_school_pips = 151
    shadow_pact = 152
    
class Disposition(Enum):
    both = 0
    beneficial = 1
    harmful = 2

class EffectTarget(Enum):
    invalid_target = 0
    spell = 1
    specific_spells = 2
    target_global = 3
    enemy_team = 4
    enemy_team_all_at_once = 5
    friendly_team = 6
    friendly_team_all_at_once = 7
    enemy_single = 8
    friendly_single = 9
    minion = 10
    friendly_minion = 17
    enemy_minion = 18
    caster_minion = 19
    target_minion = 20
    self = 11
    at_least_one_enemy = 13
    preselected_enemy_single = 12
    multi_target_enemy = 14
    multi_target_friendly = 15
    friendly_single_not_me = 16

class EffectClass(Enum):
    spell_effect = 0
    random_spell_effect = 1
    variable_spell_effect = 2
    conditional_spell_effect = 3
    conditional_spell_element = 4
    target_count_spell_effect = 5
    hanging_conversion_spell_effect = 6
    shadow_pact_spell_effect = 7

class HangingEffect(Enum):
    any = 0
    ward = 1
    charm = 2
    overtime = 3
    specific = 4
    
class PactEffectKind(Enum):
    ward = 0
    jinx = 1
    charm = 2
    curse = 3
    DOT = 4
    HOT = 5


def find_effects(d, effects, damage_types, num_rounds):
    dictionaries_to_search = []
    for k, v in d.items():
        if d["$__type"] == "class SpellEffect" or (d["$__type"] == "class ShadowPactSpellEffect" and len(d["m_effectList"]) == 0):
            match k:
                case "m_effectParam":
                    effects.append(v)
                case "m_sDamageType":
                    try:
                        damage_types.append(SCHOOLS.index(v))
                    except ValueError:
                        damage_types.append(0)

                case "m_numRounds":
                    num_rounds.append(v)

        match v:
            case dict():
                dictionaries_to_search.append(v)
            case list():
                for item in v:
                    if isinstance(item, dict):
                        dictionaries_to_search.append(item)
                        
    for dictionary in dictionaries_to_search:
        find_effects(dictionary, effects, damage_types, num_rounds)


def remove_duplicates(lst):
    seen = {}
    result = []
    
    for element in list(lst):
        if element not in seen:
            seen[element] = True
            result.append(element)
    
    return result

target_type = {
    0: "Caster",
    1: "Target",
    2: "Caster Minion",
    3: "Target Minion",
}

operator_type = {
    0: "and",
    1: "or"
}

def parse_condition(obj: LazyObject, types: TypeList):
    req_list = []
    neg_aura_added = False
    for req in obj["m_requirements"]:
        req_class = types.name_for(req.type_hash)
        match req_class:
            case "class ReqHangingCharm" | "class ReqHangingWard" | "class ReqHangingOverTime":
                count = req["m_minCount"]
                applyNot = int(req["m_applyNOT"])
                disposition = int(req["m_disposition"])
                target = target_type[req["m_targetType"]]
                operator = operator_type[req["m_operator"]]
                
                req_string = f"{operator}" + " not"*applyNot + f" {count}"
                
                if disposition == 2:
                    if req_class == "class ReqHangingCharm":
                        req_string += " Weakness"
                    if req_class == "class ReqHangingWard":
                        req_string += " Trap"
                    if req_class == "class ReqHangingOverTime":
                        req_string += " DOT"
                        
                if disposition == 1:
                    if req_class == "class ReqHangingCharm":
                        req_string += " Blade"
                    if req_class == "class ReqHangingWard":
                        req_string += " Shield"
                    if req_class == "class ReqHangingOverTime":
                        req_string += " HOT"
                
                if disposition == 0:
                    if req_class == "class ReqHangingCharm":
                        req_string += " Charm"
                    if req_class == "class ReqHangingWard":
                        req_string += " Ward"
                    if req_class == "class ReqHangingOverTime":
                        req_string += " OT"
                
                req_string += f" on {target}"
                req_list.append((req.type_hash, req_string))
            
            case "class ReqHangingAura":
                applyNot = int(req["m_applyNOT"])
                disposition = req["m_disposition"]
                target = target_type[req["m_targetType"]]
                operator = operator_type[req["m_operator"]]
                
                req_string = f"{operator}" + " not"*applyNot
                
                if disposition == 2:
                    req_string += " Negative Aura"
                    req_string += f" on {target}"
                
                if disposition == 1:
                    req_string += " Aura"
                    req_string += f" on {target}"
                
                if disposition == 0:
                    req_string += " Global"
                
                if not neg_aura_added:
                    req_list.append((1, req_string))
                    neg_aura_added = True
            
            case "class ReqIsSchool":
                school = req["m_magicSchoolName"].decode("utf-8")
                applyNot = int(req["m_applyNOT"])
                target = target_type[req["m_targetType"]]
                operator = operator_type[req["m_operator"]]
                req_list.append((0, f"{operator}" + " not"*applyNot + f" {target} School {school}"))
            
            case "class ReqIsSecondarySchool":
                school = req["m_magicSchoolName"].decode("utf-8")
                if school == "":
                    school = "None"
                applyNot = int(req["m_applyNOT"])
                target = target_type[req["m_targetType"]]
                operator = operator_type[req["m_operator"]]
                req_list.append((0, f"{operator}" + " not"*applyNot + f" {target} Secondary School {school}"))
            
            case "class ReqMinion":
                #minion_type = req["m_minionType"]
                applyNot = int(req["m_applyNOT"])
                target = target_type[req["m_targetType"]]
                operator = operator_type[req["m_operator"]]
                req_list.append((2, f"{operator}" + " not"*applyNot + f" {target} has Minion"))
            
            case 'class ReqHangingEffectType':
                applyNot = int(req["m_applyNOT"])
                count = req["m_min_count"]
                effect_type = SpellEffects(req["m_effectType"]).name.replace("_", " ").title()
                target = target_type[req["m_targetType"]]
                operator = operator_type[req["m_operator"]]
                req_list.append((3, f"{operator}" + " not"*applyNot + f" {target} has {count} {effect_type}"))
            
            case 'class ReqCombatHealth':
                max_health = int(req["m_fMaxPercent"]*100)
                min_health = int(req["m_fMinPercent"]*100)
                applyNot = int(req["m_applyNOT"])
                target = target_type[req["m_targetType"]]
                operator = operator_type[req["m_operator"]]
                req_string = f"{operator}" + " not"*applyNot + f" {target} "
                
                if max_health > 100:
                    req_string += f"above {min_health}% HP"
                elif min_health < 0:
                    req_string += f"below {max_health}% HP"
                else:
                    req_string += f"between {min_health}% and {max_health}% HP"
                
                req_list.append((4, req_string))
            
            case 'class ReqShadowPipCount':
                min_pips = req["m_minPips"]
                applyNot = int(req["m_applyNOT"])
                target = target_type[req["m_targetType"]]
                operator = operator_type[req["m_operator"]]
                req_list.append((5, f"{operator}" + " not"*applyNot + f" {min_pips} Shadow Pips on {target}"))
            
            case 'class ReqPipCount':
                min_pips = req["m_minPips"]
                applyNot = int(req["m_applyNOT"])
                target = target_type[req["m_targetType"]]
                operator = operator_type[req["m_operator"]]
                req_list.append((6, f"{operator}" + " not"*applyNot + f" {min_pips} Pips on {target}"))
            
            case 'class ReqPvPCombat':
                applyNot = int(req["m_applyNOT"])
                operator = operator_type[req["m_operator"]]
                req_list.append((7, f"{operator}" + " not"*applyNot + f" PvP"))
            
            case 'class ReqCombatStatus':
                status = req["m_status"]
                applyNot = int(req["m_applyNOT"])
                target = target_type[req["m_targetType"]]
                operator = operator_type[req["m_operator"]]
                req_list.append((8, f"{operator}" + " not"*applyNot + f" {target} {status}"))
            
            case "class ReqMinionHealth":
                applyNot = int(req["m_applyNOT"])
                target = target_type[req["m_targetType2"]]
                operator = operator_type[req["m_operator"]]
                numericValue = req["m_numericValue"]
                req_list.append((9, f"{operator}" + " not"*applyNot + f" {target} has {numericValue} Rank"))
    
    if len(req_list) == 0:
        return ""
    
    sorted_req_list = sorted(req_list, key=lambda x: x[0])
    req_string_list = [x[1] for x in sorted_req_list]
    
    first_req = req_string_list[0].removeprefix("and ").removeprefix("or ")
    ret = f"If {first_req}"
    
    if len(req_string_list) == 1:
        return ret
    
    for req in req_string_list[1:]:
        ret += f" {req}"
    
    return ret

def parse_convert_condition(obj):
    disposition = obj["m_disposition"]
    match obj["m_hangingEffectType"]:
        case 0:
            input_effect = "Any"
        case 1:
            if disposition in [0, 1]:
                input_effect = "Shield"
            else:
                input_effect = "Trap"
        case 2:
            if disposition in [0, 1]:
                input_effect = "Blade"
            else:
                input_effect = "Weakness"
        case 3:
            if disposition in [0, 1]:
                input_effect = "HOT"
            else:
                input_effect = "DOT"
        case 4:
            input_effect = ""
            for effect in obj["m_specificEffectTypes"]:
                match effect:
                    case 22: # Shield/Trap
                        if disposition in [0, 1]:
                            input_effect += "Shield, "
                        else:
                            input_effect += "Trap, "
                    case 27: # Blade/Weak
                        if disposition in [0, 1]:
                            input_effect += "Blade, "
                        else:
                            input_effect += "Weakness, "
            
            input_effect = input_effect.removesuffix(", ")
        
    count = obj["m_maxEffectCount"]
    return f"Convert {count} {input_effect}"


class SpellEffect:
    def __init__(self, spell_id):
        self.spell_id = spell_id
        self.effect_class = EffectClass.spell_effect
        self.param = -1
        self.disposition = 0
        self.target = 0
        self.type = 0
        self.heal_modifier = 1.0
        self.rounds = 0
        self.pip_num = 0
        self.protected = False
        self.rank = 0
        self.school = 0
        self.condition = ""
        self.num_targets = 0
        self.sub_effects = []
    
    def build_effect_tree(self, obj: LazyObject, types: TypeList, conversion_disposition=-1, conversion_percentage=-1.0, num_targets=0):
        self.num_targets = num_targets
        match types.name_for(obj.type_hash):
            case "class SpellEffect":
                self.effect_class = EffectClass.spell_effect
                self.param = obj["m_effectParam"]
                self.disposition = obj["m_disposition"]
                self.target = obj["m_effectTarget"]
                self.type = obj["m_effectType"]
                self.heal_modifier = obj["m_healModifier"]
                self.rounds = obj["m_numRounds"]
                self.pip_num = obj["m_pipNum"]
                self.protected = obj["m_protected"]
                self.rank = obj["m_rank"]
                if obj["m_sDamageType"] in SCHOOLS:
                    self.school = SCHOOLS.index(obj["m_sDamageType"])
                else:
                    self.school = 0
                
            case "class RandomSpellEffect":
                self.effect_class = EffectClass.random_spell_effect
                self.condition = "Random"
                self.param = obj["m_effectParam"]
                self.disposition = obj["m_disposition"]
                self.target = obj["m_effectTarget"]
                self.type = obj["m_effectType"]
                self.heal_modifier = obj["m_healModifier"]
                self.rounds = obj["m_numRounds"]
                self.pip_num = obj["m_pipNum"]
                self.protected = obj["m_protected"]
                self.rank = obj["m_rank"]
                if obj["m_sDamageType"] in SCHOOLS:
                    self.school = SCHOOLS.index(obj["m_sDamageType"])
                else:
                    self.school = 0
                
                for sub_effect in obj["m_effectList"]:
                    sub_effect_obj = SpellEffect(self.spell_id)
                    sub_effect_obj.build_effect_tree(sub_effect, types, num_targets=num_targets)
                    self.sub_effects.append(sub_effect_obj)
            
            case "class VariableSpellEffect":
                self.effect_class = EffectClass.variable_spell_effect
                self.condition = "Variable"
                self.param = obj["m_effectParam"]
                self.disposition = obj["m_disposition"]
                self.target = obj["m_effectTarget"]
                self.type = obj["m_effectType"]
                self.heal_modifier = obj["m_healModifier"]
                self.rounds = obj["m_numRounds"]
                self.pip_num = obj["m_pipNum"]
                self.protected = obj["m_protected"]
                self.rank = obj["m_rank"]
                if obj["m_sDamageType"] in SCHOOLS:
                    self.school = SCHOOLS.index(obj["m_sDamageType"])
                else:
                    self.school = 0
                
                for sub_effect in obj["m_effectList"]:
                    sub_effect_obj = SpellEffect(self.spell_id)
                    sub_effect_obj.build_effect_tree(sub_effect, types, num_targets=num_targets)
                    self.sub_effects.append(sub_effect_obj)
            
            case "class ConditionalSpellEffect":
                self.effect_class = EffectClass.conditional_spell_effect
                self.param = obj["m_effectParam"]
                self.disposition = obj["m_disposition"]
                self.target = obj["m_effectTarget"]
                self.type = obj["m_effectType"]
                self.heal_modifier = obj["m_healModifier"]
                self.rounds = obj["m_numRounds"]
                self.pip_num = obj["m_pipNum"]
                self.protected = obj["m_protected"]
                self.rank = obj["m_rank"]
                if obj["m_sDamageType"] in SCHOOLS:
                    self.school = SCHOOLS.index(obj["m_sDamageType"])
                else:
                    self.school = 0
                
                for element in obj["m_elements"]:
                    sub_effect_obj = SpellEffect(self.spell_id)
                    sub_effect_obj.build_effect_tree(element, types, num_targets=num_targets)
                    self.sub_effects.append(sub_effect_obj)
            
            case "class ConditionalSpellElement":
                self.effect_class = EffectClass.conditional_spell_element
                if obj["m_pReqs"] != None:
                    self.condition = parse_condition(obj["m_pReqs"], types)
                sub_effect = obj["m_pEffect"]
                sub_effect_obj = SpellEffect(self.spell_id)
                sub_effect_obj.build_effect_tree(sub_effect, types, num_targets=num_targets)
                self.sub_effects.append(sub_effect_obj)
            
            case "class TargetCountSpellEffect":
                self.effect_class = EffectClass.target_count_spell_effect
                for i, sub_effect in enumerate(obj["m_effectLists"]):
                    sub_effect_obj = SpellEffect(self.spell_id)
                    sub_effect_obj.build_effect_tree(sub_effect, types, num_targets=(i+1))
                    self.sub_effects.append(sub_effect_obj)

            case "class EffectListSpellEffect" | "class ShadowSpellEffect":
                self.effect_class = EffectClass.conditional_spell_effect
                self.param = obj["m_effectParam"]
                self.disposition = obj["m_disposition"]
                self.target = obj["m_effectTarget"]
                self.type = obj["m_effectType"]
                self.heal_modifier = obj["m_healModifier"]
                self.rounds = obj["m_numRounds"]
                self.pip_num = obj["m_pipNum"]
                self.protected = obj["m_protected"]
                self.rank = obj["m_rank"]
                if obj["m_sDamageType"] in SCHOOLS:
                    self.school = SCHOOLS.index(obj["m_sDamageType"])
                else:
                    self.school = 0
                
                for sub_effect in obj["m_effectList"]:
                    sub_effect_obj = SpellEffect(self.spell_id)
                    sub_effect_obj.build_effect_tree(sub_effect, types, num_targets=num_targets)
                    self.sub_effects.append(sub_effect_obj)
            
            case "class HangingConversionSpellEffect":
                self.effect_class = EffectClass.hanging_conversion_spell_effect
                self.condition = parse_convert_condition(obj)
                self.param = obj["m_effectParam"]
                self.disposition = obj["m_disposition"]
                self.target = obj["m_effectTarget"]
                self.type = obj["m_effectType"]
                self.heal_modifier = obj["m_healModifier"]
                self.rounds = obj["m_numRounds"]
                self.pip_num = obj["m_pipNum"]
                self.protected = obj["m_protected"]
                self.rank = obj["m_rank"]
                if obj["m_sDamageType"] in SCHOOLS:
                    self.school = SCHOOLS.index(obj["m_sDamageType"])
                else:
                    self.school = 0
                
                for sub_effect in obj["m_outputEffect"]:
                    sub_effect_obj = SpellEffect(self.spell_id)
                    sub_effect_obj.build_effect_tree(sub_effect, types, conversion_disposition=self.disposition, conversion_percentage=obj["m_sourceEffectValuePercent"]*100, num_targets=num_targets)
                    self.sub_effects.append(sub_effect_obj)
            
            case "class ShadowPactSpellEffect":
                self.effect_class = EffectClass.shadow_pact_spell_effect
                self.type = 151
                self.target = obj["m_effectTarget"]
                self.rounds = obj["m_numRounds"]
                self.param = obj["m_pactEffectKind"]
                
                for sub_effect in obj["m_effectList"]:
                    sub_effect_obj = SpellEffect(self.spell_id)
                    sub_effect_obj.build_effect_tree(sub_effect, types, num_targets=num_targets)
                    self.sub_effects.append(sub_effect_obj)
        
        if self.disposition == 0 and conversion_disposition != -1:
            self.disposition = conversion_disposition
        
        if self.param == -1 and conversion_percentage != -1.0:
            self.param = conversion_percentage

class Spell:
    def __init__(self, template_id: int, state, obj: dict):
        self.template = template_id
        self.name = state.make_lang_key(obj)
        if self.name.id is None:
            self.name.id = state.cache.add_entry(obj["m_name"], obj["m_name"].decode())
        self.real_name = obj["m_name"]
        self.image = obj["m_imageName"].decode()
        self.accuracy = obj["m_accuracy"]
        try:
            self.levelreq = obj["m_levelRestriction"]
        except KeyError:
            self.levelreq = 0

        self.pve = int(obj["m_PvE"])
        self.pvp = int(obj["m_PvP"])

        if "m_energyCost" in obj:
            self.energy = obj["m_energyCost"]
        else:
            self.energy = 0

        school = obj["m_sMagicSchoolName"]
        self.description = state.make_lang_key({"m_displayName": obj["m_description"]})
        if school == b"Gardening":
            try:
                self.type_name = obj["m_gardenSpellType"]
            except KeyError:
                self.type_name = SPELL_TYPES.index(obj["m_sTypeName"])
        elif school == b"Fishing":
            self.type_name = obj["m_fishingSpellType"]
        elif school == b"Cantrips":
            self.type_name = obj["m_cantripsSpellType"]
        else:
            self.type_name = SPELL_TYPES.index(obj["m_sTypeName"])
        
        self.school = SCHOOLS.index(school)

        rank = obj["m_spellRank"]
        self.rank = rank["m_spellRank"]
        self.x_pips = rank["m_xPipSpell"]
        self.shadow_pips = rank["m_shadowPips"]
        
        self.fire_pips = rank["m_firePips"]
        self.ice_pips = rank["m_icePips"]
        self.storm_pips = rank["m_stormPips"]
        self.myth_pips = rank["m_mythPips"]
        self.life_pips = rank["m_lifePips"]
        self.death_pips = rank["m_deathPips"]
        self.balance_pips = rank["m_balancePips"]

        raw_effects = []
        raw_damage_types = []
        raw_num_rounds = []
        dict_obj = op_to_dict(state.de.types, obj)
        find_effects(dict_obj, raw_effects, raw_damage_types, raw_num_rounds)
        
        self.spell_effects = []
        for effect in obj["m_effects"]:
            effect_obj = SpellEffect(template_id)
            effect_obj.build_effect_tree(effect, state.de.types)
            self.spell_effects.append(effect_obj)
            
        self.effect_params= raw_effects
        self.damage_types = raw_damage_types
        self.num_rounds = raw_num_rounds




class SpellCache:
    def __init__(self, state):
        self.cache = {}
        self.name_to_id = {}

        for file, template in state.file_to_id.items():
            if not file.startswith("Spells/"):
                continue
            
            value = state.de.deserialize_from_path(file)

            spell = Spell(template, state, value)
            self.cache[template] = spell
            self.name_to_id[value["m_name"].decode()] = template

    def get(self, name: str) -> int:
        if tid := self.name_to_id.get(name):
            return tid
        else:
            return None
