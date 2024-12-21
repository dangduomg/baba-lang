"""baba-lang function type"""

from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional, Protocol, TYPE_CHECKING
from collections.abc import Callable
from importlib import import_module

from lark.tree import Meta

from bl_ast.nodes import FormArgs, Body

from .base import (
    ExpressionResult,
    Value,
    Success,
    String,
    Int,
    Float,
    Bool,
    BOOLS,
    Null,
    NULL,
    error_not_implemented,
    error_wrong_argc,
)
from .colls import BLList, BLDict
from .exits import Return
from .env import Env

if TYPE_CHECKING:
    from .main import ASTInterpreter


@dataclass(frozen=True)
class BLFunction(Value):
    """baba-lang function type"""

    name: str
    form_args: FormArgs
    body: Body
    env: Optional[Env] = None

    def call(self, args, interpreter, meta):
        # Create an environment (call frame)
        old_env = interpreter.locals
        env = Env(parent=self.env)
        # Populate it with arguments
        form_args = self.form_args.args
        try:
            for farg, arg in zip(form_args, args, strict=True):
                env.new_var(farg, arg)
        except ValueError:
            return error_wrong_argc.fill_args(self.name, len(form_args)) \
                                   .set_meta(meta)
        # Run the body
        interpreter.locals = env
        res = interpreter.visit_stmt(self.body)
        # Clean it up
        interpreter.locals = old_env
        # Return!
        match res:
            case Success():
                return NULL
            case Return(value=value):
                return value
        return error_not_implemented.set_meta(meta)

    def dump(self, meta):
        return String(f"<function '{self.name}'>")


class SupportsWrappedByPythonFunction(Protocol):
    """Protocol for functions that support being wrapped by PythonFunction"""

    # pylint: disable=too-few-public-methods

    __name__: str

    @abstractmethod
    def __call__(
        self, meta: Optional[Meta], interpreter: "ASTInterpreter", /, *args
    ) -> ExpressionResult: ...


@dataclass(frozen=True)
class PythonFunction(Value):
    """Python function wrapper type"""

    function: SupportsWrappedByPythonFunction

    def call(self, args, interpreter, meta):
        return self.function(meta, interpreter, *args)

    def dump(self, meta):
        return String(f"<python function {self.function!r}>")

    def to_string(self, meta):
        return String(f"<python function '{self.function.__name__}'>")


@dataclass(frozen=True)
class PythonValue(Value):
    """Python value. Returned by calling ConvenientPythonWrapper"""

    value: object


@dataclass(frozen=True)
class ConvenientPythonWrapper(PythonFunction):
    """Convenient wrapper for Python functions to baba-lang"""

    function: Callable

    def call(self, args, interpreter, meta):
        # pylint: disable=too-many-return-statements
        args_to_py = []
        for arg in args:
            match arg:
                case Int(value=value) | Float(value=value) \
                   | Bool(value=value) | String(value=value) \
                   | BLList(elems=value) | BLDict(content=value):
                    args_to_py.append(value)
                case Null():
                    args_to_py.append(None)
                case _:
                    return error_not_implemented.set_meta(meta)
        res = self.function(*args_to_py)
        if isinstance(res, int):
            return Int(res)
        if isinstance(res, float):
            return Float(res)
        if isinstance(res, bool):
            return BOOLS[res]
        if res is None:
            return NULL
        if isinstance(res, str):
            return String(res)
        if isinstance(res, list):
            return BLList(res)
        if isinstance(res, dict):
            return BLDict(res)
        return PythonValue(res)


def py_function(
    meta: Optional[Meta],
    interpreter: "ASTInterpreter",
    /,
    module: String,
    name: String,
    *_
) -> ConvenientPythonWrapper:
    """Function to get a Python function from baba-lang"""
    # pylint: disable=unused-argument
    return ConvenientPythonWrapper(
        getattr(import_module(module.value), name.value)
    )
