# pylint: disable=redefined-outer-name
import pathlib
import pytest
import numpy as np
from pytest import MonkeyPatch
from pytest_mock import MockerFixture, mocker  # pylint: disable=unused-import

from libretro_finder.main import organize, main
from libretro_finder.utils import hash_file
from tests import TEST_SAMPLE_SIZE
from tests.fixtures import setup_files  # pylint: disable=unused-import


class TestOrganize:
    """Bundle of pytest asserts for main.organize"""

    def test_matching(
        self, setup_files, tmp_path: pathlib.Path, monkeypatch: MonkeyPatch
    ) -> None:
        """main.organize with (only) matching files

        :param setup_files: A pytest fixture that generates fake BIOS files and reference dataframe
        :param tmp_path: A pytest fixture that creates a temporary directory unique to this test
        :param monkeypatch: A pytest fixture that allows us to set certain testing conditions
        """

        bios_dir, bios_lut = setup_files
        assert bios_dir.exists()

        # checking saved files (excluding directories)
        file_paths = list(bios_dir.rglob("*"))
        file_paths = [file_path for file_path in file_paths if file_path.is_file()]
        assert len(file_paths) == TEST_SAMPLE_SIZE

        # making output_dir
        output_dir = tmp_path / "test_matching"
        output_dir.mkdir()

        # checking if currently empty
        output_paths = list(output_dir.rglob(pattern="*"))
        assert len(output_paths) == 0

        # swapping out system_df to the one generated from setup_files
        # this is needed because we can't include actual bios files for testing
        monkeypatch.setattr("libretro_finder.main.system_df", bios_lut)
        organize(search_dir=bios_dir, output_dir=output_dir)

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

    def test_non_matching(self, setup_files, tmp_path: pathlib.Path) -> None:
        """main.organize without matching files

        :param setup_files: A pytest fixture that generates fake BIOS files and reference dataframe
        :param tmp_path: A pytest fixture that creates a temporary directory unique to this test
        """

        # same as 'matching' test but without monkeypatching (i.e. different hashes so no matches)
        bios_dir, _ = setup_files
        assert bios_dir.exists()

        # checking saved files (excluding directories)
        file_paths = list(bios_dir.rglob("*"))
        file_paths = [file_path for file_path in file_paths if file_path.is_file()]
        assert len(file_paths) == TEST_SAMPLE_SIZE

        # making output_dir
        output_dir = tmp_path / "test_non_matching"
        output_dir.mkdir()

        # checking if currently empty
        output_paths = list(output_dir.rglob(pattern="*"))
        assert len(output_paths) == 0

        # running organize with libretro's dataframe
        organize(search_dir=bios_dir, output_dir=output_dir)

        # checking if still empty
        assert len(list(output_dir.rglob("*"))) == 0

    def test_empty(self, tmp_path: pathlib.Path) -> None:
        """main.organize with empty search_dir

        :param tmp_path: A pytest fixture that creates a temporary directory unique to this test
        """

        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"
        input_dir.mkdir()
        output_dir.mkdir()

        # checking if exists but empty
        assert input_dir.exists()
        assert len(list(input_dir.rglob("*"))) == 0
        assert output_dir.exists()
        assert len(list(output_dir.rglob("*"))) == 0

        # checking if still empty
        organize(search_dir=input_dir, output_dir=output_dir)
        assert len(list(output_dir.rglob("*"))) == 0

    def test_same_input(self, setup_files, monkeypatch: MonkeyPatch) -> None:
        """main.organize with shared input for search_dir and output_dir (verifies if non-additive)

        :param setup_files: A pytest fixture that generates fake BIOS files and reference dataframe
        :param monkeypatch: A pytest fixture that allows us to set certain testing conditions
        """

        # organize but with (prepopulated) bios_dir as input and output
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
        organize(search_dir=bios_dir, output_dir=bios_dir)

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


class TestMain:
    """Bundle of pytest asserts for main.main"""

    def test_main(self, tmp_path: pathlib.Path, mocker: MockerFixture):
        """main.main with valid input

        :param tmp_path: A pytest fixture that creates a temporary directory unique to this test
        :param mocker: A pytest fixture that mocks specific objects for testing purposes
        """

        # Mocking the organize function to prevent actual file operations
        mock_organize = mocker.patch("libretro_finder.main.organize")

        search_dir = tmp_path / "search"
        output_dir = tmp_path / "output"
        search_dir.mkdir()
        output_dir.mkdir()

        argv = [str(search_dir), str(output_dir)]
        main(argv)
        mock_organize.assert_called_once_with(
            search_dir=search_dir, output_dir=output_dir
        )

    def test_main_search_directory_not_exists(self, tmp_path: pathlib.Path):
        """main.main with non-existent search_dir

        :param tmp_path: A pytest fixture that creates a temporary directory unique to this test
        """

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        argv = ["/path/to/nonexistent/search", str(output_dir)]
        with pytest.raises(FileNotFoundError):
            main(argv)

    def test_main_search_directory_not_directory(self, tmp_path: pathlib.Path):
        """main.main with file as search_dir

        :param tmp_path: A pytest fixture that creates a temporary directory unique to this test
        """

        file_path = tmp_path / "search.txt"
        output_dir = tmp_path / "output"
        file_path.touch()
        output_dir.mkdir()

        argv = [str(file_path), str(output_dir)]
        with pytest.raises(NotADirectoryError):
            main(argv)
