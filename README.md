# libretro_finder
[![PyPI](https://img.shields.io/pypi/v/libretro-finder)](https://pypi.org/project/libretro-finder/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/libretro-finder)
![PyPI - License](https://img.shields.io/pypi/l/libretro-finder)

Simple tool that finds and prepares your BIOS files for usage with Libretro (or its RetroArch frontend).  

No more need to manually select, rename and move your BIOS files to some RetroArch installation somewhere, just dump them in LibretroFinder and let it sort it out for you. It does this by generating checksums for your local files (i.e. unique identifiers) and comparing them against their known counterparts as documented by Libretro [here](https://github.com/libretro/libretro-database/blob/4a98ea9726b3954a4e5a940d255bd14c307ddfba/dat/System.dat). It then refactors *copies* of all matching files to the format expected by Libretro (name *and* folder structure). 

This repository does **NOT** include the BIOS files themselves.

## Features
- Simple graphical user interface (GUI)
- Scriptable command line interface (CLI)
- Works on Windows, Linux and MacOS
- Available through the Python Package Index (Python >=3.8) 
- Available as portable executable (currently only on X86 Windows machines)


<p float="left">
  <img src="https://github.com/jaspersiebring/libretro_finder/assets/25051531/36e3a236-ef4f-46e2-bcf3-19fe0ddb4e65" width="45%" height = 250/>
  <img src="https://github.com/jaspersiebring/libretro_finder/assets/25051531/280f6d97-1232-48ee-8dc4-e6cd229263ad" width="45%" height = 250 />
</p>

# Installation

Installing from the Python Package Index (PyPI):
````
# Install from PYPI with Python's package installer (pip)
pip install libretro-finder

# [Optional] Install as isolated application through pipx (https://pypa.github.io/pipx/)
pipx install libretro-finder
````
You can also download the prebuilt standalone executable which includes Python and all the program's dependencies, no installation required (currently only available for X86 Windows machines). See [releases](https://github.com/jaspersiebring/libretro_finder/releases).

<p float="left">
  <img src="https://github.com/jaspersiebring/libretro_finder/assets/25051531/3ee6056c-0311-4071-8423-2b120ffff68e" width="150" height = 130/>
</p>

## Example of usage

#### Command line interface

If installed with pip, LibretroFinder can be called directly from your preferred terminal by running `libretro_finder`. You can use the tool entirely from your terminal by providing values for the search directory (e.g. `~/Downloads/bios_files/`) and the output directory (`~/.config/retroarch/system/`):

````
some_user@some_machine:~ libretro_finder ~/Downloads/bios_files/ ~/.config/retroarch/system/
Hashing files: 100%|█████████████████████████████████████████████████████████████████████████████████| 983/983 [00:00<00:00, 3333.95it/s]
89 matching BIOS files were found for 3 unique systems:
        Sega - Mega Drive - Genesis (1)
        Sony - PlayStation (19)
        Sony - PlayStation 2 (69)
````

Although the output directory defaults to retroarch's `system` folder (if `retroarch` was found), you can manually specify whatever output folder you want and `libretro_finder` will create it for you. If your path contains spaces, wrap it in double quotes like so:

````
some_user@some_machine:~ libretro_finder "D:\Games\My Roms" "C:\Program Files (x86)\Steam\steamapps\common\RetroArch\system"
Hashing files: 100%|█████████████████████████████████████████████████████████████████████████████████| 983/983 [00:00<00:00, 3333.95it/s]
89 matching BIOS files were found for 3 unique systems:
        Sega - Mega Drive - Genesis (1)
        Sony - PlayStation (19)
        Sony - PlayStation 2 (69)
````
No matter what you select as search- or output directory, rest assured that no existing files on your file system will be modified. You can also call `libretro_finder` with `--help` to get some more information on the expected input:  
````
some_user@some_machine:~ libretro_finder --help

Locate and prepare your BIOS files for libretro.

positional arguments:
  Search directory  Where to look for BIOS files
  Output directory  Where to output refactored BIOS files (defaults to ./retroarch/system)

optional arguments:
  -h, --help            show this help message and exit
````


#### Graphical user interface

If `libretro_finder` is called without any additional arguments, LibretroFinder will start with a graphical interface. This is functionally identical to the CLI version with the only real difference that it automatically tries to set the output directory to retroarch's `system` folder. 

<p float="left">
  <img src="https://github.com/jaspersiebring/libretro_finder/assets/25051531/36e3a236-ef4f-46e2-bcf3-19fe0ddb4e65" width="45%" />
  <img src="https://github.com/jaspersiebring/libretro_finder/assets/25051531/2b74cc06-c031-466a-9eaa-24135be06194" width="45%"  />
</p>


### Missing features? Have some feedback? Let me know!
- [My Reddit account](https://www.reddit.com/user/qtieb/)
- [My Github account](https://github.com/jaspersiebring)