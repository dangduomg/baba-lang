"""Interpreter classes"""


from typing import Optional, Self
from dataclasses import dataclass

from lark import Token
from lark.tree import Meta


#pylint: disable=too-few-public-methods
#pylint: disable=unused-argument


class Result:
    """Interpreter result base class"""


@dataclass(frozen=True)
class Success(Result):
    """Object signaling sucessful statement execution (without returning any value)"""


class Exit(Result):
    """Object signaling early exit"""


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

    def is_eq(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Equality test"""
        return Bool(self is other)

    def is_ne(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Equality test"""
        return Bool(self is not other)

    def is_lt(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Equality test"""
        return self.unimplemented_binary_op(other, meta)

    def is_le(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Equality test"""
        return self.unimplemented_binary_op(other, meta)

    def is_gt(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Equality test"""
        return self.unimplemented_binary_op(other, meta)

    def is_ge(self, other: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        """Equality test"""
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

    def to_string(self, meta: Meta) -> 'String':
        return String('<value>')


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

    def subscript(self, index: 'ExpressionResult', meta: Meta) -> 'ExpressionResult':
        return self


# Errors
error_not_implemented = BLError('Operation not implemented')
error_div_by_zero = BLError('Division by zero')


# Value types


class Value(ExpressionResult):
    """Value"""


@dataclass(frozen=True)
class String(Value):
    """String type"""

    value: str

    def add(self, other, meta):
        match other:
            case String(other_val):
                return String(self.value + other_val)
        return super().add(other, meta)

    def mul(self, other, meta):
        match other:
            case Int(times):
                return String(self.value * times)
        return super().add(other, meta)

    def is_eq(self, other, meta):
        match other:
            case String(other_val):
                return Bool(self.value == other_val)
        return super().is_eq(other, meta)

    def is_ne(self, other, meta):
        match other:
            case String(other_val):
                return Bool(self.value != other_val)
        return super().is_ne(other, meta)

    def is_lt(self, other, meta):
        match other:
            case String(other_val):
                return Bool(self.value < other_val)
        return super().is_lt(other, meta)

    def is_le(self, other, meta):
        match other:
            case String(other_val):
                return Bool(self.value <= other_val)
        return super().is_le(other, meta)

    def is_gt(self, other, meta):
        match other:
            case String(other_val):
                return Bool(self.value > other_val)
        return super().is_gt(other, meta)

    def is_ge(self, other, meta):
        match other:
            case String(other_val):
                return Bool(self.value >= other_val)
        return super().is_ge(other, meta)


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

    def sub(self, other, meta):
        match other:
            case Int(other_val):
                return Int(self.value - other_val)
            case Float(other_val):
                return Float(self.value - other_val)
        return super().sub(other, meta)

    def mul(self, other, meta):
        match other:
            case Int(other_val):
                return Int(self.value * other_val)
            case Float(other_val):
                return Float(self.value - other_val)
        return super().mul(other, meta)

    def div(self, other, meta):
        match other:
            case Int(other_val) | Float(other_val):
                try:
                    return Float(self.value / other_val)
                except ZeroDivisionError:
                    return error_div_by_zero.set_meta(meta)
        return super().div(other, meta)

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

    def floordiv(self, other, meta):
        try:
            match other:
                case Int(other_val):
                    return Int(self.value // other_val)
                case Float(other_val):
                    return Float(self.value // other_val)
        except ZeroDivisionError:
            return error_div_by_zero.set_meta(meta)
        return super().floordiv(other, meta)

    def is_eq(self, other, meta):
        match other:
            case Int(other_val) | Float(other_val):
                return Bool(self.value == other_val)
        return super().is_eq(other, meta)

    def is_ne(self, other, meta):
        match other:
            case Int(other_val) | Float(other_val):
                return Bool(self.value != other_val)
        return super().is_ne(other, meta)

    def is_lt(self, other, meta):
        match other:
            case Int(other_val) | Float(other_val):
                return Bool(self.value < other_val)
        return super().is_lt(other, meta)

    def is_le(self, other, meta):
        match other:
            case Int(other_val) | Float(other_val):
                return Bool(self.value <= other_val)
        return super().is_le(other, meta)

    def is_gt(self, other, meta):
        match other:
            case Int(other_val) | Float(other_val):
                return Bool(self.value > other_val)
        return super().is_gt(other, meta)

    def is_ge(self, other, meta):
        match other:
            case Int(other_val) | Float(other_val):
                return Bool(self.value >= other_val)
        return super().is_ge(other, meta)

    def pos(self, meta):
        return Int(+self.value)

    def neg(self, meta):
        return Int(-self.value)


@dataclass(frozen=True)
class Float(Value):
    """Float type"""

    value: float

    def add(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return Float(self.value + other_val)
        return super().add(other, meta)

    def sub(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return Float(self.value - other_val)
        return super().sub(other, meta)

    def mul(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return Float(self.value * other_val)
        return super().mul(other, meta)

    def div(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                try:
                    return Float(self.value / other_val)
                except ZeroDivisionError:
                    return error_div_by_zero.set_meta(meta)
        return super().div(other, meta)

    def mod(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                try:
                    return Float(self.value % other_val)
                except ZeroDivisionError:
                    return error_div_by_zero.set_meta(meta)
        return super().mod(other, meta)

    def floordiv(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                try:
                    return Float(self.value // other_val)
                except ZeroDivisionError:
                    return error_div_by_zero.set_meta(meta)
        return super().floordiv(other, meta)

    def is_eq(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return Bool(self.value == other_val)
        return super().is_eq(other, meta)

    def is_ne(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return Bool(self.value != other_val)
        return super().is_ne(other, meta)

    def is_lt(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return Bool(self.value < other_val)
        return super().is_lt(other, meta)

    def is_le(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return Bool(self.value <= other_val)
        return super().is_le(other, meta)

    def is_gt(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return Bool(self.value > other_val)
        return super().is_gt(other, meta)

    def is_ge(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return Bool(self.value >= other_val)
        return super().is_ge(other, meta)

    def pos(self, meta):
        return Float(+self.value)

    def neg(self, meta):
        return Float(-self.value)


@dataclass(frozen=True)
class _Bool(Value):
    """Boolean type"""

    value: bool


class Bool(_Bool):
    """Wrapper for Boolean type (to ensure Booleans are doubletons)"""

    _instances = _Bool(False), _Bool(True)

    def __new__(cls, value: bool) -> '_Bool':
        return cls._instances[value]


@dataclass(frozen=True, init=False)
class Null(Value):
    """Null value"""

    _instance = None

    def __new__(cls) -> 'Null':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


@dataclass(frozen=True)
class List(Value):
    """List type"""

    elems: list[Value]

    def add(self, other, meta):
        match other:
            case List(other_elems):
                return List(self.elems + other_elems)
        return super().add(other, meta)

    def mul(self, other, meta):
        match other:
            case Int(times):
                return List(self.elems * times)
        return super().add(other, meta)

    def get_item(self, index, meta):
        match index:
            case Int(index_val):
                return self.elems[index_val]
        return super().get_item(index, meta)


@dataclass(frozen=True)
class Dict(Value):
    """Dict type"""

    content: dict[Value, Value]

    def get_item(self, index, meta):
        match index:
            case Value():
                return self.content[index]
        return super().get_item(index, meta)
