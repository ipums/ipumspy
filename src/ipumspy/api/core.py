"""
Core utilities for interacting with the IPUMS API
"""
import copy
import time
from functools import wraps
from http import HTTPStatus
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import requests
from requests.models import Response

from ..__version__ import __version__
from ..types import FilenameType
from .exceptions import (
    BadIpumsApiRequest,
    IpumsAPIAuthenticationError,
    IpumsApiException,
    IpumsExtractFailure,
    IpumsExtractNotReady,
    IpumsNotFound,
    IpumsTimeoutException,
    TransientIpumsApiException,
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


def _prettify_message(response_message: Union[str, List[str]]) -> str:
    if isinstance(response_message, list):
        return "\n".join(response_message)
    else:
        return response_message


def _reconstitute_purged_extract(
    collection: str, api_response: Dict[str, Any]
) -> BaseExtract:
    return BaseExtract._collection_to_extract[collection].from_api_response(
        api_response
    )


class IpumsApiClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.ipums.org/extracts",
        api_version: str = "beta",
        num_retries: int = 3,
        session: Optional[requests.Session] = None,
    ):
        """
        Class for creating and retrieving IPUMS extracts via API

        Args:
            api_key: User's IPUMs API key
            base_url: IPUMS API url
            num_retries: number of times a request will be retried before
                        raising `TransientIpumsApiException`
            session: requests session object

        """

        self.api_key = api_key
        self.num_retries = num_retries
        self.base_url = base_url
        self.api_version = api_version

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
            if response.status_code == HTTPStatus.BAD_REQUEST:
                error_details = _prettify_message(response.json()["detail"])
                raise BadIpumsApiRequest(error_details)
            # 401 errors should be preempted by the need to pass an API key to
            # IpumsApiClient, but...
            elif (
                response.status_code == HTTPStatus.UNAUTHORIZED
                or response.status_code == HTTPStatus.FORBIDDEN
            ):
                try:
                    error_details = _prettify_message(response.json()["error"])
                except KeyError:
                    error_details = _prettify_message(response.json()["detail"])
                raise IpumsAPIAuthenticationError(error_details)
            elif response.status_code == HTTPStatus.NOT_FOUND:
                # No request with the passed error
                raise IpumsNotFound(
                    "Page not found. Perhaps you passed the wrong extract id?"
                )
            else:
                error_details = _prettify_message(response.json()["detail"])
                raise IpumsApiException(error_details)
        except Exception as err:
            raise IpumsApiException(f"other error occured: {err}")

    def get(self, *args, **kwargs) -> requests.Response:
        """GET a request from the IPUMS API"""
        return self.request("get", *args, **kwargs)

    def post(self, *args, **kwargs) -> requests.Response:
        """POST a request from the IPUMS API"""
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
            params={"collection": extract.collection, "version": self.api_version},
            json=extract.build(),
        )

        extract_id = int(response.json()["number"])
        extract._id = extract_id

        extract_info = response.json()
        extract._info = extract_info
        extract.api_version = self.api_version
        return extract

    def extract_status(
        self, extract: Union[BaseExtract, int], collection: Optional[str] = None
    ) -> str:
        """
        Check on the status of an extract request. If no such extract exists, return
        'not found'.

        Args:
            extract: The extract to download. This extract must have been submitted.
                Alternatively, can be an extract id. If an extract id is provided, you
                must supply the collection name
            collection: The name of the collection to pull the extract from. If None,
                then ``extract`` must be a ``BaseExtract``

        Returns:
            str: The status of the request. Valid statuses are:
                 'queued', 'started', 'completed', 'failed', or 'not found'
        """
        extract_id, collection = _extract_and_collection(extract, collection)

        try:
            response = self.get(
                f"{self.base_url}/{extract_id}",
                params={"collection": collection, "version": self.api_version},
            )
        except IpumsNotFound:
            return "not found"

        return response.json()["status"].lower()

    def download_extract(
        self,
        extract: Union[BaseExtract, int],
        collection: Optional[str] = None,
        download_dir: Optional[FilenameType] = None,
        stata_command_file: Optional[bool] = False,
        spss_command_file: Optional[bool] = False,
        sas_command_file: Optional[bool] = False,
        r_command_file: Optional[bool] = False,
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
            stata_command_file: Set to True to download the stata command file with
                the extract data file.
            spss_command_file: Set to True to download the SPSS command file with the
                extract data file.
            sas_command_file: Set to True to download the SAS command file with the
                extract data file.
            R_command_file: Set to True to download the R command file with the
                extract data file.
        """
        extract_id, collection = _extract_and_collection(extract, collection)

        # if download_dir specified check if it exists
        download_dir = Path(download_dir or Path.cwd())
        if not download_dir.exists():
            raise FileNotFoundError(f"{download_dir} does not exist")

        # check to see if extract complete
        extract_status = self.extract_status(extract_id, collection=collection)
        if extract_status == "not found":
            raise IpumsNotFound(
                f"There is no IPUMS extract with extract number "
                f"{extract_id} in collection {collection}. Be sure to submit your "
                f"extract before trying to download it!"
            )
        if extract_status == "failed":
            raise IpumsExtractFailure(
                f"Your IPUMS {collection} extract number {extract_id} "
                f"failed to complete. Please resubmit your extract. "
                f"If the issue lingers, please reach out to ipums@umn.edu for assistance."
            )
        if extract_status != "completed":
            raise IpumsExtractNotReady(
                f"Your IPUMS {collection} extract number {extract_id} "
                f"is not finished yet!"
            )

        response = self.get(
            f"{self.base_url}/{extract_id}",
            params={"collection": collection, "version": self.api_version},
        )

        download_links = response.json()["download_links"]
        try:
            # if the extract has been purged, the download_links element will be
            # an empty dict
            data_url = download_links["data"]["url"]
            ddi_url = download_links["ddi_codebook"]["url"]
            download_urls = [data_url, ddi_url]

            if stata_command_file:
                _url = download_links["stata_command_file"]["url"]
                download_urls.append(_url)
            if spss_command_file:
                _url = download_links["spss_command_file"]["url"]
                download_urls.append(_url)
            if sas_command_file:
                _url = download_links["sas_command_file"]["url"]
                download_urls.append(_url)
            if r_command_file:
                _url = download_links["R_command_file"]["url"]
                download_urls.append(_url)

        except KeyError:
            raise IpumsExtractNotReady(
                f"Your IPUMS {collection} extract number {extract_id} was purged "
                f"from our cache. Please resubmit your extract."
            )
        for url in download_urls:
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
            if status == "failed":
                # TODO: follow up with IT and user support to see if we should
                # instruct people to email us about extract failures.
                raise IpumsExtractFailure(
                    f"Oops! Your {collection} extract number {extract_id} failed "
                    f"to complete."
                )
            elif status == "not found":
                raise IpumsNotFound(
                    f"There is no IPUMS extract with extract number {extract_id} in collection {collection}"
                )
            elif status != "completed":
                time.sleep(wait_time)
                total_time += wait_time
                wait_time = min(wait_time * 2, max_wait_time)
            else:
                break

    def retrieve_previous_extracts(
        self, collection: str, limit: int = 10
    ) -> List[Dict]:
        """
        Return details about the past ``limit`` requests

        Args:
            collection: The collection for which to look up most recent previous extracts.
            limit: The number of extracts to look up. Default is 10

        Returns:
            A list of the user's most recent previous extract definitions.
        """
        # TODO: Wrap results in Extract objects.
        output = self.get(
            self.base_url,
            params={
                "collection": collection,
                "limit": limit,
                "version": self.api_version,
            },
        ).json()
        return output

    def get_extract_info(
        self,
        extract: Union[BaseExtract, int],
        collection: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Returns details about a past IPUMS extract

        extract: The extract to download. This extract must have been submitted.
                Alternatively, can be an extract id. If an extract id is provided, you
                must supply the collection name
        collection: The name of the collection to pull the extract from. If None,
            then ``extract`` must be a ``BaseExtract``

        Returns:
            An IPUMS extract definition
        """
        extract_id, collection = _extract_and_collection(extract, collection)

        if isinstance(extract, BaseExtract):
            return extract._info
        else:
            extract_info = self.get(
                f"{self.base_url}/{extract_id}",
                params={"collection": collection, "version": self.api_version},
            ).json()

            return extract_info

    def extract_was_purged(
        self,
        extract: Union[BaseExtract, int],
        collection: Optional[str] = None,
    ) -> bool:
        """
        Returns True if the IPUMS extract's files have been purged from the cache.

        extract: An extract object. This extract must have been submitted.
                 Alternatively, can be an extract id. If an extract id is provided, you
                 must supply the collection name
        collection: The name of the collection to pull the extract from. If None,
            then ``extract`` must be a ``BaseExtract``
        """
        extract_id, collection = _extract_and_collection(extract, collection)
        extract_definition = self.get_extract_info(extract_id, collection)
        if not extract_definition["download_links"]:
            return True
        else:
            return False

    def resubmit_purged_extract(self, extract: str, collection: str):
        """
        Re-submits an IPUMS extract for which the data and ddi files have been purged
        from the IPUMS extract system cache.

        Args:
            collection: The collection of the purged extract to be re-submitted
            extract_id: The extract id of the purged extract to be re-submitted

        Returns:
            An IPUMS extract object. NB: the re-submitted extract will have its own
            extract id number, different from the extract_id of the purged extract!
        """

        if self.extract_was_purged(collection=collection, extract=extract):
            extract_definition = self.get_extract_info(extract, collection)
            base_obj = _reconstitute_purged_extract(collection, extract_definition)
            base_obj.description = f"Revision of ({base_obj.description})"
            extract_obj = self.submit_extract(base_obj, collection=collection)

            return extract_obj
        else:
            raise IpumsApiException(
                f"IPUMS {collection} extract number {extract} "
                f"has not been purged. You may download the data "
                f"and ddi files directly using download_extract()"
            )
