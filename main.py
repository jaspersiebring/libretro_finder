import argparse
import os
import hashlib
import shutil
import string
import pathlib
import datetime
from config import BIOS_SPECS
from config import Core
from config import core_dict
from config import all_cores


def check_hash(file: pathlib.Path, md5sum: str) -> bool:
    """

    :param file:
    :param md5sum:
    :return:
    """

    bytes = file.read_bytes()
    hash = hashlib.md5(bytes)
    return hash.hexdigest() == md5sum


def sizeof_fmt(num: int, suffix: str ="B") -> str:
    """

    :param num:
    :param suffix:
    :return:
    """

    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def find_hash_match(directory: pathlib.Path, md5sum: str, glob: str = "*") -> list:
    """

    :param directory:
    :param md5sum:
    :param glob:
    :return:
    """

    max_n_bytes = 15728640 # not expecting BIOS files over 15mb
    matches = []

    file_gen = directory.rglob(pattern=glob)
    for file in file_gen:
        if file.stat().st_size > max_n_bytes or not file.is_file():
            continue
        check = check_hash(file=file, md5sum=md5sum)
        if check:
            matches.append(file)
    return matches


def scrape_bios(directory: pathlib.Path, output_dir: pathlib.Path, core: Core, glob: str = "*"):
    """

    :param directory:
    :param output_dir:
    :param core:
    :param glob:
    :return:
    """

    missing_bios = []
    present_bios = []
    os.makedirs(output_dir, exist_ok=True)

    for bios_key in BIOS_SPECS[core.name].keys():
        filename = BIOS_SPECS[core.name][bios_key]['filename']
        md5sum = BIOS_SPECS[core.name][bios_key]['md5sum']
        bios_dst = output_dir.joinpath(filename)
        bios_name = ".".join([core.name, bios_key])

        if bios_dst.exists() and check_hash(file=bios_dst, md5sum=md5sum):
            present_bios.append(bios_name)
            continue

        matches = find_hash_match(directory=directory, md5sum=md5sum, glob=glob)

        if len(matches) == 0:
            missing_bios.append(bios_name)
            continue

        elif len(matches) == 1:
            shutil.copy(src=matches[0], dst=bios_dst)
            present_bios.append(bios_name)

        elif len(matches) > 1:
            print(f"Multiple matches found for: {bios_name} ({filename}). Pick one from the following options:")
            chars = list(string.ascii_lowercase)
            for i, match in enumerate(matches):
                file_stats = match.stat()
                modified_time_m = file_stats.st_mtime  # Modified
                modified_time = datetime.datetime.fromtimestamp(modified_time_m)
                created_time_m = file_stats.st_ctime  # Created
                created_time = datetime.datetime.fromtimestamp(created_time_m)
                file_size = sizeof_fmt(file_stats.st_size)

                print(f"Option ({chars[i]}): \n"
                      f"\t NAME: {match.name} \n"
                      f"\t DIR: {match.parent} \n"
                      f"\t SIZE: {file_size} ({file_stats.st_size}) \n"
                      f"\t CREATED: {created_time} \n"
                      f"\t MODIFIED: {modified_time} \n"
                      )

            choice = input(f"Pick option (a-{chars[i]}):").lower()
            if not choice in chars[:i+1]:
                raise ValueError(f"Input ({choice}) not in option list ({' '.join(chars[:i + 1])})")

            index = [i for i, c in enumerate(chars[:i + 1]) if c == choice][0]
            shutil.copy(src=matches[index], dst=bios_dst)
            present_bios.append(bios_name)

    return present_bios, missing_bios


def main(directory: pathlib.Path, output_dir: pathlib.Path, core_id: int = 0, glob: str = "*"):
    """

    :param directory:
    :param output_dir:
    :param core_id:
    :param glob:
    :return:
    """

    all_present_bios = []
    all_missing_bios = []

    if core_id == 0:
        cores = all_cores
    elif core_id not in core_dict.keys():
        raise ValueError(f"Specified core_id ({core_id}) not supported (i.e. not in {core_dict}). Exiting..")
    else:
        cores = [Core(core_id)]

    for core in cores:
        present_bios, missing_bios = scrape_bios(directory=directory, output_dir=output_dir, core=core, glob=glob)
        all_present_bios.append(present_bios)
        all_missing_bios.append(missing_bios)

    return all_present_bios, all_missing_bios


if __name__ == "__main__":
    # TODO check file permissions (try except)
    # TODO Add verbosity levels (report on found and/or dumped files)
    #rs_bios_scraper
    #retroarch_local_scraper
    #RetroArch BIOS Scraper

    parser = argparse.ArgumentParser(description="Local BIOS file scraper for Retroarch",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("search_dir", help="Directory to look for BIOS files", type = str)
    parser.add_argument("output_dir", help="Directory to save found BIOS files to", type = str)
    parser.add_argument("-g", "--glob", help="Directory to save found BIOS files to", type = str, default="*")
    parser.add_argument("-c", "--core", help=f"Only look for BIOS files associated with a specific Retroarch core ({core_dict}, 0 is all keys)", type = int, default=0)
    parser.add_argument("-v", "--verbose", help="Increase verbosity", action="store_true")
    args = vars(parser.parse_args())

    directory = pathlib.Path(args["search_dir"])
    output_dir = pathlib.Path(args["output_dir"])
    glob = args["glob"]
    core_id = args["core"]
    verbose = args["verbose"]

    all_present_bios, all_missing_bios = main(directory=directory,
                                              output_dir=output_dir,
                                              core_id=core_id,
                                              glob=glob)
