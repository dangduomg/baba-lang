"""Iterator helpers

How do iterators work:
An iterator has a 'next' method that returns either the next item in the
iterator as an Item or null. If the iterator is exhausted, it returns null.
Therefore, implementing a for loop is as simple as calling the 'next' method
until it returns null. The for loop has to check for other types too, but
that's about it"""


from dataclasses import dataclass

from lark.tree import Meta

from .base import ExpressionResult
from .value import Value


@dataclass(frozen=True)
class Item(Value):
    """Iterator item"""

    value: Value

    def get_attr(self, attr: str, meta: Meta | None) -> ExpressionResult:
        if attr == "value":
            return self.value
        return super().get_attr(attr, meta)
