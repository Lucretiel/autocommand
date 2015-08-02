from .automain import automain
from .autoparse import autoparse, smart_open
from .autocommand import autocommand

try:
    from .autoasync import autoasync
except ImportError:  # pragma: no cover
    pass
