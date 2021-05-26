import tempfile
from pathlib import Path

from ipumspy import fileutils


def test_open_or_yield(capsys):
    # Test if you pass a filename
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        with fileutils.open_or_yield(tmpdir / "test.txt", "wt") as outfile:
            outfile.write("hello")

        with open(tmpdir / "test.txt", "rt") as infile:
            assert infile.read() == "hello"

    # Test if you pass an open file
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        with open(tmpdir / "test.txt", "wt") as outfile:
            outfile.write("again")

        with open(tmpdir / "test.txt", "rt") as infile:
            with fileutils.open_or_yield(infile) as wrapped_infile:
                assert wrapped_infile.read() == "again"

    # Test if you pass '-'
    with fileutils.open_or_yield("-", "wt") as outfile:
        outfile.write("test me")

    captured = capsys.readouterr()
    assert captured.out == "test me"

    # Test if you pass None
    with fileutils.open_or_yield("-", "wt") as outfile:
        outfile.write("test me again")

    captured = capsys.readouterr()
    assert captured.out == "test me again"
