# Contributing
Thank you for considering improving this project! By participating, you
agree to abide by the [code of conduct](https://github.com/ipums/ipumspy/blob/master/CONDUCT.md).

## Issues (Reporting a problem or suggestion)
If you've experience a problem with the package, or have a suggestion for it, 
please post it on the [issues tab](https://github.com/ipums/ipumspy/issues).
This space is meant for questions directly related to the python package, so questions
related to your specific extract may be better answered via email to ipums@umn.edu
(but don't worry about making a mistake, we know it is tough to tell the difference). 

Since our extracts are such large files, posting minimal reproducible examples
may be difficult. Therefore, it will be most helpful if you can provide as 
much detail about your problem as possible including the code and error message,
the project the extract is from, the variables you have selected, file type, etc. 
We'll do our best to answer your question.

## Pull Requests (Making changes to the package)
We appreciate pull requests that follow these guidelines:
1) Make sure that tests pass (and add new ones if possible). 

2) Try to conform to the code style of the package.

3) Please add your name and affiliation to the NOTICE.txt file.

4) Summarize your changes in the [change log](https://github.com/ipums/ipumspy/tree/master/docs/source/change-log.rst). This package adheres to [semantic versioning](https://semver.org/)

## Development setup

Install [uv](https://docs.astral.sh/uv/getting-started/installation/), then run
`uv sync --locked` from the repository root. This installs the package in editable
mode and the development and test dependencies. Python 3.11 or newer is required.

Run tests with `uv run pytest` and check formatting with `uv run ruff format --check .`.
Apply formatting with `uv run ruff format .`.
Check import ordering with `uv run ruff check .`, and sort imports in a file with
`uv run ruff check --fix path/to/file.py`. Existing imports have been left in
their current order; CI and pre-commit enforce formatting only.
API tests use recorded responses and a local mock server. To prevent new API
requests while testing, use
`IPUMS_API_KEY=offline-test-key uv run pytest --record-mode=none`.
Build documentation with `uv run --extra docs sphinx-build -b html docs/source docs/_build/html`,
and build release artifacts with `uv build`.

After changing dependencies in `pyproject.toml`, run `uv lock` and commit the
updated `uv.lock` alongside the configuration change.
