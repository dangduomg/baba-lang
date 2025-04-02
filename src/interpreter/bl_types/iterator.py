"""Iterator helpers

How do iterators work:
An iterator has a 'next' method that returns either the next item in the
iterator as an Item or null. If the iterator is exhausted, it returns null.
Therefore, implementing a for loop is as simple as calling the 'next' method
until it returns null. The for loop has to check for other types too, but
that's about it"""


from typing import TYPE_CHECKING, cast
from dataclasses import dataclass

from lark.tree import Meta

from .essentials import Value, String, Class, ObjectClass, Instance

if TYPE_CHECKING:
    from ..main import ASTInterpreter


ItemClass = Class(String("Item"), ObjectClass, {})
ItemClass.new = lambda args, interpreter, meta: Item(args[0])


@dataclass(init=False)
class Item(Instance):
    """Iterator item"""

    def __init__(self, value: Value) -> None:
        super().__init__(ItemClass, {"value": value})

    def dump(self, interpreter: "ASTInterpreter", meta: Meta | None) -> String:
        value = cast(Value, self.get_attr("value", interpreter, meta))
        return String(f"<item: {value.dump(interpreter, meta)}>")
