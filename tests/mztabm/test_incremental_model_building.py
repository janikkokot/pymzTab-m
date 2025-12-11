from pydantic import AnyUrl
import pydantic
import pytest
from mztab_m_io import MzTabM
from mztab_m_io.model.section.mtd import Metadata
from mztab_m_io.model.section.sml import SmallMoleculeSummary
from mztab_m_io.model.section.smf import SmallMoleculeFeature
from mztab_m_io.model.section.sme import SmallMoleculeEvidence


@pytest.fixture
def raw_metadata():
    meta = Metadata.model_construct()
    meta.mztab_version = "2.0.1-M"
    meta.mztab_id = "1"
    meta.software = [{}]
    meta.ms_run = [{"location": "some/path"}]
    meta.assay = [{"name": "assay1", "ms_run_ref": [1]}]
    meta.study_variable = [
        {
            "name": "sv1",
            "assay_refs": [1],
        }
    ]
    meta.cv = [
        {
            "label": "cv1",
            "full_name": "controlled_vocabulary",
            "version": "1",
            "uri": AnyUrl("http://www.uri.com"),
        }
    ]
    # why is cv uri as anyurl and database not?
    meta.database = [
        {"param": {}, "prefix": "DB", "version": "1", "uri": "www.uri.com"}
    ]
    meta.quantification_method = {}
    meta.small_molecule_quantification_unit = {}
    meta.small_molecule_feature_quantification_unit = {}
    return meta


@pytest.fixture
def validated_metadata(raw_metadata):
    raw_metadata.id_confidence_measure = [{}]
    return Metadata.model_validate(raw_metadata.__dict__)


def test_iterative_metadata_creation(validated_metadata):
    pass


def test_faulty_metadata_validation(raw_metadata):
    with pytest.raises(pydantic.ValidationError) as error:
        Metadata.model_validate(raw_metadata.__dict__)

    assert error.value.error_count() == 1


def test_faulty_metadata_assignment(validated_metadata):
    with pytest.raises(pydantic.ValidationError) as error:
        validated_metadata.mztab_id = None

    assert error.value.error_count() == 1


@pytest.fixture
def raw_sml():
    model = SmallMoleculeSummary.model_construct()
    return model


@pytest.fixture
def validated_sml(raw_sml):
    raw_sml.sml_id = 1
    return SmallMoleculeSummary.model_validate(raw_sml.__dict__)


def test_iterative_sml_creation(validated_sml):
    pass


@pytest.fixture
def raw_smf():
    model = SmallMoleculeFeature.model_construct()
    model.smf_id = 1
    model.exp_mass_to_charge = 1
    return model


@pytest.fixture
def validated_smf(raw_smf):
    raw_smf.charge = 1
    return SmallMoleculeFeature.model_validate(raw_smf.__dict__)


def test_iterative_smf_creation(validated_smf):
    pass


@pytest.fixture
def raw_sme():
    model = SmallMoleculeEvidence.model_construct()
    model.sme_id = 1
    model.evidence_input_id = "ms_run[1]:458.75"
    model.database_identifier = "1,null"
    model.exp_mass_to_charge = 1
    model.charge = 1
    model.theoretical_mass_to_charge = 1
    model.spectra_ref = []
    model.identification_method = {}
    model.ms_level = {}
    model.rank = 1
    return model


@pytest.fixture
def validated_sme(raw_sme):
    return SmallMoleculeEvidence.model_validate(raw_sme.__dict__)


def test_iterative_sme_creation(validated_sme):
    pass


def test_working_mztab(validated_metadata, validated_sml):
    MzTabM(metadata=validated_metadata, smallMoleculeSummary=[validated_sml])


@pytest.mark.xfail(reason="Raises AttributeError instead")
def test_faulty_metadata(raw_metadata, validated_sml):
    with pytest.raises(pydantic.ValidationError) as err:
        MzTabM(metadata=raw_metadata, smallMoleculeSummary=[validated_sml])
    assert err.value.error_count() == 1
    assert "metadata" in err.value.errors()[0]["loc"]


def test_missing_metadata(validated_sml):
    with pytest.raises(pydantic.ValidationError) as err:
        MzTabM(smallMoleculeSummary=[validated_sml])
    assert err.value.error_count() == 1
    assert "metadata" in err.value.errors()[0]["loc"]


def test_faulty_sml(validated_metadata, raw_sml):
    with pytest.raises(pydantic.ValidationError) as err:
        MzTabM(metadata=validated_metadata, SmallMoleculeSummary=[raw_sml])
    assert err.value.error_count() == 1
    assert "small_molecule_summary" in err.value.errors()[0]["loc"]


def test_missing_sml(validated_metadata):
    with pytest.raises(pydantic.ValidationError) as err:
        MzTabM(metadata=validated_metadata)
    assert err.value.error_count() == 1
    assert "small_molecule_summary" in err.value.errors()[0]["loc"]
