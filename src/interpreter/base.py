"""Base, error and essential value classes"""

from typing import Optional, Self, TYPE_CHECKING
from dataclasses import dataclass

from lark import Token
from lark.tree import Meta

if TYPE_CHECKING:
    from .main import ASTInterpreter


# pylint: disable=too-few-public-methods
# pylint: disable=too-many-public-methods
# pylint: disable=unused-argument


# ---- Result type ----


class Result:
    """Interpreter result base class"""


@dataclass(frozen=True)
class Success(Result):
    """Object signaling sucessful statement execution (without returning
any value)"""


class Exit(Result):
    """Object signaling early exit"""


# ---- Expression result ----


class ExpressionResult(Result):
    """Expression result base class"""

    def binary_op(
        self, op: str | Token, other: "ExpressionResult", meta: Optional[Meta]
    ) -> "ExpressionResult":
        """Binary operation"""
        # pylint: disable=too-many-return-statements
        match op:
            case "+":
                return self.add(other, meta)
            case "-":
                return self.subtract(other, meta)
            case "*":
                return self.multiply(other, meta)
            case "/":
                return self.divide(other, meta)
            case "%":
                return self.mod(other, meta)
            case "%/%":
                return self.floor_div(other, meta)
            case "&":
                return self.bitwise_and(other, meta)
            case "|":
                return self.bitwise_or(other, meta)
            case "^":
                return self.bitwise_xor(other, meta)
            case "<<":
                return self.left_shift(other, meta)
            case ">>":
                return self.right_shift(other, meta)
            case "==":
                return self.is_equal(other, meta)
            case "!=":
                return self.is_not_equal(other, meta)
            case "<":
                return self.is_less(other, meta)
            case "<=":
                return self.is_less_or_equal(other, meta)
            case ">":
                return self.is_greater(other, meta)
            case ">=":
                return self.is_greater_or_equal(other, meta)
        return error_not_implemented.set_meta(meta)

    def add(
        self, other: "ExpressionResult", meta: Optional[Meta]
    ) -> "ExpressionResult":
        """Addition"""
        return self._unimplemented_binary_op(other, meta)

    def subtract(
        self, other: "ExpressionResult", meta: Optional[Meta]
    ) -> "ExpressionResult":
        """Subtraction"""
        return self._unimplemented_binary_op(other, meta)

    def multiply(
        self, other: "ExpressionResult", meta: Optional[Meta]
    ) -> "ExpressionResult":
        """Multiplication"""
        return self._unimplemented_binary_op(other, meta)

    def divide(
        self, other: "ExpressionResult", meta: Optional[Meta]
    ) -> "ExpressionResult":
        """Division"""
        return self._unimplemented_binary_op(other, meta)

    def mod(
        self, other: "ExpressionResult", meta: Optional[Meta]
    ) -> "ExpressionResult":
        """Modulo"""
        return self._unimplemented_binary_op(other, meta)

    def floor_div(
        self, other: "ExpressionResult", meta: Optional[Meta]
    ) -> "ExpressionResult":
        """Floor division"""
        return self._unimplemented_binary_op(other, meta)

    def bitwise_and(
        self, other: "ExpressionResult", meta: Optional[Meta]
    ) -> "ExpressionResult":
        """Bitwise and"""
        return self._unimplemented_binary_op(other, meta)

    def bitwise_or(
        self, other: "ExpressionResult", meta: Optional[Meta]
    ) -> "ExpressionResult":
        """Bitwise or"""
        return self._unimplemented_binary_op(other, meta)

    def bitwise_xor(
        self, other: "ExpressionResult", meta: Optional[Meta]
    ) -> "ExpressionResult":
        """Bitwise xor"""
        return self._unimplemented_binary_op(other, meta)

    def left_shift(
        self, other: "ExpressionResult", meta: Optional[Meta]
    ) -> "ExpressionResult":
        """Bitwise left shift"""
        return self._unimplemented_binary_op(other, meta)

    def right_shift(
        self, other: "ExpressionResult", meta: Optional[Meta]
    ) -> "ExpressionResult":
        """Bitwise right shift"""
        return self._unimplemented_binary_op(other, meta)

    def is_equal(
        self, other: "ExpressionResult", meta: Optional[Meta]
    ) -> "ExpressionResult":
        """Equality test"""
        return self._unimplemented_binary_op(other, meta)

    def is_not_equal(
        self, other: "ExpressionResult", meta: Optional[Meta]
    ) -> "ExpressionResult":
        """Inequality test"""
        return self._unimplemented_binary_op(other, meta)

    def is_less(
        self, other: "ExpressionResult", meta: Optional[Meta]
    ) -> "ExpressionResult":
        """Less than"""
        return self._unimplemented_binary_op(other, meta)

    def is_less_or_equal(
        self, other: "ExpressionResult", meta: Optional[Meta]
    ) -> "ExpressionResult":
        """Less than or equal to"""
        return self._unimplemented_binary_op(other, meta)

    def is_greater(
        self, other: "ExpressionResult", meta: Optional[Meta]
    ) -> "ExpressionResult":
        """Greater than"""
        return self._unimplemented_binary_op(other, meta)

    def is_greater_or_equal(
        self, other: "ExpressionResult", meta: Optional[Meta]
    ) -> "ExpressionResult":
        """Greater than or equal to"""
        return self._unimplemented_binary_op(other, meta)

    def _unimplemented_binary_op(
        self, other: "ExpressionResult", meta: Optional[Meta]
    ) -> "BLError":
        """Unimplemented binary operation stub"""
        match other:
            case BLError():
                return other
        return error_not_implemented.set_meta(meta)

    def unary_op(self, op: Token, meta: Optional[Meta]) -> "ExpressionResult":
        """Unary operation"""
        match op:
            case "+":
                return self.plus(meta)
            case "-":
                return self.neg(meta)
            case "~":
                return self.bit_not(meta)
            case "!":
                return self.logical_not(meta)
        return error_not_implemented.set_meta(meta)

    def plus(self, meta: Optional[Meta]) -> "ExpressionResult":
        """Unary plus"""
        return error_not_implemented.set_meta(meta)

    def neg(self, meta: Optional[Meta]) -> "ExpressionResult":
        """Negation"""
        return error_not_implemented.set_meta(meta)

    def bit_not(self, meta: Optional[Meta]) -> "ExpressionResult":
        """Bitwise not"""
        return error_not_implemented.set_meta(meta)

    def logical_not(self, meta: Optional[Meta]) -> "ExpressionResult":
        """Logical not"""
        return error_not_implemented.set_meta(meta)

    def get_item(
        self, index: "ExpressionResult", meta: Optional[Meta]
    ) -> "ExpressionResult":
        """Get an item in a container"""
        return self._unimplemented_binary_op(index, meta)

    def set_item(
        self, index: "ExpressionResult", value: "ExpressionResult",
        meta: Optional[Meta]
    ) -> "ExpressionResult":
        """Set an item in a container"""
        match index:
            case BLError():
                return index
        match value:
            case BLError():
                return value
        return error_not_implemented.set_meta(meta)

    def get_attr(
        self, attr: Token, meta: Optional[Meta]
    ) -> "ExpressionResult":
        """Access an attribute"""
        return error_not_implemented.set_meta(meta)

    def call(
        self, args: list["Value"], interpreter: "ASTInterpreter",
        meta: Optional[Meta]
    ) -> "ExpressionResult":
        """Call self as a function"""
        return error_not_implemented.set_meta(meta)

    def dump(self, meta: Optional[Meta]) -> "ExpressionResult":
        """Conversion to representation for debugging"""
        return error_not_implemented.set_meta(meta)

    def to_string(self, meta: Optional[Meta]) -> "ExpressionResult":
        """Conversion to string"""
        return self.dump(meta)

    def to_bool(self, meta: Optional[Meta]) -> "ExpressionResult":
        """Conversion to boolean"""
        return error_not_implemented.set_meta(meta)


