"""
Exceptions which can arise in calls to the IPUMS API
"""
__all__ = ["IpumsApiException", "TransientIpumsApiException"]


class IpumsApiException(Exception):
    pass


class TransientIpumsApiException(IpumsApiException):
    pass


class IpumsExtractNotReady(IpumsApiException):
    """ Represents the case that your extract is not yet ready """


class IpumsTimeoutException(IpumsApiException):
    """ Represents when waiting for the IPUMS API times out """


class IpumsAPIAuthenticationError(IpumsApiException):
    """ Represents attempted unauthorized API access """
    pass


class BadIpumsApiRequest(IpumsApiException):
    """ Represents an error in the api request json, such as invalid sample id or var name"""
    pass