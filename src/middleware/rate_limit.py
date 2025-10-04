from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

class RateLimits:
    UPLOAD = "10/hour"
    DOWNLOAD = "20/hour"
    HOME = "100/minute"
    ACCEPT = "30/hour"