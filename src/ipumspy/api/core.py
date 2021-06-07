"""
Core utilities for interacting with the IPUMS API
"""
import copy
import time
from functools import wraps
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import requests

from ..__version__ import __version__
from ..types import FilenameType
from .exceptions import (
    IpumsApiException,
    IpumsExtractNotReady,
    IpumsTimeoutException,
    TransientIpumsApiException,
    IpumsAPIAuthenticationError,
    BadIpumsApiRequest,
)
from .extract import BaseExtract, OtherExtract


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


def _extract_and_collection(
    extract: Union[BaseExtract, int], collection: Optional[str]
) -> Tuple[int, str]:
    if isinstance(extract, BaseExtract):
        extract_id = extract.extract_id
        collection = extract.collection
    else:
        extract_id = extract
        if not collection:
            raise ValueError(
                "If ``extract`` is not a BaseExtract, ``collection`` must be non-null"
            )
    return extract_id, collection


class IpumsApiClient:
    def __init__(
        self,
        api_key: str,
        num_retries: int = 3,
        session: Optional[requests.Session] = None,
    ):
        self.api_key = api_key
        self.base_url = "https://demo.api.ipums.org/extracts"
        self.num_retries = num_retries

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
        """
        try:
            response = self.session.request(method, *args, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as http_err:
            # print(f"HTTP error occurred: {http_err}")
            if response.status_code == 400:
                error_details = "\n".join(response.json()["detail"])
                raise BadIpumsApiRequest(error_details)
            # 401 errors should be preempted by the need to pass an API key to
            # IpumsApiClient, but...
            elif response.status_code == 401 or response.status_code == 403:
                error_details = response.json()["error"]
                raise IpumsAPIAuthenticationError(error_details)
        except Exception as err:
            # print(f"other error occured: {err}")
            raise IpumsApiException(f"other error occured: {err}")

    def get(self, *args, **kwargs) -> requests.Response:
        """ GET a request from the IPUMS API """
        return self.request("get", *args, **kwargs)

    def post(self, *args, **kwargs) -> requests.Response:
        """ POST a request from the IPUMS API """
        return self.request("post", *args, **kwargs)

    def submit_extract(
        self,
        extract: Union[BaseExtract, Dict[str, Any]],
        collection: Optional[str] = None,
    ) -> BaseExtract:
        """
        Submit an extract request to the IPUMS API

        Args:
            extract: The extract description to submit. May be either an
                ``IpumsExtract`` object, or the ``details`` of such an
                object, in which case it must include a key named ``collection``

        Returns:
            The number of the extract for the passed user account
        """
        if not isinstance(extract, BaseExtract):
            extract = copy.deepcopy(extract)
            if "collection" in extract:
                collection = collection or extract["collection"]
                del extract["collection"]
            else:
                if not collection:
                    ValueError("You must provide a collection")

            if collection in BaseExtract._collection_to_extract:
                extract_type = BaseExtract._collection_to_extract[collection]
                extract = extract_type(**extract)
            else:
                extract = OtherExtract(collection, extract)

        response = self.post(
            self.base_url,
            params={"collection": extract.collection, "version": "v1"},
            json=extract.build(),
        )

        extract_id = int(response.json()["number"])
        extract._id = extract_id
        return extract

    def extract_status(
        self, extract: Union[BaseExtract, int], collection: Optional[str] = None
    ) -> str:
        """
        Check on the status of an extract request

        Args:
            extract: The extract to download. This extract must have been submitted.
                Alternatively, can be an extract id. If an extract id is provided, you
                must supply the collection name
            collection: The name of the collection to pull the extract from. If None,
                then ``extract`` must be a ``BaseExtract``

        Returns:
            The status of the request. Valid statuses are:
             'queued', 'started', 'completed', or 'failed'
        """
        extract_id, collection = _extract_and_collection(extract, collection)

        response = self.get(
            f"{self.base_url}/{extract_id}",
            params={"collection": collection, "version": "v1"},
        )
        return response.json()["status"]

    def download_extract(
        self,
        extract: Union[BaseExtract, int],
        collection: Optional[str] = None,
        download_dir: Optional[FilenameType] = None,
    ):
        """
        Download the extract with id ``extract_number`` to ``download_dir``
        (default location is current directory)

        Args:
            extract: The extract to download. This extract must have been submitted.
                Alternatively, can be an extract id. If an extract id is provided, you
                must supply the collection name
            collection: The name of the collection to pull the extract from. If None,
                then ``extract`` must be a ``BaseExtract``
            download_dir: The location to download the data to.
                MUST be a directory that currently exists
        """
        extract_id, collection = _extract_and_collection(extract, collection)

        # if download_dir specified check if it exists
        download_dir = Path(download_dir or Path.cwd())
        if not download_dir.exists():
            raise FileNotFoundError(f"{download_dir} does not exist")

        # check to see if extract complete
        if self.extract_status(extract_id, collection=collection) != "completed":
            raise IpumsExtractNotReady(
                f"Your IPUMS extract number {extract_id} is not finished yet!"
            )

        response = self.get(
            f"{self.base_url}/{extract_id}",
            params={"collection": collection, "version": "v1"},
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

    def wait_for_extract(
        self,
        extract: Union[BaseExtract, int],
        collection: Optional[str] = None,
        inital_wait_time: float = 1,
        max_wait_time: float = 300,
        timeout: float = 10800,
    ):
        """
        Convenience function to wait for an extract to complete. Will sleep
        until the IPUMS API returns a "completed" status for the extract.

        Args:
            extract: The extract to download. This extract must have been submitted.
                Alternatively, can be an extract id. If an extract id is provided, you
                must supply the collection name
            collection: The name of the collection to pull the extract from. If None,
                then ``extract`` must be a ``BaseExtract``
            initial_wait_time: How long in seconds to initially wait between pings to
                the IPUMS API. Future pings will be spaced by exponential backoff
            max_wait_time: Pings will always occur at least once every
                ``max_wait_time`` seconds
            timeout: If this many seconds passes, an ``IpumsTimeoutException``
                will be raised.

        Raises:
            IpumsTimemoutException: If ``timeout`` seconds pass before a "completed"
                status is returned.
        """
        extract_id, collection = _extract_and_collection(extract, collection)
        wait_time = inital_wait_time
        total_time = 0
        while True:
            if total_time >= timeout:
                raise IpumsTimeoutException(
                    f"More than {timeout} seconds have passed"
                    f"while waiting for your extract to finish building"
                )

            status = self.extract_status(extract_id, collection=collection)
            if status != "completed":
                time.sleep(wait_time)
                total_time += wait_time
                wait_time = max(wait_time * 2, max_wait_time)
            else:
                break

    def retrieve_previous_extracts(
        self, collection: Optional[str] = None, limit: int = 10
    ) -> Dict[str, dict]:
        """
        Return details about the past ``limit`` requests

        Args:
            collection: The collection for which to look up previous extracts. If
                note provided will look up extracts for _all_ collections
            limit: The number of extracts to look up _per collection_

        Returns:
            A dictionary whose keys are collection names and whose values are the
            the results of the API call.
        """
        if collection is None:
            collections = [
                name
                for name in BaseExtract._collection_to_extract.keys()
                if name != OtherExtract.collection
            ]
        else:
            collections = [collection]

        # TODO: Wrap results in Extract objects.
        output = {}
        for collection in collections:
            output.update(
                self.get(
                    self.base_url,
                    params={"collection": collection, "limit": limit, "version": "v1"},
                ).json()
            )
        return output
