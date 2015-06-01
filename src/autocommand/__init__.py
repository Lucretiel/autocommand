from .automain import automain
from .autocommand import autocommand

# If there's no asyncio, there's no autoasync
try:
    from .autoasync import autoasync
except ImportError:
    pass

