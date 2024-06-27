# This file is part of ipumspy.
# For copyright and licensing information, see the NOTICE and LICENSE files
# in this project's top-level directory, and also on-line at:
#   https://github.com/ipums/ipumspy

import os
import subprocess
import tempfile
import time
from pathlib import Path

import pandas as pd
import pytest
from click.testing import CliRunner

from ipumspy import cli
from ipumspy.api import IpumsApiClient


@pytest.fixture(scope="module")
def mock_api() -> str:
    # TODO: Would be good to randomly assign a port and return it
    p = subprocess.Popen(
        ["uvicorn", "tests.mock_api:app", "--host", "127.0.0.1", "--port", "9898"]
    )
    time.sleep(1)  # Give it enough time to warm up
    try:
        yield "http://127.0.0.1:9898"
    finally:
        p.kill()


def test_submit_command(environment_variables, fixtures_path: Path, mock_api: str):
    """Test that submitting via the CLI works"""
    runner = CliRunner()
    result = runner.invoke(
        cli.submit_command,
        [
            "-k",
            os.environ.get("IPUMS_API_KEY"),
            "--base-url",
            mock_api,
            str(fixtures_path / "example_extract_v2.yml"),
        ],
    )
    assert (
        result.output
        == "Your extract for collection usa has been successfully submitted with number 10\n"
    )


def test_convert_command(fixtures_path: Path):
    """
    Test converting an IPUMS data set into parquet
    """
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        result = runner.invoke(
            cli.convert_command,
            list(
                map(
                    str,
                    [
                        fixtures_path / "cps_00006.xml",
                        fixtures_path / "cps_00006.csv.gz",
                        tmpdir / "cps_00006.parquet",
                    ],
                )
            ),
        )
        assert result.exit_code == 0

        parquet_df = pd.read_parquet(tmpdir / "cps_00006.parquet")

    df = pd.read_csv(fixtures_path / "cps_00006.csv.gz")

    assert (df == parquet_df).all().all()
