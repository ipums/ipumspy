# This file is part of ipumspy.
# For copyright and licensing information, see the NOTICE and LICENSE files
# in this project's top-level directory, and also on-line at:
#   https://github.com/ipums/ipumspy

"""
Functions for accessing IPUMS data and metadata
"""
from typing import Dict

import bs4
import pandas as pd
import requests
from functools import lru_cache

from . import ddi as ddi_definitions


class CollectionInformation:
    def __init__(self, collection: str):
        self.collection = collection
        """Name of an IPUMS data collection"""
        # kluge to make up for lack of metadata api
        self.sample_ids_url = (
            f"https://{collection}.ipums.org/{collection}-action/samples/sample_ids"
        )
        """sample id url"""
        """
        A class to access collection-level information about IPUMS data collections.
        
        Args:
            collection: Name of an IPUMS data collection
         """

    @property
    @lru_cache(maxsize=100)
    def sample_ids(self) -> Dict[str, str]:
        """
        dict: Crosswalk of IPUMS sample descriptions and IPUMS sample IDs; keys are
        sample descriptions, values are sample ids
        """
        sample_ids_page = requests.get(self.sample_ids_url).text
        td_list = []
        soup = bs4.BeautifulSoup(sample_ids_page, "html.parser")
        match = soup.findAll("td")
        if len(match) > 0:
            for m in match:
                td_list.append(str(m))

        # ignore table formatting stuff
        table_items = td_list[4:]
        # make list of sample ids and their descriptions
        descs = []
        samps = []
        for i in range(0, len(table_items)):
            if i % 2 == 0:
                samps.append(table_items[i][4:-5])
            else:
                descs.append(table_items[i][6:-7].strip())

        # zip it into a dict for easy access
        sample_ids_dict = dict(zip(descs, samps))
        return sample_ids_dict


def tabulate(
    vardesc: ddi_definitions.VariableDescription, df: pd.DataFrame
) -> pd.DataFrame:
    """
    Single-variable table with labels.

    Args:
        vardesc: from the ddi codebook
        df: pandas DataFrame containing data to display
    Returns:
        pandas Data frame containing values, value labels, frequencies,
        and proportions for the specified variable
    """

    tab_df = pd.concat(
        [
            df[vardesc.name].value_counts().sort_index(),
            df[vardesc.name].value_counts(normalize=True).sort_index(),
        ],
        axis=1,
        keys=["counts", "pct"],
    )
    col_order = ["counts", "pct"]

    if vardesc.codes:
        tab_df["val"] = tab_df.index
        tab_df["lab"] = tab_df["val"].map({v: k for k, v in vardesc.codes.items()})
        col_order = ["val", "lab", "counts", "pct"]

    return tab_df[col_order]
