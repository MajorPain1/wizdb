from enum import Enum
from struct import pack as pk
from typing import List

from katsuba.utils import string_id # type: ignore

from .utils import SCHOOLS, SPELL_TYPES, GARDENING_TYPES, CANTRIP_TYPES, FISHING_TYPES, DISPOSITION, op_to_dict


def find_effects(d, effects, damage_types, num_rounds):
    dictionaries_to_search = []
    for k, v in d.items():
        if not "m_effectList" in d and not "m_elements" in d and not "m_outputEffect" in d:
            
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
                rank = -1
                if len(v) > 0 and isinstance(v[0], dict) and "m_rank" in v[0] and (k == "m_outputEffect" or k == "m_elements"):
                    rank = v[0]["m_rank"]

                for item in v:
                    if isinstance(item, dict) and (rank == -1 or item["m_rank"] == rank):
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
    1: "Target"
}

operator_type = {
    0: "and",
    1: "or"
}

def parse_condition(obj, types):
    req_list = []
    neg_aura_added = False
    for req in obj["m_requirements"]:
        match types.name_for(req.type_hash):
            case "class ReqHangingCharm" | "class ReqHangingWard" | "class ReqHangingOverTime":
                count = req["m_minCount"]
                applyNot = int(req["m_applyNOT"])
                disposition = req["m_disposition"]
                target = target_type[req["m_targetType"]]
                operator = operator_type[req["m_operator"]]
                
                req_string = f"{operator}" + " not"*applyNot + f" {count}"
                
                if disposition == "enum SpellEffect::kHangingDisposition::SpellEffect::kHarmful":
                    if req["$__type"] == b"class ReqHangingCharm":
                        req_string += " Weakness"
                    if req["$__type"] == b"class ReqHangingWard":
                        req_string += " Trap"
                    if req["$__type"] == b"class ReqHangingOverTime":
                        req_string += " DOT"
                        
                if disposition == "enum SpellEffect::kHangingDisposition::SpellEffect::kBeneficial":
                    if req["$__type"] == b"class ReqHangingCharm":
                        req_string += " Blade"
                    if req["$__type"] == b"class ReqHangingWard":
                        req_string += " Shield"
                    if req["$__type"] == b"class ReqHangingOverTime":
                        req_string += " HOT"
                
                if disposition == "enum SpellEffect::kHangingDisposition::SpellEffect::kBoth":
                    if req["$__type"] == b"class ReqHangingCharm":
                        req_string += " Charm"
                    if req["$__type"] == b"class ReqHangingWard":
                        req_string += " Ward"
                    if req["$__type"] == b"class ReqHangingOverTime":
                        req_string += " OT"
                
                req_string += f" on {target}"
                req_list.append(req_string)
            
            case "class ReqHangingAura":
                applyNot = int(req["m_applyNOT"])
                disposition = req["m_disposition"]
                target = target_type[req["m_targetType"]]
                operator = operator_type[req["m_operator"]]
                
                req_string = f"{operator}" + " not"*applyNot
                
                if disposition == "enum SpellEffect::kHangingDisposition::SpellEffect::kHarmful":
                    req_string += " Negative Aura"
                    req_string += f" on {target}"
                
                if disposition == "enum SpellEffect::kHangingDisposition::SpellEffect::kBeneficial":
                    req_string += " Aura"
                    req_string += f" on {target}"
                
                if disposition == "enum SpellEffect::kHangingDisposition::SpellEffect::kBoth":
                    req_string += " Global"
                
                if not neg_aura_added:
                    req_list.append(req_string)
                    neg_aura_added = True
            
            case "class ReqIsSchool":
                school = req["m_magicSchoolName"].decode("utf-8")
                applyNot = int(req["m_applyNOT"])
                target = target_type[req["m_targetType"]]
                operator = operator_type[req["m_operator"]]
                req_list.append(f"{operator}" + " not"*applyNot + f" {target} School {school}")
            
            case "class ReqMinion":
                #minion_type = req["m_minionType"]
                applyNot = int(req["m_applyNOT"])
                target = target_type[req["m_targetType"]]
                operator = operator_type[req["m_operator"]]
                req_list.append(f"{operator}" + " not"*applyNot + f" {target} has Minion")
            
            case 'class ReqHangingEffectType':
                applyNot = int(req["m_applyNOT"])
                count = req["m_min_count"]
                effect_type = req["m_effectType"]
                target = target_type[req["m_targetType"]]
                operator = operator_type[req["m_operator"]]
                req_list.append(f"{operator}" + " not"*applyNot + f" {target} has {count} {effect_type}")
            
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
                
                req_list.append(req_string)
            
            case 'class ReqShadowPipCount':
                min_pips = req["m_minPips"]
                applyNot = int(req["m_applyNOT"])
                target = target_type[req["m_targetType"]]
                operator = operator_type[req["m_operator"]]
                req_list.append(f"{operator}" + " not"*applyNot + f" {min_pips} Shadow Pips on {target}")
            
            case 'class ReqPipCount':
                min_pips = req["m_minPips"]
                applyNot = int(req["m_applyNOT"])
                target = target_type[req["m_targetType"]]
                operator = operator_type[req["m_operator"]]
                req_list.append(f"{operator}" + " not"*applyNot + f" {min_pips} Pips on {target}")
            
            case 'class ReqPvPCombat':
                applyNot = int(req["m_applyNOT"])
                operator = operator_type[req["m_operator"]]
                req_list.append(f"{operator}" + " not"*applyNot + f" PvP")
            
            case 'class ReqCombatStatus':
                status = req["m_status"]
                applyNot = int(req["m_applyNOT"])
                target = target_type[req["m_targetType"]]
                operator = operator_type[req["m_operator"]]
                req_list.append(f"{operator}" + " not"*applyNot + f" {target} {status}")
    
    if len(req_list) == 0:
        return ""
    
    first_req = req_list[0].replace("and ", "").replace("or ", "")
    ret = f"If {first_req}"
    
    if len(req_list) == 1:
        return ret
    
    for req in req_list[1:]:
        ret += f" {req}"
    
    return ret

