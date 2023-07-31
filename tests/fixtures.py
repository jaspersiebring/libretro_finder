import binascii
import hashlib
import os
import pathlib
from typing import Tuple
import tempfile

import pandas as pd
import pytest
from pytest import TempPathFactory

from config import SEED
from config import SYSTEMS as system_df
from tests import TEST_SAMPLE_SIZE


@pytest.fixture(scope="function")
def setup_files(tmp_path_factory: TempPathFactory) -> Tuple[pathlib.Path, pd.DataFrame]:
    """
    Pytest fixture that creates a temporary directory, populates it with fake BIOS files and 
    returns the path to said directory to be used in tests that expect BIOS files. The function 
    also updates the reference pandas dataFrame with the CRC32, MD5, and SHA1 hashes of the 
    dummy files (needed since hashes for the dummy files won't match the checksums for the actual 
    BIOS files)

    :param tmp_path_factory: A pytest fixture for creating temporary directories.
    :return: A tuple containing the path to the temporary directory and the updated DataFrame.
    """

    dummy_bios_lut = (
        system_df.sample(TEST_SAMPLE_SIZE, random_state=SEED)
        .copy(deep=True)
        .reset_index(drop=True)
    )

    temp_dir = tmp_path_factory.mktemp("bios")
    temp_output_dir = pathlib.Path(temp_dir)

    for index, row in dummy_bios_lut.iterrows():
        dummy_bytes = os.urandom(int(row["size"]))

        crc = binascii.crc32(dummy_bytes)
        md5 = hashlib.md5(dummy_bytes).hexdigest()
        sha1 = hashlib.sha1(dummy_bytes).hexdigest()

        dummy_bios_lut.at[index, "crc"] = crc
        dummy_bios_lut.at[index, "sha1"] = sha1
        dummy_bios_lut.at[index, "md5"] = md5

        temp_path = temp_output_dir / row["name"]
        parent = temp_path.parent
        if parent != temp_output_dir:
            parent.mkdir(parents=True, exist_ok=True)

        with open(temp_path, "wb") as src:
            src.write(dummy_bytes)

    return temp_output_dir, dummy_bios_lut
