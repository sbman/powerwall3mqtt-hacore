"""Module providing specialized locks"""
from threading import RLock

###
### TimeoutRLock class
###
class TimeoutRLock():
    """
    A wrapper around RLock that sets a default timeout
    for acquire() and 'with lock:' calls. Usage is
    identical to RLock, except the constructor takes
    an extra required parameter of 'timeout'.
    """
    timeout = None
    lock    = None

    def __init__(self, timeout: int, *args, **kwargs) -> None:
        self.timeout = timeout
        self.lock    = RLock(*args, **kwargs)

    def __enter__(self, *args, **kwargs) -> bool:
        rc = self.lock.acquire(timeout=self.timeout)
        if rc is False:
            raise TimeoutError(f"Could not acquire lock within "
                               f"specified timeout of {self.timeout}s")
        return rc

    def __exit__(self, *args, **kwargs):
        return self.lock.release()

    def acquire(self, *args, **kwargs) -> bool:
        """Acquire a lock, blocking or non-blocking."""
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout
        return self.lock.acquire(*args, **kwargs)

    def release(self, *args, **kwargs) -> None:
        """Release a lock, decrementing the recursion level."""
        return self.lock.release(*args, **kwargs)
