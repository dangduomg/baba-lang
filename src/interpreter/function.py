"""baba-lang function type"""

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, Protocol, TYPE_CHECKING, runtime_checkable
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
)
from .errors import (
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

    def call(
        self, args: list[Value], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
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

    def call(
        self, args: list[Value], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        # pylint: disable=too-many-return-statements
        try:
            unwrapped_args = [
                ConvenientPythonWrapper._unwrap_arg(a) for a in args
            ]
        except ValueError:
            return error_not_implemented.set_meta(meta)
        return ConvenientPythonWrapper._wrap_res(
            self.function(*unwrapped_args)
        )

    @staticmethod
    def _unwrap_arg(
        arg: Value
    ) -> int | float | str | bool | list | dict | None:
        """Unwrap argument for use with Python"""
        uw = ConvenientPythonWrapper._unwrap_arg
        match arg:
            case (
                Int(value=value) | Float(value=value) | Bool(value=value)
                | String(value=value)
            ):
                return value
            case Null():
                return None
            case BLList(elems=elems):
                return [uw(e) for e in elems]
            case BLDict(content=content):
                return {uw(k): uw(content[k]) for k in content}
        raise ValueError

    @staticmethod
    def _wrap_res(res: Any) -> Value:
        """Re-wrap the result for baba-lang"""
        # pylint: disable=too-many-return-statements
        w = ConvenientPythonWrapper._wrap_res
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
            return BLList([w(e) for e in res])
        if isinstance(res, dict):
            return BLDict({w(k): w(res[k]) for k in res})
        if callable(res):
            return ConvenientPythonWrapper(res)
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


def py_method(
    meta: Optional[Meta],
    interpreter: "ASTInterpreter",
    /,
    module: String,
    class_: String,
    name: String,
    *_
) -> ConvenientPythonWrapper:
    """Function to get a Python method from baba-lang"""
    # pylint: disable=unused-argument
    return ConvenientPythonWrapper(
        getattr(
            getattr(import_module(module.value), class_.value),
            name.value,
        )
    )


@runtime_checkable
class SupportsBLCall(Protocol):
    """Protocol for functions that support being called in baba-lang"""

    # pylint: disable=too-few-public-methods
    # pylint: disable=missing-function-docstring

    @abstractmethod
    def call(
        self, args: list["Value"], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult": ...


@dataclass(frozen=True)
class Call:
    """Call site type for tracebacks"""
    function: SupportsBLCall
    meta: Meta
