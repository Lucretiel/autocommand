from .automain import automain
from .autoparse import autoparse, smart_open
from .autocommand import autocommand

# If there's no asyncio, there's no autoasync
try:
    import asyncio
    del asyncio
except ImportError:
    pass
else:
    from .autoasync import autoasync
