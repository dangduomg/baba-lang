"""Objects and OOP in baba-lang"""


from dataclasses import dataclass
from typing import TYPE_CHECKING

from lark.tree import Meta

from .base import Value, BLError, ExpressionResult, String
from .colls import Module
from .function import BLFunction

if TYPE_CHECKING:
    from .main import ASTInterpreter


@dataclass(frozen=True)
class Class(Module):
    """baba-lang class"""

    name: str
    vars: dict[str, Value]

    def new(
        self, args: list[Value], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        inst = Instance(self, {})
        if "__init__" in self.vars:  # __init__ is the constructor method
            constr = inst.get_attr("__init__", meta)
            match res := constr.call(args, interpreter, meta):
                case BLError():
                    return res
        return inst

    def dump(self, meta: Meta | None) -> String:
        return String(f"<class '{self.name}'>")


@dataclass(frozen=True)
class Instance(Value):
    """baba-lang instance"""

    class_: Class
    vars: dict[str, Value]

    def get_attr(self, attr: str, meta: Meta | None) -> ExpressionResult:
        try:
            return self.vars[attr]
        except KeyError:
            match res := self.class_.get_attr(attr, meta):
                case BLFunction():
                    return res.bind(self)
                case _:
                    return res

    def set_attr(
        self, attr: str, value: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match value:
            case BLError():
                return value
            case Value():
                self.vars[attr] = value
                return value
        return super().set_attr(attr, value, meta)

    def dump(self, meta: Meta | None) -> String:
        return String(f"<object of {self.class_.dump(meta).value}>")
