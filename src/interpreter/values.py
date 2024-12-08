"""Interpreter value classes"""


from dataclasses import dataclass

from .base import ExpressionResult, error_div_by_zero, error_out_of_range


#pylint: disable=too-few-public-methods
#pylint: disable=unused-argument


class Value(ExpressionResult):
    """Value base class"""

    def is_equal(self, other, meta) -> 'Bool':
        return BOOLS[self is other]

    def is_not_equal(self, other, meta) -> 'Bool':
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
class BLList(Value):
    """List type"""

    elems: list[Value]

    def add(self, other, meta):
        match other:
            case BLList(other_elems):
                return BLList(self.elems + other_elems)
        return super().add(other, meta)

    def mul(self, other, meta):
        match other:
            case Int(times):
                return BLList(self.elems * times)
        return super().add(other, meta)

    def get_item(self, index, meta):
        match index:
            case Int(index_val):
                try:
                    return self.elems[index_val]
                except IndexError:
                    return error_out_of_range.set_meta(meta)
        return super().get_item(index, meta)

    def dump(self, meta):
        return String(f'[{', '.join(e.dump(meta).value for e in self.elems)}]')


@dataclass(frozen=True)
class BLDict(Value):
    """Dict type"""

    content: dict[Value, Value]

    def get_item(self, index, meta):
        match index:
            case Value():
                try:
                    return self.content[index]
                except KeyError:
                    return error_out_of_range.set_meta(meta)
        return super().get_item(index, meta)

    def dump(self, meta):
        pair_str_list = []
        for k, v in self.content.items():
            pair_str_list.append(f'{k.dump(meta).value}: {v.dump(meta).value}')
        return String(f'{{{', '.join(pair_str_list)}}}')
