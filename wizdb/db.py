import sqlite3
from sqlite3 import Cursor

from .lang_files import LangCache
from .set_bonus import SetBonusCache
from .spell import SpellCache
from .statcap import StatCap

INIT_QUERIES = """CREATE TABLE locale_en (
    id   integer not null primary key,
    data text not null
);

CREATE INDEX en_name_lookup ON locale_en(data);

CREATE TABLE set_bonuses (
    id   integer not null primary key,
    name integer not null,

    foreign key(name) references locale_en(id)
);

CREATE TABLE set_stats (
    id             integer not null primary key,
    bonus_set      integer not null,
    activate_count integer not null,

    kind           integer not null,
    a              integer,
    b              integer,

    foreign key(bonus_set) references set_bonuses(id)
);

CREATE INDEX set_stat_lookup ON set_stats(bonus_set);

CREATE TABLE items (
    id                 integer not null primary key,
    name               integer not null,
    real_name          text,
    bonus_set          integer,
    rarity             integer,
    jewels             integer,
    kind               integer not null,
    extra_flags        integer,

    equip_school       integer,
    equip_level        integer,

    -- When the PetJewel bit in extra_flags is set.
    min_pet_level      integer,

    -- When deck bit in kind is set.
    max_spells         integer,
    max_copies         integer,
    max_school_copies  integer,
    deck_school        integer,
    max_tcs            integer,
    archmastery_points real,

    foreign key(name)  references locale_en(id),
    foreign key(bonus_set) references set_bonuses(id)
);

CREATE TABLE item_stats (
    id       integer not null primary key,
    item     integer not null,

    kind     integer not null,
    a        integer,
    b        integer,

    foreign key(item) references items(id)
);

CREATE INDEX item_stat_lookup ON item_stats(item);

CREATE TABLE pet_talents (
    id   integer not null primary key,
    item integer not null,
    name integer not null,

    foreign key(item) references items(id),
    foreign key(name) references locale_en(id)
);

CREATE INDEX item_talent_lookup ON pet_talents(item);

CREATE TABLE spells (
    id              integer not null primary key,
    template_id     integer not null,
    name            integer not null,
    real_name       text,
    image           text,
    accuracy        integer,
    energy          integer,
    school          integer,
    description     integer,
    form            integer,
    pve             integer,
    pvp             integer,
    levelreq        integer,

    rank            integer,
    x_pips          bool,
    shadow_pips     integer,
    fire_pips       integer,
    ice_pips        integer,
    storm_pips      integer,
    myth_pips       integer,
    life_pips       integer,
    death_pips      integer,
    balance_pips    integer,

    foreign key(name)        references locale_en(id)
);

CREATE TABLE spell_effects (
    id              integer not null primary key,
    spell_id        integer not null,
    parent_id       integer not null,
    idx             integer,
    effect_class    integer,
    param           integer,
    disposition     integer,
    target          integer,
    type            integer,
    heal_modifier   real,
    rounds          integer,
    pip_num         integer,
    protected       bool,
    rank            integer,
    school          integer,
    condition       text,
    
    foreign key(spell_id) references spells(id)
);

CREATE TABLE effects (
    id       integer not null primary key,
    spell    integer not null,
    indx     integer,
    param    integer,
    damage   integer,
    rounds   integer,

    foreign key(spell) references spells(id)
);


CREATE TABLE mobs (
    id                  integer not null primary key,
    name                integer not null,
    real_name           text,
    image               text,
    title               text,
    rank                integer,
    hp                  integer,
    primary_school      integer,
    secondary_school    integer,
    stunnable           bool,
    max_shadow          integer,
    has_cheats          bool,
    intelligence        real,
    selfishness         real,
    aggressiveness      real,
    monstro             integer,

    foreign key(name)        references locale_en(id)
);


CREATE TABLE mob_stats (
    id       integer not null primary key,
    mob      integer not null,

    kind     integer not null,
    a        integer,
    b        integer,

    foreign key(mob) references mobs(id)
);


CREATE TABLE mob_items (
    id       integer not null primary key,
    mob      integer not null,
    item     integer not null,

    foreign key(mob) references mobs(id)
);


CREATE TABLE pets (
    id              integer not null primary key,
    name            integer not null,
    real_name       text,
    bonus_set       integer,
    rarity          integer,
    extra_flags     integer,
    wow_factor      integer,
    exclusive       integer,
    school          integer,
    egg_name        integer,

    strength        integer,
    intellect       integer,
    agility         integer,
    will            integer,
    power           integer,
    

    foreign key(name)        references locale_en(id)
);

CREATE TABLE fish (
    id                          integer not null primary key,
    name                        integer not null,
    real_name                   text,
    rank                        integer,
    school                      integer,
    base_length                 real,
    min_size                    real,
    max_size                    real,
    speed                       real,
    bite_seconds                real,
    initial_bite_chance         real,
    incremental_bite_chance     real,
    is_sentinel                 bool,
    

    foreign key(name)        references locale_en(id)
);

CREATE TABLE talents (
    id       integer not null primary key,
    priority integer,
    pet      integer not null,

    talent   integer,

    foreign key(pet) references pets(id)
);


CREATE TABLE pet_cards (
    id       integer not null primary key,
    pet      integer not null,
    spell    integer not null,

    foreign key(pet) references pets(id)
);

CREATE TABLE statcaps (
    level               integer,
    school              integer,

    max_pips            integer,
    max_power_pips      integer,
    hp                  integer,
    mana                integer,
    ppc                 integer,
    shad_rating         integer,
    archmastery         integer,
    outgoing            integer,
    incoming            integer,

    b_acc               integer,
    d_acc               integer,
    f_acc               integer,
    i_acc               integer,
    l_acc               integer,
    m_acc               integer,
    s_acc               integer,

    b_ap                integer,
    d_ap                integer,
    f_ap                integer,
    i_ap                integer,
    l_ap                integer,
    m_ap                integer,
    s_ap                integer,

    b_block             integer,
    d_block             integer,
    f_block             integer,
    i_block             integer,
    l_block             integer,
    m_block             integer,
    s_block             integer,

    b_crit              integer,
    d_crit              integer,
    f_crit              integer,
    i_crit              integer,
    l_crit              integer,
    m_crit              integer,
    s_crit              integer,

    b_damage            integer,
    d_damage            integer,
    f_damage            integer,
    i_damage            integer,
    l_damage            integer,
    m_damage            integer,
    s_damage            integer,

    b_pserve            integer,
    d_pserve            integer,
    f_pserve            integer,
    i_pserve            integer,
    l_pserve            integer,
    m_pserve            integer,
    s_pserve            integer,

    b_resist            integer,
    d_resist            integer,
    f_resist            integer,
    i_resist            integer,
    l_resist            integer,
    m_resist            integer,
    s_resist            integer
);


CREATE TABLE deck (
    id      integer primary key autoincrement,
    name    text,
    spell   text,
    count   integer
);

"""

