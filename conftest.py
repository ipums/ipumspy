# This file is part of ipumspy.
# For copyright and licensing information, see the NOTICE and LICENSE files
# in this project's top-level directory, and also on-line at:
#   https://github.com/ipums/ipumspy

from pathlib import Path

import pytest
from dotenv import load_dotenv


def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False, help="run slow tests",
    )
    parser.addoption(
        "--runint", action="store_true", default=False, help="run integration tests",
    )


def pytest_collection_modifyitems(config, items):
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    skip_int = pytest.mark.skip(reason="need --runing option to run")
    for item in items:
        if "slow" in item.keywords and not config.getoption("--runslow"):
            item.add_marker(skip_slow)
        elif "integration" in item.keywords and not config.getoption("--runint"):
            item.add_marker(skip_int)


@pytest.fixture(scope="session")
def environment_variables():
    """
    Test envrionment variables are stored in .env.test
    """
    filename = Path(__file__).parent / ".env.test"
    load_dotenv(dotenv_path=filename)
