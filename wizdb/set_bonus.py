class Bonus:
    def __init__(self, stats: list, activate_count: int):
        self.activate_count = activate_count
        self.stats = stats


class SetBonus:
    def __init__(self, state, obj: dict):
        self.name = state.make_lang_key(obj)

        self.bonuses = []
        for bonus in obj["m_itemSetBonusDataList"]:
            stats = []
            for effect in bonus["m_equipEffectsGranted"]:
                if stat := state.translate_stat(effect):
                    stats.append(stat)

            self.bonuses.append(Bonus(stats, bonus["m_numItemsToEquip"]))


class SetBonusCache:
    def __init__(self):
        self.cache = {}

    def add(self, state, template: int) -> int:
        if template == 0:
            return 0

        if template in self.cache:
            return template

        filename = state.id_to_file.get(template)
        if filename is None:
            return 0

        file = state.root_wad / filename
        value = state.de.deserialize_from_path(file)

        self.cache[template] = SetBonus(state, value)
        return template
