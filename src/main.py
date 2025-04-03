"""baba-lang

Yet another programming language, made in Python. Has nothing to do with the
video game "Baba is You".
"""


import importlib.util
import logging
import os
import sys
from argparse import ArgumentParser

from lark.exceptions import UnexpectedInput
from lark.tree import Meta

from interpreter import (
    ASTInterpreter, BLError, Result, Value, Call, Script
)
from static_checker import StaticChecker, StaticError

if importlib.util.find_spec('readline'):
    # pylint: disable = import-error, unused-import
    import readline  # noqa: F401


PROG = 'baba-lang'
VERSION = '0.5.1-testing'
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
    '-r', '--result',
    help='Print result',
    action='store_true',
)


default_interp = ASTInterpreter()
default_static_checker = StaticChecker()


def interpret(
    src: str, interpreter: ASTInterpreter = default_interp
) -> Result:
    """Interpret a script"""
    return interpreter.run_src(src)


def get_context(meta: Meta, text: str, span: int = 40) -> str:
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
    before = text[start:pos].rsplit('\n', 1)[-1]
    after = text[pos:end].split('\n', 1)[0]
    return (
        before + after + '\n' + ' ' * len(before.expandtabs()) +
        '^\n'
    )


def handle_runtime_errors(
    interpreter: ASTInterpreter, result: Result
) -> None:
    """Print runtime errors nicely"""
    match result:
        case BLError(value=value, meta=meta, path=path):
            match meta:
                case Meta(line=line, column=column):
                    print(f'Runtime error at line {line}, col {column}:')
                    print(value.dump(interpreter, meta).value)
                    print()
                    if path is not None:
                        with open(path, encoding='utf-8') as f:
                            path_src = f.read()
                        print(get_context(meta, path_src))
                case None:
                    print('Error:')
                    print(value.dump(interpreter, meta).value)
            print('Traceback:')
            print()
            for i, frame in enumerate(interpreter.traceback[1:], 1):
                match frame:
                    case Call(path=path, meta=meta):
                        pass
                    case Script(meta=meta):
                        prev_frame = interpreter.traceback[i-1]
                        path = (
                            prev_frame.path if prev_frame.path is not None
                            else None
                        )
                line = meta.line if meta is not None else 0
                column = meta.column if meta is not None else 0
                print(
                    f"At {path if path is not None else "<none>"}, " +
                    f"line {line}, col {column}:"
                )
                print()
                if path is not None:
                    with open(path, encoding='utf-8') as f:
                        path_src = f.read()
                    if meta is not None:
                        print(get_context(meta, path_src))


def interp_with_error_handling(
    src: str,
    interpreter: ASTInterpreter | None = None,
) -> Result | UnexpectedInput | StaticError:
    """Interpret with error handling"""
    try:
        if interpreter is None:
            interpreter = default_interp
        res = interpret(src, interpreter)
    except UnexpectedInput as e:
        print('Syntax error:')
        print()
        print(e.get_context(src))
        print(e)
        return e
    except StaticError as e:
        print(e)
        print()
        print(e.get_context(src))
        return e
    handle_runtime_errors(interpreter, res)
    return res


def main() -> int:
    """Main function"""
    args = argparser.parse_args()
    if args.path is None:
        return main_interactive()
    path = os.path.abspath(args.path)
    src_stream = open(path, encoding='utf-8')
    with src_stream:
        src = src_stream.read()
    interpreter = ASTInterpreter(path)
    res = interp_with_error_handling(src, interpreter)
    match res:
        case UnexpectedInput() | StaticError() | BLError():
            return 1
        case Value():
            if args.result:
                print(res.dump(interpreter, None).value)
    return 0


def main_interactive() -> int:
    """Interactive main function"""
    logging.basicConfig()
    print(VERSION_STRING % {'prog': PROG}, "REPL")
    print("Press Ctrl-C to terminate the current line")
    print("Send EOF (Ctrl-Z on Windows, Ctrl-D on Linux) to exit the REPL")
    while True:
        try:
            input_ = input('> ')
            res = interp_with_error_handling(input_, default_interp)
            match res:
                case Value():
                    print(res.dump(default_interp, None).value)
        except KeyboardInterrupt:
            print()
            logging.debug("ctrl-C is pressed")
        except EOFError:
            logging.debug("EOF is sent")
            return 0


if __name__ == '__main__':
    sys.exit(main())
