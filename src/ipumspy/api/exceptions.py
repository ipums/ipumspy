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
