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
from typing import Iterator, List, Optional, Union, Dict

import pandas as pd
import numpy as np
import yaml

from ipumspy import noextract

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
    dtype: Optional[dict] = None,
    **kwargs,
):
    # if ddi.file_description.structure != "rectangular":
    #     raise NotImplementedError("Structure must be rectangular")

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
                # numpy_type since _fix_decimal_expansion call will convert any shiftable integer columns to float anyway.
                "dtype": {desc.name: desc.numpy_type for desc in data_description},
            }
        )

        reader = pd.read_fwf
        mode = "rt"

        # Fixed width files also require fixing decimal expansions
        def _fix_decimal_expansion(df):
            for desc in data_description:
                if desc.shift:
                    shift = 10**desc.shift
                    df[desc.name] /= shift
            return df

    elif ".csv" in filename.suffixes:
        # A csv!
        reader = pd.read_csv
        kwargs.update(
            {
                "usecols": [desc.name for desc in data_description],
            }
        )

        if dtype is None:
            kwargs.update(
                {"dtype": {desc.name: desc.numpy_type for desc in data_description}}
            )
        else:
            kwargs.update({"dtype": dtype})

        mode = "rt"

        # CSVs have correct decimal expansions already; so we just make
        # this the identity function
        def _fix_decimal_expansion(df):
            return df

    elif ".parquet" in filename.suffixes:
        # A parquet file
        if dtype is not None:
            raise ValueError("dtype argument can't be used with parquet files.")
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

        if dtype is None:
            dtype = {desc.name: desc.pandas_type for desc in data_description}
            # NOTE(khw): The following line is for specifically handling YRBSS data,
            # which uses a different .dat format from all other files. This should
            # be resolved in the future by offering a `.parquet` version of the file
            # NOTE(rr): Looking at the codebook, I don't _think_ there are similar variables
            # in the NYTS data.
            if ddi.ipums_collection == "yrbss":
                for col in dtype:
                    if any(name in col for name in ["WEIGHT", "BMIPCTILE"]):
                        dtype[col] = pd.Float64Dtype()
            yield from (_fix_decimal_expansion(df).astype(dtype) for df in data)
        else:
            if ".dat" in filename.suffixes:
                # convert variables from default numpy_type to corresponding type in dtype.
                yield from (_fix_decimal_expansion(df).astype(dtype) for df in data)
            else:
                # In contrary to counter condition, df already has right dtype. It would be expensive to call astype for
                # nothing.
                yield from (_fix_decimal_expansion(df) for df in data)


def _get_common_vars(ddi: ddi_definitions.Codebook, data_description: List):
    # identify common variables
    # these variables have all rectypes listed in the variable-level rectype attribute
    # these are delimited by spaces within the string attribute
    # this list would probably be a useful thing to have as a file-level attribute...
    common_vars = [
        desc.name
        for desc in data_description
        if sorted(desc.rectype.split(" ")) == sorted(ddi.file_description.rectypes)
    ]
    return common_vars


def _get_rectype_vars(
    ddi: ddi_definitions.Codebook,
    rectype: str,
    common_vars: List,
    data_description: List,
):
    # NB: This might result in empty data frames for some rectypes
    # as the ddi contains all possible collection rectypes, even if only a few
    # are actually represented in the file.
    # TODO: prune empty rectype data frames
    rectype_vars = []
    rectype_vars.extend(common_vars)
    for desc in data_description:
        if desc.rectype == rectype:
            rectype_vars.append(desc.name)
    return rectype_vars


