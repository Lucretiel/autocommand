from .automain import automain
from .autoparse import autoparse, smart_open
from .autocommand import autocommand

# If there's no asyncio, there's no autoasync
try:
    from .autoasync import autoasync
except ImportError:
    pass
