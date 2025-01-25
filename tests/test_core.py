import pytest

from pymcap import PyMCAP


@pytest.fixture(scope="session")
def pymcap() -> PyMCAP:
    return PyMCAP()


def test_get_mcap_cli_version(pymcap: PyMCAP):
    assert pymcap.mcap_cli_version == "v0.0.51\n"
