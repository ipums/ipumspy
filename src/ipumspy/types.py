"""
Some standard types used throughout the library
"""
import io
from pathlib import Path
from typing import Union

# Represents a filename. Typically you'll want to immediately cast to Path
FilenameType = Union[str, Path]

# Represents a file that can be passed either as a filename or as an open stream
FileType = Union[FilenameType, io.IOBase]
