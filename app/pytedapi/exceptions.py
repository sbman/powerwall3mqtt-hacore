class TEDAPIException(Exception):
    # "Error fetching %s: %d"
    pass

class TEDAPIRateLimitedException(TEDAPIException):
    def __init__(self):
        super().__init__(self, "Possible Rate limiting by Powerwall - API calls paused")

class TEDAPIRateLimitingException(TEDAPIException):
    def __init__(self):
        super().__init__(self, "Possible Rate limiting by Powerwall - Activating cooldown")

class TEDAPIAccessDeniedException(TEDAPIException):
    def __init__(self):
        super().__init__(self, "Access Denied: Check your Gateway Password")

class TEDAPINotConnectedException(TEDAPIException):
    def __init__(self):
        super().__init__(self, "Not Connected - Unable to get configuration")



# Old stuff
class PyPowerwallTEDAPINoTeslaAuthFile(Exception):
    pass


class PyPowerwallTEDAPITeslaNotConnected(Exception):
    pass


class PyPowerwallTEDAPINotImplemented(Exception):
    pass


class PyPowerwallTEDAPIInvalidPayload(Exception):
    pass
