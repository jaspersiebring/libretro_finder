# libretro_finder
[![PyPI](https://img.shields.io/pypi/v/libretro-finder)](https://pypi.org/project/libretro-finder/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/libretro-finder)
![PyPI - License](https://img.shields.io/pypi/l/libretro-finder)

Simple command line utility that recursively looks for specific BIOS files for RetroArch cores and, if found, refactors them to the expected format as documented by Libretro [here](https://github.com/libretro/libretro-database/blob/4a98ea9726b3954a4e5a940d255bd14c307ddfba/dat/System.dat) (i.e. name and directory structure). This is useful if you source your BIOS files from many different places and have them saved them under different names (often with duplicates). This script is able to find these exact BIOS files by comparing their hashes against their known counterparts. Uses concurrency and vectorization for added performance.   

This repository does **NOT** include the BIOS files themselves.

## Installation
Available through the Python Package Index (PyPI):

````
# with pip
pip install libretro-finder

# with poetry
poetry add libretro-finder
````

## Example of usage:
````
some_user@some_machine:~ libretro_finder ~/Downloads/bios_files/ ~/Downloads/libretro_bios

89 matching BIOS files were found for 3 unique systems:
        Sega - Mega Drive - Genesis (1)
        Sony - PlayStation (19)
        Sony - PlayStation 2 (69)
100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 89/89 [00:00<00:00, 617.57it/s]
````

You can also safely use the `system` directory of retroarch as `output_dir` since we never overwrite files (i.e. libretro_finder only adds to your list of BIOS files)  
````
some_user@some_machine:~ libretro_finder ~/Downloads/bios_files/ ~/.config/retroarch/system/

89 matching BIOS files were found for 3 unique systems:
        Sega - Mega Drive - Genesis (1)
        Sony - PlayStation (19)
        Sony - PlayStation 2 (69)
100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 89/89 [00:00<00:00, 617.57it/s]
````

You can also use libretro's `system` directory as `search_dir` to find all aliased BIOS files (i.e. identical BIOS files that are usable by different cores for the same system but just under different names). 

````
some_user@some_machine:~ libretro_finder ~/.config/retroarch/system/ ~/.config/retroarch/system/

89 matching BIOS files were found for 3 unique systems:
        Sega - Mega Drive - Genesis (1)
        Sony - PlayStation (19)
        Sony - PlayStation 2 (69)
100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 89/89 [00:00<00:00, 617.57it/s]
````

Help page:
````
some_user@some_machine:~ libretro_finder --help

Local BIOS file scraper for Retroarch

positional arguments:
  search_dir            Directory to look for BIOS files
  output_dir            Directory to refactor found BIOS files to

optional arguments:
  -h, --help            show this help message and exit
````