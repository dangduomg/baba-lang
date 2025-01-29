"""Built-in functions"""

import sys
from typing import TYPE_CHECKING

from lark.tree import Meta

from .bl_types.essentials import (
    Value, BLError, String, Bool, Null, NULL, Instance,
    IncorrectTypeException, cast_to_instance,
)
from .bl_types.numbers import Int, Float

if TYPE_CHECKING:
    from .main import ASTInterpreter


def print_(
    meta: Meta | None, interpreter: "ASTInterpreter", this: Instance | None,
    /, *args: Value
) -> Null:
    """Print objects"""
    # pylint: disable=unused-argument
    print(*(arg.to_string(interpreter, meta).value for arg in args))
    return NULL


def printf(
    meta: Meta | None, interpreter: "ASTInterpreter", this: Instance | None,
    /, fmt: String, *args: Value
) -> Null:
    """Print formatted string, following Python old-style string formatting"""
    # pylint: disable=unused-argument
    converted_args = tuple(
        arg.to_string(interpreter, meta).value for arg in args
    )
    print(fmt.value % converted_args, end="")
    return NULL


def input_(
    meta: Meta | None, interpreter: "ASTInterpreter", this: Instance | None,
    /, *args: Value
) -> String:
    """Prompt for user input"""
    # pylint: disable=unused-argument
    return String(
        input(args[0].to_string(interpreter, meta).value if args else "")
    )


def to_int(
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
    ), meta, interpreter.path)


def to_float(
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
    ), meta, interpreter.path)


def to_bool(
    meta: Meta | None, interpreter: "ASTInterpreter", this: Instance | None,
    /, arg: Value, *_
) -> Bool | BLError:
    """Convert to boolean"""
    # pylint: disable=unused-argument
    return arg.to_bool(interpreter, meta)


def dump(
    meta: Meta | None, interpreter: "ASTInterpreter", this: Instance | None,
    /, arg: Value, *_
) -> String | BLError:
    """Dump an argument"""
    # pylint: disable=unused-argument
    return arg.dump(interpreter, meta)


def to_string(
    meta: Meta | None, interpreter: "ASTInterpreter", this: Instance | None,
    /, arg: Value, *_
) -> String | BLError:
    """Convert to string"""
    # pylint: disable=unused-argument
    return arg.to_string(interpreter, meta)


def exit_(
    meta: Meta | None, interpreter: "ASTInterpreter", this: Instance | None,
    /, arg: Value, *_
) -> Null | BLError:
    """Exit the program"""
    # pylint: disable=unused-argument
    match arg:
        case Int(value=value):
            sys.exit(value)
            return NULL  # pylint: disable=unreachable
    return BLError(cast_to_instance(
        IncorrectTypeException.new([], interpreter, meta)
    ), meta, interpreter.path)
