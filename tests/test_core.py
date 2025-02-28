import pytest

from pymcap import PyMCAP
from mcap.writer import Writer
from time import time_ns
import json
from pathlib import Path


@pytest.fixture(scope="session")
def pymcap() -> PyMCAP:
    return PyMCAP()


def write_to_simple_mcap(mcap_file: Path, to_recover: bool) -> Path:
    with open(mcap_file, "wb") as stream:
        writer = Writer(stream)
        writer.start()
        schema_id = writer.register_schema(
            name="sample",
            encoding="jsonschema",
            data=json.dumps(
                {
                    "type": "object",
                    "properties": {
                        "sample": {
                            "type": "string",
                        }
                    },
                }
            ).encode(),
        )
        channel_id = writer.register_channel(
            schema_id=schema_id,
            topic="sample_topic",
            message_encoding="json",
        )
        writer.add_message(
            channel_id=channel_id,
            log_time=time_ns(),
            data=json.dumps({"sample": "test"}).encode("utf-8"),
            publish_time=time_ns(),
        )
        if not to_recover:
            writer.finish()
    return mcap_file


@pytest.fixture
def normal_mcap_file(tmp_path: Path) -> Path:
    mcap_file = tmp_path / "normal.mcap"
    write_to_simple_mcap(mcap_file, False)
    return Path(mcap_file)


@pytest.fixture
def corrupted_mcap(tmp_path: Path) -> Path:
    mcap_file = tmp_path / "normal.mcap"
    write_to_simple_mcap(mcap_file, True)
    return Path(mcap_file)


def test_get_mcap_cli_version(pymcap: PyMCAP) -> None:
    assert pymcap.mcap_cli_version == "v0.0.51"


def test_get_version(pymcap: PyMCAP) -> None:
    assert pymcap.version == "0.0.2"


def check_if_mcap_equal(file1: Path, file2: Path) -> bool:
    with open(file1, "rb") as f1, open(file2, "rb") as f2:
        return f1.read() == f2.read()


def test_mcap_corrupted_for_normal_file(pymcap: PyMCAP, normal_mcap_file: Path) -> None:
    assert pymcap.is_mcap_corrupted(normal_mcap_file) is False


def test_mcap_corrupted_for_currupted_file(
    pymcap: PyMCAP, corrupted_mcap: Path
) -> None:
    assert pymcap.is_mcap_corrupted(corrupted_mcap) is True


def test_recover_normal_file_inplace(pymcap: PyMCAP, normal_mcap_file: Path) -> None:
    recovered = pymcap.recover(normal_mcap_file, inplace=True)
    assert recovered == normal_mcap_file
    assert check_if_mcap_equal(recovered, normal_mcap_file)


def test_recover_normal_file_outplace(pymcap: PyMCAP, normal_mcap_file: Path) -> None:
    out_file = normal_mcap_file.parent / "recovered.mcap"
    recovered = pymcap.recover(normal_mcap_file, out=out_file, inplace=False)
    assert recovered == out_file
    assert check_if_mcap_equal(recovered, normal_mcap_file)


def test_recover_corrupted_file_inplace(
    pymcap: PyMCAP, corrupted_mcap: Path, normal_mcap_file: Path
) -> None:
    recovered = pymcap.recover(corrupted_mcap, inplace=True)
    assert recovered == normal_mcap_file
    assert check_if_mcap_equal(recovered, normal_mcap_file)


def test_recover_corrupted_file_outplace(
    pymcap: PyMCAP, corrupted_mcap: Path, normal_mcap_file: Path
) -> None:
    out_file = corrupted_mcap.parent / "recovered.mcap"
    recovered = pymcap.recover(corrupted_mcap, out=out_file, inplace=False)
    assert recovered == out_file
    assert check_if_mcap_equal(recovered, normal_mcap_file)
