# This file is part of ipumspy.
# For copyright and licensing information, see the NOTICE and LICENSE files
# in this project's top-level directory, and also on-line at:
#   https://github.com/ipums/ipumspy

"""
Functions for reading and processing IPUMS data
"""
import copy
import json
import re
import warnings
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterator, List, Optional, Union

import pandas as pd
import yaml

from . import ddi as ddi_definitions
from . import fileutils
from .fileutils import open_or_yield
from .types import FilenameType


class CitationWarning(Warning):
    pass


def read_ipums_ddi(ddi_file: fileutils.FileType) -> ddi_definitions.Codebook:
    """
    Read a DDI from a IPUMS XML file

    Args:
        ddi_file: path to an IPUMS DDI XML

    Returns:
        A parsed IPUMS ddi codebook
    """
    with fileutils.xml_opener(ddi_file) as opened_file:
        root = ET.parse(opened_file).getroot()

    # Extract the namespace if there is one
    match = re.match(r"^\{(.*)\}", root.tag)
    namespace = match.groups()[0] if match else ""
    warnings.warn(
        "Use of data from IPUMS is subject to conditions including that users "
        "should cite the data appropriately.\n"
        "See the `ipums_conditions` attribute of this codebook for terms of use.\n"
        "See the `ipums_citation` attribute of this codebook for the appropriate "
        "citation.",
        CitationWarning,
    )
    return ddi_definitions.Codebook.read(root, namespace)


def _read_microdata(
    ddi: ddi_definitions.Codebook,
    filename: Optional[fileutils.FileType] = None,
    encoding: Optional[str] = None,
    subset: Optional[List[str]] = None,
    iterator: bool = False,
    chunksize: Optional[int] = None,
    **kwargs
):
    if ddi.file_description.structure != "rectangular":
        raise NotImplementedError("Structure must be rectangular")

    if subset is not None:
        data_description = [
            desc for desc in ddi.data_description if desc.name in subset
        ]
    else:
        data_description = ddi.data_description

    filename = Path(filename or ddi.file_description.filename)
    encoding = encoding or ddi.file_description.encoding

    iterator = iterator or (chunksize is not None)

    # Set up the correct reader for our file type
    kwargs = copy.deepcopy(kwargs)
    if ".dat" in filename.suffixes:
        # This is a fixed width file
        kwargs.update(
            {
                "colspecs": [(desc.start, desc.end) for desc in data_description],
                "names": [desc.name for desc in data_description],
                "dtype": {desc.name: desc.numpy_type for desc in data_description},
            }
        )
        reader = pd.read_fwf
        mode = "rt"

        # Fixed width files also require fixing decimal expansions
        def _fix_decimal_expansion(df):
            for desc in data_description:
                if desc.shift:
                    shift = 10 ** desc.shift
                    df[desc.name] /= shift
            return df

    elif ".csv" in filename.suffixes:
        # A csv!
        reader = pd.read_csv
        kwargs.update(
            {
                "usecols": [desc.name for desc in data_description],
                "dtype": {desc.name: desc.numpy_type for desc in data_description},
            }
        )
        mode = "rt"

        # CSVs have correct decimal expansions already; so we just make
        # this the identity function
        def _fix_decimal_expansion(df):
            return df

    elif ".parquet" in filename.suffixes:
        # A parquet file
        reader = pd.read_parquet
        kwargs.update({"columns": [desc.name for desc in data_description]})
        mode = "rb"

        # Parquets have correct decimal expansions already; so we just make
        # this the identity function
        def _fix_decimal_expansion(df):
            return df

    else:
        raise ValueError("Only CSV and .dat files are supported")

    with fileutils.data_opener(filename, encoding=encoding, mode=mode) as infile:
        if not iterator:
            data = [reader(infile, **kwargs)]
        else:
            kwargs.update({"iterator": True, "chunksize": chunksize})
            data = reader(infile, **kwargs)

        yield from (
            _fix_decimal_expansion(df).astype(
                {desc.name: desc.pandas_type for desc in ddi.data_description}
            )
            for df in data
        )


def read_microdata(
    ddi: ddi_definitions.Codebook,
    filename: Optional[fileutils.FileType] = None,
    encoding: Optional[str] = None,
    subset: Optional[List[str]] = None,
    **kwargs
) -> Union[pd.DataFrame, pd.io.parsers.TextFileReader]:
    """
    Read in microdata as specified by the Codebook. Both .dat and .csv file types
    are supported.

    Args:
        ddi: The codebook representing the data
        filename: The path to the data file. If not present, gets from
                        ddi and assumes the file is relative to the current
                        working directory
        encoding: The encoding of the data file. If not present, reads from ddi
        subset: A list of variable names to keep. If None, will keep all
        kwargs: keyword args to be passed to the engine (pd.read_fwf, pd.read_csv, or
            pd.read_parquet depending on the file type)

    Returns:
        pandas data frame and pandas text file reader
    """
    return next(
        _read_microdata(
            ddi, filename=filename, encoding=encoding, subset=subset, **kwargs
        )
    )


def read_microdata_chunked(
    ddi: ddi_definitions.Codebook,
    filename: Optional[fileutils.FileType] = None,
    encoding: Optional[str] = None,
    subset: Optional[List[str]] = None,
    chunksize: Optional[int] = None,
    **kwargs
) -> Iterator[pd.DataFrame]:
    """
    Read in microdata in chunks as specified by the Codebook.
    As these files are often large, you may wish to filter or read in chunks.
    As an example of how you might do that, consider the following example that
    filters only for rows in Rhode Island::

        iter_microdata = read_microdata_chunked(ddi, chunksize=1000)
        df = pd.concat([df[df['STATEFIP'] == 44]] for df in iter_microdata])

    Args:
        ddi: The codebook representing the data
        filename: The path to the data file. If not present, gets from
                     ddi and assumes the file is relative to the current working directory
        encoding: The encoding of the data file. If not present, reads from ddi
        subset: A list of variable names to keep. If None, will keep all
        chunksize: The size of the chunk to return with iterator. See `pandas.read_csv`
        kwargs: keyword args to be passed to pd.read_fwf
    Yields:
        An iterator of data frames
    """
    yield from _read_microdata(
        ddi,
        filename=filename,
        encoding=encoding,
        subset=subset,
        iterator=True,
        chunksize=chunksize,
        **kwargs
    )


def read_extract_description(extract_filename: FilenameType) -> dict:
    """
    Open an extract description (either yaml or json are accepted) and return it
    as a dictionary.

    Args:
        extract_filename: The path to the extract description file

    Returns:
        The contents of the extract description
    """
    with open_or_yield(extract_filename) as infile:
        data = infile.read()

    try:
        return json.loads(data)
    except json.decoder.JSONDecodeError:
        # Assume this is a yaml file and not a json file
        pass

    try:
        return yaml.safe_load(data)
    except yaml.error.YAMLError:
        raise ValueError("Contents of extract file appear to be neither json nor yaml")
