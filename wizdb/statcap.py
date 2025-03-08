from struct import pack as pk
from typing import List

from .utils import SCHOOLS, SPELL_TYPES


class StatCap:
    def __init__(self, obj: dict):
        # Identifiers
        self.level = int(obj["m_level"])
        self.school = SCHOOLS.index(obj["m_school"])



        # General Stats
        self.max_pips = int(obj["m_maximumPips"])
        self.max_power_pips = int(obj["m_maximumPowerPips"])
        self.max_health = int(obj["m_canonicalMaxHealth"])
        self.max_mana = int(obj["m_canonicalMaxMana"])
        self.ppc = int(round(obj["m_canonicalPowerPip"]*100))
        self.shadow_pip_rating = int(obj["m_canonicalShadowPipRating"])
        self.archmastery = int(obj["m_canonicalAllArchmastery"])
        self.out_healing = int(round(obj["m_canonicalLifeHealing"]*100))
        self.inc_healing = int(round(obj["m_canonicalIncHealing"]*100))

        # Accuracy
        self.b_acc = int(round(obj["m_canonicalBalanceAccuracy"]*100))
        self.d_acc = int(round(obj["m_canonicalDeathAccuracy"]*100))
        self.f_acc = int(round(obj["m_canonicalFireAccuracy"]*100))
        self.i_acc = int(round(obj["m_canonicalIceAccuracy"]*100))
        self.l_acc = int(round(obj["m_canonicalLifeAccuracy"]*100))
        self.m_acc = int(round(obj["m_canonicalMythAccuracy"]*100))
        self.s_acc = int(round(obj["m_canonicalStormAccuracy"]*100))

        # Armor Piercing
        self.b_ap = int(round(obj["m_canonicalBalanceArmorPiercing"]*100))
        self.d_ap = int(round(obj["m_canonicalDeathArmorPiercing"]*100))
        self.f_ap = int(round(obj["m_canonicalFireArmorPiercing"]*100))
        self.i_ap = int(round(obj["m_canonicalIceArmorPiercing"]*100))
        self.l_ap = int(round(obj["m_canonicalLifeArmorPiercing"]*100))
        self.m_ap = int(round(obj["m_canonicalMythArmorPiercing"]*100))
        self.s_ap = int(round(obj["m_canonicalStormArmorPiercing"]*100))

        # Block
        self.b_block = int(obj["m_canonicalBalanceBlock"])
        self.d_block = int(obj["m_canonicalDeathBlock"])
        self.f_block = int(obj["m_canonicalFireBlock"])
        self.i_block = int(obj["m_canonicalIceBlock"])
        self.l_block = int(obj["m_canonicalLifeBlock"])
        self.m_block = int(obj["m_canonicalMythBlock"])
        self.s_block = int(obj["m_canonicalStormBlock"])

        # Crit
        self.b_crit = int(obj["m_canonicalBalanceCriticalHit"])
        self.d_crit = int(obj["m_canonicalDeathCriticalHit"])
        self.f_crit = int(obj["m_canonicalFireCriticalHit"])
        self.i_crit = int(obj["m_canonicalIceCriticalHit"])
        self.l_crit = int(obj["m_canonicalLifeCriticalHit"])
        self.m_crit = int(obj["m_canonicalMythCriticalHit"])
        self.s_crit = int(obj["m_canonicalStormCriticalHit"])

        # Damage
        self.b_damage = int(round(obj["m_canonicalBalanceDamage"]*100))
        self.d_damage = int(round(obj["m_canonicalDeathDamage"]*100))
        self.f_damage = int(round(obj["m_canonicalFireDamage"]*100))
        self.i_damage = int(round(obj["m_canonicalIceDamage"]*100))
        self.l_damage = int(round(obj["m_canonicalLifeDamage"]*100))
        self.m_damage = int(round(obj["m_canonicalMythDamage"]*100))
        self.s_damage = int(round(obj["m_canonicalStormDamage"]*100))

        # P Serve
        self.b_pserve = int(obj["m_canonicalBalancePipConversion"])
        self.d_pserve = int(obj["m_canonicalDeathPipConversion"])
        self.f_pserve = int(obj["m_canonicalFirePipConversion"])
        self.i_pserve = int(obj["m_canonicalIcePipConversion"])
        self.l_pserve = int(obj["m_canonicalLifePipConversion"])
        self.m_pserve = int(obj["m_canonicalMythPipConversion"])
        self.s_pserve = int(obj["m_canonicalStormPipConversion"])

        # Resist
        self.b_resist = int(round(obj["m_canonicalBalanceReduceDamage"]*100))
        self.d_resist = int(round(obj["m_canonicalDeathReduceDamage"]*100))
        self.f_resist = int(round(obj["m_canonicalFireReduceDamage"]*100))
        self.i_resist = int(round(obj["m_canonicalIceReduceDamage"]*100))
        self.l_resist = int(round(obj["m_canonicalLifeReduceDamage"]*100))
        self.m_resist = int(round(obj["m_canonicalMythReduceDamage"]*100))
        self.s_resist = int(round(obj["m_canonicalStormReduceDamage"] *100))       

