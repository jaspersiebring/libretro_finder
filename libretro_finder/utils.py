import pathlib
import hashlib
import concurrent.futures
from typing import Tuple, List
from config import MAX_BIOS_BYTES

def hash_file(file_path: pathlib.Path) -> str:
    """

    :param file_path:
    :return:
    """

    bytes = file_path.read_bytes()
    hash = hashlib.md5(bytes)
    return hash.hexdigest()

def recursive_hash(directory: pathlib.Path, glob: str = "*") -> Tuple[List[pathlib.Path], List[str]]:
    """

    :param directory:
    :param glob:
    :return:
    """

    file_paths = list(directory.rglob(pattern=glob))
    file_paths = [file_path for file_path in file_paths if file_path.stat().st_size <= MAX_BIOS_BYTES and file_path.is_file()]

    file_hashes = []            
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for hash in executor.map(hash_file, file_paths):
            file_hashes.append(hash)
    return file_paths, file_hashes