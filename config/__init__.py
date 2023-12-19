import sys
import pathlib
import re
import urllib.request

import pandas as pd
from libretro_finder.utils import find_retroarch

SEED = 0

# Pulling all BIOS names and hashes from Libretro's system.dat (https://docs.libretro.com/)
FILE_PATH = pathlib.Path(__file__).parent / "system.dat"
GITHUB_URL = (
    "https://raw.githubusercontent.com/libretro/libretro-database/master/dat/System.dat"
)
if not FILE_PATH.exists():
    print("Getting BIOS names from libretro-database..")
    urllib.request.urlretrieve(GITHUB_URL, FILE_PATH)
    print("Done.")

# Parsing Libretro's system.dat and formatting as pandas dataframe
system_series = []
with open(FILE_PATH, "r", encoding="utf-8") as file:
    for line in file:
        line = line.strip()
        if line.startswith("comment"):
            current_system = line.split('"')[1]
            continue
        
        regex_string = r'\brom.+name\s+(?P<name>"[^"]+"|\S+)(?:(?:(?:\s+size\s+(?P<size>\S+))|(?:\s+crc\s+(?P<crc>\S+))|(?:\s+md5\s+(?P<md5>\S+))|(?:\s+sha1\s+(?P<sha1>\S+)))(?=\s|$))*'
        match = re.search(regex_string, line)
        
        if match:
            data = match.groupdict()
            data["system"] = current_system
            data["name"] = data["name"].replace('"', "")
            system_series.append(data)

# join dfs and drop features without checksums
SYSTEMS = pd.DataFrame(system_series)
SYSTEMS = SYSTEMS[~SYSTEMS["md5"].isnull()].reset_index(drop=True)

# path to retroarch/system (if found)
RETROARCH_PATH = find_retroarch()

# 'cli' if user passes arguments else 'start gui'
# Needs to be present before the @Gooey decorator (https://github.com/chriskiehl/Gooey/issues/449)
if len(sys.argv) >= 2:
    if "--ignore-gooey" not in sys.argv:
        sys.argv.append("--ignore-gooey")
