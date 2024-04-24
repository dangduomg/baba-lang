import sys
import logging
from ast_parser import ast_compile

import bl_init
import info


state = bl_init.state


def interpret(src, state):
    return ast_compile(src).interp(state)


def main(args):    
    if len(args) > 1:
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
                interpret(inpt, state)
            except Exception as e:
                logging.error(e)

if __name__ == '__main__':
    main(sys.argv)