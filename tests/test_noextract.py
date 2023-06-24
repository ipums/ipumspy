from pathlib import Path
import pytest
import vcr

from ipumspy import noextract


def test_read_noextract_codebook():
    codebook = noextract.read_noextract_codebook("yrbss")
    assert codebook.file_description.structure == "rectangular"
    assert (
        codebook.file_description.description
        == "The Youth Risk Behavior Surveillance System (YRBSS) is a school-based, cross-sectional national survey of youth in grades 9-12. The YRBSS focuses on health risk behaviors that are often established during childhood and early adolescence, including behaviors associated with tobacco use, alcohol and other drug use, unintentional injuries, sexual behaviors related to unintended pregnancy and sexually transmitted infections, unhealthy diet, and inadequate physical activity."
    )
    assert codebook.data_description[0].id == "RECTYPE"
    assert codebook.data_description[0].name == "RECTYPE"
    assert codebook.data_description[0].rectype == "P"
    assert codebook.data_description[0].codes == {}
    assert codebook.data_description[0].start == 0
    assert codebook.data_description[0].end == 2
    assert codebook.data_description[0].label == "Record type"

    assert len(codebook.samples_description) == 0
    assert (
        codebook.ipums_citation
        == "Matthew Sobek, Daniel Backman, Greg Freedman Ellis, and Kari C.W. Williams. IPUMS Youth Risk Behavior Surveillance System: Version 1.0 [dataset]. Minneapolis, MN: IPUMS, 2017. https://doi.org/10.18128/D0111.V1.0."
    )
    assert codebook.ipums_collection == "yrbss"
    assert codebook.ipums_conditions == ""
    assert codebook.ipums_doi == ""

    with pytest.raises(ValueError):
        codebook = noextract.read_noextract_codebook("notproj")


@pytest.mark.vcr
def test_download_yrbss(tmpdir: Path):
    noextract.download_noextract_data("yrbss", tmpdir / "yrbss_test.dat.gz")
    assert Path(tmpdir / "yrbss_test.dat.gz").exists()


@pytest.mark.vcr
def test_download_nyts(tmpdir: Path):
    noextract.download_noextract_data("nyts", tmpdir / "nyts_test.dat.gz")
    assert Path(tmpdir / "nyts_test.dat.gz").exists()


@pytest.mark.vcr
def test_download_notproj(tmpdir: Path):
    with pytest.raises(ValueError) as e:
        noextract.download_noextract_data("notproj", tmpdir / "notproj_test.dat.gz")
    assert e.value.args[0] == (
        f"notproj is not a non-extractable IPUMS data collection. "
        f"Non-extractable IPUMS data collections include yrbss nyts"
    )
