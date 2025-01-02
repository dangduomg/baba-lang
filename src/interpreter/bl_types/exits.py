"""Early-exit types"""

from dataclasses import dataclass

from .essentials import Exit


# pylint: disable=too-few-public-methods


@dataclass(frozen=True)
class Break(Exit):
    """Break statement"""


@dataclass(frozen=True)
class Continue(Exit):
    """Continue statement"""
