---
layout: default
---


[Back](index.md)


# Scoping

Scoping rules in baba-lang is simple. There are only three types of variables in baba-lang:
- Global variables
- Function-local variables
- Non-local variables


## Experiment with scoping

1. Follow step 1-2 of [Create the first baba-lang program](hello-world.md#create-the-first-baba-lang-program) if you haven't already.

2. Create file `scoping.bl` in your `my-bl-scripts` directory, then write this:

        a = 1;

        print("outside function f, a =", a);

        fun f() {
            b = 2;
            print("inside function f, b =", b);
            print("inside function f, a =", a);
        }
        f();

        print("outside function f, b =", b);

3. Run the baba-lang interpreter
```sh
python3 src/main.py my-bl-scripts/scoping.bl
```
This should be the output:

        outside function f, a = 1
        inside function f, b = 2
        inside function f, a = 1
        Runtime error at line 12, column 34:
        Variable b is undefined

        print("outside function f, b =", b);
                                        ^

        Traceback:


You can see that:
- The variable `a` can be accessed both at the top level, and inside function `f`. It is a *global* variable.
- The variable `b` can only be accessed inside function `f`. Outside of `f`, it's undefined. Therefore, it is a *function-local* (or just *local*) variable. In this case, it is local only to `f`.


## Lexical scoping

baba-lang is a lexically-scoped programming language, meaning the scope of a variable can be determined entirely by its position in the source code, ideally with no exceptions. Take the example above:
```
a = 1;

print("outside function f, a =", a);

fun f() {
    b = 2;
    print("inside function f, b =", b);
    print("inside function f, a =", a);
}
f();

print("outside function f, b =", b);
```
The variable `a` is in global scope, meaning, according to lexical scoping, it can be accessed anywhere in the code after it is defined in the code. Therefore, both the 1st and 3rd `print` calls can access the variable. However, any code before the variable definition cannot use it:
```
print(a);  # error

a = 1;
```
The variable `b`, meanwhile, is in function-local scope, so, according to lexical scoping, it is only accessible to the body of function `f`, after it is defined. Therefore, the 2nd `print` call, inside of `f`, can access `b`, but the 4th call results in an error, as it is outside `f`, and the variable `b` is not defined in the global scope.

### Implications with nested functions

In baba-lang, functions can be nested and are first-class citizens (can be assigned to variables, passed to arguments and returned from a function just like other values), resulting in this somewhat counterintuitive example:
```
fun counter() {
    i = 0;
    fun inc() {
        i += 1;
        return i;
    }
    return inc;
}

my_counter = counter();

print(my_counter());  # 1
print(my_counter());  # 2
print(my_counter());  # 3
```
The variable `i` seems to "outlive" its scope (local to `counter`), as it is still accessed and modified by an instance of the `inc` function (`my_counter`), even after `counter` finished executing. However, it does not violate lexical scoping rules, as `i` is in `counter`'s body, therefore in the enclosing scope of `inc`, so are always accessible by `inc`.

baba-lang use closures to make this possible. Closures allow functions to be first-class citizens while preserving lexical scoping.


## Types of variables

As detailed above, baba-lang has 3 types of variables:
- **Global variables**: Variables that can be accessed anywhere after it is defined.
- **Local variables**: Variables that can be accessed only inside the function it is defined in.
- **Non-local variables**: Subtype of local variables that can be accessed by nested functions, therefore "outlive" its scope.


## Next

Not done yet.
