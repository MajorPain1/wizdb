from pathlib import Path

from .utils import fnv_1a


# https://github.com/StarrFox/wizwalker/blob/master/wizwalker/file_readers/cache_handler.py#L114
def _parse_lang_file(file_data: bytes) -> dict:
    try:
        decoded = file_data.decode("utf-16")
    except UnicodeDecodeError:
        # empty file
        return {}

    file_lines = decoded.split("\r\n")

    header, *lines = file_lines
    _, lang_name = header.split(":")

    lang_mapping = {}
    for locale_id, locale_string in zip(lines[::3], lines[2::3]):
        lang_mapping[f"{lang_name}_{locale_id}"] = locale_string

    return lang_mapping


class LangCache:
    def __init__(self, locale_dir: Path):
        self.locale = locale_dir
        self.lookup = {}

    def add_entry(self, key: bytes, value: str) -> int:
        key = fnv_1a(key)
        self.lookup[key] = value
        return key

    def find_entry(self, key):
        key_hash = fnv_1a(key)

        if self.lookup.get(key_hash) is None:
            file, _ = key.decode().split("_", 1)
            self.add_file((self.locale / file).with_suffix(".lang"))

        if self.lookup.get(key_hash) is not None:
            return key_hash
        else:
            return None

    def add_file(self, path: Path):
        data = path.read_bytes()
        mapping = _parse_lang_file(data)

        for key, name in mapping.items():
            self.add_entry(key, name)


class LangKey:
    def __init__(self, cache: LangCache, obj: dict):
        key = obj["m_displayName"]
        if key == b"":
            self.id = None
            return

        self.id = cache.find_entry(key)
        if self.id is None:
            return
