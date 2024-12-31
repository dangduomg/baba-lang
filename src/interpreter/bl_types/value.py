"""Essential value types"""


from typing import TYPE_CHECKING, Self
from dataclasses import dataclass

from lark.tree import Meta

from .base import ExpressionResult
from .errors import error_div_by_zero


if TYPE_CHECKING:
    from .errors import BLError
    from ..main import ASTInterpreter


class Value(ExpressionResult):
    """Value base class"""

    def is_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> "Bool":
        return BOOLS[self is other]

    def is_not_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> "Bool":
        return BOOLS[self is not other]

    def logical_not(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "Bool":
        return BOOLS[not self.to_bool(interpreter, meta)]

    def dump(self, meta: Meta | None) -> "String":
        return String("<value>")

    def to_string(self, meta: Meta | None) -> "String":
        return self.dump(meta)

    def to_bool(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "Bool | BLError":
        return BOOLS[True]


@dataclass(frozen=True)
class Bool(Value):
    """Boolean type"""

    value: bool

    def dump(self, meta: Meta | None) -> "String":
        if self.value:
            return String("true")
        return String("false")

    def to_bool(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "Bool":
        return self


BOOLS = Bool(False), Bool(True)


@dataclass(frozen=True)
class Null(Value):
    """Null value"""

    def dump(self, meta: Meta | None) -> "String":
        return String("null")

    def to_bool(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> Bool:
        return BOOLS[False]


NULL = Null()


@dataclass(frozen=True)
class String(Value):
    """String type"""

    value: str

    def add(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return String(self.value + other_val)
        return super().add(other, interpreter, meta)

    def multiply(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(times):
                return String(self.value * times)
        return super().multiply(other, interpreter, meta)

    def is_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Bool:
        match other:
            case String(other_val):
                return BOOLS[self.value == other_val]
        return super().is_equal(other, interpreter, meta)

    def is_not_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Bool:
        match other:
            case String(other_val):
                return BOOLS[self.value != other_val]
        return super().is_not_equal(other, interpreter, meta)

    def is_less(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return BOOLS[self.value < other_val]
        return super().is_less(other, interpreter, meta)

    def is_less_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return BOOLS[self.value <= other_val]
        return super().is_less_or_equal(other, interpreter, meta)

    def is_greater(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return BOOLS[self.value > other_val]
        return super().is_greater(other, interpreter, meta)

    def is_greater_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return BOOLS[self.value >= other_val]
        return super().is_greater_or_equal(other, interpreter, meta)

    def dump(self, meta: Meta | None) -> "String":
        return String(f"{self.value!r}")

    def to_string(self, meta: Meta | None) -> Self:
        return self

    def to_bool(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> Bool:
        return BOOLS[bool(self.value)]


@dataclass(frozen=True)
class Int(Value):
    """Integer type"""

    value: int

    def add(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value + other_val)
            case Float(other_val):
                return Float(self.value + other_val)
        return super().add(other, interpreter, meta)

    def subtract(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value - other_val)
            case Float(other_val):
                return Float(self.value - other_val)
        return super().subtract(other, interpreter, meta)

    def multiply(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value * other_val)
            case Float(other_val):
                return Float(self.value * other_val)
        return super().multiply(other, interpreter, meta)

    def divide(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val) | Float(other_val):
                try:
                    return Float(self.value / other_val)
                except ZeroDivisionError:
                    return error_div_by_zero.copy().set_meta(meta)
        return super().divide(other, interpreter, meta)

    def mod(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        try:
            match other:
                case Int(other_val):
                    return Int(self.value % other_val)
                case Float(other_val):
                    return Float(self.value % other_val)
        except ZeroDivisionError:
            return error_div_by_zero.copy().set_meta(meta)
        return super().mod(other, interpreter, meta)

    def floor_div(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        try:
            match other:
                case Int(other_val):
                    return Int(self.value // other_val)
                case Float(other_val):
                    return Float(self.value // other_val)
        except ZeroDivisionError:
            return error_div_by_zero.copy().set_meta(meta)
        return super().floor_div(other, interpreter, meta)

    def pow(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        try:
            match other:
                case Int(other_val):
                    return Int(self.value ** other_val)
                case Float(other_val):
                    return Float(self.value ** other_val)
        except ZeroDivisionError:
            return error_div_by_zero.copy().set_meta(meta)
        return super().pow(other, interpreter, meta)

    def bitwise_and(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value & other_val)
        return super().bitwise_and(other, interpreter, meta)

    def bitwise_or(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value | other_val)
        return super().bitwise_or(other, interpreter, meta)

    def bitwise_xor(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value ^ other_val)
        return super().bitwise_xor(other, interpreter, meta)

    def left_shift(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value << other_val)
        return super().left_shift(other, interpreter, meta)

    def right_shift(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value >> other_val)
        return super().right_shift(other, interpreter, meta)

    def is_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Bool:
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value == other_val]
        return super().is_equal(other, interpreter, meta)

    def is_not_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Bool:
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value != other_val]
        return super().is_not_equal(other, interpreter, meta)

    def is_less(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value < other_val]
        return super().is_less(other, interpreter, meta)

    def is_less_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value <= other_val]
        return super().is_less_or_equal(other, interpreter, meta)

    def is_greater(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value > other_val]
        return super().is_greater(other, interpreter, meta)

    def is_greater_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value >= other_val]
        return super().is_greater_or_equal(other, interpreter, meta)

    def plus(self, interpreter: "ASTInterpreter", meta: Meta | None) -> "Int":
        return Int(+self.value)

    def neg(self, interpreter: "ASTInterpreter", meta: Meta | None) -> "Int":
        return Int(-self.value)

    def bitwise_not(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "Int":
        return Int(~self.value)

    def dump(self, meta: Meta | None) -> String:
        return String(repr(self.value))

    def to_bool(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> Bool:
        return BOOLS[bool(self.value)]


@dataclass(frozen=True)
class Float(Value):
    """Float type"""

    value: float

    def add(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return Float(self.value + other_val)
        return super().add(other, interpreter, meta)

    def subtract(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return Float(self.value - other_val)
        return super().subtract(other, interpreter, meta)

    def multiply(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return Float(self.value * other_val)
        return super().multiply(other, interpreter, meta)

    def divide(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                try:
                    return Float(self.value / other_val)
                except ZeroDivisionError:
                    return error_div_by_zero.copy().set_meta(meta)
        return super().divide(other, interpreter, meta)

    def floor_div(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                try:
                    return Float(self.value // other_val)
                except ZeroDivisionError:
                    return error_div_by_zero.copy().set_meta(meta)
        return super().floor_div(other, interpreter, meta)

    def mod(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                try:
                    return Float(self.value % other_val)
                except ZeroDivisionError:
                    return error_div_by_zero.copy().set_meta(meta)
        return super().mod(other, interpreter, meta)

    def is_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Bool:
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value == other_val]
        return super().is_equal(other, interpreter, meta)

    def is_not_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Bool:
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value != other_val]
        return super().is_not_equal(other, interpreter, meta)

    def is_less(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value < other_val]
        return super().is_less(other, interpreter, meta)

    def is_less_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value <= other_val]
        return super().is_less_or_equal(other, interpreter, meta)

    def is_greater(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value > other_val]
        return super().is_greater(other, interpreter, meta)

    def is_greater_or_equal(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value >= other_val]
        return super().is_greater_or_equal(other, interpreter, meta)

    def plus(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "Float":
        return Float(+self.value)

    def neg(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "Float":
        return Float(-self.value)

    def dump(self, meta: Meta | None) -> String:
        return String(repr(self.value))

    def to_string(self, meta: Meta | None) -> String:
        return String(str(self.value))

    def to_bool(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> Bool:
        return BOOLS[bool(self.value)]
