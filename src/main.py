"""baba-lang

Yet another programming language, made in Python. Has nothing to do with the
video game "Baba is You".
"""


import sys
import logging
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


logging.basicConfig()


default_interp = ASTInterpreter()


def interpret(src: str, interpreter: ASTInterpreter = default_interp
              ) -> Result:
    """Interpret a script"""
    return interpreter.visit(parse_to_ast(src))


def interpret_expr(src: str, interpreter: ASTInterpreter = default_interp
                   ) -> ExpressionResult:
    """Interpret an expression"""
    return interpreter.visit_expr(parse_expr_to_ast(src))


def main() -> int:
    """Main function"""
    args = argparser.parse_args()
    if args.interactive:
        return main_interactive()
    if args.filename is None:
        src_stream = sys.stdin
    else:
        src_stream = open(args.filename, encoding='utf-8')
    with src_stream:
        src = src_stream.read()
    try:
        if args.expression:
            res = interpret_expr(src)
        else:
            res = interpret(src)
    except UnexpectedInput as e:
        print()
        print(e.get_context(src))  # type: ignore
        print(e)
        return 1
    match res:
        case BLError(value=msg, meta=meta):
            match meta:
                case Meta(line=line, column=column):
                    logging.error(
                        '[line %d, column %d] %s',
                        line, column, msg
                    )
                case None:
                    logging.error('%s', msg)
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
                    case BLError(value=msg):
                        print(f'Error: {msg}')
            except UnexpectedInput:
                pass
            else:
                continue
            match interpret(input_):
                case BLError(value=msg):
                    print(f'Error: {msg}')
        except KeyboardInterrupt:
            print()
        except EOFError:
            return 0
        except UnexpectedInput as e:
            print()
            print(e.get_context(input_))  # type: ignore
            print(e)
            return 1


if __name__ == '__main__':
    sys.exit(main())
