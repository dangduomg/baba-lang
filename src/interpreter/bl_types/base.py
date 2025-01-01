"""Base, error and essential value classes"""

from abc import ABC
from typing import Self, TYPE_CHECKING
from dataclasses import dataclass

from lark import Token
from lark.tree import Meta

if TYPE_CHECKING:
    from .value import Value
    from ..main import ASTInterpreter


# pylint: disable=too-few-public-methods
# pylint: disable=too-many-public-methods
# pylint: disable=unused-argument


# ---- Result type ----


class Result(ABC):
    """Interpreter result base class"""


@dataclass(frozen=True)
class Success(Result):
    """Object signaling sucessful statement execution (without returning
any value)"""


class Exit(Result, ABC):
    """Object signaling early exit"""


class ExpressionResult(Result, ABC):
    """Expression result base class"""

    def binary_op(
        self, op: str, other: "ExpressionResult",
        interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "ExpressionResult":
        """Binary operation"""
        # pylint: disable=too-many-return-statements
        match op:
            case "+":
                return self.add(other, interpreter, meta)
            case "-":
                return self.subtract(other, interpreter, meta)
            case "*":
                return self.multiply(other, interpreter, meta)
            case "/":
                return self.divide(other, interpreter, meta)
            case "==":
                return self.is_equal(other, interpreter, meta)
            case "!=":
                return self.is_not_equal(other, interpreter, meta)
            case "<":
                return self.is_less(other, interpreter, meta)
            case "<=":
                return self.is_less_or_equal(other, interpreter, meta)
            case ">":
                return self.is_greater(other, interpreter, meta)
            case ">=":
                return self.is_greater_or_equal(other, interpreter, meta)
        return error_not_implemented.copy().set_meta(meta)

    def add(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Addition"""
        return self._unimplemented_binary_op(other, meta)

    def subtract(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Subtraction"""
        return self._unimplemented_binary_op(other, meta)

    def multiply(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Multiplication"""
        return self._unimplemented_binary_op(other, meta)

    def divide(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Division"""
        return self._unimplemented_binary_op(other, meta)

    def is_equal(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Equality test"""
        return self._unimplemented_binary_op(other, meta)

    def is_not_equal(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Inequality test"""
        return self._unimplemented_binary_op(other, meta)

    def is_less(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Less than"""
        return self._unimplemented_binary_op(other, meta)

    def is_less_or_equal(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Less than or equal to"""
        return self._unimplemented_binary_op(other, meta)

    def is_greater(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Greater than"""
        return self._unimplemented_binary_op(other, meta)

    def is_greater_or_equal(
        self, other: "ExpressionResult", interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Greater than or equal to"""
        return self._unimplemented_binary_op(other, meta)

    def _unimplemented_binary_op(
        self, other: "ExpressionResult", meta: Meta | None
    ) -> "BLError":
        """Unimplemented binary operation stub"""
        match other:
            case BLError():
                return other
        return error_not_implemented.copy().set_meta(meta)

    def unary_op(
        self, op: Token, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "ExpressionResult":
        """Unary operation"""
        match op:
            case "-":
                return self.neg(interpreter, meta)
            case "!":
                return self.logical_not(interpreter, meta)
        return error_not_implemented.copy().set_meta(meta)

    def neg(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "ExpressionResult":
        """Negation"""
        return error_not_implemented.copy().set_meta(meta)

    def logical_not(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "ExpressionResult":
        """Conversion to boolean"""
        return error_not_implemented.copy().set_meta(meta)

    def get_attr(
        self, attr: str, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "ExpressionResult":
        """Access an attribute"""
        return error_not_implemented.copy().set_meta(meta)

    def set_attr(
        self, attr: str, value: "ExpressionResult", meta: Meta | None
    ) -> "ExpressionResult":
        """Set an attribute"""
        return self._unimplemented_binary_op(value, meta)

    def call(
        self, args: list["Value"], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Call self as a function"""
        return error_not_implemented.copy().set_meta(meta)

    def new(
        self, args: list["Value"], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Instantiate an object"""
        return error_not_implemented.copy().set_meta(meta)

    def dump(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "ExpressionResult":
        """Conversion to representation for debugging"""
        return error_not_implemented.copy().set_meta(meta)


# ---- Error type ----


@dataclass
class BLError(Exit, ExpressionResult):
    """Error"""

    value: "Value"
    meta: Meta | None = None

    def copy(self) -> "BLError":
        """Copy the error"""
        return BLError(self.value, self.meta)

    def set_meta(self, meta: Meta | None) -> Self:
        """Set meta attribute to error"""
        self.meta = meta
        return self

    def add(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Self:
        return self

    def subtract(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Self:
        return self

    def multiply(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Self:
        return self

    def is_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Self:
        return self

    def is_not_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Self:
        return self

    def is_less(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Self:
        return self

    def is_less_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Self:
        return self

    def is_greater(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Self:
        return self

    def is_greater_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Self:
        return self

    def neg(self, interpreter: "ASTInterpreter", meta: Meta | None) -> Self:
        return self

    def get_attr(
        self, attr: str, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> Self:
        return self

    def set_attr(
        self, attr: str, value: ExpressionResult, meta: Meta | None
    ) -> Self:
        return self

    def call(
        self, args: list["Value"], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> Self:
        return self

    def dump(self, interpreter: "ASTInterpreter", meta: Meta | None) -> Self:
        return self


# Errors
