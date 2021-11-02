"""
Wrappers for payloads to ship to the IPUMS API
"""
from __future__ import annotations

from typing import Any, Collection, Dict, List, Optional, Type


class BaseExtract:
    _collection_to_extract: Dict[(str, str), Type[BaseExtract]] = {}

    def __init__(self):
        """
        A wrapper around an IPUMS extract. In most cases, you
        probably want to use a subclass, but if a particular collection
        does not have an ``Extract`` currently built, you can use
        this wrapper directly.
        """

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
        str:The extract id associated with this extract, assigned by the ``IpumsApiClient``

        Raises ``ValueError`` if the extract has no id number (probably because it has
        not be submitted to IPUMS)
        """
        if not self._id:
            raise ValueError("Extract has not been submitted so has no id number")
        return self._id


class OtherExtract(BaseExtract, collection="other"):
    def __init__(self, collection: str, details: Optional[Dict[str, Any]]):
        """
        A generic extract object for working with collections that are not
        yet officially supported by this API library
        """

        super().__init__()
        self.collection = collection
        """Name of an IPUMS data collection"""
        self.details = details
        """dictionary containing variable names and sample IDs"""

    def build(self) -> Dict[str, Any]:
        """
        Convert the object into a dictionary to be passed to the IPUMS API
        as a JSON string
        """
        return self.details


class UsaExtract(BaseExtract, collection="usa"):
    def __init__(
        self,
        samples: List[str],
        variables: List[str],
        description: str = "My IPUMS extract",
        data_format: str = "fixed_width",
        **kwargs
    ):
        """
        Defining an IPUMS USA extract.

        Args:
            samples: list of IPUMS USA sample IDs
            variables: list of IPUMS USA variable names
            description: short description of your extract
            data_format: fixed_width and csv supported
        """

        # Note the for now kwargs are ignored. Perhaps better error checking
        # would be good here?

        super().__init__()
        self.samples = samples
        self.variables = variables
        self.description = description
        self.data_format = data_format
        self.collection = self.collection
        """Name of an IPUMS data collection"""

    @classmethod
    def from_api_response(cls, api_response: Dict[str, Any]) -> UsaExtract:
        return cls(
            samples=list(api_response["samples"]),
            variables=list(api_response["variables"]),
            data_format=api_response["data_format"],
            description=api_response["description"],
        )

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
