"""Numeric types"""


from dataclasses import dataclass
from typing import TYPE_CHECKING, override

from lark.tree import Meta

from .essentials import (
    Value, ExpressionResult, Bool, BOOLS, String, BLError, cast_to_instance,
    Class, ExceptionClass
)

if TYPE_CHECKING:
    from ..main import ASTInterpreter


DivByZeroException = Class(String("DivByZeroException"), ExceptionClass)


@dataclass(frozen=True)
class Int(Value):
    """Integer type"""

    # pylint: disable=too-many-public-methods

    value: int

    @override
    def add(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value + other_val)
            case Float(other_val):
                return Float(self.value + other_val)
        return super().add(other, interpreter, meta)

    @override
    def subtract(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value - other_val)
            case Float(other_val):
                return Float(self.value - other_val)
        return super().subtract(other, interpreter, meta)

    @override
    def multiply(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value * other_val)
            case Float(other_val):
                return Float(self.value * other_val)
        return super().multiply(other, interpreter, meta)

    @override
    def divide(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val) | Float(other_val):
                try:
                    return Float(self.value / other_val)
                except ZeroDivisionError:
                    return BLError(cast_to_instance(
                        DivByZeroException.new([], interpreter, meta)
                    ), meta, interpreter.path)
        return super().divide(other, interpreter, meta)

    @override
    def floor_div(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val) | Float(other_val):
                try:
                    return Float(self.value // other_val)
                except ZeroDivisionError:
                    return BLError(cast_to_instance(
                        DivByZeroException.new([], interpreter, meta)
                    ), meta, interpreter.path)
        return super().floor_div(other, interpreter, meta)

    @override
    def modulo(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val) | Float(other_val):
                try:
                    return Float(self.value % other_val)
                except ZeroDivisionError:
                    return BLError(cast_to_instance(
                        DivByZeroException.new([], interpreter, meta)
                    ), meta, interpreter.path)
        return super().modulo(other, interpreter, meta)

    @override
    def power(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val) if self.value >= 0:
                return Int(self.value ** other_val)
            case Int(other_val) | Float(other_val):
                try:
                    return Float(self.value ** other_val)
                except ZeroDivisionError:
                    return BLError(cast_to_instance(
                        DivByZeroException.new([], interpreter, meta)
                    ), meta, interpreter.path)
        return super().power(other, interpreter, meta)

    @override
    def bit_and(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value & other_val)
        return super().bit_and(other, interpreter, meta)

    @override
    def bit_or(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value | other_val)
        return super().bit_or(other, interpreter, meta)

    @override
    def bit_xor(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value ^ other_val)
        return super().bit_xor(other, interpreter, meta)

    @override
    def left_shift(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value << other_val)
        return super().left_shift(other, interpreter, meta)

    @override
    def right_shift(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value >> other_val)
        return super().right_shift(other, interpreter, meta)

    @override
    def is_equal(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Bool | BLError:
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value == other_val]
        return super().is_equal(other, interpreter, meta)

    @override
    def is_less(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value < other_val]
        return super().is_less(other, interpreter, meta)

    @override
    def is_less_or_equal(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value <= other_val]
        return super().is_less_or_equal(other, interpreter, meta)

    @override
    def is_greater(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value > other_val]
        return super().is_greater(other, interpreter, meta)

    @override
    def is_greater_or_equal(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value >= other_val]
        return super().is_greater_or_equal(other, interpreter, meta)

    @override
    def plus(self, interpreter: "ASTInterpreter", meta: Meta | None) -> "Int":
        return Int(+self.value)

    @override
    def neg(self, interpreter: "ASTInterpreter", meta: Meta | None) -> "Int":
        return Int(-self.value)

    @override
    def bit_not(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "Int":
        return Int(~self.value)

    @override
    def to_bool(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> Bool:
        return BOOLS[bool(self.value)]

    @override
    def dump(self, interpreter: "ASTInterpreter", meta: Meta | None) -> String:
        return String(repr(self.value))

    @override
    def to_string(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> String:
        return String(str(self.value))


@dataclass(frozen=True)
class Float(Value):
    """Float type"""

    value: float

    @override
    def add(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return Float(self.value + other_val)
        return super().add(other, interpreter, meta)

    @override
    def subtract(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return Float(self.value - other_val)
        return super().subtract(other, interpreter, meta)

    @override
    def multiply(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return Float(self.value * other_val)
        return super().multiply(other, interpreter, meta)

    @override
    def divide(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                try:
                    return Float(self.value / other_val)
                except ZeroDivisionError:
                    return BLError(cast_to_instance(
                        DivByZeroException.new([], interpreter, meta)
                    ), meta, interpreter.path)
        return super().divide(other, interpreter, meta)

    @override
    def floor_div(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                try:
                    return Float(self.value // other_val)
                except ZeroDivisionError:
                    return BLError(cast_to_instance(
                        DivByZeroException.new([], interpreter, meta)
                    ), meta, interpreter.path)
        return super().floor_div(other, interpreter, meta)

    @override
    def modulo(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                try:
                    return Float(self.value % other_val)
                except ZeroDivisionError:
                    return BLError(cast_to_instance(
                        DivByZeroException.new([], interpreter, meta)
                    ), meta, interpreter.path)
        return super().modulo(other, interpreter, meta)

    @override
    def power(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                try:
                    return Float(self.value ** other_val)
                except ZeroDivisionError:
                    return BLError(cast_to_instance(
                        DivByZeroException.new([], interpreter, meta)
                    ), meta, interpreter.path)
        return super().power(other, interpreter, meta)

    @override
    def is_equal(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> Bool | BLError:
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value == other_val]
        return super().is_equal(other, interpreter, meta)

    @override
    def is_less(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value < other_val]
        return super().is_less(other, interpreter, meta)

    @override
    def is_less_or_equal(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value <= other_val]
        return super().is_less_or_equal(other, interpreter, meta)

    @override
    def is_greater(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value > other_val]
        return super().is_greater(other, interpreter, meta)

    @override
    def is_greater_or_equal(
        self, other: Value, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value >= other_val]
        return super().is_greater_or_equal(other, interpreter, meta)

    @override
    def plus(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "Float":
        return Float(+self.value)

    @override
    def neg(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> "Float":
        return Float(-self.value)

    @override
    def to_bool(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> Bool:
        return BOOLS[bool(self.value)]

    @override
    def dump(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> String:
        return String(repr(self.value))

    @override
    def to_string(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> String:
        return String(str(self.value))
