"""Collection types"""


from dataclasses import dataclass
from typing import TYPE_CHECKING, cast
from operator import methodcaller

from lark.tree import Meta

from .essentials import (
    ExpressionResult, Value, BLError, String, Int, Null, NULL, Class,
    PythonFunction, Instance, ObjectClass, ExceptionClass,
    IncorrectTypeException,
)

if TYPE_CHECKING:
    from ..main import ASTInterpreter


# List


ListClass = Class(String("List"), ObjectClass, {
    "get": PythonFunction(
        lambda meta, intp, /, this, index, *_: this.get(meta, intp, index)
    ),
    "set": PythonFunction(
        lambda meta, intp, /, this, index, value, *_:
        this.set(meta, intp, index, value)
    ),
    "length": PythonFunction(
        lambda meta, intp, /, this, *_: this.length(meta, intp)
    ),
    "insert": PythonFunction(
        lambda meta, intp, /, this, index, item, *_:
        this.insert(meta, intp, index, item)
    ),
    "remove_at": PythonFunction(
        lambda meta, intp, /, this, index, *_:
        this.remove_at(meta, intp, index)
    ),
})


class BLList(Instance):
    """List type"""

    elems: list[Value]

    def __init__(self, elems: list[Value]) -> None:
        super().__init__(ListClass, {})
        self.elems = elems

    def add(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case BLList(elems=other_elems):
                return BLList(self.elems + other_elems)
        return super().add(other, interpreter, meta)

    def multiply(
        self, other: ExpressionResult, interpreter: "ASTInterpreter",
        meta: Meta | None,
    ) -> ExpressionResult:
        match other:
            case Int(times):
                return BLList(self.elems * times)
        return super().add(other, interpreter, meta)

    def dump(self, interpreter: "ASTInterpreter", meta: Meta | None) -> String:
        dmp = methodcaller("dump", interpreter, meta)
        return String(f"[{', '.join(dmp(e).value for e in self.elems)}]")

    def get(
        self, meta: Meta | None, interpreter: "ASTInterpreter", /,
        index: Int, *_
    ) -> ExpressionResult:
        """Get an element from a list"""
        match index:
            case Int(index_val):
                try:
                    return self.elems[index_val]
                except IndexError:
                    return BLError(cast(
                        Instance,
                        OutOfRangeException.new([], interpreter, meta),
                    ))
        return BLError(cast(
            Instance, IncorrectTypeException.new([], interpreter, meta)
        ))

    def set(
        self, meta: Meta | None, interpreter: "ASTInterpreter", /,
        index: Int, value: Value, *_
    ) -> ExpressionResult:
        """Set an element in a list"""
        match index, value:
            case Int(index_val), Value():
                try:
                    self.elems[index_val] = value
                    return value
                except IndexError:
                    return BLError(cast(
                        Instance,
                        OutOfRangeException.new([], interpreter, meta),
                    ))
        return BLError(cast(
            Instance, IncorrectTypeException.new([], interpreter, meta)
        ))

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


# List errors
OutOfRangeException = Class(String("OutOfRangeException"), ExceptionClass)


# Dict


DictClass = Class(String("Dict"), ObjectClass, {
    "get": PythonFunction(
        lambda meta, intp, /, this, key, *_: this.get(meta, intp, key)
    ),
    "set": PythonFunction(
        lambda meta, intp, /, this, key, value, *_:
        this.set(meta, intp, key, value)
    ),
    "length": PythonFunction(
        lambda meta, intp, /, this, *_: this.length(meta, intp)
    ),
    "keys": PythonFunction(
        lambda meta, intp, /, this, *_: this.keys(meta, intp)
    ),
    "remove": PythonFunction(
        lambda meta, intp, /, this, key, *_: this.remove(meta, intp, key)
    ),
})


class BLDict(Instance):
    """Dict type"""

    content: dict[Value, Value]

    def __init__(self, content: dict[Value, Value]) -> None:
        super().__init__(DictClass, {})
        self.content = content

    def dump(self, interpreter: "ASTInterpreter", meta: Meta | None) -> String:
        dmp = methodcaller("dump", interpreter, meta)
        pair_str_list = []
        for k, v in self.content.items():
            pair_str_list.append(f"{dmp(k)}: {dmp(v)}")
        return String(f'{{{', '.join(pair_str_list)}}}')

    def get(
        self, meta: Meta | None, interpreter: "ASTInterpreter", /,
        key: Value, *_
    ) -> ExpressionResult:
        """Get a value from a dictionary"""
        match key:
            case Value():
                try:
                    return self.content[key]
                except KeyError:
                    return BLError(cast(
                        Instance,
                        KeyNotFoundException.new([], interpreter, meta),
                    ))
        return BLError(cast(
            Instance, IncorrectTypeException.new([], interpreter, meta)
        ))

    def set(
        self, meta: Meta | None, interpreter: "ASTInterpreter", /,
        key: Value, value: Value, *_
    ) -> ExpressionResult:
        """Set a value in a dictionary"""
        match key, value:
            case Value(), Value():
                self.content[key] = value
                return value
        return BLError(cast(
            Instance, IncorrectTypeException.new([], interpreter, meta)
        ))

    def length(
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


# Dict errors
KeyNotFoundException = Class(String("KeyNotFoundException"), ExceptionClass)


# Module


@dataclass(frozen=True)
class Module(Value):
    """baba-lang module"""

    name: str
    vars: dict[str, Value]

    def get_attr(
        self, attr: str, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> ExpressionResult:
        try:
            return self.vars[attr]
        except KeyError:
            return BLError(cast(
                Instance, ModuleVarNotFoundException.new([], interpreter, meta)
            ))

    def dump(self, interpreter: "ASTInterpreter", meta: Meta | None) -> String:
        return String(f"<module '{self.name}'>")


# Module errors
ModuleVarNotFoundException = Class(
    String("ModuleVarNotFoundException"), ExceptionClass
)
