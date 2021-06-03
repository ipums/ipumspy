"""
Wrappers for payloads to ship to the IPUMS API
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Type


class BaseExtract:
    """
    A wrapper around an IPUMS extract. In most cases, you
    probably want to use a subclass, but if a particular collection
    does not have an ``Extract`` currently built, you can use
    this wrapper directly.
    """

    _collection_to_extract: Dict[(str, str), Type[BaseExtract]] = {}

    def __init__(self):
        self._id: Optional[int] = None
        self.api_version = "v1"

    def __init_subclass__(cls, collection: str, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.collection = collection
        BaseExtract._collection_to_extract[collection] = cls

    def build(self) -> Dict[str, Any]:
        """
        Convert the object into a dictionary to be passed to the IPUMS API
        as a JSON string
        """
        raise NotImplementedError()

    @property
    def extract_id(self) -> int:
        """
        Returns:
            The extract id associated with this extract. Will be assigned by
            the ``IpumsApiClient``

        Raises:
            ValueError: If the extract has no id number (probably because it has
                not be submitted to IPUMS)
        """
        if not self._id:
            raise ValueError("Extract has not been submitted so has no id number")
        return self._id


class OtherExtract(BaseExtract, collection="other"):
    """
    A generic extract object for working with collections that are not
    yet officially supported by this API library
    """

    def __init__(self, collection: str, details: Optional[Dict[str, Any]]):
        super().__init__()
        self.collection = collection
        self.details = details

    def build(self) -> Dict[str, Any]:
        """
        Convert the object into a dictionary to be passed to the IPUMS API
        as a JSON string
        """
        return self.details


class UsaExtract(BaseExtract, collection="usa"):
    """
    Defining an IPUMS USA extract.
    """

    def __init__(
        self,
        samples: List[str],
        variables: List[str],
        description: str = "My IPUMS extract",
        data_format: str = "fixed_width",
        **kwargs
    ):
        # Note the for now kwargs are ignored. Perhaps better error checking
        # would be good here?

        super().__init__()
        self.samples = samples
        self.variables = variables
        self.description = description
        self.data_format = data_format

    def build(self) -> Dict[str, Any]:
        """
        Convert the object into a dictionary to be passed to the IPUMS API
        as a JSON string
        """
        return {
            "description": self.description,
            "data_format": self.data_format,
            "data_structure": {"rectangular": {"on": "P"}},
            "samples": {sample: {} for sample in self.samples},
            "variables": {variable.upper(): {} for variable in self.variables},
        }