# ---- Error type ----


@dataclass
class BLError(Exit, ExpressionResult):
    """Error"""

    value: str
    meta: Optional[Meta] = None

    def set_meta(self, meta: Optional[Meta]) -> Self:
        """Set meta attribute to error"""
        self.meta = meta
        return self

    def fill_args(self, *args, **kwargs) -> Self:
        """Fill in the arguments to the error value, if the error value is a
string"""
        if isinstance(self.value, str):
            self.value = self.value.format(*args, **kwargs)
        return self

    def add(self, other, meta) -> Self:
        return self

    def subtract(self, other, meta) -> Self:
        return self

    def multiply(self, other, meta) -> Self:
        return self

    def mod(self, other, meta) -> Self:
        return self

    def floor_div(self, other, meta) -> Self:
        return self

    def bitwise_and(self, other, meta) -> Self:
        return self

    def bitwise_or(self, other, meta) -> Self:
        return self

    def bitwise_xor(self, other, meta) -> Self:
        return self

    def left_shift(self, other, meta) -> Self:
        return self

    def right_shift(self, other, meta) -> Self:
        return self

    def is_equal(self, other, meta) -> Self:
        return self

    def is_not_equal(self, other, meta) -> Self:
        return self

    def is_less(self, other, meta) -> Self:
        return self

    def is_less_or_equal(self, other, meta) -> Self:
        return self

    def is_greater(self, other, meta) -> Self:
        return self

    def is_greater_or_equal(self, other, meta) -> Self:
        return self

    def plus(self, meta) -> Self:
        return self

    def neg(self, meta) -> Self:
        return self

    def bit_not(self, meta) -> Self:
        return self

    def logical_not(self, meta) -> Self:
        return self

    def get_item(self, index, meta) -> Self:
        return self

    def set_item(self, index, value, meta) -> Self:
        return self

    def get_attr(self, attr, meta):
        return self

    def call(self, args, interpreter, meta) -> Self:
        return self

    def dump(self, meta) -> Self:
        return self

    def to_string(self, meta) -> Self:
        return self


