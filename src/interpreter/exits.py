"""Early-exit types"""


from .base import Exit


#pylint: disable=too-few-public-methods


class Break(Exit):
    """Break statement"""

class Continue(Exit):
    """Continue statement"""
