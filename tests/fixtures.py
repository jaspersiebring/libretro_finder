import binascii
import hashlib
import os
import pathlib
from typing import Tuple

import pandas as pd
import pytest
from pytest import TempdirFactory

from config import SEED
from config import SYSTEMS as system_df
from tests import TEST_SAMPLE_SIZE


@pytest.fixture(scope="function")
def setup_files(tmpdir_factory: TempdirFactory) -> Tuple[pathlib.Path, pd.DataFrame]:
    """_summary_

    :param tmpdir_factory: _description_
    :return: _description_
    """
    
    dummy_bios_lut = system_df.sample(TEST_SAMPLE_SIZE, random_state = SEED).copy(deep=True).reset_index(drop=True)
    
    temp_dir = tmpdir_factory.mktemp("bios")
    temp_output_dir = pathlib.Path(temp_dir)

    for index, row in dummy_bios_lut.iterrows():
        dummy_bytes = os.urandom(int(row['size']))
        
        crc = binascii.crc32(dummy_bytes)
        md5 = hashlib.md5(dummy_bytes).hexdigest()
        sha1 = hashlib.sha1(dummy_bytes).hexdigest()
        
        dummy_bios_lut.at[index, 'crc'] = crc
        dummy_bios_lut.at[index, 'sha1'] = sha1
        dummy_bios_lut.at[index, 'md5'] = md5

        temp_path = temp_output_dir / row['name']
        parent = temp_path.parent
        if parent != temp_output_dir:
            parent.mkdir(parents=True, exist_ok=True) 
        
        with open(temp_path, 'wb') as src:
            src.write(dummy_bytes)

    return temp_output_dir, dummy_bios_lut
