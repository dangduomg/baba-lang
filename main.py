import sys
from ast_parser import ast_compile

from state import State


state_ = State()

def interpret(src):
    return ast_compile(src).interp(state_)


def main(args):
    if len(args) > 1:
        file = args[1]
        with open(file, encoding='utf-8') as f:
            string = f.read()
        interpret(string)
    else:
        while True:
            inpt = input('> ')
            interpret(inpt)

if __name__ == '__main__':
    main(sys.argv)