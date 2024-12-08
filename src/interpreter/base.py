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
                return self.sub(other, meta)
            case '*':
                return self.mul(other, meta)
            case '/':
                return self.div(other, meta)
            case '%':
                return self.mod(other, meta)
            case '%/%':
                return self.floordiv(other, meta)
            case '&':
                return self.bitand(other, meta)
            case '|':
                return self.bitor(other, meta)
            case '^':
                return self.bitxor(other, meta)
            case '<<':
                return self.lshift(other, meta)
            case '==':
                return self.is_eq(other, meta)
            case '!=':
                return self.is_ne(other, meta)
            case '<':
                return self.is_lt(other, meta)
            case '<=':
                return self.is_le(other, meta)
            case '>':
                return self.is_gt(other, meta)
            case '>=':
                return self.is_ge(other, meta)
        return error_not_implemented.set_meta(meta)

    def add(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Addition"""
        return self.unimplemented_binary_op(other, meta)

    def sub(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Subtraction"""
        return self.unimplemented_binary_op(other, meta)

    def mul(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Multiplication"""
        return self.unimplemented_binary_op(other, meta)

    def div(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Division"""
        return self.unimplemented_binary_op(other, meta)

    def mod(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Modulo"""
        return self.unimplemented_binary_op(other, meta)

    def floordiv(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Floor division"""
        return self.unimplemented_binary_op(other, meta)

    def bitand(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Bitwise and"""
        return self.unimplemented_binary_op(other, meta)

    def bitor(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Bitwise or"""
        return self.unimplemented_binary_op(other, meta)

    def bitxor(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Bitwise xor"""
        return self.unimplemented_binary_op(other, meta)

    def lshift(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Bitwise left shift"""
        return self.unimplemented_binary_op(other, meta)

    def rshift(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Bitwise right shift"""
        return self.unimplemented_binary_op(other, meta)

    def is_eq(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Equality test"""
        return self.unimplemented_binary_op(other, meta)

    def is_ne(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Inequality test"""
        return self.unimplemented_binary_op(other, meta)

    def is_lt(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Less than"""
        return self.unimplemented_binary_op(other, meta)

    def is_le(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Less than or equal to"""
        return self.unimplemented_binary_op(other, meta)

    def is_gt(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Greater than"""
        return self.unimplemented_binary_op(other, meta)

    def is_ge(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
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
                return self.pos(meta)
            case '-':
                return self.neg(meta)
        return error_not_implemented.set_meta(meta)

    def pos(self, meta: Meta) -> 'ExpressionResult':
        """Unary plus"""
        return error_not_implemented.set_meta(meta)

    def neg(self, meta: Meta) -> 'ExpressionResult':
        """Negation"""
        return error_not_implemented.set_meta(meta)

    def get_item(self, index: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Get an item in a container"""
        return self.unimplemented_binary_op(index, meta)

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

    def add(self, other, meta) -> Self:
        return self

    def sub(self, other, meta) -> Self:
        return self

    def mul(self, other, meta) -> Self:
        return self

    def mod(self, other, meta) -> Self:
        return self

    def floordiv(self, other, meta) -> Self:
        return self

    def is_eq(self, other, meta) -> Self:
        return self

    def is_ne(self, other, meta) -> Self:
        return self

    def is_lt(self, other, meta) -> Self:
        return self

    def is_le(self, other, meta) -> Self:
        return self

    def is_gt(self, other, meta) -> Self:
        return self

    def is_ge(self, other, meta) -> Self:
        return self

    def pos(self, meta) -> Self:
        return self

    def neg(self, meta) -> Self:
        return self

    def get_item(self, index, meta) -> Self:
        return self

    def dump(self, meta) -> Self:
        return self

    def to_string(self, meta) -> Self:
        return self

# Errors
error_not_implemented = BLError('Operation not supported')
error_div_by_zero = BLError('Division by zero')
