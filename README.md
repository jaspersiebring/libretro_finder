# libretro_finder
Simple command line utility that looks for specific BIOS files for RetroArch cores and, if found, refactors them to the expected format as documented by Libretro [here](https://github.com/libretro/libretro-database/blob/4a98ea9726b3954a4e5a940d255bd14c307ddfba/dat/System.dat)(i.e. name and directory structure). This is useful if you source your BIOS files from many different places and have them saved them under different names (often with duplicates). This script is able to find these exact BIOS files by comparing their hashes against their known counterparts.

This repository does **NOT** include the BIOS files themselves.

Only requires Python 3.6 (due to f-strings, type hinting, enum, etc.) and should work on Windows, Linux and Mac.


## Installation
Available through the Python Package Index (PyPI):

````
# with pip
pip install libretro-finder

# with poetry
poetry add libretro-finder
````

## Example of usage:
You can safely use the `system` directory of retroarch as `output_dir` since we also check existing files against the known hashes (we'll only dump them if they're not present yet). Any folder structure expected by libretro is respected (if documented).  
````
some_user@some_machine ~/repos/retroarch_bios_scraper python main.py ~/Downloads/bios_files/ ~/.config/retroarch/system/

89 matching BIOS files were found for 3 unique systems:
        Sega - Mega Drive - Genesis (1)
        Sony - PlayStation (19)
        Sony - PlayStation 2 (69)
100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 89/89 [00:00<00:00, 617.57it/s]
````
````
some_user@some_machine ~/repos/retroarch_bios_scraper python main.py --help

Local BIOS file scraper for Retroarch

positional arguments:
  search_dir            Directory to look for BIOS files
  output_dir            Directory to copy found BIOS files to

optional arguments:
  -h, --help            show this help message and exit
  -g GLOB, --glob GLOB  Glob pattern to use for file matching
  -o, --overwrite       Overwrite boolean 
````