# Errors
error_not_implemented = BLError("Operation not supported")
error_div_by_zero = BLError("Division by zero")
error_out_of_range = BLError("Index out of range: {}")
error_key_nonexistent = BLError("Non-existent key: {}")
error_var_nonexistent = BLError("Variable {} is undefined")
error_wrong_argc = BLError("Function {} needs exactly {} arguments")
error_module_var_nonexistent = BLError("Module {} doesn't have variable {}")
error_include_syntax = BLError("Error in include's syntax:\n{}")
error_inside_include = BLError(
    "Error inside include at line {}, column {}: {}"
)


# ---- Essential value types ----


class Value(ExpressionResult):
    """Value base class"""

    def is_equal(self, other, meta) -> "Bool":
        return BOOLS[self is other]

    def is_not_equal(self, other, meta) -> "Bool":
        return BOOLS[self is not other]

    def logical_not(self, meta) -> "Bool":
        return BOOLS[not self.to_bool(meta)]

    def dump(self, meta) -> "String":
        return String("<value>")

    def to_string(self, meta) -> "String":
        return self.dump(meta)

    def to_bool(self, meta) -> "Bool":
        return BOOLS[True]


@dataclass(frozen=True)
class Bool(Value):
    """Boolean type"""

    value: bool

    def dump(self, meta):
        if self.value:
            return String("true")
        return String("false")

    def to_bool(self, meta):
        return self


BOOLS = Bool(False), Bool(True)


@dataclass(frozen=True)
class Null(Value):
    """Null value"""

    def dump(self, meta):
        return String("null")

    def to_bool(self, meta):
        return BOOLS[False]


NULL = Null()


@dataclass(frozen=True)
class String(Value):
    """String type"""

    value: str

    def add(self, other, meta):
        match other:
            case String(other_val):
                return String(self.value + other_val)
        return super().add(other, meta)

    def multiply(self, other, meta):
        match other:
            case Int(times):
                return String(self.value * times)
        return super().add(other, meta)

    def is_equal(self, other, meta):
        match other:
            case String(other_val):
                return BOOLS[self.value == other_val]
        return super().is_equal(other, meta)

    def is_not_equal(self, other, meta):
        match other:
            case String(other_val):
                return BOOLS[self.value != other_val]
        return super().is_not_equal(other, meta)

    def is_less(self, other, meta):
        match other:
            case String(other_val):
                return BOOLS[self.value < other_val]
        return super().is_less(other, meta)

    def is_less_or_equal(self, other, meta):
        match other:
            case String(other_val):
                return BOOLS[self.value <= other_val]
        return super().is_less_or_equal(other, meta)

    def is_greater(self, other, meta):
        match other:
            case String(other_val):
                return BOOLS[self.value > other_val]
        return super().is_greater(other, meta)

    def is_greater_or_equal(self, other, meta):
        match other:
            case String(other_val):
                return BOOLS[self.value >= other_val]
        return super().is_greater_or_equal(other, meta)

    def dump(self, meta):
        return String(f"'{self.value}'")

    def to_string(self, meta):
        return self

    def to_bool(self, meta):
        return BOOLS[bool(self.value)]


