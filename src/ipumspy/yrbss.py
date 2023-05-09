import gzip
import importlib.resources as pkg_resources

import requests
import yaml

from ipumspy.types import FilenameType

from . import data
from .ddi import Codebook, FileDescription, VariableDescription


def __read_codebook() -> Codebook:
    with pkg_resources.open_binary(data, "yrbss.yml.gz") as infile:
        j = yaml.safe_load(gzip.decompress(infile.read()))

    return Codebook(
        file_description=FileDescription(
            "",
            "The Youth Risk Behavior Surveillance System (YRBSS) is a school-based, cross-sectional national survey of youth in grades 9-12. The YRBSS focuses on health risk behaviors that are often established during childhood and early adolescence, including behaviors associated with tobacco use, alcohol and other drug use, unintentional injuries, sexual behaviors related to unintended pregnancy and sexually transmitted infections, unhealthy diet, and inadequate physical activity.",
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
                val["start_column"] + val["width"],
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
        ipums_citation="",
        ipums_collection="yrbss",
        ipums_conditions="",
        ipums_doi="",
    )


yrbss_codebook = __read_codebook()


def download_yrbss_data(filename: FilenameType):
    """
    A convenience function to download YRBSS data directly from the IPUMS website

    Suggested usage:

        >>> from ipumspy.readers import read_microdata
        >>> from ipumspy.yrbss import download_yrbss_data, yrbss_codebook
        >>>
        >>> download_yrbss_data("yrbss.dat.gz")
        >>> read_microdata(yrbss_codebook, "yrbss.dat.gz")

    N.B. You **must** use the `yrbss_codebook` provided in this package or else
    `read_microdata` will fail.

    Args:
        filename: Where you would like do download the data to
    """
    with requests.get(
        "https://assets.ipums.org/_files/fda/yrbss/ipums-yrbss.dat.gz", stream=True
    ) as resp:

        resp.raise_for_status()
        with open(filename, "wb") as outfile:
            for chunk in resp.iter_content(chunk_size=8192):
                outfile.write(chunk)
