# This file is part of ipumspy.
# For copyright and licensing information, see the NOTICE and LICENSE files
# in this project's top-level directory, and also on-line at:
#   https://github.com/ipums/ipumspy

"""
Functions for accessing IPUMS data and metadata
"""
import pandas as pd

from . import ddi as ddi_definitions


def get_variable_info(
    varname: str, ddi: ddi_definitions.Codebook,
):
    """
    Retrieve the VariableDescription for an IPUMS variable.

    Args:
        varname: Name of a variable in your IPUMS extract
        ddi: The codebook representing the data

    Returns:
        A VariableDescription instance
    """
    for vardesc in ddi.data_description:
        if vardesc.id == varname.upper():
            varname_vardesc = vardesc
            return varname_vardesc
    else:
        # put a better error here eventually
        raise RuntimeError(f"No description found for {varname}.")


def tab(df, VariableDescription):
    """
    Tabs with labels
    """

    # get freqs and pct
    tab_df = pd.DataFrame(
        {
            "val": df[VariableDescription.name].value_counts().sort_index().index,
            "count": df[VariableDescription.name].value_counts().sort_index(),
            "pct": df[VariableDescription.name]
            .value_counts(normalize=True)
            .sort_index(),
        }
    )

    # add value labels if they exist
    if len(VariableDescription.codes.keys()) > 0:
        # get labels
        lab_df = pd.DataFrame(
            {
                "val": list(VariableDescription.codes.values()),
                "lab": list(VariableDescription.codes.keys()),
            }
        )

        lab_tab_df = pd.merge(tab_df, lab_df, on="val", how="inner")
        print(lab_tab_df[["val", "lab", "count", "pct"]].to_string(index=False))
    else:
        print(tab_df.to_string(index=False))
