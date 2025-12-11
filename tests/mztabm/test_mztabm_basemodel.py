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

    result: mztab_m_io.MzTabMLoadResult = mztab_m_io.read(invalid_mztab)

    assert len(result.messages) == 1
    captured_error = result.messages[0]
    assert captured_error.message_type == mztab_m_io.MessageType.ERROR
    assert "mzTab-ID" in captured_error.message


def test_no_sample(tmp_path):
    """
    tsv file read
    """
    file_path = "tests/data/example/example.mztab"
    lines = Path(file_path).read_text().splitlines()
    lines = (line for line in lines if not line.startswith("MTD\tsample"))
    invalid_mztab = tmp_path / "invalid.mztab"
    invalid_mztab.write_text("\n".join(lines))

    result: mztab_m_io.MzTabMLoadResult = mztab_m_io.read(invalid_mztab)
    assert result.success
    errors = [
        m for m in result.messages if m.message_type == mztab_m_io.MessageType.ERROR
    ]
    assert len(errors) == 0


def test_no_assay(tmp_path):
    """
    tsv file read
    """
    file_path = "tests/data/example/example.mztab"
    lines = Path(file_path).read_text().splitlines()
    lines = (line for line in lines if not line.startswith("MTD\tassay"))
    invalid_mztab = tmp_path / "invalid.mztab"
    invalid_mztab.write_text("\n".join(lines))

    result: mztab_m_io.MzTabMLoadResult = mztab_m_io.read(invalid_mztab)
    assert not result.success
    errors = [
        m for m in result.messages if m.message_type == mztab_m_io.MessageType.ERROR
    ]
    assert len(errors) == 1
    assert "assay" in errors[0].message


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

    result: mztab_m_io.MzTabMLoadResult = mztab_m_io.read(invalid_mztab)
    assert not result.success
    errors = [
        m for m in result.messages if m.message_type == mztab_m_io.MessageType.ERROR
    ]
    assert len(errors) == 2
