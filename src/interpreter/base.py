"""Base and error classes"""


from typing import Optional, Self
from dataclasses import dataclass

from lark import Token
from lark.tree import Meta


#pylint: disable=too-few-public-methods
#pylint: disable=unused-argument


# ---- Result type ----


class Result:
    """Interpreter result base class"""


@dataclass(frozen=True)
class Success(Result):
    """Object signaling sucessful statement execution (without returning any value)"""


class Exit(Result):
    """Object signaling early exit"""


# ---- Expression result ----


class ExpressionResult(Result):
    """Expression result base class"""

    def binary_op(self, op: Token, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Binary operation"""
        #pylint: disable=too-many-return-statements
        match op:
            case '+':
                return self.add(other, meta)
            case '-':
                return self.subtract(other, meta)
            case '*':
                return self.multiply(other, meta)
            case '/':
                return self.divide(other, meta)
            case '%':
                return self.mod(other, meta)
            case '%/%':
                return self.floor_div(other, meta)
            case '&':
                return self.bitwise_and(other, meta)
            case '|':
                return self.bitwise_or(other, meta)
            case '^':
                return self.bitwise_xor(other, meta)
            case '<<':
                return self.left_shift(other, meta)
            case '>>':
                return self.right_shift(other, meta)
            case '==':
                return self.is_equal(other, meta)
            case '!=':
                return self.is_not_equal(other, meta)
            case '<':
                return self.is_less(other, meta)
            case '<=':
                return self.is_less_or_equal(other, meta)
            case '>':
                return self.is_greater(other, meta)
            case '>=':
                return self.is_greater_or_equal(other, meta)
        return error_not_implemented.set_meta(meta)

    def add(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Addition"""
        return self.unimplemented_binary_op(other, meta)

    def subtract(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Subtraction"""
        return self.unimplemented_binary_op(other, meta)

    def multiply(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Multiplication"""
        return self.unimplemented_binary_op(other, meta)

    def divide(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Division"""
        return self.unimplemented_binary_op(other, meta)

    def mod(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Modulo"""
        return self.unimplemented_binary_op(other, meta)

    def floor_div(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Floor division"""
        return self.unimplemented_binary_op(other, meta)

    def bitwise_and(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Bitwise and"""
        return self.unimplemented_binary_op(other, meta)

    def bitwise_or(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Bitwise or"""
        return self.unimplemented_binary_op(other, meta)

    def bitwise_xor(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Bitwise xor"""
        return self.unimplemented_binary_op(other, meta)

    def left_shift(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Bitwise left shift"""
        return self.unimplemented_binary_op(other, meta)

    def right_shift(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Bitwise right shift"""
        return self.unimplemented_binary_op(other, meta)

    def is_equal(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Equality test"""
        return self.unimplemented_binary_op(other, meta)

    def is_not_equal(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Inequality test"""
        return self.unimplemented_binary_op(other, meta)

    def is_less(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Less than"""
        return self.unimplemented_binary_op(other, meta)

    def is_less_or_equal(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Less than or equal to"""
        return self.unimplemented_binary_op(other, meta)

    def is_greater(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Greater than"""
        return self.unimplemented_binary_op(other, meta)

    def is_greater_or_equal(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Greater than or equal to"""
        return self.unimplemented_binary_op(other, meta)

    def unimplemented_binary_op(self, other: 'ExpressionResult', meta: Meta) -> 'BLError':
        """Unimplemented binary operation stub"""
        match other:
            case BLError():
                return other
        return error_not_implemented.set_meta(meta)

    def unary_op(self, op: Token, meta: Meta) -> 'ExpressionResult':
        """Unary operation"""
        match op:
            case '+':
                return self.plus(meta)
            case '-':
                return self.neg(meta)
        return error_not_implemented.set_meta(meta)

    def plus(self, meta: Meta) -> 'ExpressionResult':
        """Unary plus"""
        return error_not_implemented.set_meta(meta)

    def neg(self, meta: Meta) -> 'ExpressionResult':
        """Negation"""
        return error_not_implemented.set_meta(meta)

    def get_item(self, index: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Get an item in a container"""
        return self.unimplemented_binary_op(index, meta)

    def set_item(self, index: 'ExpressionResult', value: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Set an item in a container"""
        match index:
            case BLError():
                return index
        match value:
            case BLError():
                return value
        return error_not_implemented.set_meta(meta)

    def dump(self, meta: Meta) -> 'ExpressionResult':
        """Conversion to representation for debugging"""
        return error_not_implemented.set_meta(meta)

    def to_string(self, meta: Meta) -> 'ExpressionResult':
        """Conversion to string"""
        return self.dump(meta)


# ---- Error type ----


@dataclass
class BLError(Exit, ExpressionResult):
    """Error"""

    value: object
    meta: Optional[Meta] = None

    def set_meta(self, meta: Meta) -> Self:
        """Set meta attribute to error"""
        self.meta = meta
        return self

    def fill_args(self, *args, **kwargs) -> Self:
        """Fill in the arguments to the error value, if the error value is a string"""
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

    def get_item(self, index, meta) -> Self:
        return self

    def set_item(self, index, value, meta) -> Self:
        return self

    def dump(self, meta) -> Self:
        return self

    def to_string(self, meta) -> Self:
        return self

# Errors
error_not_implemented = BLError('Operation not supported')
error_div_by_zero = BLError('Division by zero')
error_out_of_range = BLError('Index out of range: {}')
error_key_nonexistent = BLError('Non-existent key: {}')
error_var_nonexistent = BLError('Variable {} is undefined')
