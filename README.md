# baba-lang

Yet another programming language, made in Python. Has nothing to do with the video game "Baba is You".

Right now in version `0.5.1-testing`.

## Notes

- baba-lang is now in its `0.x` versions. This means that later versions of baba-lang is not guaranteed to be backward compatible with the previous ones.
- baba-lang is written for educational purposes only; it is not meant to be used in production.

## How to install and use baba-lang

Installing and running baba-lang is simple:
1. Prerequisites: Python 3 (At least 3.12 can be sure to work), Lark (see requirements.txt).
2. Either:
* Download the latest point release on GitHub (recommended, as it is stable)
* Clone the repository
```sh
git clone https://github.com/dangduomg/baba-lang.git
```
3. Set working directory to the project root.
```sh
cd baba-lang
```
4. (Optionally) Create and activate a virtual environment.
```sh
python3 -m venv .venv
source .venv/bin/activate
```
5. Install requirements.
```sh
pip install -r requirements.txt
```
6. Run `src/main.py` without arguments to open an interactive prompt. To run a source file, enter `src/main.py <file>`. Source files are of extension `.bl`. Run `src/main.py -h` for further help.

## Features
- Familiar JS-like syntax
- First-class functions
- Classes with inheritance
- Exceptions
- Modules
- Easy Python interop with `py_function` and `py_method`

## Example
Here is an example snippet to get started:
```js
min = py_function('builtins', 'min');

subjects = ['BABA', 'KEKE', 'DOOR', 'FLAG'];
verbs = ['HAS', 'HAS', 'IS', 'IS'];
objects = ['YOU', 'KEY', 'LOCK', 'WIN'];

// zipper
for (i = 0; i < min(subjects, verbs, objects); i += 1) {
    subject = subjects[i];
    verb = verbs[i];
    object = objects[i];
    if subject == 'BABA' && verb == 'HAS' {
        verb = 'IS';
    }
    print(subject + ' ' + verb + ' ' + object);
}
```

## To-do list
- A bytecode interpreter in Rust (compiler will still be written in Python)
- More tests
- Rest and keyword arguments
- Traits/mixins
- Algebraic data types
- `import` instead of `include`
- Static/Gradual type checking
- Package manager
