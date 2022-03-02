# This file is part of ipumspy.
# For copyright and licensing information, see the NOTICE and LICENSE files
# in this project's top-level directory, and also on-line at:
#   https://github.com/ipums/ipumspy

"""
Functions for accessing IPUMS data and metadata
"""
import requests
import bs4
import pandas as pd
from typing import Dict

from . import ddi as ddi_definitions


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


def get_sample_ids(collection: str) -> Dict[str, str]:
    # kluge to make up for lack of metadata api
    sample_ids_url = (
        f"https://{collection}.ipums.org/{collection}-action/samples/sample_ids"
    )
    sample_ids_page = requests.get(sample_ids_url).text
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
