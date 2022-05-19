# This file is part of ipumspy.
# For copyright and licensing information, see the NOTICE and LICENSE files
# in this project's top-level directory, and also on-line at:
#   https://github.com/ipums/ipumspy

"""
Utilities for working with IPUMS DDI formats
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from xml.etree import ElementTree as ET
from xml.etree.ElementTree import Element

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class VariableDescription:
    """
    Individual variables are described in the DDI. These are representations
    of those descriptions as dataclasses.
    """

    # pylint: disable=too-many-instance-attributes

    id: str  # pylint: disable=invalid-name
    """variable id (this is the same as its name)"""
    name: str
    """variable name"""
    codes: Dict[str, Union[int, str]]
    """a dictionary of codes and value labels"""

    start: int
    """variable's starting column in the extract data file"""
    end: int
    """variable's final column in the extract data file"""

    label: str
    """variable label"""
    description: str
    """variable description"""
    concept: str
    """IPUMS variable group"""

    vartype: str
    """variable data type"""
    shift: Optional[int]
    """number of implied decimal places"""

    @property
    def python_type(self) -> type:
        """
        The Python type of this variable.
        """
        if self.vartype == "numeric":
            if (self.shift is None) or (self.shift == 0):
                return int
            return float
        return str

    @property
    def numpy_type(self) -> type:
        """
        The Numpy type of this variable. Note that this type must support nullability,
        and hence even for integers it is "float64".
        """
        if self.vartype == "numeric":
            if (self.shift is None) or (self.shift == 0):
                return np.float64
            return np.float64
        return str

    @property
    def pandas_type(self) -> type:
        """
        The Pandas type of this variable. This supports the recently added nullable
        pandas dtypes, and so the integer type is "Int64" and the string type is
        "string" (instead of "object")
        """
        if self.vartype == "numeric":
            if (self.shift is None) or (self.shift == 0):
                return pd.Int64Dtype()
            return np.float64
        return pd.StringDtype()

    @property
    def pandas_type_efficient(self) -> type:
        """
        In contrary to `self.pandas_type`, `self.pandas_type_efficient` doesn't implement "Int64" type but "numpy.float64" for
        integer type. It's more efficient and pandas uses this approach for type inference:
        https://pandas-docs.github.io/pandas-docs-travis/user_guide/integer_na.html
        It can be considered as a mix between `self.pandas_type` and `self.numpy_type`
        """
        if self.vartype == "numeric":
            if (self.shift is None) or (self.shift == 0):
                return np.float64
            return np.float64
        return pd.StringDtype()

    @classmethod
    def read(cls, elt: Element, ddi_namespace: str) -> VariableDescription:
        """
        Read an XML description of a variable.

        Args:
            elt: xml element tree from parsed extract ddi
            ddi_namespace: ddi namespace that says what the xmlns is for the file
        Returns:
            VariableDescription object
        """
        namespaces = {"ddi": ddi_namespace}

        vartype = elt.find("./ddi:varFormat", namespaces).attrib["type"]
        labels_dict = {}
        for cat in elt.findall("./ddi:catgry", namespaces):
            label = cat.find("./ddi:labl", namespaces).text
            value = cat.find("./ddi:catValu", namespaces).text
            # make values integers when possible
            if vartype == "numeric":
                labels_dict[label] = int(value)
            else:
                labels_dict[label] = value

        return cls(
            id=elt.attrib["ID"],
            name=elt.attrib["name"],
            codes=labels_dict,
            start=int(elt.find("./ddi:location", namespaces).attrib["StartPos"])
            - 1,  # 0 based in python
            end=int(
                elt.find("./ddi:location", namespaces).attrib["EndPos"]
            ),  # Exclusive ends in python
            label=elt.find("./ddi:labl", namespaces).text,
            description=elt.find("./ddi:txt", namespaces).text,
            concept=elt.find("./ddi:concept", namespaces).text,
            vartype=vartype,
            shift=int(elt.attrib.get("dcml")) if "dcml" in elt.attrib else None,
        )


@dataclass(frozen=True)
class FileDescription:
    """
    In the IPUMS DDI, the file has its own particular description. Extract
    that from the XML.
    """

    filename: str
    """IPUMS extract ddi file name"""
    description: str
    """IPUMS ddi file description"""
    structure: str
    """
    IPUMS extract data file structure.
    Valid structures: rectangular, hierarchical
    """
    encoding: str
    """IPUMS file encoding scheme"""
    format: str
    """IPUMS extract data file format"""
    place: str
    """IPUMS physical address"""

    @classmethod
    def read(cls, elt: Element, ddi_namespace: str) -> FileDescription:
        """
        Read a FileDescription from the parsed XML

        Args:
            elt: xml element tree from parsed extract ddi
            ddi_namespace: ddi namespace that says what the xmlns is for the file
        Returns:
            FileDescription object
        """
        namespaces = {"ddi": ddi_namespace}
        return cls(
            filename=elt.find("./ddi:fileName", namespaces).text,
            description=elt.find("./ddi:fileCont", namespaces).text,
            structure=elt.find("./ddi:fileStrc", namespaces).attrib["type"],
            encoding=elt.find("./ddi:fileType", namespaces)
            .attrib.get("charset", "iso-8859-1")
            .lower(),
            format=elt.find("./ddi:format", namespaces).text,
            place=elt.find("./ddi:filePlac", namespaces).text,
        )


