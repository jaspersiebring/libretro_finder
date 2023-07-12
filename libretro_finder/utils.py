import concurrent.futures
import hashlib
import pathlib
from typing import Tuple

import numpy as np

from config import MAX_BIOS_BYTES


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
        if file_path.stat().st_size <= MAX_BIOS_BYTES and file_path.is_file()
    ]

    file_hashes = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for file_hash in executor.map(hash_file, file_paths):
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