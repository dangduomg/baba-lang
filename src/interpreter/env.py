"""Interpreter environment"""


from dataclasses import dataclass
from typing import Optional

from lark.tree import Meta

from .types.base import ExpressionResult, BLError
from .types.errors import error_var_nonexistent
from .types import Value


@dataclass
class Var:
    """Interpreter mutable binding"""

    value: Value


class Env:
    """Interpreter environment"""

    vars: dict[str, Var]
    parent: Optional['Env']

    def __init__(self, vars_: Optional[dict[str, Var]] = None,
                 parent: Optional['Env'] = None):
        if vars_ is None:
            self.vars = {}
        else:
            self.vars = vars_
        self.parent = parent

    def new_var(self, name: str, value: Value) -> None:
        """Set a new/existing variable"""
        self.vars[name] = Var(value)

    def get_var(self, name: str, meta: Optional[Meta]) -> ExpressionResult:
        """Retrieve the value of a variable"""
        resolve_result = self.resolve_var(name, meta)
        match resolve_result:
            case Var(value=value):
                return value
            case BLError():
                return resolve_result

    def set_var(self, name: str, value: Value, meta: Optional[Meta]
                ) -> Optional[BLError]:
        """Assign to an existing variable name"""
        resolve_result = self.resolve_var(name, meta)
        match resolve_result:
            case Var():
                resolve_result.value = value
            case BLError():
                return resolve_result

    def resolve_var(self, name: str, meta: Optional[Meta]) -> Var | BLError:
        """Resolve a variable name"""
        if name in self.vars:
            return self.vars[name]
        if self.parent is not None:
            return self.parent.resolve_var(name, meta)
        return error_var_nonexistent.fill_args(name).set_meta(meta)

    def copy(self) -> 'Env':
        """Copy the environment (for capturing variables in closures)"""
        return Env(self.vars.copy(), self.parent)
