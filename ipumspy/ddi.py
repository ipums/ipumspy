from dataclasses import dataclass
from typing import Dict, List, Optional
from xml.etree import ElementTree as ET


@dataclass
class VariableDescription:
  id: str
  name: str

  start: int
  end: int

  label: str
  description: str
  concept: str

  vartype: str
  shift: Optional[int]

  @classmethod
  def read(cls, elt: ET, ddi_namespace: str):
    """
    Read an XML description of a variable. Must pass a `ddi_namespace` that
    says what the xmlns is for the file
    """
    namespaces = {'ddi': ddi_namespace}
    return cls(
      id=elt.attrib['ID'],
      name=elt.attrib['name'],
      start=int(elt.find('./ddi:location', namespaces).attrib['StartPos']) - 1,  # 0 based in python
      end=int(elt.find('./ddi:location', namespaces).attrib['EndPos']),  # Exclusive ends in python
      label=elt.find('./ddi:labl', namespaces).text,
      description=elt.find('./ddi:txt', namespaces).text,
      concept=elt.find('./ddi:concept', namespaces).text,
      vartype=elt.find('./ddi:varFormat', namespaces).attrib['type'],
      shift=int(elt.attrib.get('dcml')) if 'dcml' in elt.attrib else None
    )


@dataclass
class FileDescription:
  filename: str
  description: str
  structure: str
  encoding: str
  format: str
  place: str

  @classmethod
  def read(cls, elt: ET, ddi_namespace: str):
    namespaces = {'ddi': ddi_namespace}
    return cls(
      filename=elt.find('./ddi:fileName', namespaces).text,
      description=elt.find('./ddi:fileCont', namespaces).text,
      structure=elt.find('./ddi:fileStrc', namespaces).attrib['type'],
      encoding=elt.find('./ddi:fileType', namespaces).attrib.get('charset', 'iso-8859-1').lower(),
      format=elt.find('./ddi:format', namespaces).text,
      place=elt.find('./ddi:filePlac', namespaces).text
    )


@dataclass
class Codebook:
  """
  A class representing an XML codebook downloaded from IPUMS
  """
  file_description: FileDescription
  data_description: List[VariableDescription]

  @classmethod
  def read(cls, elt: ET, ddi_namespace: str):
    namespaces = {'ddi': ddi_namespace}
    file_txts = elt.findall('./ddi:fileDscr/ddi:fileTxt', namespaces)
    if len(file_txts) != 1:
      raise NotImplementedError('Codebooks with more than one file type are not supported')

    return cls(
      file_description=FileDescription.read(file_txts[0], ddi_namespace),
      data_description=[
        VariableDescription.read(desc, ddi_namespace) for desc in elt.findall('./ddi:dataDscr/ddi:var', namespaces)
      ]
    )
