import os
import pathlib
import stat

import numpy as np
from pytest import MonkeyPatch, TempdirFactory

from libretro_finder.main import organize
from libretro_finder.utils import hash_file
from tests import TEST_SAMPLE_SIZE
from tests.fixtures import setup_files


class Test_organize:
    def test_matching(
        self, setup_files, tmpdir_factory: TempdirFactory, monkeypatch: MonkeyPatch
    ) -> None:
        bios_dir, bios_lut = setup_files
        assert bios_dir.exists()

        # checking saved files (excluding directories)
        file_paths = list(bios_dir.rglob("*"))
        file_paths = [file_path for file_path in file_paths if file_path.is_file()]
        assert len(file_paths) == TEST_SAMPLE_SIZE

        # making output_dir
        temp_dir = tmpdir_factory.mktemp("test_matching")
        output_dir = pathlib.Path(temp_dir)

        # checking if currently empty
        output_paths = list(output_dir.rglob(pattern="*"))
        assert len(output_paths) == 0

        # swapping out system_df to the one generated from setup_files
        # this is needed because we can't include actual bios files for testing
        monkeypatch.setattr("libretro_finder.main.system_df", bios_lut)
        organize(search_dir=bios_dir, output_dir=output_dir, glob="*")

        # verifying correct output
        output_paths = list(output_dir.rglob(pattern="*"))
        output_paths = [
            output_path for output_path in output_paths if output_path.is_file()
        ]
        output_names = [
            output_path.relative_to(output_dir).as_posix()
            for output_path in output_paths
        ]
        output_hashes = [hash_file(output_path) for output_path in output_paths]

        assert len(output_paths) == TEST_SAMPLE_SIZE
        assert bios_lut.shape[0] == len(output_paths)
        assert np.all(np.isin(output_hashes, bios_lut["md5"].values))
        assert np.all(np.isin(bios_lut["name"].values, output_names))

    def test_non_matching(self, setup_files, tmpdir_factory: TempdirFactory) -> None:
        # pretty much matching but we don't monkeypatch so we're comparing different hashes
        # same as 'matching' test but without monkeypatching (i.e. different hashes so no matches)
        bios_dir, _ = setup_files
        assert bios_dir.exists()

        # checking saved files (excluding directories)
        file_paths = list(bios_dir.rglob("*"))
        file_paths = [file_path for file_path in file_paths if file_path.is_file()]
        assert len(file_paths) == TEST_SAMPLE_SIZE

        # making output_dir
        temp_dir = tmpdir_factory.mktemp("test_non_matching")
        output_dir = pathlib.Path(temp_dir)

        # checking if currently empty
        output_paths = list(output_dir.rglob(pattern="*"))
        assert len(output_paths) == 0

        # running organize with libretro's dataframe
        organize(search_dir=bios_dir, output_dir=output_dir, glob="*")

        # checking if still empty
        assert len(list(output_dir.rglob("*"))) == 0

    def test_empty(self, tmpdir_factory: TempdirFactory) -> None:
        temp_input_dir = tmpdir_factory.mktemp("input")
        temp_output_dir = tmpdir_factory.mktemp("output")
        input_dir = pathlib.Path(temp_input_dir)
        output_dir = pathlib.Path(temp_output_dir)

        # checking if exists but empty
        assert input_dir.exists()
        assert len(list(input_dir.rglob("*"))) == 0
        assert output_dir.exists()
        assert len(list(output_dir.rglob("*"))) == 0

        # checking if still empty
        organize(search_dir=input_dir, output_dir=output_dir, glob="*")
        assert len(list(output_dir.rglob("*"))) == 0

    def test_same_input(
        self, setup_files, tmpdir_factory: TempdirFactory, monkeypatch: MonkeyPatch
    ) -> None:
        # organize but with (prepopulated) bios_dir as input and output
        # verifies if non-additive

        bios_dir, bios_lut = setup_files
        assert bios_dir.exists()

        # checking saved files (excluding directories)
        file_paths = list(bios_dir.rglob("*"))
        file_paths = [file_path for file_path in file_paths if file_path.is_file()]
        current_len = len(file_paths)
        assert current_len == TEST_SAMPLE_SIZE

        # swapping out system_df to the one generated from setup_files
        # this is needed because we can't include actual bios files for testing
        monkeypatch.setattr("libretro_finder.main.system_df", bios_lut)
        organize(search_dir=bios_dir, output_dir=bios_dir, glob="*")

        # verifying correct output
        output_paths = list(bios_dir.rglob(pattern="*"))
        output_paths = [
            output_path for output_path in output_paths if output_path.is_file()
        ]
        output_names = [
            output_path.relative_to(bios_dir).as_posix() for output_path in output_paths
        ]
        output_hashes = [hash_file(output_path) for output_path in output_paths]

        assert len(output_paths) == current_len
        assert bios_lut.shape[0] == len(output_paths)
        assert np.all(np.isin(output_hashes, bios_lut["md5"].values))
        assert np.all(np.isin(bios_lut["name"].values, output_names))

    # def test_permissions(
    #     self, setup_files, tmpdir_factory: TempdirFactory, monkeypatch: MonkeyPatch
    # ) -> None:
    #     bios_dir, bios_lut = setup_files
    #     assert bios_dir.exists()

    #     # checking saved files (excluding directories)
    #     file_paths = list(bios_dir.rglob("*"))
    #     file_paths = [file_path for file_path in file_paths if file_path.is_file()]
    #     assert len(file_paths) == TEST_SAMPLE_SIZE

    #     # making output_dir but with read-only permissions
    #     temp_dir = tmpdir_factory.mktemp("test_permissions")
    #     output_dir = pathlib.Path(temp_dir)
    #     print(stat.filemode(os.stat(str(temp_dir)).st_mode))
    #     os.chmod(str(temp_dir), 0o555)
    #     print(stat.filemode(os.stat(str(temp_dir)).st_mode))

    #     # checking if currently empty
    #     output_paths = list(output_dir.rglob(pattern="*"))
    #     assert len(output_paths) == 0

    #     # swapping out system_df to the one generated from setup_files
    #     # this is needed because we can't include actual bios files for testing
    #     monkeypatch.setattr("libretro_finder.main.system_df", bios_lut)
    #     organize(search_dir=bios_dir, output_dir=output_dir, glob="*")
    #     output_dir

    #     # verifying correct output
    #     output_paths = list(output_dir.rglob(pattern="*"))
    #     output_paths = [
    #         output_path for output_path in output_paths if output_path.is_file()
    #     ]
    #     output_names = [
    #         output_path.relative_to(output_dir).as_posix()
    #         for output_path in output_paths
    #     ]
    #     output_hashes = [hash_file(output_path) for output_path in output_paths]

    #     assert len(output_paths) == TEST_SAMPLE_SIZE
    #     assert bios_lut.shape[0] == len(output_paths)
    #     assert np.all(np.isin(output_hashes, bios_lut["md5"].values))
    #     assert np.all(np.isin(bios_lut["name"].values, output_names))
