# RetroArch BIOS Scraper
Local BIOS file scraper for Retroarch cores 

````
Local BIOS file scraper for Retroarch

positional arguments:
  search_dir            Directory to look for BIOS files
  output_dir            Directory to save found BIOS files to

optional arguments:
  -h, --help            show this help message and exit
  -g GLOB, --glob GLOB  Directory to save found BIOS files to (default: *)
  -c CORE, --core CORE  Only look for BIOS files associated with a specific Retroarch core ({1: 'BEETLE_PSX', 2: 'BEETLE_PSX_HW'}, 0 is
                        all keys) (default: 0)
  -v, --verbose         Increase verbosity (default: False)
```` 

### Example of usage:
````
Multiple matches found for: BEETLE_PSX.PS1_EU_BIOS (scph5502.bin). Pick one from the following options:
Option (a):
         NAME: PSX - SCPH5552.bin
         DIR: /home/some_user/Downloads/bios_files/
         SIZE: 512.0KiB (524288)
         CREATED: 2022-05-27 23:46:51.209432
         MODIFIED: 2022-05-27 23:46:38.752924

Option (b):
         NAME: scph5552 (ps-30e).bin
         DIR: /home/some_user/Downloads/bios_files/
         SIZE: 512.0KiB (524288)
         CREATED: 2022-05-27 22:52:46.061768
         MODIFIED: 2021-04-24 12:23:07.038451

Option (c):
         NAME: scph5552.bin
         DIR: C:\Users\jaspe\Downloads\misc
         SIZE: 512.0KiB (524288)
         CREATED: 2022-05-27 23:59:26.472520
         MODIFIED: 2022-05-27 23:46:38.752924

Pick option (a-c):
````