INIT_DECK_QUERY = """
CREATE TABLE deck (
    id      integer primary key autoincrement,
    name    text,
    spell   text,
    count   integer
);
"""

def convert_stat(stat):
    match stat.kind:
        case 1: return 1, stat.category, stat.value
        case 2: return 2, stat.pips, stat.power_pips
        case 3: return 3, stat.spell, stat.count
        case 4: return 4, stat.spell, stat.desc_key.id
        case 5: return 5, stat.multiplier, 0
        case 6: return 6, stat.count, 0

        case _: raise RuntimeError()


def convert_equip_reqs(reqs):
    level = 0
    school = 0

    for req in reqs:
        match req.id:
            case 1: level = req.level
            case 2: school = req.school

    return school, level


def _progress(_status, remaining, total):
    print(f'Copied {total-remaining} of {total} pages...')


def build_db(state, items, mobs, pets, fish, decks, stat_caps, out):
    mem = sqlite3.connect(":memory:")
    cursor = mem.cursor()

    initialize(cursor)
    insert_locale_data(cursor, state.cache)
    insert_spell_data(cursor, state.spells)
    insert_set_bonuses(cursor, state.bonuses)
    insert_items(cursor, items)
    insert_mobs(cursor, mobs)
    insert_pets(cursor, pets)
    insert_fish(cursor, fish)
    insert_decks(cursor, decks)
    insert_statcaps(cursor, stat_caps)
    mem.commit()

    with out:
        mem.backup(out, pages=1)

    mem.close()
    
