---
layout: default
---


[Back](index.md)


# Scoping

Scoping rules in baba-lang is simple. There are only two types of variables in baba-lang:
- Global variables
- Function-local variables


## Experiment with scoping

1. Follow step 1-2 of [Create the first baba-lang program](hello-world.md#create-the-first-baba-lang-program) if you haven't already.
2. Create file `scoping.bl` in your `my-bl-scripts` directory, then write this:

        a = 1;

        print(a);

        fun f() {
            b = 2;
            print(b);
            print(a);
        }
        f();

        print(b);

3. Run the baba-lang interpreter
```sh
python3 src/main.py my-bl-scripts/scoping.bl
```
This should be the output:
```
1
2
1
Runtime error at line 12, column 7:
Variable b is undefined

print(b);
      ^

Traceback:

```