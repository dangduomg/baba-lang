---
layout: default
---


# Functions

Functions are very important in any programming language. They are used to
reuse code, organize code and create abstractions. baba-lang is no exception.
Functions in baba-lang are first-class citizens, meaning they behave just like
normal objects, can be assigned to variables, be part of composite types,
passed as arguments, returned from functions, and even has their own literal
syntaxes. 


## Syntax

Functions in baba-lang are defined using this syntax:
```
fun f(x, y) {
    return x + y;
}
```
An anonymous (lambda) function literal can also be defined:
```
f = fun(x, y) {
    return x + y;
};
```
Or even shorter (for single expressions only):
```
f = fun(x, y) -> x + y;
```
And they are called using this syntax:
```
v = f(3, 2);

print(v);  # 5
```


## Semantics

baba-lang functions can return early, which is useful. For example:
```
fun contains(haystack, needle) {
    for x in haystack {
        if x == needle {
            return true;
        }
    }
    return false;
}

a = [1, 2, 3, 4, 'orange'];

print(contains(a, 'orange'));  # true
print(contains(a, 'apple'));  # false
```

baba-lang does not support implicit returns. All functions without `return`
returns `null`. Similarly, `return` statements without value return `null`.
```
fun f() {
    print('hello');
    return;
}

fun g() {
    print('hello');
}

print(f());  # `hello` then `null`
print(g());  # same thing
```

### Scoping

Each function creates a function-local scope. All variables defined inside a
function are local to that function. Moreover, baba-lang uses lexical scoping,
meaning the scope of a variable can be deduced just from its position within
the source code. See [Scoping](scoping.md) for details.

### How does functions work

When a function is declared, the current local environment is shallow copied,
if it exists, to support closures.

When a function is called, these will happen:
1. A new local environment is created. The environment's parent is the
closure's environment, not the current local environment.
2. The function is added as a traceback frame (baba-lang doesn't have an
unified stack frame)
3. Arguments and `this` are assigned to the new local environment.
4. The body of the function is evaluated. It can either:
    - Return a value
    - Not return a value, in which case the function returns `null`
    - Throw an error
5. The traceback (if the function succeeds) and local environment frame are
cleaned before finally actually returning.


## Next

[Scoping](scoping.md)