class Talent:
    def __init__(self, template_id: int, state, obj: dict):
        self.template_id = template_id
        self.name = state.make_lang_key(obj)


class TalentCache:
    def __init__(self, state):
        self.cache = {}
        self.name_to_id = {}

        for file, template in state.file_to_id.items():
            if not file.startswith("TalentData/"):
                continue

            value = state.de.deserialize_from_path((state.root_wad / file))

            talent = Talent(template, state, value)
            self.cache[template] = talent
            self.name_to_id[value["m_talentName"].decode()] = template

    def get(self, name: str) -> Talent:
        if tid := self.name_to_id.get(name):
            return self.cache[tid]
        else:
            return None
