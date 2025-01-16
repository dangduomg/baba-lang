"""Useful ABCs and protocols for the interpreter"""


from abc import ABC, abstractmethod
from typing import Protocol, TYPE_CHECKING, runtime_checkable

from lark.tree import Meta

if TYPE_CHECKING:
    from .essentials import ExpressionResult, Value, Instance
    from ..main import ASTInterpreter


# pylint: disable=too-few-public-methods


class Result(ABC):
    """Interpreter result base class"""


class Exit(Result, ABC):
    """Object signaling early exit"""


@runtime_checkable
class SupportsBLCall(Protocol):
    """Protocol for functions that support being called in baba-lang"""

    # pylint: disable=too-few-public-methods
    # pylint: disable=missing-function-docstring

    this: "Instance | None"

    @abstractmethod
    def call(
        self, args: list["Value"], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> "ExpressionResult": ...

    def bind(self, this: "Instance") -> "SupportsBLCall": ...


class SupportsWrappedByPythonFunction(Protocol):
    """Protocol for functions that support being wrapped by PythonFunction"""

    # pylint: disable=too-few-public-methods

    __name__: str

    @abstractmethod
    def __call__(
        self, meta: Meta | None, interpreter: "ASTInterpreter",
        this: "Instance | None", /, *args
    ) -> "ExpressionResult": ...