def parse_convert_condition(obj):
    input_effect = obj["m_hangingEffectType"]
    count = obj["m_maxEffectCount"]
    return f"Convert Up To {count} {input_effect}"

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
    self = 11
    at_least_one_enemy = 13
    preselected_enemy_single = 12
    multi_target_enemy = 14
    multi_target_friendly = 15
    friendly_single_not_me = 16

class SpellEffects(Enum):
    invalid_spell_effect = 0
    damage = 1
    damage_no_crit = 2
    heal = 3
    heal_percent = 4
    set_heal_percent = 111
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
    modify_incoming_damage = 22
    modify_incoming_damage_flat = 117
    maximum_incoming_damage = 23
    modify_incoming_heal = 24
    modify_incoming_heal_flat = 116
    modify_incoming_damage_type = 25
    modify_incoming_armor_piercing = 26
    modify_outgoing_damage = 27
    modify_outgoing_damage_flat = 119
    modify_outgoing_heal = 28
    modify_outgoing_heal_flat = 118
    modify_outgoing_damage_type = 29
    modify_outgoing_armor_piercing = 30
    bounce_next = 31
    bounce_previous = 32
    bounce_back = 33
    bounce_all = 34
    absorb_damage = 35
    absorb_heal = 36
    modify_accuracy = 37
    dispel = 38
    confusion = 39
    cloaked_charm = 40
    cloaked_ward = 41
    stun_resist = 42
    clue = 109
    pip_conversion = 43
    crit_boost = 44
    crit_block = 45
    polymorph = 46
    delay_cast = 47
    modify_card_cloak = 48
    modify_card_damage = 49
    modify_card_accuracy = 51
    modify_card_mutation = 52
    modify_card_rank = 53
    modify_card_armor_piercing = 54
    summon_creature = 63
    teleport_player = 64
    stun = 65
    dampen = 66
    reshuffle = 67
    mind_control = 68
    modify_pips = 69
    modify_power_pips = 70
    modify_shadow_pips = 71
    modify_hate = 72
    damage_over_time = 73
    heal_over_time = 74
    modify_power_pip_chance = 75
    modify_rank = 76
    stun_block = 77
    reveal_cloak = 78
    instant_kill = 79
    after_life = 80
    deferred_damage = 81
    damage_per_total_pip_power = 82
    modify_card_heal = 50
    modify_card_charm = 55
    modify_card_warn = 56
    modify_card_outgoing_damage = 57
    modify_card_outgoing_accuracy = 58
    modify_card_outgoing_heal = 59
    modify_card_outgoing_armor_piercing = 60
    modify_card_incoming_damage = 61
    modify_card_absorb_damage = 62
    cloaked_ward_no_remove = 84
    add_combat_trigger_list = 85
    remove_combat_trigger_list = 86
    backlash_damage = 87
    modify_backlash = 88
    intercept = 89
    shadow_self = 90
    shadow_creature = 91
    modify_shadow_creature_level = 92
    select_shadow_creature_attack_target = 93
    shadow_decrement_turn = 94
    crit_boost_school_specific = 95
    spawn_creature = 96
    unpolymorph = 97
    power_pip_conversion = 98
    protect_card_beneficial = 99
    protect_card_harmful = 100
    protect_beneficial = 101
    protect_harmful = 102
    divide_damage = 103
    collect_essence = 104
    kill_creature = 105
    dispel_block = 106
    confusion_block = 107
    modify_pip_round_rate = 108
    max_health_damage = 110
    untargetable = 112
    make_targetable = 113
    force_targetable = 114
    remove_stun_block = 115
    exit_combat = 120
    suspend_pips = 121
    resume_pips = 122
    auto_pass = 123
    stop_auto_pass = 124
    vanish = 125
    stop_vanish = 126
    max_health_heal = 127
    heal_by_ward = 128
    taunt = 129
    pacify = 130
    remove_target_restriction = 131
    convert_hanging_effect = 132
    add_spell_to_deck = 133
    add_spell_to_hand = 134
    modify_incoming_damage_over_time = 135
    modify_incoming_heal_over_time = 136
    modify_card_damage_by_rank = 137
    push_converted_charm = 138
    steal_converted_charm = 139
    push_converted_ward = 140
    steal_converted_ward = 141
    push_converted_over_time = 142
    steal_converted_over_time = 143
    remove_converted_charm = 144
    remove_converted_ward = 145
    remove_converted_over_time = 146
    modify_over_time_duration = 147

