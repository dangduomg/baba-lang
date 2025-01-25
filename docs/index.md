---
layout: default
---


The site is **under construction**


## What is baba-lang?

baba-lang is a programming language created with Python (with a bytecode interpreter planned to be written in Rust). Right now, it's still incomplete, but has supported most control flow operators, closures, modules and easy Python integration via `py_*` functions. It is currently in version `0.5.0-testing`.

baba-lang is written for educational purposes only, and is not production-ready.


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


## baba-lang reference and tutorial

1. [Hello world](hello-world.md)
2. [Operators](operators.md)
3. [Types](types.md)
4. [Scoping](scoping.md)
5. [Syntax](syntax.md)