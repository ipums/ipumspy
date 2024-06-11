import gzip
import importlib.resources as pkg_resources

import requests
from typing import Optional
import yaml

from ipumspy.types import FilenameType

from . import data
from .ddi import Codebook, FileDescription, VariableDescription

NOEXTRACT_COLLECTIONS = ["yrbss", "nyts"]


def read_noextract_codebook(collection: str) -> Codebook:
    """
    A method to parse the codebooks for non-extractable IPUMS datasets that come with this package

    Args:
        collection (str): A valid non-extractable IPUMS data collection (yrbss or nyts)

    Raises:
        ValueError: If an invalid or extractable IPUMS data collection is specified

    Returns:
        Codebook: an ipumspy Codebook object
    """
    if collection not in NOEXTRACT_COLLECTIONS:
        raise ValueError(
            f"{collection} is not a non-extractable IPUMS data collection. "
            f"Non-extractable IPUMS data collections include {' '.join(NOEXTRACT_COLLECTIONS)}"
        )
    else:
        with pkg_resources.open_binary(data, f"{collection}.yml.gz") as infile:
            j = yaml.safe_load(gzip.decompress(infile.read()))

        return Codebook(
            file_description=FileDescription(
                "",
                j["project_desc"],
                "rectangular",
                [],
                "",
                "",
                "UTF-8",
                "fixed_width",
                "IPUMS, 50 Willey Hall, 225 - 19th Avenue South, Minneapolis, MN 55455",
            ),
            data_description=[
                VariableDescription(
                    val["name"],
                    val["name"],
                    val["record_type"],
                    {v["label"]: v["value"] for v in val["values"]},
                    val["start_column"] - 1,
                    val["start_column"] + val["width"] - 1,
                    val["label"],
                    val["label"],
                    "",  # No concept tracked
                    "character" if val["is_string_var"] else "numeric",
                    "",  # No notes tracked
                    val["implied_decimals"],
                )
                for val in j["variables"]
            ],
            samples_description=[],
            ipums_citation=j["citation"],
            ipums_collection=f"{collection}",
            ipums_conditions="",
            ipums_doi="",
        )


def download_noextract_data(collection: str, filename: Optional[FilenameType] = None):
    """
    A convenience function to download non-extractable IPUMS data directly from the IPUMS website

    Suggested usage to retrieve YRBSS data:

        >>> from ipumspy.readers import read_microdata
        >>> from ipumspy.noextract import read_noextract_codebook, download_noextract_data
        >>>
        >>> yrbss_codebook = read_noextract_codebook("yrbss")
        >>> download_noextract_data("yrbss")
        >>> read_microdata(yrbss_codebook, "ipums-yrbss.dat.gz")

    N.B. You **must** use `read_noextract_codebook()` to parse the codebook provided in this package or else
    `read_microdata` will fail.

    Args:
        collection (str): A valid non-extractable IPUMS data collection (yrbss or nyts)
        filename (Optional, FilnameType): Files to download the data to. Defaults to ipums-<collection>.dat.gz

    Raises:
        ValueError: If an invalid or extractable IPUMS data collection is specified
    """
    if collection not in NOEXTRACT_COLLECTIONS:
        raise ValueError(
            f"{collection} is not a non-extractable IPUMS data collection. "
            f"Non-extractable IPUMS data collections include {' '.join(NOEXTRACT_COLLECTIONS)}"
        )

    if filename is None:
        filename = f"ipums-{collection}.dat.gz"
    with requests.get(
        f"https://assets.ipums.org/_files/fda/{collection}/ipums-{collection}.dat.gz",
        stream=True,
    ) as resp:

        resp.raise_for_status()
        with open(filename, "wb") as outfile:
            for chunk in resp.iter_content(chunk_size=8192):
                outfile.write(chunk)