class EffectClass(Enum):
    spell_effect = 0
    random_spell_effect = 1
    variable_spell_effect = 2
    conditional_spell_effect = 3
    conditional_spell_element = 4
    target_count_spell_effect = 5
    hanging_conversion_spell_effect = 6


class SpellEffect:
    def __init__(self, spell_id):
        self.spell_id = spell_id
        self.effect_class = EffectClass.spell_effect
        self.param = -1
        self.disposition = 0
        self.target = ""
        self.type = ""
        self.heal_modifier = 1.0
        self.rounds = 0
        self.pip_num = 0
        self.protected = False
        self.rank = 0
        self.school = 0
        self.condition = ""
        self.sub_effects = []
    
    def build_effect_tree(self, obj, types):
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
                    sub_effect_obj.build_effect_tree(sub_effect, types)
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
                    sub_effect_obj.build_effect_tree(sub_effect, types)
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
                    sub_effect_obj.build_effect_tree(element, types)
                    self.sub_effects.append(sub_effect_obj)
            
            case "class ConditionalSpellElement":
                self.effect_class = EffectClass.conditional_spell_element
                if obj["m_pReqs"] != None:
                    self.condition = parse_condition(obj["m_pReqs"], types)
                sub_effect = obj["m_pEffect"]
                sub_effect_obj = SpellEffect(self.spell_id)
                sub_effect_obj.build_effect_tree(sub_effect, types)
                self.sub_effects.append(sub_effect_obj)
            
            case "class TargetCountSpellEffect":
                self.effect_class = EffectClass.target_count_spell_effect
                sub_effect = obj["m_effectLists"][0]
                sub_effect_obj = SpellEffect(self.spell_id)
                sub_effect_obj.build_effect_tree(sub_effect, types)
                self.sub_effects.append(sub_effect_obj)

            case "class EffectListSpellEffect" | b"class ShadowSpellEffect":
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
                    sub_effect_obj.build_effect_tree(sub_effect, types)
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
                    sub_effect_obj.build_effect_tree(sub_effect, types)
                    self.sub_effects.append(sub_effect_obj)

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
