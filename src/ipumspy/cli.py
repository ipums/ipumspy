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
import yaml
from pyarrow.parquet import ParquetWriter

from . import readers
from .api import IpumsApi
from .fileutils import open_or_yield


@click.group("ipums")
def ipums_group():
    """
    Tools for working with IPUMS files via the command line
    """


@ipums_group.group("api")
def ipums_api_group():
    """ Interact with the IPUMS API """


@ipums_api_group.command("submit")
@click.argument(
    "extract",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, allow_dash=True),
)
@click.option(
    "--api-key",
    "-k",
    envvar="IPUMS_API_KEY",
    default=None,
    type=str,
    help="Your IPUMS API key. Must be provided either here or via the IPUMS_API_KEY environment variable",
)
@click.option(
    "--num-retries",
    "-n",
    default=3,
    type=int,
    help="The number of retries on transient errors",
)
def ipums_api_submit_command(extract: str, api_key: str, num_retries: int):
    """ Submit an extract request to the IPUMS API """
    if not api_key:
        click.BadOptionUsage("api_key", "You must provide an API key")

    api_client = IpumsApi(api_key, num_retries=num_retries)
    with open_or_yield(extract) as infile:
        extract_description: dict = yaml.safe_load(infile)

    # For now we only support a single extract
    extract_description = extract_description["extracts"][0]
    extract_description.setdefault("data_format", "fixed_width")
    extract_description.setdefault("data_structure", {"rectangular": {"on", "P"}})

    extract_number = getattr(
        api_client, extract_description["collection"]
    ).submit_extract(extract_description)
    click.echo(
        f"Your extract has been successfully submitted with number {extract_number}"
    )


@ipums_api_group.command("check")
@click.argument("collection", type=str)
@click.argument("extract_number", type=int)
@click.option(
    "--api-key",
    "-k",
    envvar="IPUMS_API_KEY",
    default=None,
    type=str,
    help="Your IPUMS API key. Must be provided either here or via the IPUMS_API_KEY environment variable",
)
@click.option(
    "--num-retries",
    "-n",
    default=3,
    type=int,
    help="The number of retries on transient errors",
)
def ipums_api_check_command(
    collection: str, extract_number: int, api_key: str, num_retries: int
):
    """ Check the status of an extract """
    if not api_key:
        click.BadOptionUsage("api_key", "You must provide an API key")

    api_client = IpumsApi(api_key, num_retries=num_retries)
    status = getattr(api_client, "collection").extract_status(extract_number)

    click.echo(
        f"Extract {extract_number} in collection {collection} has status {status}"
    )


@ipums_api_group.command("download")
@click.argument("collection", type=str)
@click.argument("extract_number", type=int)
@click.option(
    "--output-dir",
    "-o",
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    help="The directory to download the extract to. If not passed, current working directory is used. If passed, must be a directory that exists.",
)
@click.option(
    "--api-key",
    "-k",
    envvar="IPUMS_API_KEY",
    default=None,
    type=str,
    help="Your IPUMS API key. Must be provided either here or via the IPUMS_API_KEY environment variable",
)
@click.option(
    "--num-retries",
    "-n",
    default=3,
    type=int,
    help="The number of retries on transient errors",
)
def ipums_api_download_command(
    collection: str,
    extract_number: int,
    output_dir: str,
    api_key: str,
    num_retries: int,
):
    """ Download an IPUMS extract """
    if not api_key:
        click.BadOptionUsage("api_key", "You must provide an API key")

    api_client = IpumsApi(api_key, num_retries=num_retries)
    getattr(api_client, collection).download_extract(
        extract_number, download_dir=output_dir
    )


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
