"""baba-lang

Yet another programming language, made in Python. Has nothing to do with the
video game "Baba is You".
"""


import sys
import logging
from argparse import ArgumentParser

import info


def interpret(src: str, state):
    print('TODO')


def interpret_expr(src: str, state):
    print('TODO')


def main(args: list[str]) -> None:
    if len(args) > 2:
        print('Usage: main.py [file]')
    elif len(args) == 2:
        file = args[1]
        with open(file, encoding='utf-8') as f:
            string = f.read()
        interpret(string, None)
    else:
        logging.basicConfig(format='%(levelname)s: %(message)s')
        print(info.ABOUT)
        print()
        while True:
            inpt = input('> ')
            try:
                print('TODO')
            except Exception as e:
                logging.error(e)

if __name__ == '__main__':
    main(sys.argv)