@dataclass(frozen=True)
class Codebook:
    """
    A class representing an XML codebook downloaded from IPUMS
    """

    file_description: FileDescription
    """FileDescription object"""
    data_description: List[VariableDescription]
    """list of VariableDescription objects"""
    samples_description: List[str]
    """list of IPUMS sample descriptions"""
    ipums_citation: str
    """The appropriate citation for the IPUMS extract. Please use it!"""
    ipums_conditions: str
    """IPUMS terms of use"""
    ipums_collection: str
    """IPUMS collection name"""
    ipums_doi: str
    """"DOI of IPUMS data set"""

    @classmethod
    def read(cls, elt: ET, ddi_namespace: str) -> Codebook:
        """
        Read a Codebook from the parsed XML

        Args:
            elt: xml element tree from parsed extract ddi
            ddi_namespace: ddi namespace that says what the xmlns is for the file
        Returns:
            Codebook object
        """
        namespaces = {"ddi": ddi_namespace}

        file_txts = elt.findall("./ddi:fileDscr/ddi:fileTxt", namespaces)
        if len(file_txts) != 1:
            raise NotImplementedError(
                "Codebooks with more than one file type are not supported"
            )

        # compensation for lack of metadata api
        _sample_descriptions = []
        for item in elt.findall("./ddi:stdyDscr/ddi:stdyInfo/ddi:notes", namespaces):
            sample_name_row = item.text.strip().split("\n")[0]
            _sample_descriptions.append(sample_name_row)
        ipums_samples = [desc.split(":")[-1].strip() for desc in _sample_descriptions]

        ipums_citation = elt.find(
            "./ddi:stdyDscr/ddi:dataAccs/ddi:useStmt/ddi:citReq", namespaces
        ).text
        ipums_conditions = elt.find(
            "./ddi:stdyDscr/ddi:dataAccs/ddi:useStmt/ddi:conditions", namespaces
        ).text
        ipums_collection = elt.find(
            "./ddi:stdyDscr/ddi:citation/ddi:serStmt/ddi:serName", namespaces
        ).attrib["abbr"]
        ipums_doi = elt.find(
            "./ddi:stdyDscr/ddi:citation/ddi:serStmt/ddi:serInfo", namespaces
        ).text

        return cls(
            file_description=FileDescription.read(file_txts[0], ddi_namespace),
            data_description=[
                VariableDescription.read(desc, ddi_namespace)
                for desc in elt.findall("./ddi:dataDscr/ddi:var", namespaces)
            ],
            samples_description=ipums_samples,
            ipums_citation=ipums_citation,
            ipums_conditions=ipums_conditions,
            ipums_collection=ipums_collection,
            ipums_doi=ipums_doi,
        )

    def get_variable_info(self, name: str) -> VariableDescription:
        """
        Retrieve the VariableDescription for an IPUMS variable

        Args:
            name: Name of a variable in your IPUMS extract
        Returns:
            A VariableDescription instance
        """
        try:
            return [
                vardesc
                for vardesc in self.data_description
                if vardesc.id == name.upper()
            ][0]
        except IndexError:
            raise ValueError(f"No description found for {name}.")

    def get_all_types(self, type_format: str, string_pyarrow: bool = False) -> dict:
        """
        Retrieve all column types

        Args:
            type_format: type format. Should be one of ["numpy_type", "pandas_type", "pandas_type_efficient",
                         "python_type", "vartype"]
            string_pyarrow: has an effect when True and used with type_format in ["pandas_type", "pandas_type_efficient"].
             In this case, string types==pd.StringDtype() is replaced with pd.StringDtype(storage='pyarrow').

        Returns:
            A dict with column names column dtype mapping.

        Examples:
            Let's see an example of usage with pandas.read_csv engine:

            >>> from ipumspy import readers
            >>> ddi_codebook = readers.read_ipums_ddi('extract_ddi.xml')
            >>> dataframe_dtypes = ddi_codebook.get_all_types(type_format='pandas_type', string_pyarrow=False)
            >>> df = readers.read_microdata(ddi=ddi_codebook, filename="extract.csv", dtype=dataframe_dtypes)

            And an example of usecase of string_pyarrow set to True:

            >>> from ipumspy import readers
            >>> ddi_codebook = readers.read_ipums_ddi('extract_ddi.xml')
            >>> dataframe_dtypes = ddi_codebook.get_all_types(type_format='pandas_type', string_pyarrow=True)
            >>> # No particular impact for reading from csv.
            >>> df = readers.read_microdata(ddi=ddi_codebook, filename="extract.csv", dtype=dataframe_dtypes)
            >>> # The benefit of using string_pyarrow: converting to parquet. The writing time is reduced.
            >>> df.to_parquet("extract.parquet")
            >>> # Also, the data loaded from the derived extract.parquet will be faster than if the csv file was converted
            >>> # using string_pyarrow=False


        """
        if (
            type_format not in ["pandas_type", "pandas_type_efficient"]
            and string_pyarrow is True
        ):
            raise ValueError(
                'string_pyarrow can be set to True only if type_format in ["pandas_type", "pandas_type_efficient"].'
            )
        try:
            # traversing the doc.
            all_types = {}
            for variable_descr in self.data_description:
                type_value = getattr(variable_descr, type_format)
                if type_value == pd.StringDtype() and string_pyarrow is True:
                    type_value = pd.StringDtype(storage="pyarrow")
                all_types.update({variable_descr.name: type_value})
            return all_types
        except AttributeError:
            acceptable_values = [
                "numpy_type",
                "pandas_type",
                "pandas_type_efficient",
                "python_type",
                "vartype",
            ]
            raise ValueError(f"{type_format} not in {acceptable_values}")
