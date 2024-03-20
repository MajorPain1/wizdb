import sqlite3
from sqlite3 import Cursor

from .lang_files import LangCache
from .set_bonus import SetBonusCache
from .spell import SpellCache

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


def build_db(state, items, mobs, pets, out):
    mem = sqlite3.connect(":memory:")
    cursor = mem.cursor()

    initialize(cursor)
    insert_locale_data(cursor, state.cache)
    insert_spell_data(cursor, state.spells)
    insert_set_bonuses(cursor, state.bonuses)
    insert_items(cursor, items)
    insert_mobs(cursor, mobs)
    insert_pets(cursor, pets)
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


def insert_spell_data(cursor: Cursor, cache: SpellCache):
    spells = []
    effects = []
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



    cursor.executemany(
        "INSERT INTO spells(template_id,name,real_name,image,accuracy,energy,school,description,form,pve,pvp,rank,x_pips,shadow_pips,fire_pips,ice_pips,storm_pips,myth_pips,life_pips,death_pips,balance_pips) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        spells
    )

    cursor.executemany(
        """INSERT INTO effects (spell, indx, param, damage, rounds) 
        VALUES (?, ?, ?, ?, ?)""",
        effects
    )
    


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


    cursor.executemany(
        "INSERT INTO mobs(id,name,real_name,image,title,rank,hp,primary_school,secondary_school,max_shadow,has_cheats,intelligence,selfishness,aggressiveness,monstro) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
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


