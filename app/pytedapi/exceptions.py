"""Module providing exceptions for the pytedapi module"""

class TEDAPIException(Exception):
    """Base class for TEDAPI exceptions"""
    # "Error fetching %s: %d"

class TEDAPIRateLimitedException(TEDAPIException):
    """Exception class indicating TEDAPI calls are being rate limited"""
    def __init__(self):
        super().__init__(self, "Possible Rate limiting by Powerwall - API calls paused")

class TEDAPIRateLimitingException(TEDAPIException):
    """Exception class indicating TEDAPI calls will be rate limited"""
    def __init__(self):
        super().__init__(self, "Possible Rate limiting by Powerwall - API calls paused")

class TEDAPIAccessDeniedException(TEDAPIException):
    """Exception class indicating TEDAPI denied access"""
    def __init__(self):
        super().__init__(self, "Access Denied: Check your Gateway Password")

class TEDAPINotConnectedException(TEDAPIException):
    """Exception class indicating TEDAPI is not able to connect"""
    def __init__(self):
        super().__init__(self, "Not Connected - Unable to get configuration")

class TEDAPIPowerwallVersionException(TEDAPIException):
    """Exception class indicating the version of a Powerwall is not supported"""
    def __init__(self):
        super().__init__(self, "Powerwall version not supported")
