"""Interpreter value classes"""


from dataclasses import dataclass

from .base import ExpressionResult, error_div_by_zero


#pylint: disable=too-few-public-methods
#pylint: disable=unused-argument


class Value(ExpressionResult):
    """Value base class"""

    def is_eq(self, other, meta) -> 'Bool':
        return BOOLS[self is other]

    def is_ne(self, other, meta) -> 'Bool':
        return BOOLS[self is not other]

    def dump(self, meta) -> 'String':
        return String('<value>')


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
                return BOOLS[self.value == other_val]
        return super().is_eq(other, meta)

    def is_ne(self, other, meta):
        match other:
            case String(other_val):
                return BOOLS[self.value != other_val]
        return super().is_ne(other, meta)

    def is_lt(self, other, meta):
        match other:
            case String(other_val):
                return BOOLS[self.value < other_val]
        return super().is_lt(other, meta)

    def is_le(self, other, meta):
        match other:
            case String(other_val):
                return BOOLS[self.value <= other_val]
        return super().is_le(other, meta)

    def is_gt(self, other, meta):
        match other:
            case String(other_val):
                return BOOLS[self.value > other_val]
        return super().is_gt(other, meta)

    def is_ge(self, other, meta):
        match other:
            case String(other_val):
                return BOOLS[self.value >= other_val]
        return super().is_ge(other, meta)

    def dump(self, meta):
        return String(f"'{self.value}'")

    def to_string(self, meta):
        return self


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

    def bitand(self, other, meta):
        match other:
            case Int(other_val):
                return Int(self.value & other_val)
        return super().floordiv(other, meta)

    def bitor(self, other, meta):
        match other:
            case Int(other_val):
                return Int(self.value | other_val)
        return super().floordiv(other, meta)

    def bitxor(self, other, meta):
        match other:
            case Int(other_val):
                return Int(self.value ^ other_val)
        return super().floordiv(other, meta)

    def lshift(self, other, meta):
        match other:
            case Int(other_val):
                return Int(self.value << other_val)
        return super().floordiv(other, meta)

    def rshift(self, other, meta):
        match other:
            case Int(other_val):
                return Int(self.value >> other_val)
        return super().floordiv(other, meta)

    def is_eq(self, other, meta):
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value == other_val]
        return super().is_eq(other, meta)

    def is_ne(self, other, meta):
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value != other_val]
        return super().is_ne(other, meta)

    def is_lt(self, other, meta):
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value < other_val]
        return super().is_lt(other, meta)

    def is_le(self, other, meta):
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value <= other_val]
        return super().is_le(other, meta)

    def is_gt(self, other, meta):
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value > other_val]
        return super().is_gt(other, meta)

    def is_ge(self, other, meta):
        match other:
            case Int(other_val) | Float(other_val):
                return BOOLS[self.value >= other_val]
        return super().is_ge(other, meta)

    def pos(self, meta):
        return Int(+self.value)

    def neg(self, meta):
        return Int(-self.value)

    def dump(self, meta):
        return String(str(self.value))


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
                return BOOLS[self.value == other_val]
        return super().is_eq(other, meta)

    def is_ne(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value != other_val]
        return super().is_ne(other, meta)

    def is_lt(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value < other_val]
        return super().is_lt(other, meta)

    def is_le(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value <= other_val]
        return super().is_le(other, meta)

    def is_gt(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value > other_val]
        return super().is_gt(other, meta)

    def is_ge(self, other, meta):
        match other:
            case Float(other_val) | Int(other_val):
                return BOOLS[self.value >= other_val]
        return super().is_ge(other, meta)

    def pos(self, meta):
        return Float(+self.value)

    def neg(self, meta):
        return Float(-self.value)

    def dump(self, meta):
        return String(str(self.value))


@dataclass(frozen=True)
class Bool(Value):
    """Boolean type"""

    value: bool

    def dump(self, meta):
        if self.value:
            return String('true')
        return String('false')


BOOLS = Bool(False), Bool(True)


@dataclass(frozen=True)
class Null(Value):
    """Null value"""

    def dump(self, meta):
        return String('null')


NULL = Null()


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

    def dump(self, meta):
        return String(f'[{', '.join(e.dump(meta).value for e in self.elems)}]')


@dataclass(frozen=True)
class Dict(Value):
    """Dict type"""

    content: dict[Value, Value]

    def get_item(self, index, meta):
        match index:
            case Value():
                return self.content[index]
        return super().get_item(index, meta)

    def dump(self, meta):
        pair_str_list = []
        for k, v in self.content.items():
            pair_str_list.append(f'{k.dump(meta).value}: {v.dump(meta).value}')
        return String(f'{{{', '.join(pair_str_list)}}}')
