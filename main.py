import sys
import logging

import bl_init
import info
import intr_classes
from ast_parser import ast_compile, ast_compile_expr


state = bl_init.state


def interpret(src, state):
    res = ast_compile(src).interp(state)
    if isinstance(res, intr_classes.Throw):
        raise RuntimeError(f'unhandled throw: {res}')

def interpret_expr(src, state):
    res = ast_compile_expr(src).interp(state)
    if isinstance(res, intr_classes.Throw):
        print(f'unhandled throw: {res}')
    return res


def main(args):
    if len(args) > 2:
        print('Usage: main.py [file]')
    elif len(args) == 2:
        file = args[1]
        with open(file, encoding='utf-8') as f:
            string = f.read()
        interpret(string, state)
    else:
        logging.basicConfig(format='%(levelname)s: %(message)s')
        print(info.ABOUT)
        print()
        while True:
            inpt = input('> ')
            try:
                try:
                    ast = ast_compile(inpt)
                except Exception as e:
                    print(interpret_expr(inpt, state).code_repr())
                else:
                    ast.interp(state)
            except Exception as e:
                logging.error(e)

if __name__ == '__main__':
    main(sys.argv)
