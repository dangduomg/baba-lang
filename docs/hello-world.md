---
layout: default
---


[Back](./)

# Hello world

Welcome to the baba-lang tutorial (and reference)! baba-lang is a language made by me for the purpose of learning how programming languages work, from parsing to static analysis to interpretation. To start with, lets make a Hello World program in baba-lang.


## Make sure that you have baba-lang in your local machine

See [How to install and use baba-lang](/#How to install and use baba-lang) for how to do so


## Create the first baba-lang program

1. Make a directory inside the baba-lang project directory for your scripts to reside in. Name it whatever you like.
```sh
mkdir my-bl-scripts
```
2. Activate your virtual environment, if you have a venv and haven't activated already.
```sh
source "<your venv root>/bin/activate"
```
3. Create a file in your script directory. Let's call it `hello-world.bl`. baba-lang source code uses the extension `.bl`
4. Write this to the file using your favorite editor and save it.

        # my first baba-lang program!

        print('Hello, world!');

5. Run the baba-lang interpreter
```sh
python3 src/main.py my-bl-scripts/hello-world.bl
```

If you see "Hello, world!" printed to the console, then you have successfully ran your first baba-lang program!


## Explanation

You can see that:
* The `print` function takes a string input and prints it to the console. The syntax for calling functions in baba-lang is like that of typical imperative languages
* Strings are either single-quoted or double-quoted. This would be fine:
```
print("Hello, world!");
```
Unlike Perl, there is no difference between single-quoting and double-quoting.
* A semicolon is used to end a statement in baba-lang. It is required.


## Next

Not done yet.