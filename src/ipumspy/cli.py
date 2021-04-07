"""
A CLI for accessing IPUMS utilities
"""
import copy
import dataclasses
import json
from typing import Tuple

import click
import pandas as pd
import pyarrow as pa
from pyarrow.parquet import ParquetWriter

from . import readers


@click.group("ipums")
def ipums_group():
    """
    Tools for working with IPUMS files via the command line
    """


def _append_ipums_schema(df: pd.DataFrame, ddi):
    # Append ipums data to schema
    schema = pa.Schema.from_pandas(df)
    metadata = copy.deepcopy(schema.metadata)
    metadata[b"ipums"] = json.dumps(dataclasses.asdict(ddi)).encode("utf8")
    schema = schema.with_metadata(metadata)
    return schema


@ipums_group.command("convert")
@click.argument("ddifile", type=click.Path(exists=True))
@click.argument("datafile", type=click.Path(exists=True))
@click.argument("outfile", type=click.Path())
@click.option(
    "--string-column",
    "-s",
    "string_columns",
    multiple=True,
    help="Columns which we will always cast as a sting type",
)
def convert_command(
    ddifile: str, datafile: str, outfile: str, string_columns: Tuple[str]
):
    """
    Perform one-off conversions for faster loading times in the future

    DDIFILE is a path to an XML codebook describing an IPUMS extract.
    DATAFILE is the path to the associated .dat.gz file.
    OUTFILE is the path that you'd like the file to be saved to. For now, the
    output format will be parquet.
    """
    ddi = readers.read_ipums_ddi(ddifile)
    string_columns = string_columns or []

    # Just read a few lines for getting the schema
    # This is because I'm lazy. Should be able to construct from ddi
    tmp_df = next(
        readers.read_microdata_chunked(ddi, filename=datafile, chunksize=1024)
    ).convert_dtypes(
        infer_objects=False,
        convert_boolean=False,
        convert_integer=True,
        convert_string=False,
    )

    for string_column in string_columns:
        tmp_df[string_column] = tmp_df[string_column].astype("string")

    with ParquetWriter(
        outfile, pa.Schema.from_pandas(tmp_df), compression="snappy"
    ) as writer:
        reader = readers.read_microdata_chunked(
            ddi, filename=datafile, chunksize=100000
        )
        # TODO(khw): Figure out how to get a progressbar of the appropriate length here
        for df in reader:
            # Convert some missing data types
            df = df.convert_dtypes(
                infer_objects=False,
                convert_boolean=False,
                convert_integer=True,
                convert_string=False,
            )
            for string_column in string_columns:
                tmp_df[string_column] = tmp_df[string_column].astype("string")
            batch = pa.Table.from_pandas(df)
            writer.write_table(batch)
