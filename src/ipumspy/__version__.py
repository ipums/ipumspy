"""
Simple version wrapper
"""
try:
    import importlib.metadata as metadata
except ImportError:
    import importlib_metadata as metadata


__version__ = metadata.version("ipumspy")
