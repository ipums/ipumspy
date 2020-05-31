import copy
import dataclasses
import json

import click
import pyarrow as pa

from . import readers


@click.group()
def cli():
  """
  Tools for working with IPUMS files via the command line
  """


@cli.command('convert')
@click.argument('infile', type=click.Path(exists=True))
@click.argument('outfile', type=click.Path())
def convert_command(infile, outfile):
  """
  Perform one-off conversions for faster loading times in the future

  INFILE is a path to an XML codebook describing an IPUMS extract.

  OUTFILE is the path that you'd like the file to be saved to. For now, the
  output format will be parquet.
  """
  ddi = readers.read_ipums_ddi(infile)
  data = readers.read_microdata(ddi)

  # Append ipums data to schema
  schema = pa.Schema.from_pandas(data)
  metadata = copy.deepcopy(schema.metadata)
  metadata[b'ipums'] = json.dumps(dataclasses.asdict(ddi)).encode('utf8')
  schema = schema.with_metadata(metadata)
  data.to_parquet(outfile, schema=schema)


if __name__ == '__main__':
  cli()