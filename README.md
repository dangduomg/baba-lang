# baba-lang

Yet another programming language, made in Python. Has nothing to do with the video game "Baba is You".

Right now in version `0.2.10`.

## How to use
1. Prerequisites: Python 3, Lark
2. Download the repository
3. Run `main.py` without arguments to open an interactive prompt. To run a source file, enter `main.py <file>`.

## Features
- Hardcoded commands: `\print`, `\about`, `\set`, `\py_call`, `\goto`, `\py_exec`, `\call`, `\callsave`, `\sleep`, `\exit`, `\input`, `\nonlocal_set`, `\include`
- First-class function support
- Operators: `==`, `!=`, `<`, `<=`, `>`, `>=`, `+`, `-`, `*`, `/`, `%/%`, `%`, `**`, unary `+`, unary `-`, function call, subscripting
- In-place operators: `=`, `+=`, `-=`, `*=`, `/=`, `%=`, `%/%=`
- Control flow constructs: `goto`, `if`, `while`, `do..while`, C-style `for`, `break` and `continue`
- Data types: integers, floats, strings, booleans, lists, dictionaries

## To-do list
- Bitwise and logical operators
- Rest and keyword arguments
- Better Python interface
- OOP
- Exceptions
- Modules
