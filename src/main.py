"""baba-lang

Yet another programming language, made in Python. Has nothing to do with the
video game "Baba is You".
"""


import sys
from argparse import ArgumentParser

from lark.tree import Meta

from bl_ast import parse_to_ast, expr_parser
from interpreter import ASTInterpreter, Result, BLError


VERSION = '0.4.0'
VERSION_STRING = f'%(prog)s {VERSION}'


argparser = ArgumentParser(prog='baba-lang')
argparser.add_argument(
    'filename',
    nargs='?',
)
argparser.add_argument(
    '-v', '--version',
    dest='show version',
    action='version',
    version=VERSION_STRING,
)
argparser.add_argument(
    '-e', '--expression',
    action='store_true',
)
argparser.add_argument(
    '-i', '--interactive',
    action='store_true',
)


default_interp = ASTInterpreter()


def interpret(src: str, interpreter: ASTInterpreter = default_interp) -> Result:
    """Interpret a script"""
    return interpreter.visit(parse_to_ast(src))


def interpret_expr(src: str, interpreter: ASTInterpreter = default_interp) -> Result:
    """Interpret an expression"""
    return interpreter.visit(parse_to_ast(src, expr_parser))

def main() -> None:
    """Main function"""
    args = argparser.parse_args()
    if args.filename is None:
        src_stream = sys.stdin
    else:
        src_stream = open(args.filename, encoding='utf-8')
    with src_stream:
        src = src_stream.read()
    if args.expression:
        res = interpret_expr(src)
    else:
        res = interpret(src)
    match res:
        case BLError(value=msg, meta=meta):
            match meta:
                case Meta(line=line, column=column):
                    raise RuntimeError(f'Error at line {line}, column {column}: {msg}')
                case None:
                    raise RuntimeError(f'Error: {msg}')

if __name__ == '__main__':
    main()
