import copy
import re
import xml.etree.ElementTree as ET
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, List, Optional, Union

import pandas as pd

from . import ddi, fileutils


def read_ipums_ddi(ddi_file: fileutils.FILE_TYPE) -> ddi.Codebook:
    with fileutils.xml_opener(ddi_file) as opened_file:
        root = ET.parse(opened_file).getroot()

    # Extract the namespace if there is one
    match = re.match(r"^\{(.*)\}", root.tag)
    namespace = match.groups()[0] if match else ""

    return ddi.Codebook.read(root, namespace)


def _read_microdata(
    ddi: ddi.Codebook,
    filename: Optional[fileutils.FILE_TYPE] = None,
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

    # Set up the correct reader for our file type
    kwargs = copy.deepcopy(kwargs)
    if ".dat" in filename.suffixes:
        # This is a fixed width file
        kwargs.update(
            {
                "colspecs": [(desc.start, desc.end) for desc in data_description],
                "names": [desc.name for desc in data_description],
            }
        )
        reader = pd.read_fwf

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
        kwargs.update({"usecols": [desc.name for desc in data_description]})

        # CSVs have correct decimal expansions already; so we just make this the identity function
        def _fix_decimal_expansion(df):
            return df

    else:
        raise ValueError("Only CSV and .dat files are supported")

    with fileutils.data_opener(filename, encoding=encoding) as infile:
        if iterator:
            data = [reader(infile, **kwargs)]
        else:
            kwargs.update({"iterator": True, "chunksize": chunksize})
            data = reader(infile, **kwargs)

        yield from (_fix_decimal_expansion(df) for df in data)


def read_microdata(
    ddi: ddi.Codebook,
    filename: Optional[fileutils.FILE_TYPE] = None,
    encoding: Optional[str] = None,
    subset: Optional[List[str]] = None,
    **kwargs
) -> Union[pd.DataFrame, pd.io.parsers.TextFileReader]:
    """
  Read in microdata as specified by the Codebook.

  Args:
    ddi: The codebook representing the data
    filename: The path to the data file. If not present, gets from
      ddi and assumes the file is relative to the current working directory
    encoding: The encoding of the data file. If not present, reads from ddi
    subset: A list of variable names to keep. If None, will keep all
    kwargs: keyword args to be passed to pd.read_fwf

  Returns: The dataframe to read
  """
    return next(
        _read_microdata(
            ddi, filename=filename, encoding=encoding, subset=subset, **kwargs
        )
    )


def read_microdata_chunked(
    ddi: ddi.Codebook,
    filename: Optional[fileutils.FILE_TYPE] = None,
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
