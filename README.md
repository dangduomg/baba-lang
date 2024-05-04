# baba-lang

Yet another programming language, made in Python. Has nothing to do with the video game "Baba is You".

Right now in version `0.3.2`.

## Notes

- baba-lang is now in its `0.x` versions. This means that later versions of baba-lang is not guaranteed to be backward compatible with the previous ones.
- baba-lang is written for educational purposes only; it is not meant to be used in production.

## How to use
1. Prerequisites: Python 3, Lark
2. Download the repository
3. Run `main.py` without arguments to open an interactive prompt. To run a source file, enter `main.py <file>`. Source files are of extension `.bl`

## Features
- First-class functions
- Operators: `==`, `!=`, `<`, `<=`, `>`, `>=`, `+`, `-`, `*`, `/`, `%/%`, `%`, `**`, `&`, `|`, `^`, `<<`, `>>`, `~`, unary `+`, unary `-`, function call, subscripting
- In-place operators: `=`, `+=`, `-=`, `*=`, `/=`, `%=`, `%/%=`, `**=`, `&=`, `|=`, `^=`, `<<=`, `>>=`
- Control flow constructs: `if`, `while`, `do..while`, C-style `for`, `break`, `continue`, functions
- Data types: integers, floats, strings, booleans, lists, dictionaries
- Python interop with `py_function`

## To-do list
- Logical operators
- Rest and keyword arguments
- OOP
- Exceptions
- Modules
