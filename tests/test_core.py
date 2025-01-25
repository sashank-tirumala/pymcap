import pytest

from pymcap import PyMCAP


@pytest.fixture(scope='session')
def pymcap() -> PyMCAP:
    return PyMCAP()


def test_get_version(pymcap: PyMCAP):
    assert pymcap.version == 'v0.0.51\n'

