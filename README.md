# baba-lang

Your typical toy programming language, made in Python.

Right now in version `0.2.5`.

## Features
- Hardcoded commands: `\print`, `\about`, `\set`, `\py_call`, `\goto`, `\py_exec`, `\call`, `\callsave`, `\sleep`, `\exit`, `\input`, `\nonlocal_set`, `\include`
- First-class function support
- Operators: `==`, `!=`, `<`, `<=`, `>`, `>=`, `+`, `-`, `*`, `/`, `%/%`, `%`, `**`, unary `+`, unary `-`, function call
- In-place operators: `+=`, `-=`, `*=`, `/=`, `%=`, `%/%=`
- Control flow constructs: `goto`, `if`, `while`, `do..while`, C-style `for`, `break` and `continue`
- Data types: integers, floats, strings, booleans

For the specifics of the language, please look at the source code.

## To-do list
- Bitwise and logical operators
- Collection types (`list` and `dict`)
- Rest and keyword arguments
- Better Python interface
- OOP
- Exceptions
- Modules

## Requirements
- Python 3
- Lark
