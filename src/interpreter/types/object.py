"""Objects and OOP in baba-lang"""


from dataclasses import dataclass
from typing import TYPE_CHECKING

from lark.tree import Meta

from .base import BLError, ExpressionResult
from .value import Value, String, Bool
from . import Module
from .function import BLFunction
from .errors import error_var_nonexistent

if TYPE_CHECKING:
    from ..main import ASTInterpreter


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

    def add(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        res = self._call_method_if_exists(
            "__add__", [other], interpreter, meta
        )
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().add(other, interpreter, meta)
        return res

    def subtract(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        res = self._call_method_if_exists(
            "__sub__", [other], interpreter, meta
        )
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().subtract(other, interpreter, meta)
        return res

    def multiply(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        res = self._call_method_if_exists(
            "__mul__", [other], interpreter, meta
        )
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().multiply(other, interpreter, meta)
        return res

    def divide(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        res = self._call_method_if_exists(
            "__div__", [other], interpreter, meta
        )
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().divide(other, interpreter, meta)
        return res

    def floor_div(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        res = self._call_method_if_exists(
            "__floordiv__", [other], interpreter, meta
        )
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().floor_div(other, interpreter, meta)
        return res

    def mod(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        res = self._call_method_if_exists(
            "__mod__", [other], interpreter, meta
        )
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().mod(other, interpreter, meta)
        return res

    def pow(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        res = self._call_method_if_exists(
            "__pow__", [other], interpreter, meta
        )
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().pow(other, interpreter, meta)
        return res

    def bitwise_and(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        res = self._call_method_if_exists(
            "__and__", [other], interpreter, meta
        )
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().bitwise_and(other, interpreter, meta)
        return res

    def bitwise_or(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        res = self._call_method_if_exists(
            "__or__", [other], interpreter, meta
        )
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().bitwise_or(other, interpreter, meta)
        return res

    def bitwise_xor(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        res = self._call_method_if_exists(
            "__xor__", [other], interpreter, meta
        )
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().bitwise_xor(other, interpreter, meta)
        return res

    def is_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        res = self._call_method_if_exists(
            "__eq__", [other], interpreter, meta
        )
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().is_equal(other, interpreter, meta)
        return res

    def is_not_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        res = self._call_method_if_exists(
            "__ne__", [other], interpreter, meta
        )
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().is_not_equal(other, interpreter, meta)
        return res

    def is_less(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        res = self._call_method_if_exists(
            "__lt__", [other], interpreter, meta
        )
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().is_less(other, interpreter, meta)
        return res

    def is_less_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        res = self._call_method_if_exists(
            "__le__", [other], interpreter, meta
        )
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().is_less_or_equal(other, interpreter, meta)
        return res

    def is_greater(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        res = self._call_method_if_exists(
            "__gt__", [other], interpreter, meta
        )
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().is_greater(other, interpreter, meta)
        return res

    def is_greater_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        res = self._call_method_if_exists(
            "__ge__", [other], interpreter, meta
        )
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().is_greater_or_equal(other, interpreter, meta)
        return res

    def plus(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> ExpressionResult:
        res = self._call_method_if_exists("__pos__", [], interpreter, meta)
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().plus(interpreter, meta)
        return res

    def neg(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> ExpressionResult:
        res = self._call_method_if_exists("__neg__", [], interpreter, meta)
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().neg(interpreter, meta)
        return res

    def bitwise_not(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> ExpressionResult:
        res = self._call_method_if_exists(
            "__invert__", [], interpreter, meta
        )
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().bitwise_not(interpreter, meta)
        return res

    def logical_not(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> ExpressionResult:
        res = self._call_method_if_exists("__not__", [], interpreter, meta)
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().logical_not(interpreter, meta)
        return res

    def get_item(
        self, index: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        res = self._call_method_if_exists(
            "__getitem__", [index], interpreter, meta
        )
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().get_item(index, interpreter, meta)
        return res

    def set_item(
        self, index: ExpressionResult, value: ExpressionResult,
        interpreter: "ASTInterpreter", meta: Meta | None,
    ) -> ExpressionResult:
        res = self._call_method_if_exists(
            "__setitem__", [index, value], interpreter, meta
        )
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().set_item(index, value, interpreter, meta)
        return res

    def to_bool(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> Bool:
        res = self._call_method_if_exists("__bool__", [], interpreter, meta)
        if isinstance(res, BLError):
            if res.value == error_var_nonexistent.value:
                return super().to_bool(interpreter, meta)
        return res

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

    def _call_method_if_exists(
        self, name: str, args: list[Value], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        match res := self.get_attr(name, meta):
            case BLFunction():
                return res.bind(self).call(args, interpreter, meta)
        return res
