"""Built-in functions"""

from typing import TYPE_CHECKING

from lark.tree import Meta

from .bl_types import (
    Value, BLError, Int, Float, String, Null, NULL, Instance,
    IncorrectTypeException, cast_to_instance,
)

if TYPE_CHECKING:
    from .main import ASTInterpreter


def print_(
    meta: Meta | None, interpreter: "ASTInterpreter", this: Instance | None,
    /, *args: Value
) -> Null:
    """Print objects"""
    # pylint: disable=unused-argument
    print(*(arg.dump(interpreter, meta).value for arg in args))
    return NULL


def input_(
    meta: Meta | None, interpreter: "ASTInterpreter", this: Instance | None,
    /, *args: Value
) -> String:
    """Prompt for user input"""
    # pylint: disable=unused-argument
    return String(
        input(args[0].dump(interpreter, meta).value if args else "")
    )


def int_(
    meta: Meta | None, interpreter: "ASTInterpreter", this: Instance | None,
    /, arg: Value, *_
) -> Int | BLError:
    """Convert to integer"""
    # pylint: disable=unused-argument
    match arg:
        case String(value=value) | Float(value=value):
            return Int(int(value))
        case Int():
            return arg
    return BLError(cast_to_instance(
        IncorrectTypeException.new([], interpreter, meta)
    ), meta)


def float_(
    meta: Meta | None, interpreter: "ASTInterpreter", this: Instance | None,
    /, arg: Value, *_
) -> Float | BLError:
    """Convert to float"""
    # pylint: disable=unused-argument
    match arg:
        case String(value=value) | Int(value=value):
            return Float(float(value))
        case Float():
            return arg
    return BLError(cast_to_instance(
        IncorrectTypeException.new([], interpreter, meta)
    ), meta)


def dump(
    meta: Meta | None, interpreter: "ASTInterpreter", this: Instance | None,
    /, arg: Value, *_
) -> String | BLError:
    """Convert to string"""
    # pylint: disable=unused-argument
    return arg.dump(interpreter, meta)
