"""Collection types"""


from dataclasses import dataclass
from typing import TYPE_CHECKING

from lark import Token
from lark.tree import Meta

from .base import (
    ExpressionResult,
    Value,
    String,
    Int,
    BOOLS,
    Null,
    NULL,
)
from .errors import (
    error_out_of_range, error_key_nonexistent,
    error_module_var_nonexistent,
)
from .function import PythonFunction

if TYPE_CHECKING:
    from .main import ASTInterpreter


@dataclass(frozen=True)
class BLList(Value):
    """List type"""

    elems: list[Value]

    def add(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case BLList(other_elems):
                return BLList(self.elems + other_elems)
        return super().add(other, meta)

    def multiply(
        self, other: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match other:
            case Int(times):
                return BLList(self.elems * times)
        return super().add(other, meta)

    def get_item(
        self, index: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match index:
            case Int(index_val):
                try:
                    return self.elems[index_val]
                except IndexError:
                    return error_out_of_range.fill_args(index_val) \
                                             .set_meta(meta)
        return super().get_item(index, meta)

    def set_item(
        self, index: ExpressionResult, value: ExpressionResult,
        meta: Meta | None
    ) -> ExpressionResult:
        match index, value:
            case Int(index_val), Value():
                try:
                    self.elems[index_val] = value
                    return value
                except IndexError:
                    return error_out_of_range.fill_args(index_val) \
                                             .set_meta(meta)
        return super().set_item(index, value, meta)

    def get_attr(self, attr: Token, meta: Meta | None) -> ExpressionResult:
        match attr:
            case 'length':
                return PythonFunction(self.length)
            case 'insert':
                return PythonFunction(self.insert)
            case 'remove_at':
                return PythonFunction(self.remove_at)
        return super().get_attr(attr, meta)

    def dump(self, meta):
        return String(f'[{', '.join(e.dump(meta).value for e in self.elems)}]')

    def to_bool(self, meta):
        return BOOLS[bool(self.elems)]

    def length(
        self, meta: Meta | None, interpreter: "ASTInterpreter", /, *_
    ) -> Int:
        """Get length (number of elements) of a list"""
        # pylint: disable=unused-argument
        return Int(len(self.elems))

    def insert(
        self, meta: Meta | None, interpreter: "ASTInterpreter", /,
        index: Int, item: Value, *_
    ) -> Null:
        """Insert an element into a list"""
        # pylint: disable=unused-argument
        self.elems.insert(index.value, item)
        return NULL

    def remove_at(
        self, meta: Meta | None, interpreter: "ASTInterpreter", /,
        index: Int, *_
    ) -> Null:
        """Remove an element from a list given index"""
        # pylint: disable=unused-argument
        self.elems.pop(index.value)
        return NULL


def list_len(
    meta: Meta | None, interpreter: "ASTInterpreter", /, list_: BLList, *_
) -> Int:
    """Get length (number of elements) of a list"""
    return list_.length(meta, interpreter)


def list_insert(
    meta: Meta | None, interpreter: "ASTInterpreter", /,
    list_: BLList, index: Int, item: Value, *_
) -> Null:
    """Insert an element into a list"""
    return list_.insert(meta, interpreter, index, item)


def list_remove_at(
    meta: Meta | None, interpreter: "ASTInterpreter", /,
    list_: BLList, index: Int, *_
) -> Null:
    """Remove an element from a list given index"""
    return list_.remove_at(meta, interpreter, index)


@dataclass(frozen=True)
class BLDict(Value):
    """Dict type"""

    content: dict[Value, Value]

    def get_item(
        self, index: ExpressionResult, meta: Meta | None
    ) -> ExpressionResult:
        match index:
            case Value():
                try:
                    return self.content[index]
                except KeyError:
                    return error_key_nonexistent.fill_args(
                        index.dump(meta).value
                    ).set_meta(meta)
        return super().get_item(index, meta)

    def set_item(
        self, index: ExpressionResult, value: ExpressionResult,
        meta: Meta | None,
    ) -> ExpressionResult:
        match index, value:
            case Value(), Value():
                try:
                    self.content[index] = value
                    return value
                except KeyError:
                    return error_key_nonexistent.fill_args(
                        index.dump(meta).value
                    ).set_meta(meta)
        return super().set_item(index, value, meta)

    def get_attr(self, attr: Token, meta: Meta | None) -> ExpressionResult:
        match attr:
            case 'size':
                return PythonFunction(dict_size)
            case 'keys':
                return PythonFunction(dict_keys)
            case 'remove':
                return PythonFunction(dict_remove)
        return super().get_attr(attr, meta)

    def dump(self, meta):
        pair_str_list = []
        for k, v in self.content.items():
            pair_str_list.append(f"{k.dump(meta).value}: {v.dump(meta).value}")
        return String(f'{{{', '.join(pair_str_list)}}}')

    def to_bool(self, meta):
        return BOOLS[bool(self.content)]

    def size(
        self, meta: Meta | None, interpreter: "ASTInterpreter", /, *_
    ) -> Int:
        """Get length (number of elements) of a dictionary"""
        # pylint: disable=unused-argument
        return Int(len(self.content))

    def keys(
        self, meta: Meta | None, interpreter: "ASTInterpreter", /, *_
    ) -> BLList:
        """Get all keys of a dictionary as a list"""
        # pylint: disable=unused-argument
        return BLList(list(self.content))

    def remove(
        self, meta: Meta | None, interpreter: "ASTInterpreter", /,
        key: Value, *_
    ) -> Null:
        """Remove a key from a dictionary"""
        # pylint: disable=unused-argument
        del self.content[key]
        return NULL


def dict_size(
    meta: Meta | None, interpreter: "ASTInterpreter", /,
    dict_: BLDict, *_
) -> Int:
    """Get length (number of elements) of a dictionary"""
    return dict_.size(meta, interpreter)


def dict_keys(
    meta: Meta | None, interpreter: "ASTInterpreter", /,
    dict_: BLDict, *_
) -> BLList:
    """Get all keys of a dictionary as a list"""
    return dict_.keys(meta, interpreter)


def dict_remove(
    meta: Meta | None, interpreter: "ASTInterpreter", /,
    dict_: BLDict, key: Value, *_
) -> Null:
    """Remove a key from a dictionary"""
    return dict_.remove(meta, interpreter, key)


@dataclass(frozen=True)
class Module(Value):
    """baba-lang module"""

    name: str
    vars: dict[str, Value]

    def get_attr(self, attr, meta):
        try:
            return self.vars[attr]
        except KeyError:
            return (
                error_module_var_nonexistent
                .fill_args(self.name, str(attr))
                .set_meta(meta)
            )

    def dump(self, meta):
        return String(f"<module '{self.name}'>")
