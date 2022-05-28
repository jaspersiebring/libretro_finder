import json
import os
from .core_names import Core


# Contains BIOS filenames and md5 hashes from https://docs.libretro.com/
json_path = os.path.join(os.path.dirname(__file__), "BIOS_SPECS.json")

with open(json_path) as json_file:
    BIOS_SPECS = json.load(json_file)

all_cores = list(Core.__dict__['_member_map_'].values())
all_cores = [c for c in all_cores if c.value != 0]
core_dict = dict([[c.value, c.name] for c in all_cores])