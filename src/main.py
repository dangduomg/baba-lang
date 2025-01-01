"""baba-lang

Yet another programming language, made in Python. Has nothing to do with the
video game "Baba is You".
"""


import importlib.util
import logging
import os
import sys
from argparse import ArgumentParser
from lark.tree import Meta

from bl_ast import parse_expr_to_ast, parse_to_ast
from interpreter import ASTInterpreter, ExpressionResult, Result
from static_checker import StaticChecker

if importlib.util.find_spec('readline'):
    # pylint: disable = import-error, unused-import
    import readline  # noqa: F401


PROG = 'mini-baba-lang'
VERSION = '0.5.0'
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
    raw_ast = parse_to_ast(src)
    ast_ = default_static_checker.visit(raw_ast)
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
        before + after + b'\n' + b' ' * len(before.expandtabs()) + b'^\n'
    ).decode("ascii", "backslashreplace")


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
    interpreter = ASTInterpreter(path)
    interp_func(src, interpreter)
    return 0


def main_interactive() -> int:
    """Interactive main function"""
    logging.basicConfig()
    print(VERSION_STRING % {'prog': PROG}, "REPL")
    print("Press Ctrl-C to terminate the current line")
    print("Send EOF (Ctrl-Z on Windows, Ctrl-D on Linux) to exit the REPL")
    while True:
        input_ = input('> ')
        res = interpret_expr(input_)
        print(res)


if __name__ == '__main__':
    sys.exit(main())
