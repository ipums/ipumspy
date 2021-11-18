# This file is part of ipumspy.
# For copyright and licensing information, see the NOTICE and LICENSE files
# in this project's top-level directory, and also on-line at:
#   https://github.com/ipums/ipumspy

"""
A CLI for accessing IPUMS utilities
"""
from typing import Optional, Tuple

import click
import pyarrow as pa
from pyarrow.parquet import ParquetWriter

from ipumspy.api.exceptions import IpumsApiException
from ipumspy.api.extract import extract_from_dict

from . import readers
from .api import IpumsApiClient


@click.group()
def cli():
    """
    Tools for working with IPUMS files via the command line
    """


@cli.command("submit")
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
def submit_command(extract: str, api_key: str, num_retries: int):
    """Submit an extract request to the IPUMS API"""
    api_client = IpumsApiClient(api_key, num_retries=int(num_retries))
    extract_description = readers.read_extract_description(extract)
    extract = extract_from_dict(extract_description)
    if not isinstance(extract, list):
        extract = [extract]

    for ext in extract:
        api_client.submit_extract(ext)

        click.echo(
            f"Your extract for collection {ext.collection} has been successfully "
            f"submitted with number {ext.extract_id}"
        )


@cli.command("check")
@click.argument("collection", type=str)
@click.argument("extract_id", type=int, nargs=-1)
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
def check_command(collection: str, extract_id: Tuple[int], api_key: str, num_retries: int):
    """Check the status of an extract"""
    api_client = IpumsApiClient(api_key, num_retries=int(num_retries))
    for extract in extract_id:
        status = api_client.extract_status(extract, collection=collection)
        click.echo(f"Extract {extract_id} in collection {collection} has status {status}")


@cli.command("download")
@click.argument("collection", type=str)
@click.argument("extract_id", type=int, nargs=-1)
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
def download_command(
    collection: str,
    extract_id: Tuple[int],
    output_dir: Optional[str],
    api_key: str,
    num_retries: int,
):
    """Download an IPUMS extract"""
    api_client = IpumsApiClient(api_key, num_retries=int(num_retries))
    for extract in extract_id:
        api_client.download_extract(
            extract, collection=collection, download_dir=output_dir
        )


@cli.command("submit-and-download")
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
def submit_and_download_command(
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
    api_client = IpumsApiClient(api_key, num_retries=int(num_retries))
    extract_description = readers.read_extract_description(extract)
    extract = extract_from_dict(extract_description)
    if not isinstance(extract, list):
        extract = [extract]

    for ext in extract:
        api_client.submit_extract(ext)

        click.echo(
            f"Your extract for collection {ext.collection} has been successfully "
            f"submitted with number {ext.extract_id}"
        )

    click.echo("Waiting for extract(s) to be ready...")
    for ext in extract:
        try:
            api_client.wait_for_extract(
                ext,
                inital_wait_time=float(inital_wait_time),
                max_wait_time=float(max_wait_time),
                timeout=timeout if timeout is not None else float(timeout),
            )
            click.echo(
                f"Downloading extract '{ext.description}' in collection {ext.collection}..."
            )
            api_client.download_extract(extract, download_dir=output_dir)
            click.echo(
                f"Done downloading '{ext.description}' in collection {ext.collection}"
            )
        except IpumsApiException as exc:
            click.echo(
                f"Something went wrong for extract '{ext.description}' in collection {ext.collection}: {exc}"
            )

    click.echo("All download(s) complete.")


@cli.command("convert")
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
            ddi, filename=datafile, chunksize=100_000
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
    cli()
