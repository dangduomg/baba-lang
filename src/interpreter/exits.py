"""Early-exit types"""


from dataclasses import dataclass

from .base import Exit, Value


#pylint: disable=too-few-public-methods


@dataclass(frozen=True)
class Break(Exit):
    """Break statement"""


@dataclass(frozen=True)
class Continue(Exit):
    """Continue statement"""


@dataclass(frozen=True)
class Return(Exit):
    """Return statement"""

    value: Value
