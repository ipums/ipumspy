# This file is part of ipumspy.
# For copyright and licensing information, see the NOTICE and LICENSE files
# in this project's top-level directory, and also on-line at:
#   https://github.com/ipums/ipumspy

"""
Functions for accessing IPUMS data and metadata
"""
import pandas as pd

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
