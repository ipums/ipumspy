"""
Exceptions which can arise in calls to the IPUMS API
"""
__all__ = ["IpumsApiException", "TransientIpumsApiException"]


class IpumsApiException(Exception):
    pass


class TransientIpumsApiException(IpumsApiException):
    pass


class IpumsExtractFailure(IpumsApiException):
    """Represents the case when an extract fails for unknown reasons"""


class IpumsNotFound(IpumsApiException):
    """Represents the case that there is no extract with the provided id"""


class IpumsExtractNotReady(IpumsApiException):
    """Represents the case that your extract is not yet ready"""


class IpumsTimeoutException(IpumsApiException):
    """Represents when waiting for the IPUMS API times out"""


class IpumsAPIAuthenticationError(IpumsApiException):
    """Represents attempted unauthorized API access"""


class BadIpumsApiRequest(IpumsApiException):
    """Represents an error in the api request json, such as invalid sample id or var name"""
