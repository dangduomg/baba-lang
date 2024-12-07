"""Interpreter classes"""


from typing import Optional, Self
from dataclasses import dataclass

from lark import Token
from lark.tree import Meta


#pylint: disable=too-few-public-methods
#pylint: disable=unused-argument


class Result:
    """Interpreter result base class"""


class ExpressionResult(Result):
    """Expression result base class"""

    def binary_op(self, op: Token, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Binary operation"""
        match op:
            case '+':
                return self.add(other, meta)
            case '-':
                return self.sub(other, meta)
            case '*':
                return self.mul(other, meta)
            case '%':
                return self.mod(other, meta)
            case '%/%':
                return self.floordiv(other, meta)
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

    def mod(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Modulo"""
        return self.unimplemented_binary_op(other, meta)

    def floordiv(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Floor division"""
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


class Exit(Result):
    """Object signaling early exit"""


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
        """Addition"""
        return self

    def sub(self, other, meta) -> Self:
        """Subtraction"""
        return self

    def mul(self, other, meta) -> Self:
        """Multiplication"""
        return self

    def mod(self, other, meta) -> Self:
        """Modulo"""
        return self

    def floordiv(self, other, meta) -> Self:
        """Floor division"""
        return self

    def pos(self, meta) -> Self:
        return self

    def neg(self, meta) -> Self:
        return self


# Errors
error_not_implemented = BLError('Operation not implemented')
error_div_by_zero = BLError('Division by zero')


# Value types


class Value(ExpressionResult):
    """Value"""


@dataclass(frozen=True)
class Int(Value):
    """Integer type"""

    value: int

    def add(self, other, meta):
        match other:
            case Int(other_val):
                return Int(self.value + other_val)
        return super().add(other, meta)

    def sub(self, other, meta):
        match other:
            case Int(other_val):
                return Int(self.value - other_val)
        return super().sub(other, meta)

    def mul(self, other, meta):
        match other:
            case Int(other_val):
                return Int(self.value * other_val)
        return super().mul(other, meta)

    def mod(self, other, meta):
        match other:
            case Int(other_val):
                try:
                    return Int(self.value % other_val)
                except ZeroDivisionError:
                    return error_div_by_zero.set_meta(meta)
        return super().mod(other, meta)

    def floordiv(self, other, meta):
        match other:
            case Int(other_val):
                try:
                    return Int(self.value // other_val)
                except ZeroDivisionError:
                    return error_div_by_zero.set_meta(meta)
        return super().floordiv(other, meta)

    def pos(self, meta):
        return Int(+self.value)

    def neg(self, meta):
        return Int(-self.value)