def read_microdata(
    ddi: ddi_definitions.Codebook,
    filename: Optional[fileutils.FileType] = None,
    encoding: Optional[str] = None,
    subset: Optional[List[str]] = None,
    dtype: Optional[dict] = None,
    **kwargs,
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
        dtype: A dictionary with variable names as keys and variable types as values.
            Has an effect only when used with pd.read_fwf or pd.read_csv engine. If None, pd.read_fwf or pd.read_csv use
            type ddi.data_description.pandas_type for all variables. See ipumspy.ddi.VariableDescription for more
            precision on ddi.data_description.pandas_type. If files are csv, and dtype is not None, pandas converts the
            column types once: on pd.read_csv call. When file format is .dat or .csv and dtype is None, two conversion
            occur: one on load, and one when returning the dataframe.
        kwargs: keyword args to be passed to the engine (pd.read_fwf, pd.read_csv, or
            pd.read_parquet depending on the file type)

    Returns:
        pandas data frame and pandas text file reader
    """
    # raise a warning if this is a hierarchical file
    if ddi.file_description.structure == "hierarchical":
        raise NotImplementedError(
            "Structure must be rectangular. Use `read_hierarchical_microdata()` for hierarchical extracts."
        )
    # just read it if its rectangular
    else:
        return next(
            _read_microdata(
                ddi,
                filename=filename,
                encoding=encoding,
                subset=subset,
                dtype=dtype,
                **kwargs,
            )
        )


def read_hierarchical_microdata(
    ddi: ddi_definitions.Codebook,
    filename: Optional[fileutils.FileType] = None,
    encoding: Optional[str] = None,
    subset: Optional[List[str]] = None,
    dtype: Optional[dict] = None,
    as_dict: Optional[bool] = True,
    **kwargs,
) -> Union[pd.DataFrame, Dict]:
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
        dtype: A dictionary with variable names as keys and variable types as values.
            Has an effect only when used with pd.read_fwf or pd.read_csv engine. If None, pd.read_fwf or pd.read_csv use
            type ddi.data_description.pandas_type for all variables. See ipumspy.ddi.VariableDescription for more
            precision on ddi.data_description.pandas_type. If files are csv, and dtype is not None, pandas converts the
            column types once: on pd.read_csv call. When file format is .dat or .csv and dtype is None, two conversion
            occur: one on load, and one when returning the dataframe.
        as_dict: A flag to indicate whether to return a single data frame or a dictionary with one data frame per record
            type in the extract data file. Set to True to recieve a dictionary of data frames.
        kwargs: keyword args to be passed to the engine (pd.read_fwf, pd.read_csv, or
            pd.read_parquet depending on the file type)

    Returns:
        pandas data frame or a dictionary of pandas data frames
    """
    # RECTYPE must be included if subset list is specified
    if subset is not None:
        if "RECTYPE" not in subset:
            raise ValueError(
                "RECTYPE must be included in the subset list for hierarchical extracts."
            )
        else:
            data_description = [
                desc for desc in ddi.data_description if desc.name in subset
            ]
    else:
        data_description = ddi.data_description

    # raise a warning if this is a rectantgular file
    if ddi.file_description.structure == "rectangular":
        raise NotImplementedError(
            "Structure must be hierarchical. Use `read_microdata()` for rectangular extracts."
        )
    else:
        df_dict = {}
        common_vars = _get_common_vars(ddi, data_description)
        for rectype in ddi.file_description.rectypes:
            rectype_vars = _get_rectype_vars(
                ddi, rectype, common_vars, data_description
            )
            # it feels like there should be a better way to do this bit...
            rectype_df = pd.concat(
                [
                    df
                    for df in _read_microdata(
                        ddi, filename, encoding, rectype_vars, dtype, **kwargs
                    )
                ]
            )
            # filter out non-relevant rectype records
            df_dict[rectype] = rectype_df[rectype_df["RECTYPE"] == rectype]
        if as_dict:
            return df_dict
        else:
            # read the hierarchical file
            df = pd.concat(
                [
                    df
                    for df in _read_microdata(
                        ddi, filename, encoding, subset, dtype, **kwargs
                    )
                ]
            )
            # for each rectype, nullify variables that belong to other rectypes
            for rectype in df_dict.keys():
                # create a list of variables that are for rectypes other than the current rectype
                # and are not included in the list of varaibles that are common across rectypes
                non_rt_cols = [
                    cols
                    for rt in df_dict.keys()
                    for cols in df_dict[rt].columns
                    if rt != rectype and cols not in common_vars
                ]
                for col in non_rt_cols:
                    # maintain data type when "nullifying" variables from other record types
                    if df[col].dtype == pd.Int64Dtype():
                        df[col] = np.where(df["RECTYPE"] == rectype, pd.NA, df[col])
                        df[col] = df[col].astype(pd.Int64Dtype())
                    elif df[col].dtype == pd.StringDtype():
                        df[col] = np.where(df["RECTYPE"] == rectype, "", df[col])
                        df[col] = df[col].astype(pd.StringDtype())
                    elif df[col].dtype == float:
                        df[col] = np.where(df["RECTYPE"] == rectype, np.nan, df[col])
                        df[col] = df[col].astype(float)
                    # this should (theoretically) never be hit... unless someone specifies an illegal data type
                    # themselves, but that should also be caught before this stage.
                    else:
                        raise TypeError(
                            f"Data type {df[col].dtype} for {col} is not an allowed type."
                        )
            return df


def read_microdata_chunked(
    ddi: ddi_definitions.Codebook,
    filename: Optional[fileutils.FileType] = None,
    encoding: Optional[str] = None,
    subset: Optional[List[str]] = None,
    chunksize: Optional[int] = None,
    dtype: Optional[dict] = None,
    **kwargs,
) -> Iterator[pd.DataFrame]:
    """
    Read in microdata in chunks as specified by the Codebook.
    As these files are often large, you may wish to filter or read in chunks.
    As an example of how you might do that, consider the following example that
    filters only for rows in Rhode Island:

        iter_microdata = read_microdata_chunked(ddi, chunksize=1000)
        df = pd.concat([df[df['STATEFIP'] == 44]] for df in iter_microdata])

    This method also works for large hierarchical files. When reading these files
    in chunks, users will want to be sure to filter on the RECTYPE variable. For example,
    the code below reads in only household records in Rhode Island:

        iter_microdata = read_microdata_chunked(ddi, chunksize=1000)
        df = pd.concat([df[(df['RECTYPE'] == 'H') & (df['STATEFIP'] == 44)] for df in iter_microdata])

    Args:
        ddi: The codebook representing the data
        filename: The path to the data file. If not present, gets from
                     ddi and assumes the file is relative to the current working directory
        encoding: The encoding of the data file. If not present, reads from ddi
        subset: A list of variable names to keep. If None, will keep all
        dtype: A dictionary with variable names as keys and variable types as values.
            Has an effect only when used with pd.read_fwf or pd.read_csv engine. If None, pd.read_fwf or pd.read_csv use
            type ddi.data_description.pandas_type for all variables. See ipumspy.ddi.VariableDescription for more
            precision on ddi.data_description.pandas_type. If files are csv, and dtype is not None, pandas converts the
            column types once: on pd.read_csv call. When file format is .dat or .csv and dtype is None, two conversion
            occur: one on load, and one when returning the dataframe.
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
        dtype=dtype,
        chunksize=chunksize,
        **kwargs,
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
