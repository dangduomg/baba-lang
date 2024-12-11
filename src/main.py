"""baba-lang

Yet another programming language, made in Python. Has nothing to do with the
video game "Baba is You".
"""


import sys
from argparse import ArgumentParser

from bl_ast import parse_to_ast, expr_parser
from interpreter import ASTInterpreter
from interpreter.base import Result, ExpressionResult


argparser = ArgumentParser()
argparser.add_argument(
    'filename',
    nargs='?',
)


default_interp = ASTInterpreter()


def interpret(src: str, state):
    raise NotImplementedError('TODO')


def interpret_expr(src: str, interpreter: ASTInterpreter = default_interp) -> Result:
    return interpreter.visit(parse_to_ast(src, expr_parser))


def main() -> None:
    args = argparser.parse_args()
    if args.filename is None:
        src_stream = sys.stdin
    else:
        src_stream = open(args.filename, encoding='utf-8')
    with src_stream:
        src = src_stream.read()
    print(interpret_expr(src))

if __name__ == '__main__':
    main()
