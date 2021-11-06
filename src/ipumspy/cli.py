# This file is part of ipumspy.
# For copyright and licensing information, see the NOTICE and LICENSE files
# in this project's top-level directory, and also on-line at:
#   https://github.com/ipums/ipumspy

"""
A CLI for accessing IPUMS utilities
"""
import copy
import dataclasses
import json
import sys
import time
from typing import Optional, Tuple

import click
import pandas as pd
import pyarrow as pa
from pyarrow.parquet import ParquetWriter

from . import readers
from .api import BaseExtract, IpumsApiClient, OtherExtract


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
    help=(
        "Your IPUMS API key. Must be provided either here or "
        "via the IPUMS_API_KEY environment variable"
    ),
    required=True,
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
    api_client = IpumsApiClient(api_key, num_retries=num_retries)
    extract_description = readers.read_extract_description(extract)

    # For now we only support a single extract
    extract_description = extract_description["extracts"][0]
    if extract_description["collection"] in BaseExtract._collection_to_extract:
        extract = BaseExtract._collection_to_extract[extract_description["collection"]](
            **extract_description
        )
    else:
        extract = OtherExtract(extract_description["collection"], extract_description)

    api_client.submit_extract(extract)

    click.echo(
        f"Your extract for collection {extract.collection} has been successfully "
        f"submitted with number {extract.extract_id}"
    )


@ipums_api_group.command("check")
@click.argument("collection", type=str)
@click.argument("extract_id", type=int)
@click.option(
    "--api-key",
    "-k",
    envvar="IPUMS_API_KEY",
    default=None,
    type=str,
    help=(
        "Your IPUMS API key. Must be provided either here or "
        "via the IPUMS_API_KEY environment variable"
    ),
    required=True,
)
@click.option(
    "--num-retries",
    "-n",
    default=3,
    type=int,
    help="The number of retries on transient errors",
)
def ipums_api_check_command(
    collection: str, extract_id: int, api_key: str, num_retries: int
):
    """ Check the status of an extract """
    api_client = IpumsApiClient(api_key, num_retries=num_retries)
    status = api_client.extract_status(extract_id, collection=collection)

    click.echo(f"Extract {extract_id} in collection {collection} has status {status}")


@ipums_api_group.command("download")
@click.argument("collection", type=str)
@click.argument("extract_number", type=int)
@click.option(
    "--output-dir",
    "-o",
    default=None,
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    help=(
        "The directory to download the extract to. If not passed, current "
        "working directory is used. If passed, must be a directory that exists."
    ),
)
@click.option(
    "--api-key",
    "-k",
    envvar="IPUMS_API_KEY",
    default=None,
    type=str,
    help=(
        "Your IPUMS API key. Must be provided either here or "
        "via the IPUMS_API_KEY environment variable"
    ),
    required=True,
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
    output_dir: Optional[str],
    api_key: str,
    num_retries: int,
):
    """ Download an IPUMS extract """
    api_client = IpumsApiClient(api_key, num_retries=num_retries)
    api_client.download_extract(
        extract_number, collection=collection, download_dir=output_dir
    )


@ipums_api_group.command("submit-and-download")
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
    help=(
        "Your IPUMS API key. Must be provided either here or "
        "via the IPUMS_API_KEY environment variable"
    ),
    required=True,
)
@click.option(
    "--output-dir",
    "-o",
    default=None,
    type=click.Path(exists=True, dir_okay=True, file_okay=False),
    help=(
        "The directory to download the extract to. If not passed, current "
        "working directory is used. If passed, must be a directory that exists."
    ),
)
@click.option(
    "--num-retries",
    "-n",
    default=3,
    type=int,
    help="The number of retries on transient errors",
)
@click.option(
    "--initial-wait-time",
    default=1,
    type=float,
    help=(
        "How long to wait (in seconds) before initially pinging the "
        "API to download an extract"
    ),
)
@click.option(
    "--max-wait-time",
    default=300,
    type=float,
    help=(
        "Maximum time (in seconds) between pings to the API "
        "while waiting for the extract"
    ),
)
@click.option(
    "--timeout",
    default=None,
    type=float,
    help="Maximum time (in seconds) to wait for an extract before giving up",
)
def ipums_api_submit_and_download(
    extract: str,
    api_key: str,
    output_dir: Optional[str],
    num_retries: int,
    inital_wait_time: float,
    max_wait_time: float,
    timeout: Optional[float],
):
    """
    Submit an extract request to the IPUMS API, then wait for it to
    be ready and download it
    """
    api_client = IpumsApiClient(api_key, num_retries=num_retries)
    extract_description = readers.read_extract_description(extract)

    # For now we only support a single extract
    extract_description = extract_description["extracts"][0]
    if extract_description["collection"] in BaseExtract._collection_to_extract:
        extract = BaseExtract._collection_to_extract[extract_description["collection"]](
            **extract_description
        )
    else:
        extract = OtherExtract(extract_description["collection"], extract_description)

    api_client.submit_extract(extract)

    click.echo(
        f"Your extract for collection {extract.collection} has been successfully "
        f"submitted with number {extract.extract_id}"
    )

    click.echo("Waiting for it to be ready...")

    wait_time = inital_wait_time
    total_time = 0
    while True:
        if timeout and (total_time >= timeout):
            click.echo("Too much time has passed. Stopping waiting")
            sys.exit(1)

        status = api_client.extract_status(extract)
        if status != "completed":
            click.echo(
                f"Extract in collection {extract.collection} with id "
                f"{extract.extract_id} is not yet ready. Sleeping for "
                f"{wait_time:0.2f} seconds..."
            )
            time.sleep(wait_time)
            total_time += wait_time
            wait_time = max(wait_time * 2, max_wait_time)
        else:
            click.echo(
                f"Extract in collection {extract.collection} with id "
                f"{extract.extract_id} is ready. Downloading..."
            )
            break

    api_client.download_extract(extract, download_dir=output_dir)
    click.echo("Download completed.")


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


if __name__ == "__main__":
    ipums_group()
