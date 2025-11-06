# request_handler.py
from abc import ABC, abstractmethod

class RequestHandler(ABC):
    """Base class for all request handlers in the chain."""

    def __init__(self):
        self._next = None

    def set_next(self, handler):
        """Set the next handler in the chain."""
        self._next = handler
        return handler  #allows chaining: a.set_next(b).set_next(c)

    @abstractmethod
    def handle(self, request):
        """Handle the request and optionally pass to the next handler."""
        if self._next:
            return self._next.handle(request)
        return request
