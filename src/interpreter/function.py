"""baba-lang function type"""

from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional, Protocol, TYPE_CHECKING, runtime_checkable

from lark.tree import Meta

from bl_ast.nodes import FormArgs, Body

from .base import (
    ExpressionResult,
    Value,
    Success,
    String,
    NULL,
)
from .errors import error_not_implemented, error_wrong_argc
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
