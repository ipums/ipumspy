# This file is part of ipumspy.
# For copyright and licensing information, see the NOTICE and LICENSE files
# in this project's top-level directory, and also on-line at:
#   https://github.com/ipums/ipumspy

"""
Functions for reading and processing IPUMS data
"""
import copy
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterator, List, Optional, Union

import pandas as pd

from . import ddi as ddi_definitions


def get_variable_info(varname: str,
                      ddi: ddi_definitions.Codebook,):
    for vardesc in ddi.data_description:
        if vardesc.id == varname.upper():
            varname_vardesc = vardesc
            return varname_vardesc
    else:
        # put a better error here eventually
        raise RuntimeError(f'No description found for {varname}.')
