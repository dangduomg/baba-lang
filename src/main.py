"""baba-lang

Yet another programming language, made in Python. Has nothing to do with the
video game "Baba is You".
"""


import importlib.util
import logging
import os
import sys
from argparse import ArgumentParser
from collections.abc import Callable

from lark.exceptions import UnexpectedInput
from lark.tree import Meta

from bl_ast import parse_expr_to_ast, parse_to_ast
from interpreter import (
    ASTInterpreter, BLError, ExpressionResult, Result, Value
)
from static_checker import StaticChecker, StaticError

if importlib.util.find_spec('readline'):
    # pylint: disable = import-error, unused-import
    import readline  # noqa: F401


PROG = 'baba-lang'
VERSION = '0.4.4-beta'
VERSION_STRING = f'%(prog)s {VERSION}'


argparser = ArgumentParser(prog=PROG)
argparser.add_argument(
    'path',
    nargs='?',
)
argparser.add_argument(
    '-v', '--version',
    action='version',
    version=VERSION_STRING,
)
argparser.add_argument(
    '-e', '--expression',
    help='Evaluate an expression',
    action='store_true',
)


default_interp = ASTInterpreter()
default_static_checker = StaticChecker()


def interpret(
    src: str, interpreter: ASTInterpreter = default_interp
) -> Result:
    """Interpret a script"""
    ast_ = parse_to_ast(src)
    default_static_checker.visit(ast_)
    return interpreter.visit(ast_)


def interpret_expr(
        src: str, interpreter: ASTInterpreter = default_interp
) -> ExpressionResult:
    """Interpret an expression"""
    ast_ = parse_expr_to_ast(src)
    default_static_checker.visit(ast_)
    return interpreter.visit_expr(ast_)


def get_context(meta: Meta, text: str | bytes, span: int = 40) -> str:
    """Returns a pretty string pinpointing the error in the text,
    with span amount of context characters around it.

    Note:
        The parser doesn't hold a copy of the text it has to parse,
        so you have to provide it again
    """
    # stolen from Lark
    pos = meta.start_pos
    start = max(pos - span, 0)
    end = pos + span
    if isinstance(text, str):
        before = text[start:pos].rsplit('\n', 1)[-1]
        after = text[pos:end].split('\n', 1)[0]
        return (
            before + after + '\n' + ' ' * len(before.expandtabs()) +
            '^\n'
        )
    text = bytes(text)
    before = text[start:pos].rsplit(b'\n', 1)[-1]
    after = text[pos:end].split(b'\n', 1)[0]
    return (
        (before + after + b'\n' + b' ' * len(before.expandtabs()) +
            b'^\n').decode("ascii", "backslashreplace")
    )


def handle_runtime_errors(
    interpreter: ASTInterpreter, src: str, error: BLError
) -> None:
    """Print runtime errors nicely"""
    match error:
        case BLError(value=msg, meta=meta):
            match meta:
                case Meta(line=line, column=column):
                    print(f'Runtime error at line {line}, column {column}:')
                    print(msg)
                    print()
                    print(get_context(meta, src))
                case None:
                    print('Error:')
                    print(msg)
            print('Traceback:')
            for call in interpreter.calls:
                print(f'At line {call.meta.line}, column {call.meta.column}:')
                print(get_context(call.meta, src))


def interp_with_error_handling(
    interp_func: Callable,
    src: str,
    interpreter: ASTInterpreter | None = None,
) -> ExpressionResult | UnexpectedInput | StaticError:
    """Interpret with error handling"""
    try:
        if interpreter is None:
            res = interp_func(src)
        else:
            res = interp_func(src, interpreter)
    except UnexpectedInput as e:
        print('Syntax error:')
        print()
        print(e.get_context(src))
        print(e)
        return e
    except StaticError as e:
        print(e)
        print()
        print(e.get_context(src))
        return e
    handle_runtime_errors(interpreter, src, res)
    return res


def main() -> int:
    """Main function"""
    args = argparser.parse_args()
    if args.path is None:
        return main_interactive()
    path = os.path.abspath(args.path)
    src_stream = open(args.path, encoding='utf-8')
    with src_stream:
        src = src_stream.read()
    if args.expression:
        interp_func = interpret_expr
    else:
        interp_func = interpret
    res = interp_with_error_handling(
        interp_func, src, ASTInterpreter(path)
    )
    match res:
        case UnexpectedInput() | BLError():
            return 1
        case Value():
            if args.expression:
                print(res.dump(None).value)
    return 0


def main_interactive() -> int:
    """Interactive main function"""
    logging.basicConfig()
    print(VERSION_STRING % {'prog': PROG}, "REPL")
    print("Press Ctrl-C to terminate the current line")
    print("Send EOF (Ctrl-Z on Windows, Ctrl-D on Linux) to exit the REPL")
    while True:
        try:
            input_ = input('> ')
            try:
                match res := interpret_expr(input_):
                    case Value():
                        print(res.dump(None).value)
                    case BLError():
                        handle_runtime_errors(default_interp, input_, res)
            except UnexpectedInput:
                interp_with_error_handling(interpret, input_, default_interp)
        except KeyboardInterrupt:
            print()
            logging.debug("ctrl-C is pressed")
        except EOFError:
            logging.debug("EOF is sent")
            return 0


if __name__ == '__main__':
    sys.exit(main())
