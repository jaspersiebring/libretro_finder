import pytest
from tests.fixtures import setup_files







class Test_organize():
    def test_all_match(setup_files):
        bios_dir, bios_lut = setup_files
        assert True

    def test_some_match(setup_files):
        bios_dir, bios_lut = setup_files
        assert True

    def test_no_match():
        assert True


    def test_no_files():
        assert True

    

