"""Collection types"""


from dataclasses import dataclass

from .base import Value, String, Int, BOOLS, error_out_of_range, error_key_nonexistent


@dataclass(frozen=True)
class BLList(Value):
    """List type"""

    elems: list[Value]

    def add(self, other, meta):
        match other:
            case BLList(other_elems):
                return BLList(self.elems + other_elems)
        return super().add(other, meta)

    def multiply(self, other, meta):
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
                    return error_out_of_range.fill_args(index_val).set_meta(meta)
        return super().get_item(index, meta)

    def set_item(self, index, value, meta):
        match index, value:
            case Int(index_val), Value():
                try:
                    self.elems[index_val] = value
                    return value
                except IndexError:
                    return error_out_of_range.fill_args(index_val).set_meta(meta)
        return super().set_item(index, value, meta)

    def dump(self, meta):
        return String(f'[{', '.join(e.dump(meta).value for e in self.elems)}]')

    def to_bool(self, meta):
        return BOOLS[bool(self.elems)]


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
                    return error_key_nonexistent.fill_args(index.dump(meta).value).set_meta(meta)
        return super().get_item(index, meta)

    def set_item(self, index, value, meta):
        match index, value:
            case Value(), Value():
                try:
                    self.content[index] = value
                    return value
                except KeyError:
                    return error_key_nonexistent.fill_args(index.dump(meta).value).set_meta(meta)
        return super().set_item(index, value, meta)

    def dump(self, meta):
        pair_str_list = []
        for k, v in self.content.items():
            pair_str_list.append(f'{k.dump(meta).value}: {v.dump(meta).value}')
        return String(f'{{{', '.join(pair_str_list)}}}')

    def to_bool(self, meta):
        return BOOLS[bool(self.content)]