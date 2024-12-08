"""baba-lang

Yet another programming language, made in Python. Has nothing to do with the
video game "Baba is You".
"""


import sys
import logging
from argparse import ArgumentParser

import info


argparser = ArgumentParser()
argparser.add_argument('filename')


def interpret(src: str, state):
    print('TODO')


def interpret_expr(src: str, state):
    print('TODO')


def main(args: list[str]) -> None:
    print('TODO')

if __name__ == '__main__':
    main(sys.argv)
