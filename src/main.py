"""baba-lang

Yet another programming language, made in Python. Has nothing to do with the
video game "Baba is You".
"""


import os
import sys
from typing import Optional
from collections.abc import Callable
from argparse import ArgumentParser

from lark.exceptions import UnexpectedInput
from lark.tree import Meta

from bl_ast import parse_to_ast, parse_expr_to_ast
from interpreter import ASTInterpreter, Result, ExpressionResult, BLError, \
                        Value


PROG = 'baba-lang'
VERSION = '0.4.0'
VERSION_STRING = f'%(prog)s {VERSION}'


argparser = ArgumentParser(prog=PROG)
argparser.add_argument(
    'path',
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


def interpret(src: str, interpreter: ASTInterpreter = default_interp
              ) -> Result:
    """Interpret a script"""
    return interpreter.visit(parse_to_ast(src))


def interpret_expr(src: str, interpreter: ASTInterpreter = default_interp
                   ) -> ExpressionResult:
    """Interpret an expression"""
    return interpreter.visit_expr(parse_expr_to_ast(src))


def handle_errors(error: BLError) -> None:
    """Print errors nicely"""
    match error:
        case BLError(value=msg, meta=meta):
            match meta:
                case Meta(line=line, column=column):
                    print(
                        f'Runtime error at line {line}, column {column}:',
                        msg,
                        sep='\n',
                    )
                case None:
                    print('Error:')
                    print(msg)


def interp_with_error_handling(
    interp_func: Callable,
    src: str,
    interpreter: Optional[ASTInterpreter] = None,
) -> ExpressionResult | UnexpectedInput:
    """Interpret with error handling"""
    try:
        if interpreter is None:
            res = interp_func(src)
        else:
            res = interp_func(src, interpreter)
    except UnexpectedInput as e:
        print('%s', 'Syntax error:')
        print()
        print(e.get_context(src))
        print(e)
        return e
    handle_errors(res)
    return res


def main() -> int:
    """Main function"""
    args = argparser.parse_args()
    if args.interactive:
        return main_interactive()
    if args.path is None:
        path = ''
        src_stream = sys.stdin
    else:
        path = os.path.abspath(args.path)
        src_stream = open(args.path, encoding='utf-8')
    with src_stream:
        src = src_stream.read()
    if args.expression:
        interp_func = interpret_expr
    else:
        interp_func = interpret
    match res := interp_with_error_handling(
        interp_func,
        src,
        ASTInterpreter(path)
    ):
        case UnexpectedInput() | BLError():
            return 1
        case Value():
            if args.expression:
                print(res.dump(None).value)
    return 0


def main_interactive() -> int:
    """Interactive main function"""
    print(VERSION_STRING % {'prog': PROG})
    while True:
        try:
            input_ = input('> ')
            try:
                match res := interpret_expr(input_):
                    case Value():
                        print(res.dump(None).value)
                    case BLError():
                        handle_errors(res)
            except UnexpectedInput:
                interp_with_error_handling(interpret, input_, default_interp)
        except KeyboardInterrupt:
            print()
        except EOFError:
            return 0


if __name__ == '__main__':
    sys.exit(main())
