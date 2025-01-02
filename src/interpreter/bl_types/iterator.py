"""Iterator helpers

How do iterators work:
An iterator has a 'next' method that returns either the next item in the
iterator as an Item or null. If the iterator is exhausted, it returns null.
Therefore, implementing a for loop is as simple as calling the 'next' method
until it returns null. The for loop has to check for other types too, but
that's about it"""


from dataclasses import dataclass

from .essentials import Value, String, Class, ObjectClass, Instance


ItemClass = Class(String("Item"), ObjectClass, {})
ItemClass.new = lambda args, interpreter, meta: Item(args[0])


@dataclass(frozen=True)
class Item(Instance):
    """Iterator item"""

    def __init__(self, value: Value) -> None:
        super().__init__(ItemClass, {"value": value})
