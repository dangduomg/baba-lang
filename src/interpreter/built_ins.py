"""Built-in functions"""

from typing import Optional, TYPE_CHECKING

from lark.tree import Meta

from .bl_types.base import BLError
from .bl_types.errors import error_not_implemented
from .bl_types import Value, Int, Float, Bool, String, Null, NULL

if TYPE_CHECKING:
    from .main import ASTInterpreter


def print_(
    meta: Optional[Meta], interpreter: "ASTInterpreter", /, *args: Value
) -> Null:
    """Print objects"""
    # pylint: disable=unused-argument
    print(*(arg.to_string(interpreter, meta).value for arg in args))
    return NULL


def print_dump(
    meta: Optional[Meta], interpreter: "ASTInterpreter", /, *args: Value
) -> Null:
    """'Dump' (print detailed, debug-friendly representation) objects"""
    # pylint: disable=unused-argument
    print(*(arg.dump(interpreter, meta) for arg in args))
    return NULL


def input_(
    meta: Optional[Meta], interpreter: "ASTInterpreter", /, *args: Value
) -> String:
    """Prompt for user input"""
    # pylint: disable=unused-argument
    return String(
        input(args[0].to_string(interpreter, meta).value if args else "")
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
    return error_not_implemented.copy().set_meta(meta)


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
    return error_not_implemented.copy().set_meta(meta)


def bool_(
    meta: Optional[Meta], interpreter: "ASTInterpreter", /, arg: Value, *_
) -> Bool | BLError:
    """Convert to boolean"""
    # pylint: disable=unused-argument
    return arg.to_bool(interpreter, meta)


def str_(
    meta: Optional[Meta], interpreter: "ASTInterpreter", /, arg: Value, *_
) -> String | BLError:
    """Convert to string"""
    # pylint: disable=unused-argument
    return arg.to_string(interpreter, meta)