@dataclass(frozen=True)
class Int(Value):
    """Integer type"""

    value: int

    def add(self, other, meta):
        match other:
            case Int(other_val):
                return Int(self.value + other_val)
            case Float(other_val):
                return Float(self.value + other_val)
        return super().add(other, meta)

    def subtract(self, other, meta):
        match other:
            case Int(other_val):
                return Int(self.value - other_val)
            case Float(other_val):
                return Float(self.value - other_val)
        return super().subtract(other, meta)

    def multiply(self, other, meta):
        match other:
            case Int(other_val):
                return Int(self.value * other_val)
            case Float(other_val):
                return Float(self.value - other_val)
        return super().multiply(other, meta)

    def divide(self, other, meta):
        match other:
            case Int(other_val) | Float(other_val):
                try:
                    return Float(self.value / other_val)
                except ZeroDivisionError:
                    return error_div_by_zero.set_meta(meta)
        return super().divide(other, meta)

    def mod(self, other, meta):
        try:
            match other:
                case Int(other_val):
                    return Int(self.value % other_val)
                case Float(other_val):
                    return Float(self.value % other_val)
        except ZeroDivisionError:
            return error_div_by_zero.set_meta(meta)
        return super().mod(other, meta)

    def floor_div(self, other, meta):
        try:
            match other:
                case Int(other_val):
                    return Int(self.value // other_val)
                case Float(other_val):
                    return Float(self.value // other_val)
        except ZeroDivisionError:
            return error_div_by_zero.set_meta(meta)
        return super().floor_div(other, meta)

    def bitwise_and(self, other, meta):
        match other:
            case Int(other_val):
                return Int(self.value & other_val)
        return super().floor_div(other, meta)

    def bitwise_or(self, other, meta):
        match other:
            case Int(other_val):
                return Int(self.value | other_val)
        return super().floor_div(other, meta)

    def bitwise_xor(self, other, meta):
        match other:
            case Int(other_val):
                return Int(self.value ^ other_val)
        return super().floor_div(other, meta)

    def left_shift(self, other, meta):
        match other:
            case Int(other_val):
                return Int(self.value << other_val)
        return super().floor_div(other, meta)

    def right_shift(self, other, meta):
        match other:
            case Int(other_val):
                return Int(self.value >> other_val)
        return super().floor_div(other, meta)

    def is_equal(self, other, meta):
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value == other_val]
        return super().is_equal(other, meta)

    def is_not_equal(self, other, meta):
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value != other_val]
        return super().is_not_equal(other, meta)

    def is_less(self, other, meta):
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value < other_val]
        return super().is_less(other, meta)

    def is_less_or_equal(self, other, meta):
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value <= other_val]
        return super().is_less_or_equal(other, meta)

    def is_greater(self, other, meta):
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value > other_val]
        return super().is_greater(other, meta)

    def is_greater_or_equal(self, other, meta):
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value >= other_val]
        return super().is_greater_or_equal(other, meta)

    def plus(self, meta):
        return Int(+self.value)

    def neg(self, meta):
        return Int(-self.value)

    def bit_not(self, meta):
        return Int(~self.value)

    def dump(self, meta):
        return String(repr(self.value))

    def to_bool(self, meta):
        return BOOLS[bool(self.value)]


@dataclass(frozen=True)
class Float(Value):
    """Float type"""

    value: float

    def add(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return Float(self.value + other_val)
        return super().add(other, meta)

    def subtract(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return Float(self.value - other_val)
        return super().subtract(other, meta)

    def multiply(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return Float(self.value * other_val)
        return super().multiply(other, meta)

    def divide(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                try:
                    return Float(self.value / other_val)
                except ZeroDivisionError:
                    return error_div_by_zero.set_meta(meta)
        return super().divide(other, meta)

    def mod(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                try:
                    return Float(self.value % other_val)
                except ZeroDivisionError:
                    return error_div_by_zero.set_meta(meta)
        return super().mod(other, meta)

    def floor_div(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                try:
                    return Float(self.value // other_val)
                except ZeroDivisionError:
                    return error_div_by_zero.set_meta(meta)
        return super().floor_div(other, meta)

    def is_equal(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value == other_val]
        return super().is_equal(other, meta)

    def is_not_equal(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value != other_val]
        return super().is_not_equal(other, meta)

    def is_less(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value < other_val]
        return super().is_less(other, meta)

    def is_less_or_equal(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value <= other_val]
        return super().is_less_or_equal(other, meta)

    def is_greater(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value > other_val]
        return super().is_greater(other, meta)

    def is_greater_or_equal(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value >= other_val]
        return super().is_greater_or_equal(other, meta)

    def plus(self, meta):
        return Float(+self.value)

    def neg(self, meta):
        return Float(-self.value)

    def dump(self, meta):
        return String(repr(self.value))

    def to_string(self, meta):
        return String(str(self.value))

    def to_bool(self, meta):
        return BOOLS[bool(self.value)]
