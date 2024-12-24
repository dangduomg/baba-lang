"""Base, error and essential value classes"""

from typing import Self, TYPE_CHECKING
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


class ExpressionResult(Result):
    """Expression result base class"""

    def binary_op(
        self, op: str | Token, other: "ExpressionResult", meta: Meta | None
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
            case "**":
                return self.pow(other, meta)
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
        self, other: "ExpressionResult", meta: Meta | None
    ) -> "ExpressionResult":
        """Addition"""
        return self._unimplemented_binary_op(other, meta)

    def subtract(
        self, other: "ExpressionResult", meta: Meta | None
    ) -> "ExpressionResult":
        """Subtraction"""
        return self._unimplemented_binary_op(other, meta)

    def multiply(
        self, other: "ExpressionResult", meta: Meta | None
    ) -> "ExpressionResult":
        """Multiplication"""
        return self._unimplemented_binary_op(other, meta)

    def divide(
        self, other: "ExpressionResult", meta: Meta | None
    ) -> "ExpressionResult":
        """Division"""
        return self._unimplemented_binary_op(other, meta)

    def mod(
        self, other: "ExpressionResult", meta: Meta | None
    ) -> "ExpressionResult":
        """Modulo"""
        return self._unimplemented_binary_op(other, meta)

    def floor_div(
        self, other: "ExpressionResult", meta: Meta | None
    ) -> "ExpressionResult":
        """Floor division"""
        return self._unimplemented_binary_op(other, meta)

    def pow(
        self, other: "ExpressionResult", meta: Meta | None
    ) -> "ExpressionResult":
        """Power"""
        return self._unimplemented_binary_op(other, meta)

    def bitwise_and(
        self, other: "ExpressionResult", meta: Meta | None
    ) -> "ExpressionResult":
        """Bitwise and"""
        return self._unimplemented_binary_op(other, meta)

    def bitwise_or(
        self, other: "ExpressionResult", meta: Meta | None
    ) -> "ExpressionResult":
        """Bitwise or"""
        return self._unimplemented_binary_op(other, meta)

    def bitwise_xor(
        self, other: "ExpressionResult", meta: Meta | None
    ) -> "ExpressionResult":
        """Bitwise xor"""
        return self._unimplemented_binary_op(other, meta)

    def left_shift(
        self, other: "ExpressionResult", meta: Meta | None
    ) -> "ExpressionResult":
        """Bitwise left shift"""
        return self._unimplemented_binary_op(other, meta)

    def right_shift(
        self, other: "ExpressionResult", meta: Meta | None
    ) -> "ExpressionResult":
        """Bitwise right shift"""
        return self._unimplemented_binary_op(other, meta)

    def is_equal(
        self, other: "ExpressionResult", meta: Meta | None
    ) -> "ExpressionResult":
        """Equality test"""
        return self._unimplemented_binary_op(other, meta)

    def is_not_equal(
        self, other: "ExpressionResult", meta: Meta | None
    ) -> "ExpressionResult":
        """Inequality test"""
        return self._unimplemented_binary_op(other, meta)

    def is_less(
        self, other: "ExpressionResult", meta: Meta | None
    ) -> "ExpressionResult":
        """Less than"""
        return self._unimplemented_binary_op(other, meta)

    def is_less_or_equal(
        self, other: "ExpressionResult", meta: Meta | None
    ) -> "ExpressionResult":
        """Less than or equal to"""
        return self._unimplemented_binary_op(other, meta)

    def is_greater(
        self, other: "ExpressionResult", meta: Meta | None
    ) -> "ExpressionResult":
        """Greater than"""
        return self._unimplemented_binary_op(other, meta)

    def is_greater_or_equal(
        self, other: "ExpressionResult", meta: Meta | None
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
        return error_not_implemented.set_meta(meta)

    def unary_op(self, op: Token, meta: Meta | None) -> "ExpressionResult":
        """Unary operation"""
        match op:
            case "+":
                return self.plus(meta)
            case "-":
                return self.neg(meta)
            case "~":
                return self.bitwise_not(meta)
            case "!":
                return self.logical_not(meta)
        return error_not_implemented.set_meta(meta)

    def plus(self, meta: Meta | None) -> "ExpressionResult":
        """Unary plus"""
        return error_not_implemented.set_meta(meta)

    def neg(self, meta: Meta | None) -> "ExpressionResult":
        """Negation"""
        return error_not_implemented.set_meta(meta)

    def bitwise_not(self, meta: Meta | None) -> "ExpressionResult":
        """Bitwise not"""
        return error_not_implemented.set_meta(meta)

    def logical_not(self, meta: Meta | None) -> "ExpressionResult":
        """Logical not"""
        return error_not_implemented.set_meta(meta)

    def get_item(
        self, index: "ExpressionResult", meta: Meta | None
    ) -> "ExpressionResult":
        """Get an item in a container"""
        return self._unimplemented_binary_op(index, meta)

    def set_item(
        self, index: "ExpressionResult", value: "ExpressionResult",
        meta: Meta | None
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
        self, attr: Token, meta: Meta | None
    ) -> "ExpressionResult":
        """Access an attribute"""
        return error_not_implemented.set_meta(meta)

    def call(
        self, args: list["Value"], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult":
        """Call self as a function"""
        return error_not_implemented.set_meta(meta)

    def dump(self, meta: Meta | None) -> "ExpressionResult":
        """Conversion to representation for debugging"""
        return error_not_implemented.set_meta(meta)

    def to_string(self, meta: Meta | None) -> "ExpressionResult":
        """Conversion to string"""
        return self.dump(meta)

    def to_bool(self, meta: Meta | None) -> "ExpressionResult":
        """Conversion to boolean"""
        return error_not_implemented.set_meta(meta)


# ---- Error type ----


@dataclass
class BLError(Exit, ExpressionResult):
    """Error"""

    value: str
    meta: Meta | None = None

    def set_meta(self, meta: Meta | None) -> Self:
        """Set meta attribute to error"""
        self.meta = meta
        return self

    def fill_args(self, *args, **kwargs) -> Self:
        """Fill in the arguments to the error value, if the error value is a
string"""
        if isinstance(self.value, str):
            self.value = self.value.format(*args, **kwargs)
        return self

    def add(self, other: ExpressionResult, meta: Meta | None) -> Self:
        return self

    def subtract(self, other: ExpressionResult, meta: Meta | None) -> Self:
        return self

    def multiply(self, other: ExpressionResult, meta: Meta | None) -> Self:
        return self

    def mod(self, other: ExpressionResult, meta: Meta | None) -> Self:
        return self

    def pow(self, other: ExpressionResult, meta: Meta | None) -> Self:
        return self

    def floor_div(self, other: ExpressionResult, meta: Meta | None) -> Self:
        return self

    def bitwise_and(self, other: ExpressionResult, meta: Meta | None) -> Self:
        return self

    def bitwise_or(self, other: ExpressionResult, meta: Meta | None) -> Self:
        return self

    def bitwise_xor(self, other: ExpressionResult, meta: Meta | None) -> Self:
        return self

    def left_shift(self, other: ExpressionResult, meta: Meta | None) -> Self:
        return self

    def right_shift(self, other: ExpressionResult, meta: Meta | None) -> Self:
        return self

    def is_equal(self, other: ExpressionResult, meta: Meta | None) -> Self:
        return self

    def is_not_equal(
        self, other: ExpressionResult, meta: Meta | None
    ) -> Self:
        return self

    def is_less(self, other: ExpressionResult, meta: Meta | None) -> Self:
        return self

    def is_less_or_equal(
        self, other: ExpressionResult, meta: Meta | None
    ) -> Self:
        return self

    def is_greater(self, other: ExpressionResult, meta: Meta | None) -> Self:
        return self

    def is_greater_or_equal(
        self, other: ExpressionResult, meta: Meta | None
    ) -> Self:
        return self

    def plus(self, meta: Meta | None) -> Self:
        return self

    def neg(self, meta: Meta | None) -> Self:
        return self

    def bitwise_not(self, meta: Meta | None) -> Self:
        return self

    def logical_not(self, meta: Meta | None) -> Self:
        return self

    def get_item(self, index: ExpressionResult, meta: Meta | None) -> Self:
        return self

    def set_item(
        self, index: ExpressionResult, value: ExpressionResult,
        meta: Meta | None
    ) -> Self:
        return self

    def get_attr(self, attr: Token, meta: Meta | None) -> Self:
        return self

    def call(
        self, args: list["Value"], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> Self:
        return self

    def dump(self, meta: Meta | None) -> Self:
        return self

    def to_string(self, meta: Meta | None) -> Self:
        return self


# Errors
error_not_implemented = BLError("Operation not supported")
error_div_by_zero = BLError("Division by zero")


# ---- Essential value types ----


class Value(ExpressionResult):
    """Value base class"""

    def is_equal(self, other: ExpressionResult, meta: Meta | None) -> "Bool":
        return BOOLS[self is other]

    def is_not_equal(
        self, other: ExpressionResult, meta: Meta | None
    ) -> "Bool":
        return BOOLS[self is not other]

    def logical_not(self, meta: Meta | None) -> "Bool":
        return BOOLS[not self.to_bool(meta)]

    def dump(self, meta: Meta | None) -> "String":
        return String("<value>")

    def to_string(self, meta: Meta | None) -> "String":
        return self.dump(meta)

    def to_bool(self, meta: Meta | None) -> "Bool":
        return BOOLS[True]


@dataclass(frozen=True)
class Bool(Value):
    """Boolean type"""

    value: bool

    def dump(self, meta: Meta | None) -> "String":
        if self.value:
            return String("true")
        return String("false")

    def to_bool(self, meta: Meta | None) -> "Bool":
        return self


BOOLS = Bool(False), Bool(True)


@dataclass(frozen=True)
class Null(Value):
    """Null value"""

    def dump(self, meta: Meta | None) -> "String":
        return String("null")

    def to_bool(self, meta: Meta | None) -> Bool:
        return BOOLS[False]


NULL = Null()


@dataclass(frozen=True)
class String(Value):
    """String type"""

    value: str

    def add(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return String(self.value + other_val)
        return super().add(other, meta)

    def multiply(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Int(times):
                return String(self.value * times)
        return super().multiply(other, meta)

    def is_equal(
        self, other: ExpressionResult, meta: Meta | None
    ) -> Bool:
        match other:
            case String(other_val):
                return BOOLS[self.value == other_val]
        return super().is_equal(other, meta)

    def is_not_equal(
        self, other: ExpressionResult, meta: Meta | None
    ) -> Bool:
        match other:
            case String(other_val):
                return BOOLS[self.value != other_val]
        return super().is_not_equal(other, meta)

    def is_less(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return BOOLS[self.value < other_val]
        return super().is_less(other, meta)

    def is_less_or_equal(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return BOOLS[self.value <= other_val]
        return super().is_less_or_equal(other, meta)

    def is_greater(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return BOOLS[self.value > other_val]
        return super().is_greater(other, meta)

    def is_greater_or_equal(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case String(other_val):
                return BOOLS[self.value >= other_val]
        return super().is_greater_or_equal(other, meta)

    def dump(self, meta: Meta | None) -> "String":
        return String(f"'{self.value}'")

    def to_string(self, meta: Meta | None) -> Self:
        return self

    def to_bool(self, meta: Meta | None) -> Bool:
        return BOOLS[bool(self.value)]


@dataclass(frozen=True)
class Int(Value):
    """Integer type"""

    value: int

    def add(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value + other_val)
            case Float(other_val):
                return Float(self.value + other_val)
        return super().add(other, meta)

    def subtract(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value - other_val)
            case Float(other_val):
                return Float(self.value - other_val)
        return super().subtract(other, meta)

    def multiply(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value * other_val)
            case Float(other_val):
                return Float(self.value * other_val)
        return super().multiply(other, meta)

    def divide(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Int(other_val) | Float(other_val):
                try:
                    return Float(self.value / other_val)
                except ZeroDivisionError:
                    return error_div_by_zero.set_meta(meta)
        return super().divide(other, meta)

    def mod(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        try:
            match other:
                case Int(other_val):
                    return Int(self.value % other_val)
                case Float(other_val):
                    return Float(self.value % other_val)
        except ZeroDivisionError:
            return error_div_by_zero.set_meta(meta)
        return super().mod(other, meta)

    def floor_div(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        try:
            match other:
                case Int(other_val):
                    return Int(self.value // other_val)
                case Float(other_val):
                    return Float(self.value // other_val)
        except ZeroDivisionError:
            return error_div_by_zero.set_meta(meta)
        return super().floor_div(other, meta)

    def pow(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        try:
            match other:
                case Int(other_val):
                    return Int(self.value ** other_val)
                case Float(other_val):
                    return Float(self.value ** other_val)
        except ZeroDivisionError:
            return error_div_by_zero.set_meta(meta)
        return super().pow(other, meta)

    def bitwise_and(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value & other_val)
        return super().bitwise_and(other, meta)

    def bitwise_or(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value | other_val)
        return super().bitwise_or(other, meta)

    def bitwise_xor(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value ^ other_val)
        return super().bitwise_xor(other, meta)

    def left_shift(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value << other_val)
        return super().left_shift(other, meta)

    def right_shift(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Int(other_val):
                return Int(self.value >> other_val)
        return super().right_shift(other, meta)

    def is_equal(
        self, other: ExpressionResult, meta: Meta | None
    ) -> Bool:
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value == other_val]
        return super().is_equal(other, meta)

    def is_not_equal(
        self, other: ExpressionResult, meta: Meta | None
    ) -> Bool:
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value != other_val]
        return super().is_not_equal(other, meta)

    def is_less(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value < other_val]
        return super().is_less(other, meta)

    def is_less_or_equal(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value <= other_val]
        return super().is_less_or_equal(other, meta)

    def is_greater(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value > other_val]
        return super().is_greater(other, meta)

    def is_greater_or_equal(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value >= other_val]
        return super().is_greater_or_equal(other, meta)

    def plus(self, meta: Meta | None) -> "Int":
        return Int(+self.value)

    def neg(self, meta: Meta | None) -> "Int":
        return Int(-self.value)

    def bitwise_not(self, meta: Meta | None) -> "Int":
        return Int(~self.value)

    def dump(self, meta: Meta | None) -> String:
        return String(repr(self.value))

    def to_bool(self, meta: Meta | None) -> Bool:
        return BOOLS[bool(self.value)]


@dataclass(frozen=True)
class Float(Value):
    """Float type"""

    value: float

    def add(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return Float(self.value + other_val)
        return super().add(other, meta)

    def subtract(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return Float(self.value - other_val)
        return super().subtract(other, meta)

    def multiply(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return Float(self.value * other_val)
        return super().multiply(other, meta)

    def divide(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                try:
                    return Float(self.value / other_val)
                except ZeroDivisionError:
                    return error_div_by_zero.set_meta(meta)
        return super().divide(other, meta)

    def mod(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                try:
                    return Float(self.value % other_val)
                except ZeroDivisionError:
                    return error_div_by_zero.set_meta(meta)
        return super().mod(other, meta)

    def floor_div(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                try:
                    return Float(self.value // other_val)
                except ZeroDivisionError:
                    return error_div_by_zero.set_meta(meta)
        return super().floor_div(other, meta)

    def is_equal(
        self, other: ExpressionResult, meta: Meta | None
    ) -> Bool:
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value == other_val]
        return super().is_equal(other, meta)

    def is_not_equal(
        self, other: ExpressionResult, meta: Meta | None
    ) -> Bool:
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value != other_val]
        return super().is_not_equal(other, meta)

    def is_less(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value < other_val]
        return super().is_less(other, meta)

    def is_less_or_equal(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value <= other_val]
        return super().is_less_or_equal(other, meta)

    def is_greater(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value > other_val]
        return super().is_greater(other, meta)

    def is_greater_or_equal(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value >= other_val]
        return super().is_greater_or_equal(other, meta)

    def plus(self, meta: Meta | None) -> "Float":
        return Float(+self.value)

    def neg(self, meta: Meta | None) -> "Float":
        return Float(-self.value)

    def dump(self, meta: Meta | None) -> String:
        return String(repr(self.value))

    def to_string(self, meta: Meta | None) -> String:
        return String(str(self.value))

    def to_bool(self, meta: Meta | None) -> Bool:
        return BOOLS[bool(self.value)]
