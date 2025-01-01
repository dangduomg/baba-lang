"""baba-lang function type"""

from abc import abstractmethod
from dataclasses import dataclass
from typing import Optional, Protocol, TYPE_CHECKING

from lark.tree import Meta

from .essentials import ExpressionResult, Value, String

if TYPE_CHECKING:
    from ..main import ASTInterpreter


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

    def dump(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> String:
        return String(f"<python function {self.function!r}>")