def build_deck_db(decks, out):
    mem = sqlite3.connect(":memory:")
    cursor = mem.cursor()

    cursor.executescript(INIT_DECK_QUERY)
    insert_decks(cursor, decks)
    mem.commit()

    with out:
        mem.backup(out, pages=1)

    mem.close()


def initialize(cursor):
    cursor.executescript(INIT_QUERIES)


def insert_locale_data(cursor, cache: LangCache):
    cursor.executemany(
        "INSERT INTO locale_en(id, data) VALUES (?, ?)",
        cache.lookup.items()
    )

def insert_effect(cursor: Cursor, i, effect, parent_id):
    # Insert the current effect into the database
    cursor.execute(
        """
        INSERT INTO spell_effects (
            spell_id, parent_id, idx, effect_class, param, disposition, target, 
            type, heal_modifier, rounds, pip_num, protected, rank, school, condition
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            effect.spell_id,
            parent_id,
            i,
            effect.effect_class.value,
            effect.param,
            effect.disposition,
            effect.target,
            effect.type,
            effect.heal_modifier,
            effect.rounds,
            effect.pip_num,
            effect.protected,
            effect.rank,
            effect.school,
            effect.condition,
        )
    )
    
    # Get the ID of the inserted effect
    current_id = cursor.lastrowid
    
    # Recursively insert sub-effects
    for j, sub_effect in enumerate(effect.sub_effects):
        insert_effect(cursor, j, sub_effect, current_id)

def insert_spell_data(cursor: Cursor, cache: SpellCache):
    spells = []
    effects = []
    spell_effects = []
    for template, spell in cache.cache.items():
        spells.append((
            template,
            spell.name.id,
            spell.real_name,
            spell.image,
            spell.accuracy,
            spell.energy,
            spell.school,
            spell.description.id,
            spell.type_name,
            spell.pve,
            spell.pvp,
            spell.levelreq,
            spell.rank,
            spell.x_pips,
            spell.shadow_pips,
            spell.fire_pips,
            spell.ice_pips,
            spell.storm_pips,
            spell.myth_pips,
            spell.life_pips,
            spell.death_pips,
            spell.balance_pips,
        ))

        for i in range(len(spell.effect_params)):
            effects.append((
                template,
                i,
                spell.effect_params[i],
                spell.damage_types[i],
                spell.num_rounds[i],
            ))
        
        for effect in enumerate(spell.spell_effects):
            spell_effects.append(effect)

    cursor.executemany(
        "INSERT INTO spells(template_id,name,real_name,image,accuracy,energy,school,description,form,pve,pvp,levelreq,rank,x_pips,shadow_pips,fire_pips,ice_pips,storm_pips,myth_pips,life_pips,death_pips,balance_pips) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        spells
    )

    cursor.executemany(
        """INSERT INTO effects (spell, indx, param, damage, rounds) 
        VALUES (?, ?, ?, ?, ?)""",
        effects
    )
    
    for i, effect in spell_effects:
        insert_effect(cursor, i, effect, parent_id=-1)


def insert_set_bonuses(cursor, cache: SetBonusCache):
    set_bonuses = []
    set_stats = []

    for template, bonus in cache.cache.items():
        set_bonuses.append((template, bonus.name.id))
        for bonus in bonus.bonuses:
            for stat in bonus.stats:
                set_stats.append((template, bonus.activate_count, *convert_stat(stat)))
    
    cursor.executemany(
        "INSERT INTO set_bonuses (id,name) VALUES (?,?)",
        set_bonuses
    )
    cursor.executemany(
        """INSERT INTO set_stats (bonus_set,activate_count,kind,a,b) VALUES (?,?,?,?,?)""",
        set_stats
    )


def insert_items(cursor, items):
    values = []
    talents = []
    stats = []

    for item in items:
        values.append((
            item.template_id,
            item.name.id,
            item.real_name,
            item.set_bonus_id,
            item.rarity,
            item.jewel_sockets.value,
            item.adjectives & 0xFFFF,
            item.adjectives >> 16,
            *convert_equip_reqs(item.equip_reqs),
            item.min_pet_level,
            item.max_spells,
            item.max_copies,
            item.max_school_copies,
            item.deck_school,
            item.max_tcs,
            item.archmastery_points,
        ))

        if item.min_pet_level != 0:
            for talent in item.pet_talents:
                talents.append((item.template_id, talent.name.id))

        for stat in item.stats:
            stats.append((item.template_id, *convert_stat(stat)))
    
    cursor.executemany(
        "INSERT INTO items(id,name,real_name,bonus_set,rarity,jewels,kind,extra_flags,equip_school,equip_level,min_pet_level,max_spells,max_copies,max_school_copies,deck_school,max_tcs,archmastery_points) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        values
    )
    cursor.executemany(
        """INSERT INTO item_stats(item,kind,a,b) VALUES (?,?,?,?)""",
        stats
    )
    cursor.executemany("INSERT INTO pet_talents (item,name) VALUES (?,?)", talents)

def insert_mobs(cursor, mobs):
    values = []
    stats = []
    items = []
    spells = []

    for mob in mobs:
        values.append((
            mob.template_id,
            mob.name.id,
            mob.real_name,
            mob.image,
            mob.title,
            mob.rank,
            mob.hitpoints,
            mob.primarySchool,
            mob.secondarySchool,
            mob.stunnable,
            mob.max_shadow,
            mob.has_cheats,
            mob.intelligence,
            mob.selfishFactor,
            mob.aggressiveFactor,
            mob.adjectives,
        ))

        for stat in mob.stats:
            stats.append((mob.template_id, *convert_stat(stat)))

        for item in mob.items:
            items.append((mob.template_id, item))
            
        for spell, count in mob.spells.items():
            spells.append((
                mob.real_name,
                spell,
                count
            ))

    cursor.executemany(
        "INSERT INTO mobs(id,name,real_name,image,title,rank,hp,primary_school,secondary_school,stunnable,max_shadow,has_cheats,intelligence,selfishness,aggressiveness,monstro) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        values
    )
    cursor.executemany(
        """INSERT INTO mob_stats(mob,kind,a,b) VALUES (?,?,?,?)""",
        stats
    )
    cursor.executemany(
        """INSERT INTO mob_items(mob,item) VALUES (?,?)""",
        items
    )
    
    cursor.executemany(
        "INSERT INTO deck(id,name,spell,count) VALUES (NULL,?,?,?)",
        spells
    )


def insert_pets(cursor, pets):
    values = []
    talents = []
    cards = []

    for pet in pets:
        values.append((
            pet.template_id,
            pet.name.id,
            pet.real_name,
            pet.set_bonus_id,
            pet.rarity,
            pet.adjectives,
            pet.wow_factor,
            pet.exclusive,
            pet.school,
            pet.egg_name,
            pet.strength,
            pet.intellect,
            pet.agility,
            pet.will,
            pet.power
        ))

        for talent in pet.talents:
            talents.append((pet.template_id, talent[0], talent[1].id))

        for talent in pet.derby:
            talents.append((pet.template_id, talent[0], talent[1].id))

        for card in pet.cards:
            cards.append((pet.template_id, card))
    
    cursor.executemany(
        "INSERT INTO pets(id,name,real_name,bonus_set,rarity,extra_flags,wow_factor,exclusive,school,egg_name,strength,intellect,agility,will,power) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        values
    )
    cursor.executemany(
        """INSERT INTO talents(pet,priority,talent) VALUES (?,?,?)""",
        talents
    )
    cursor.executemany(
        """INSERT INTO pet_cards(pet,spell) VALUES (?,?)""",
        cards
    )
    
def insert_fish(cursor, fishs):
    values = []

    for fish in fishs:
        values.append((
            fish.template_id,
            fish.name.id,
            fish.real_name,
            fish.rank,
            fish.school,
            fish.base_length,
            fish.min_size,
            fish.max_size,
            fish.speed,
            fish.bite_seconds,
            fish.initial_bite_chance,
            fish.incremental_bite_chance,
            fish.is_sentinel
        ))
        
    cursor.executemany(
        "INSERT INTO fish(id,name,real_name,rank,school,base_length,min_size,max_size,speed,bite_seconds,initial_bite_chance,incremental_bite_chance,is_sentinel) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
        values
    )
    
def insert_decks(cursor, decks):
    values = []

    for deck in decks:
        for spell, count in deck.spells.items():
            values.append((
                deck.name,
                spell,
                count
            ))
        
    cursor.executemany(
        "INSERT INTO deck(id,name,spell,count) VALUES (NULL,?,?,?)",
        values
    )

def insert_statcaps(cursor, stat_caps):
    values = []

    for stat_cap in stat_caps:
        stat_cap: StatCap
        values.append((
            stat_cap.level,
            stat_cap.school,
            stat_cap.max_pips,
            stat_cap.max_power_pips,
            stat_cap.max_health,
            stat_cap.max_mana,
            stat_cap.ppc,
            stat_cap.shadow_pip_rating,
            stat_cap.archmastery,
            stat_cap.out_healing,
            stat_cap.inc_healing,
            stat_cap.b_acc,
            stat_cap.d_acc,
            stat_cap.f_acc,
            stat_cap.i_acc,
            stat_cap.l_acc,
            stat_cap.m_acc,
            stat_cap.s_acc,
            stat_cap.b_ap,
            stat_cap.d_ap,
            stat_cap.f_ap,
            stat_cap.i_ap,
            stat_cap.l_ap,
            stat_cap.m_ap,
            stat_cap.s_ap,
            stat_cap.b_block,
            stat_cap.d_block,
            stat_cap.f_block,
            stat_cap.i_block,
            stat_cap.l_block,
            stat_cap.m_block,
            stat_cap.s_block,
            stat_cap.b_crit,
            stat_cap.d_crit,
            stat_cap.f_crit,
            stat_cap.i_crit,
            stat_cap.l_crit,
            stat_cap.m_crit,
            stat_cap.s_crit,
            stat_cap.b_damage,
            stat_cap.d_damage,
            stat_cap.f_damage,
            stat_cap.i_damage,
            stat_cap.l_damage,
            stat_cap.m_damage,
            stat_cap.s_damage,
            stat_cap.b_pserve,
            stat_cap.d_pserve,
            stat_cap.f_pserve,
            stat_cap.i_pserve,
            stat_cap.l_pserve,
            stat_cap.m_pserve,
            stat_cap.s_pserve,
            stat_cap.b_resist,
            stat_cap.d_resist,
            stat_cap.f_resist,
            stat_cap.i_resist,
            stat_cap.l_resist,
            stat_cap.m_resist,
            stat_cap.s_resist,
        ))
    
    cursor.executemany(
        """INSERT INTO statcaps (level, school, max_pips, max_power_pips, hp, mana, ppc, shad_rating, archmastery, outgoing, incoming, b_acc, d_acc, f_acc, i_acc, l_acc, m_acc, s_acc, b_ap, d_ap, f_ap, i_ap, l_ap, m_ap, s_ap, b_block, d_block, f_block, i_block, l_block, m_block, s_block, b_crit, d_crit, f_crit, i_crit, l_crit, m_crit, s_crit, b_damage, d_damage, f_damage, i_damage, l_damage, m_damage, s_damage, b_pserve, d_pserve, f_pserve, i_pserve, l_pserve, m_pserve, s_pserve, b_resist, d_resist, f_resist, i_resist, l_resist, m_resist, s_resist) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        values
    )


