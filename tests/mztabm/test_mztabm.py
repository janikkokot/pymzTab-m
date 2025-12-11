import json
import mztab_m_io
import pytest


@pytest.mark.parametrize(
    "file_path,format_",
    [
        ("tests/data/example/example.mztab", "tsv"),
        ("tests/data/example/example.json", "json"),
        ("tests/data/example/example.yaml", "yaml"),
    ],
)
def test_read(file_path, format_):
    """
    Test reading to a mzTab-M from several file formats
    """
    mztabm: mztab_m_io.MzTabM = mztab_m_io.read(file_path, format=format_)
    mztabm_dict = mztab_m_io.convert_to_dict(mztabm)
    assert mztabm_dict


def test_load_from_dict():
    """
    Load from dict
    """
    file_path = "tests/data/example/example.json"
    with open(file_path) as f:
        mztabm_dict = json.load(f)
    mztabm_model = mztab_m_io.load_from_dict(mztabm_dict)
    assert mztabm_model


@pytest.mark.parametrize(
    "file_path,format_",
    [
        ("tests/data/example/example.mztab", "tsv"),
        ("tests/data/example/example.json", "json"),
        ("tests/data/example/example.yaml", "yaml"),
    ],
)
def test_write(file_path, format_, tmp_path):
    """
    Test writing of an mztab-M model to several file formats
    """
    mztabm: mztab_m_io.MzTabM = mztab_m_io.read(file_path, format=format_)
    target_path = tmp_path / "example"
    mztab_m_io.write(mztabm, str(target_path), format=format_)
    mztabm2: mztab_m_io.MzTabM = mztab_m_io.read(target_path, format=format_)
    assert mztabm == mztabm2
