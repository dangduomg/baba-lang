"""Interpreter value classes"""


from typing import Optional, Protocol
from abc import abstractmethod
from dataclasses import dataclass

from lark.tree import Meta

from .base import ExpressionResult, Value, String
from .main import ASTInterpreter

#pylint: disable=unused-import
#ruff: noqa: F401
from .base import Int, Float, Bool, BOOLS, Null, NULL
from .colls import BLList, BLDict
from .function import BLFunction


#pylint: disable=unused-argument


class SupportsWrappedByPythonFunction(Protocol):
    """Protocol for functions that support being wrapped by PythonFunction"""

    #pylint: disable=too-few-public-methods

    __name__: str

    @abstractmethod
    def __call__(self, meta: Optional[Meta], interpreter: ASTInterpreter, /, *args: Value
                 ) -> ExpressionResult:
        ...


@dataclass(frozen=True)
class PythonFunction(Value):
    """Python function wrapper type"""

    function: SupportsWrappedByPythonFunction

    def call(self, args, interpreter, meta):
        return self.function(meta, interpreter, *args)

    def dump(self, meta):
        return String(f'<python function: {self.function!r}>')

    def to_string(self, meta):
        return String(f'<python function: {self.function.__name__}>')
