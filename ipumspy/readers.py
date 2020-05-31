import re
import xml.etree.ElementTree as ET
from typing import Union

import pandas as pd

from . import ddi, fileutils


def read_ipums_ddi(ddi_file: fileutils.FILE_TYPE) -> ddi.Codebook:
  with fileutils.xml_opener(ddi_file) as opened_file:
    root = ET.parse(opened_file).getroot()

  # Extract the namespace if there is one
  match = re.match(r'^\{(.*)\}', root.tag)
  namespace = match.groups()[0] if match else ''

  return ddi.Codebook.read(root, namespace)


def read_microdata(ddi: ddi.Codebook) -> pd.DataFrame:
  if ddi.file_description.structure != 'rectangular':
    raise NotImplementedError('Structure must be rectangular')

  with fileutils.data_opener(ddi.file_description.filename, encoding=ddi.file_description.encoding) as infile:
    return pd.read_fwf(
      infile,
      colspecs=[(desc.start, desc.end) for desc in ddi.data_description],
      names=[desc.name for desc in ddi.data_description]
    )
