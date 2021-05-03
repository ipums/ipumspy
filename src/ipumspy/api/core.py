"""
Core utilities for interacting with the IPUMS API
"""
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from ..__version__ import __version__
from ..types import FilenameType
from .exceptions import IpumsExtractNotReady, TransientIpumsApiException


def retry_on_transient_error(func):
    """
    Retry a request up to self.num_retries times. If it exits with a
    ``TransientIpumsApiException``, then retry, else just immediately ``raise``
    """

    @wraps(func)
    def wrapped_func(self, *args, **kwargs):
        for _ in range(self.num_retries - 1):
            try:
                return func(self, *args, **kwargs)
            except TransientIpumsApiException:
                pass
        return func(self, *args, **kwargs)

    return wrapped_func


class IpumsApiClient:
    def __init__(
        self,
        collection: str,
        api_key: str,
        num_retries: int = 3,
        session: Optional[requests.Session] = None,
    ):
        self.collection = collection
        self.api_key = api_key
        self.base_url = "https://demo.api.ipums.org/extracts"
        self.num_retries = num_retries

        self.api_version = "v1"

        self.session = session or requests.session()
        self.session.headers.update(
            {
                "User-Agent": f"python-ipumspy:{__version__}.github.com/ipums/ipumspy",
                "Authorization": api_key,
            }
        )

    @retry_on_transient_error
    def request(self, method: str, *args, **kwargs) -> requests.Response:
        """
        Submit a request to the IPUMS API

        TODO: Convert these prints into procesed requests and build
            appropriate Exceptions
        """
        try:
            response = self.session.request(method, *args, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
            try:
                error_details = "\n".join(response.json()["detail"]["base"])
                print(error_details)
            except KeyError:
                pass
        except Exception as err:
            print(f"other error occured: {err}")

        # TODO Replace this return with raises
        return None

    def get(self, *args, **kwargs) -> requests.Response:
        """ GET a request from the IPUMS API """
        return self.request("get", *args, **kwargs)

    def post(self, *args, **kwargs) -> requests.Response:
        """ POST a request from the IPUMS API """
        return self.request("post", *args, **kwargs)

    def _build_body(
        self,
        samples: List[str],
        variables: List[str],
        description: str = "My IPUMS extract",
        data_format: str = "fixed_width",
    ) -> Dict[str, Any]:
        return {
            "description": description,
            "data_format": data_format,
            "data_structure": {"rectangular": {"on": "P"}},
            "samples": {sample: {} for sample in samples},
            "variables": {variable.upper(): {} for variable in variables},
        }

    def submit_extract(
        self,
        samples: List[str],
        variables: List[str],
        description: str = "My IPUMS extract",
        data_format: str = "fixed_width",
    ) -> int:
        """
        Submit an extract request to the IPUMS API

        Args:
            samples:
            variables:
            description:
            data_format:

        Returns:
            The number of the extract for the passed user account
        """
        body = self._build_body(
            samples, variables, description=description, data_format=data_format
        )

        response = self.post(
            self.base_url,
            params={"collection": self.collection, "version": self.api_version},
            json=body,
        )

        return int(response.json()["number"])

    def extract_status(self, extract_number: int) -> str:
        """
        Check on the status of an extract request

        Args:
            extract_number: The id of the extract request to check

        Returns:
            The status of the request
            TODO: What are valid statuses?
        """
        response = self.get(
            f"{self.base_url}/{extract_number}",
            params={"collection": self.collection, "version": self.api_version},
        )
        return response.json()["status"]

    def download_extract(
        self, extract_number: int, download_dir: Optional[FilenameType] = None
    ):
        """
        Download the extract with id ``extract_number`` to ``download_dir``
        (default location is current directory)

        Args:
            extract_number: The id of the extract to download
            download_dir: The location to download the data to.
                MUST be a directory that currently exists
        """
        # if download_dir specified check if it exists
        download_dir = Path(download_dir or Path.cwd())
        if not download_dir.exists():
            raise FileNotFoundError(f"{download_dir} does not exist")

        # check to see if extract complete
        if self.extract_status(extract_number) != "completed":
            raise IpumsExtractNotReady(
                f"Your IPUMS extract number {extract_number} is not finished yet!"
            )

        response = self.get(
            f"{self.base_url}/{extract_number}",
            params={"collection": self.collection, "version": self.api_version},
        )
        response.raise_for_status()

        download_links = response.json()["download_links"]
        data_url = download_links["data"]["url"]
        ddi_url = download_links["ddi_codebook"]["url"]
        for url in [data_url, ddi_url]:
            file_name = url.split("/")[-1]
            download_path = download_dir / file_name
            with self.get(url, stream=True) as response:
                response.raise_for_status()
                with open(download_path, "wb") as outfile:
                    for chunk in response.iter_content(chunk_size=8192):
                        outfile.write(chunk)

    def retrieve_previous_extracts(self, limit: int = 10) -> dict:
        """
        Return details about the past ``limit`` requests
        """
        return self.get(
            self.base_url,
            params={
                "collection": self.collection,
                "limit": limit,
                "version": self.api_version,
            },
        ).json()


class IpumsApi:
    def __init__(
        self,
        api_key: str,
        num_retries: int = 3,
        session: Optional[requests.Session] = None,
    ):
        session = session or requests.session()

        self.acs = IpumsApiClient(
            "acs", api_key, num_retries=num_retries, session=session
        )
        self.cps = IpumsApiClient(
            "cps", api_key, num_retries=num_retries, session=session
        )
