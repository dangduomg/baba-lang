# baba-lang

Yet another programming language, made in Python. Has nothing to do with the video game "Baba is You".

Right now in version `0.4.1`.

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
- Modules
- Easy Python interop with `py_function` and `py_method`

## Example
Here is an example snippet to get started:
```js
min = py_function('builtins', 'min');

subjects = ['BABA', 'KEKE', 'DOOR', 'FLAG'];
verbs = ['HAS', 'HAS', 'IS', 'IS'];
objects = ['YOU', 'KEY', 'LOCK', 'WIN'];

# zipper
for (i = 0; i < min(subjects, verbs, objects); i += 1) {
    subject = subjects[i];
    verb = verbs[i];
    object = objects[i];
    # right now this is the only way to combine booleans :sob:
    if subject == 'BABA' {
        if verb == 'HAS' {
            verb = 'IS';
        }
    }
    print(subject + ' ' + verb + ' ' + object);
}
```

## To-do list
- Logical operators
- Rest and keyword arguments
- OOP
- Exceptions
