import os
import concurrent.futures
import hashlib
import pathlib
from typing import Tuple, Optional, List, Union
from tqdm import tqdm
import numpy as np
import vdf
import platform
from string import ascii_uppercase

# not expecting BIOS files over 15mb
MAX_BIOS_BYTES = 15728640


def hash_file(file_path: pathlib.Path) -> str:
    """

    :param file_path:
    :return:
    """

    file_bytes = file_path.read_bytes()
    file_hash = hashlib.md5(file_bytes)
    return file_hash.hexdigest()


def recursive_hash(
    directory: pathlib.Path, glob: str = "*"
) -> Tuple[np.ndarray, np.ndarray]:
    """

    :param directory:
    :param glob:
    :return:
    """

    file_paths = list(directory.rglob(pattern=glob))
    file_paths = [
        file_path
        for file_path in file_paths
        if file_path.exists()
        and file_path.stat().st_size <= MAX_BIOS_BYTES
        and file_path.is_file()
    ]

    file_hashes = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for file_hash in tqdm(
            executor.map(hash_file, file_paths),
            total=len(file_paths),
            desc="Hashing files",
        ):
            file_hashes.append(file_hash)
    return np.array(file_paths), np.array(file_hashes)


def match_arrays(
    array_a: np.ndarray, array_b: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Element-wise array comparison, returns unique values and matching indices per input array

    :param array_a:
    :param array_b:
    :return:
    """

    # expecting 1D arrays
    if np.sum([len(array_a.shape), len(array_b.shape)]) > 2:
        raise ValueError("input arrays need to be one-dimensional, exiting..")

    comparisons = np.equal(array_a.reshape(1, -1), array_b.reshape(-1, 1))

    indices_b, indices_a = np.where(comparisons)
    matching_values = np.unique(array_a[indices_a])

    return matching_values, indices_a, indices_b


def check_env_var(var_name: str) -> Optional[str]:
    """
    This function checks if a specific environment variable exists in the system.

    Args:
        var_name (str): The name of the environment variable to check.

    Returns:
        Optional[str]: The value of the environment variable if it exists, None otherwise.
    """

    if var_name in os.environ:
        return os.environ[var_name]
    else:
        return None


def list_steam_libraries(path: pathlib.Path) -> List[pathlib.Path]:
    library_paths = []
    with open(path, "r", encoding="utf-8") as src:
        library_info = vdf.parse(src)
        for key in library_info["libraryfolders"].keys():
            library_path = pathlib.Path(library_info["libraryfolders"][key]["path"])
            if library_path.exists():
                library_paths.append(library_path)

    return library_paths


def find_retroarch() -> Optional[pathlib.Path]:
    paths_to_check = []
    system = platform.system()

    if system == "Windows":
        system_glob = "RetroArch*/system"
        # Non-Steam
        drives = [
            pathlib.Path(f"{drive}:").resolve()
            for drive in ascii_uppercase
            if pathlib.Path(f"{drive}:").exists()
        ]
        for drive in drives:
            paths_to_check.append(drive)

        env_vars = ["PROGRAMFILES(X86)", "PROGRAMFILES"]
        for env_var in env_vars:
            env_var = check_env_var(var_name=env_var)
            env_path = pathlib.Path(env_var)

            if env_path.exists():
                paths_to_check.append(env_path)

                # adding steam libraries
                vdf_path = env_path / pathlib.Path(
                    "Steam", "steamapps", "libraryfolders.vdf"
                )
                if vdf_path.exists():
                    for library_path in list_steam_libraries(path=vdf_path):
                        paths_to_check.append(
                            library_path / pathlib.Path("steamapps/common")
                        )

    elif system == "Linux":
        # system_glob = "retroarch/system"
        # home = pathlib.Path.home()
        # paths_to_check.append(home / pathlib.Path(".config"))
        # Linux: ~/.local/share/Steam/steamapps/libraryfolders.vdf
        raise NotImplementedError("To be implemented..")
    elif system == "Darwin":
        # MacOS: ~/Library/Application Support/Steam/steamapps/libraryfolders.vdf
        raise NotImplementedError("To be implemented..")

    # checking for retroarch/system (one level down)
    for path_to_check in paths_to_check:
        # glob is needed for installers (e.g. RetroArch-Win32)
        for path in path_to_check.glob(system_glob):
            return path
    return None


# path to retroarch installation (if found)
RETROARCH_PATH = find_retroarch()
