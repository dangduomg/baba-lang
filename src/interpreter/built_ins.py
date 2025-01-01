"""Built-in functions"""

from typing import Optional, TYPE_CHECKING, cast

from lark.tree import Meta

from .bl_types.essentials import BLError, IncorrectTypeException
from .bl_types import Value, Int, Float, String, Null, NULL, Instance

if TYPE_CHECKING:
    from .main import ASTInterpreter


def print_(
    meta: Optional[Meta], interpreter: "ASTInterpreter", /, *args: Value
) -> Null:
    """Print objects"""
    # pylint: disable=unused-argument
    print(*(arg.dump(interpreter, meta).value for arg in args))
    return NULL


def input_(
    meta: Optional[Meta], interpreter: "ASTInterpreter", /, *args: Value
) -> String:
    """Prompt for user input"""
    # pylint: disable=unused-argument
    return String(
        input(args[0].dump(interpreter, meta).value if args else "")
    )


def int_(
    meta: Optional[Meta], interpreter: "ASTInterpreter", /, arg: Value, *_
) -> Int | BLError:
    """Convert to integer"""
    # pylint: disable=unused-argument
    match arg:
        case String(value=value) | Float(value=value):
            return Int(int(value))
        case Int():
            return arg
    return BLError(cast(
        Instance, IncorrectTypeException.new([], interpreter, meta)
    ))


def float_(
    meta: Optional[Meta], interpreter: "ASTInterpreter", /, arg: Value, *_
) -> Float | BLError:
    """Convert to float"""
    # pylint: disable=unused-argument
    match arg:
        case String(value=value) | Int(value=value):
            return Float(float(value))
        case Float():
            return arg
    return BLError(cast(
        Instance, IncorrectTypeException.new([], interpreter, meta)
    ))


def dump(
    meta: Optional[Meta], interpreter: "ASTInterpreter", /, arg: Value, *_
) -> String | BLError:
    """Convert to string"""
    # pylint: disable=unused-argument
    return arg.dump(interpreter, meta)
