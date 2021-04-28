"""
Some standard types used throughout the library
"""
from pathlib import Path
from typing import Union

# Represents a filename. Typically you'll want to immediately cast to Path
FilenameType = Union[str, Path]
