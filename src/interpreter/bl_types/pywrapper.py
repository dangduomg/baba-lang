"""Convenient python wrapper for baba-lang"""


from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
from importlib import import_module

from lark.tree import Meta

from .essentials import (
    ExpressionResult, PythonFunction, Value, BLError, cast_to_instance,
    NotImplementedException, String, Bool, BOOLS, Null, NULL, PythonValue,
)
from .numbers import Int, Float
from .colls import BLList, BLDict

if TYPE_CHECKING:
    from .essentials import Instance
    from ..main import ASTInterpreter


@dataclass
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
                ConvenientPythonWrapper.unwrap_arg(a) for a in args
            ]
        except ValueError:
            return BLError(cast_to_instance(
                NotImplementedException.new([], interpreter, meta)
            ), meta, interpreter.path)
        return ConvenientPythonWrapper.wrap_res(
            self.function(*unwrapped_args)
        )

    @staticmethod
    def unwrap_arg(
        arg: Value
    ) -> int | float | str | bool | list | dict | None:
        """Unwrap argument for use with Python"""
        uw = ConvenientPythonWrapper.unwrap_arg
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
    def wrap_res(res: Any) -> Value:
        """Re-wrap the result for baba-lang"""
        # pylint: disable=too-many-return-statements
        w = ConvenientPythonWrapper.wrap_res
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
        if isinstance(res, (tuple, list, set, frozenset)):
            return BLList([w(e) for e in res])
        if isinstance(res, dict):
            return BLDict({w(k): w(res[k]) for k in res})
        if callable(res):
            return ConvenientPythonWrapper(res)
        return PythonValue(res)


def py_function(
    meta: Meta | None, interpreter: "ASTInterpreter", /,
    this: "Instance | None", module: String, name: String, *_
) -> ConvenientPythonWrapper:
    """Function to get a Python function from baba-lang"""
    # pylint: disable=unused-argument
    return ConvenientPythonWrapper(
        getattr(import_module(module.value), name.value)
    )


def py_method(
    meta: Meta | None, interpreter: "ASTInterpreter", /,
    this: "Instance | None", module: String, class_: String, name: String, *_
) -> ConvenientPythonWrapper:
    """Function to get a Python method from baba-lang"""
    # pylint: disable=unused-argument
    return ConvenientPythonWrapper(
        getattr(
            getattr(import_module(module.value), class_.value),
            name.value,
        )
    )


def py_constant(
    meta: Meta | None, interpreter: "ASTInterpreter", /,
    this: "Instance | None", module: String, name: String, *_
) -> Value:
    """Function to get a Python constant to baba-lang"""
    # pylint: disable=unused-argument
    return ConvenientPythonWrapper.wrap_res(
        getattr(import_module(module.value), name.value)
    )
