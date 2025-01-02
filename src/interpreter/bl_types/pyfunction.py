"""baba-lang function type"""


from dataclasses import dataclass
from typing import TYPE_CHECKING

from lark.tree import Meta

from .essentials import ExpressionResult, Value, String

if TYPE_CHECKING:
    from .abc_protocols import SupportsWrappedByPythonFunction
    from ..main import ASTInterpreter


@dataclass(frozen=True)
class PythonFunction(Value):
    """Python function wrapper type"""

    function: "SupportsWrappedByPythonFunction"

    def call(
        self, args: list[Value], interpreter: "ASTInterpreter",
        meta: Meta | None
    ) -> ExpressionResult:
        return self.function(meta, interpreter, *args)

    def dump(
        self, interpreter: "ASTInterpreter", meta: Meta | None
    ) -> String:
        return String(f"<python function {self.function!r}>")
