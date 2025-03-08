from pathlib import Path

from katsuba.op import * # type: ignore
from katsuba.wad import Archive # type: ignore

class BinDeserializer:
    def __init__(self, root_wad, types_path: Path):
        opts = SerializerOptions()
        opts.flags = 1
        opts.shallow = False
        opts.skip_unknown_types = True
        
        self.archive = Archive.mmap(root_wad)
        
        self.types = TypeList.open_many((types_path, "mobdeckbehaviortypes.json"))

        self.ser = Serializer(opts, self.types)

    def deserialize(self, data):
        return self.ser.deserialize(data)
    
    def deserialize_from_path(self, path: str):
        return self.archive.deserialize(path, self.ser)