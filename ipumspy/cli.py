import click

from . import readers


@click.group()
def cli():
  """
  Tools for working with IPUMS files via the command line
  """


@click.command('convert')
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
  data.to_parquet(outfile)


if __name__ == '__main__':
  cli()