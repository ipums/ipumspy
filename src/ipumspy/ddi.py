# This file is part of ipumspy.
# For copyright and licensing information, see the NOTICE and LICENSE files
# in this project's top-level directory, and also on-line at:
#   https://github.com/ipums/ipumspy

"""
Utilities for working with IPUMS DDI formats
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
from xml.etree import ElementTree as ET


@dataclass
class VariableDescription:
    """
    Individual variables are described in the DDI. These are representations
    of those descriptions as dataclasses.
    """

    # pylint: disable=too-many-instance-attributes

    id: str  # pylint: disable=invalid-name
    name: str
    codes: dict

    start: int
    end: int

    label: str
    description: str
    concept: str

    vartype: str
    shift: Optional[int]

    @classmethod
    def read(cls, elt: ET, ddi_namespace: str) -> VariableDescription:
        """
        Read an XML description of a variable. Must pass a `ddi_namespace` that
        says what the xmlns is for the file
        """
        namespaces = {"ddi": ddi_namespace}

        labels_dict = {}
        for cat in elt.findall("./ddi:catgry", namespaces):
            label = cat.find("./ddi:labl", namespaces).text
            value = cat.find("./ddi:catValu", namespaces).text
            # make values integers when possible
            try:
                labels_dict[label] = int(value)
            except TypeError:
                labels_dict[label] = int(value)

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
            vartype=elt.find("./ddi:varFormat", namespaces).attrib["type"],
            shift=int(elt.attrib.get("dcml")) if "dcml" in elt.attrib else None,
        )


@dataclass
class FileDescription:
    """
    In the IPUMS DDI, the file has its own particular description. Extract
    that from the XML.
    """

    filename: str
    description: str
    structure: str
    encoding: str
    format: str
    place: str

    @classmethod
    def read(cls, elt: ET, ddi_namespace: str) -> FileDescription:
        """
        Read a FileDescription from the parsed XML
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


@dataclass
class Codebook:
    """
    A class representing an XML codebook downloaded from IPUMS
    """

    file_description: FileDescription
    data_description: List[VariableDescription]
    citation: str
    conditions: str

    @classmethod
    def read(cls, elt: ET, ddi_namespace: str) -> Codebook:
        """
        Read a Codebook from the parsed XML
        """
        namespaces = {"ddi": ddi_namespace}

        file_txts = elt.findall("./ddi:fileDscr/ddi:fileTxt", namespaces)
        if len(file_txts) != 1:
            raise NotImplementedError(
                "Codebooks with more than one file type are not supported"
            )

        citation = elt.find(
            "./ddi:stdyDscr/ddi:dataAccs/ddi:useStmt/ddi:citReq", namespaces
        ).text
        conditions = elt.find(
            "./ddi:stdyDscr/ddi:dataAccs/ddi:useStmt/ddi:conditions", namespaces
        ).text

        return cls(
            file_description=FileDescription.read(file_txts[0], ddi_namespace),
            data_description=[
                VariableDescription.read(desc, ddi_namespace)
                for desc in elt.findall("./ddi:dataDscr/ddi:var", namespaces)
            ],
            citation=citation,
            conditions=conditions,
        )
