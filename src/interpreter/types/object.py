"""Objects and OOP in baba-lang"""


from dataclasses import dataclass
from typing import TYPE_CHECKING
from collections.abc import Callable

from lark.tree import Meta

from .base import BLError, ExpressionResult
from .value import Value, String, Bool
from . import Module
from .function import BLFunction
from .errors import (
    error_var_nonexistent, error_not_implemented,
    error_incorrect_rettype_to_bool
)

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
        return self._overloaded_binary_op("__add__", "add")(
            other, interpreter, meta
        )

    def subtract(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__sub__", "subtract")(
            other, interpreter, meta
        )

    def multiply(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__mul__", "multiply")(
            other, interpreter, meta
        )

    def divide(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__div__", "divide")(
            other, interpreter, meta
        )

    def floor_div(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__floordiv__", "floor_div")(
            other, interpreter, meta
        )

    def mod(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__mod__", "mod")(
            other, interpreter, meta
        )

    def pow(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__pow__", "pow")(
            other, interpreter, meta
        )

    def bitwise_and(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__and__", "bitwise_and")(
            other, interpreter, meta
        )

    def bitwise_or(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__or__", "bitwise_or")(
            other, interpreter, meta
        )

    def bitwise_xor(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__xor__", "bitwise_xor")(
            other, interpreter, meta
        )

    def is_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Bool:
        return self._overloaded_binary_op("__eq__", "is_equal")(
            other, interpreter, meta
        )

    def is_less(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__lt__", "is_less")(
            other, interpreter, meta
        )

    def is_less_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__le__", "is_less_or_equal")(
            other, interpreter, meta
        )

    def is_greater(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__gt__", "is_greater")(
            other, interpreter, meta
        )

    def is_greater_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__ge__", "is_greater_or_equal")(
            other, interpreter, meta
        )

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

    def get_item(
        self, index: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        return self._overloaded_binary_op("__get_item__", "get_item")(
            index, interpreter, meta
        )

    def set_item(
        self, index: ExpressionResult, value: ExpressionResult,
        interpreter: "ASTInterpreter", meta: Meta | None,
    ) -> ExpressionResult:
        if isinstance(index, BLError):
            return index
        if isinstance(index, Value) and isinstance(value, BLError):
            return value
        if isinstance(index, Value) and isinstance(value, Value):
            res = self._call_method_if_exists(
                "__set_item__", [index], interpreter, meta
            )
            if isinstance(res, BLError):
                if res.value == error_var_nonexistent.value:
                    return super().__getattribute__("set_item")(
                        index, interpreter, meta
                    )
            return res
        return error_not_implemented.copy().set_meta(meta)

    def to_bool(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> Bool | BLError:
        res = self._call_method_if_exists("__bool__", [], interpreter, meta)
        if not isinstance(res, Bool):
            if isinstance(res, BLError):
                if res.value == error_var_nonexistent.value:
                    return super().to_bool(interpreter, meta)
            return error_incorrect_rettype_to_bool.copy().set_meta(meta)
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

    def _overloaded_binary_op(self, name: str, fallback_name: str) -> Callable:
        def _wrapper(
            other: ExpressionResult, interpreter: "ASTInterpreter",
            meta: Meta | None,
        ) -> ExpressionResult:
            if isinstance(other, BLError):
                return other
            if isinstance(other, Value):
                res = self._call_method_if_exists(
                    name, [other], interpreter, meta
                )
                if isinstance(res, BLError):
                    if res.value == error_var_nonexistent.value:
                        return super().__getattribute__(fallback_name)(
                            other, interpreter, meta
                        )
                return res
            return error_not_implemented.copy().set_meta(meta)
        return _wrapper

    def _call_method_if_exists(
        self, name: str, args: list[Value], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        match res := self.get_attr(name, meta):
            case BLFunction():
                return res.bind(self).call(args, interpreter, meta)
        return res
