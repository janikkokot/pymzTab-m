import warnings
import pytest
import mztab_m_io


@pytest.fixture
def mztabm():
    data = mztab_m_io.read("tests/data/example/example.mztab", format="tsv")
    return data


@pytest.mark.parametrize(
    "table",
    [
        "metadata",
        "small_molecule_summary",
        "small_molecule_feature",
        "small_molecule_evidence",
    ],
)
def test_successful_table_serialization(table, mztabm):
    tbl = getattr(mztabm, table)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        _ = str(tbl)


# data = mztab_m_io.read("../data/example/example.mztab", format="tsv")
# meta = data.metadata
# sml = data.small_molecule_summary
# smf = data.small_molecule_feature
# sme = data.small_molecule_evidence
