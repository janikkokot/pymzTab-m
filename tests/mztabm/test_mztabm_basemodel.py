import warnings
import pytest
import pydantic
import mztab_m_io
from pathlib import Path


def test_no_id(tmp_path):
    """
    tsv file read
    """
    file_path = "tests/data/example/example.mztab"
    lines = Path(file_path).read_text().splitlines()
    lines = (line for line in lines if not line.startswith("MTD\tmzTab-ID"))
    invalid_mztab = tmp_path / "invalid.mztab"
    invalid_mztab.write_text("\n".join(lines))
    with pytest.raises(pydantic.ValidationError) as error:
        mztabm = mztab_m_io.MzTabM = mztab_m_io.read(invalid_mztab)
    assert error.value.error_count() == 1
    error = error.value.errors()[0]
    assert "mzTab-ID" in error["loc"]


def test_no_sample(tmp_path):
    """
    tsv file read
    """
    file_path = "tests/data/example/example.mztab"
    lines = Path(file_path).read_text().splitlines()
    lines = (line for line in lines if not line.startswith("MTD\tsample"))
    invalid_mztab = tmp_path / "invalid.mztab"
    invalid_mztab.write_text("\n".join(lines))

    with warnings.catch_warnings(record=True) as w:
        mztabm: mztab_m_io.MzTabM = mztab_m_io.read(invalid_mztab)
        assert len(w) > 0


def test_no_assay(tmp_path):
    """
    tsv file read
    """
    file_path = "tests/data/example/example.mztab"
    lines = Path(file_path).read_text().splitlines()
    lines = (line for line in lines if not line.startswith("MTD\tassay"))
    invalid_mztab = tmp_path / "invalid.mztab"
    invalid_mztab.write_text("\n".join(lines))

    with pytest.raises(pydantic.ValidationError) as error:
        mztabm = mztab_m_io.MzTabM = mztab_m_io.read(invalid_mztab)
    assert error.value.error_count() == 1
    error = error.value.errors()[0]
    assert "assay" in error["loc"]


def test_multiple_errors(tmp_path):
    """
    tsv file read
    """
    file_path = "tests/data/example/example.mztab"
    lines = Path(file_path).read_text().splitlines()
    lines = (
        line
        for line in lines
        if not line.startswith("MTD\tassay") and not line.startswith("MTD\tmzTab-ID")
    )
    invalid_mztab = tmp_path / "invalid.mztab"
    invalid_mztab.write_text("\n".join(lines))

    with pytest.raises(pydantic.ValidationError) as error:
        mztabm = mztab_m_io.MzTabM = mztab_m_io.read(invalid_mztab)
    assert error.value.error_count() == 2
