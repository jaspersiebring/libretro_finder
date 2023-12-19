# pylint: disable=redefined-outer-name
import hashlib
import os
import pathlib
from typing import Tuple

import numpy as np
import pandas as pd
import pytest

from libretro_finder.utils import hash_file, match_arrays, recursive_hash
from tests import TEST_BYTES, TEST_SAMPLE_SIZE
from tests.fixtures import setup_files # noqa: F401

def test_libretro_meta_import():
    """verifies that (remote) libretro-database can pulled, parsed and dumped to pandas DataFrame"""
    from config import SYSTEMS # noqa: F401 PLC0415


class TestHashFile:
    """Bundle of pytest asserts for utils.hash_file"""

    def test_existing(self, tmp_path: pathlib.Path) -> None:
        """utils.hash_file with existing input

        :param tmp_path: A pytest fixture that creates a temporary directory unique to this test
        """

        file_path = tmp_path / "some_file"
        random_bytes = os.urandom(TEST_BYTES)

        with open(file_path, "wb") as src:
            src.write(random_bytes)
        _ = hash_file(file_path)

    def test_nonexistent(self, tmp_path: pathlib.Path) -> None:
        """utils.hash_file with non-existing input

        :param tmp_path: A pytest fixture that creates a temporary directory unique to this test
        """

        file_path = tmp_path / "some_file"
        with pytest.raises(FileNotFoundError):
            hash_file(file_path)


class TestRecursiveHash:
    """Bundle of pytest asserts for utils.recursive_hash"""

    def test_with_fixture(self, setup_files: Tuple[pathlib.Path, pd.DataFrame]) -> None:
        """utils.recursive_hash with (exclusively) matching files

        :param setup_files: A pytest fixture that generates fake BIOS files and reference dataframe
        """

        bios_dir, bios_lut = setup_files

        file_paths, file_hashes = recursive_hash(directory=bios_dir, glob="*")
        assert file_paths.size == TEST_SAMPLE_SIZE
        assert file_hashes.size == TEST_SAMPLE_SIZE

        file_names = np.array(
            [file_path.relative_to(bios_dir).as_posix() for file_path in file_paths]
        )
        assert np.all(np.isin(file_names, bios_lut["name"].values))  # type: ignore

        index_a, index_b = np.where(
            file_names.reshape(1, -1) == bios_lut["name"].values.reshape(-1, 1)  # type: ignore
        )
        assert np.array_equal(file_names[index_b], bios_lut["name"].values[index_a])
        assert np.array_equal(file_hashes[index_b], bios_lut["md5"].values[index_a])

    def test_without_fixture(self, tmp_path: pathlib.Path) -> None:
        """utils.recursive_hash without matching files

        :param tmp_path: A pytest fixture that creates a temporary directory unique to this test
        """

        temp_output_dir = tmp_path / "rhash"
        temp_output_dir.mkdir()

        file_names = [f"system_{i}.bin" for i in range(1, 11)]
        file_bytes = [os.urandom(TEST_BYTES * i) for i in range(1, 11)]

        input_paths = []
        input_hashes = []

        for i, file_name in enumerate(file_names):
            temp_path = temp_output_dir / file_name
            md5 = hashlib.md5(file_bytes[i]).hexdigest()
            input_hashes.append(md5)
            input_paths.append(temp_path)
            with open(temp_path, "wb") as src:
                src.write(file_bytes[i])

        output_paths, output_hashes = recursive_hash(
            directory=temp_output_dir, glob="*"
        )

        # check whether the generated files are actually different
        assert np.unique(output_hashes).size == output_hashes.size
        assert len(input_paths) == len(output_paths)

        assert np.all(np.isin(input_paths, output_paths))  # type: ignore
        assert np.all(np.isin(input_hashes, output_hashes))


class TestMatchArrays:
    """Bundle of pytest asserts for utils.match_arrays"""

    def test_overlap(self):
        """utils.match_arrays with partial overlap"""

        array_a = np.array([0, 1, 2, 3, 4, 5])
        array_b = np.array([5, 2, 5, 16])

        matching_values, indices_a, indices_b = match_arrays(
            array_a=array_a, array_b=array_b
        )

        assert np.any(matching_values)
        assert np.all(np.isin(np.array([5, 2]), matching_values))
        assert np.array_equal(array_a[indices_a], array_b[indices_b])

    def test_no_overlap(self):
        """utils.match_arrays with no overlap"""

        array_a = np.array([0, 1, 2, 3, 4, 5])
        array_b = np.array([9, 9, 7, 16])

        matching_values, indices_a, indices_b = match_arrays(
            array_a=array_a, array_b=array_b
        )

        assert not np.any(matching_values)
        assert not np.any(indices_a)
        assert not np.any(indices_b)

    def test_type(self):
        """utils.match_arrays with invalid input type"""

        array_a = [0, 1, 2, 3, 4, 5]
        array_b = np.array([5, 2, 5, 16])

        with pytest.raises(AttributeError):
            _ = match_arrays(array_a=array_a, array_b=array_b)

    def test_shape(self):
        """utils.match_arrays with input arrays of invalid shape"""

        array_a = np.array([[0, 1, 2, 3, 4, 5]])
        array_b = np.array([[5, 2, 5, 16]])

        with pytest.raises(ValueError):
            _ = match_arrays(array_a=array_a, array_b=array_b)

    def test_nptype(self):
        """utils.match_arrays with valid non-numerical arrays as input"""

        array_a = np.array(["a", "b"])
        array_b = np.array(["c", "a", "a", "x", "b"])

        matching_values, indices_a, indices_b = match_arrays(
            array_a=array_a, array_b=array_b
        )
        assert np.size(matching_values) > 0
        assert np.all(np.isin(np.array(["a", "b"]), matching_values))
        assert np.array_equal(array_a[indices_a], array_b[indices_b])
