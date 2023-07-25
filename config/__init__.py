import pathlib
import re
import urllib.request

import pandas as pd

# not expecting BIOS files over 15mb
MAX_BIOS_BYTES = 15728640
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
index = 0 # pylint: disable=invalid-name
SYSTEMS = []
with open(FILE_PATH, "r", encoding='utf-8') as file:
    for line in file:
        line = line.strip()
        if line.startswith("comment"):
            current_system = line.split('"')[1]
        elif line.startswith("rom"):
            match = re.search(
                r"name (\S+)(?: size (\S+))?(?: crc (\S+))?(?: md5 (\S+))?(?: sha1 (\S+))?",
                line,
            )
            data = {
                "system": current_system,
                "name": match.group(1).replace('"', "").replace("'", ""),
                "size": match.group(2) if match.group(2) else None,
                "crc": match.group(3) if match.group(3) else None,
                "md5": match.group(4) if match.group(4) else None,
                "sha1": match.group(5) if match.group(5) else None,
            }
            SYSTEMS.append(pd.DataFrame(data, index=[index]))
            index += 1

# join dfs and drop features without checksums
SYSTEMS = pd.concat(SYSTEMS)
SYSTEMS = SYSTEMS[~SYSTEMS["md5"].isnull()].reset_index(drop=True)
