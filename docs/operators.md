---
layout: default
---


[Back](index.md)


# Operators

Expressions in baba-lang are composed of operators. There are 32 operators in baba-lang, that can be categorized to 6 types:
* Binary operators
* Logical operators
* Unary operators
* Assignment operators
* Special operators


## Play with operators

1. Make sure baba-lang is in your local machine. See [How to install and use baba-lang](index.md#how-to-install-and-use-baba-lang) to obtain and run baba-lang in your local machine.
2. Run baba-lang without arguments to go to interactive mode.
3. Try to enter a mathematical expression in baba-lang:

        baba-lang 0.4.2
        > 1 + 2 * 3 - 4
        3
        > 1 + 1 * 1 / 1 - 1
        1.0

4. baba-lang would evaluate the expression according to the rules you have learned at school (PEMDAS), like a glorified calculator. Experiment with other operators as well.
5. Once you are done, type `Ctrl-Z` (Windows) or `Ctrl-D` (Linux) to exit the interpreter.


## Binary operators

Binary operators take two values. Binary arithmetic operators in baba-lang are almost always *infix*, meaning they are placed between their arguments. They follow precedence rules, such as the aforementioned PEMDAS, among others, and are either left- or right-associative. Comparison operators, however, are *non-associative*, which means multiple comparison operators without parentheses (e.g. `a == b == c`) will cause a syntax error.

| Name                     | Symbol | Notes |
| ------------------------ | ------ | - |
| Addition                 | `+`    | Adds numbers, concatenates strings and lists |
| Subtraction              | `-`    | |
| Multiplication           | `*`    | Multiplies numbers, repeats strings |
| Division                 | `/`    | Always return floats |
| Floor division           | `%/%`  | |
| Modulo                   | `%`    | Satisfies `a % b == a - b * (a %/% b)` |
| Power                    | `**`   | |
| Bitwise and              | `&`    | |
| Bitwise or               | `|`    | |
| Bitwise xor              | `^`    | |
| Left shift               | `<<`   | |
| Right shift              | `>>`   | |
| Equality                 | `==`   | |
| Inequality               | `!=`   | |
| Greater than             | `>`    | |
| Greater than or equal to | `>=`   | |
| Less than                | `<`    | |
| Less than or equal to    | `<=`   | |


## Logical operators

Unlike normal operators, logical operators are *short-circuit*, meaning they may not evaluate the second argument if the result is obvious from the first argument. This can be used to implement conditionals in an expression (`a && b || c`). Only `&&` (logical and) and `||` (logical or) have this property. `!` (logical not) behave like a normal unary operator.

| Name        | Symbol | Notes |
| ----------- | ------ | - |
| Logical and | `&&`   | |
| Logical or  | `||`   | |
| Logical not | `!`    | |


## Unary operators

Unary operators take one argument only. In baba-lang, they are prefix operators, meaning they precede their only argument.

| Name        | Symbol | Notes |
| ----------- | ------ | - |
| Unary plus  | `+`    | |
| Negation    | `-`    | |
| Bitwise not | `~`    | |


## Assignment operators

Assignment operations consists of an *assignment target* on the left-hand side, which is currently either:
* an identifier (variable)
* a subscript
, the operator itself and the rest at the right hand side.

| Name                | Symbol                          | Notes |
| ------------------- | ------------------------------- | - |
| Assignment          | `=`                             | If assigning variables, always creates new ones |
| In-place assignment | `+=` `-=` `*=` `/=` `%=` `%/%=` | |


## Special operators

These operators have special syntax and they are detailed in other sections of the reference.

| Name          | Notes |
| ------------- | - |
| Function call | Syntax: `f(a, b, ...)` |
| Subscript     | Syntax: `a[i]` |
| Dot access    | Syntax: `a.b` |


## Operator precedence table

All operators in baba-lang have a *precedence*, which allows ambiguity to be solved. The precedence table of operators are shown here, with 0 being the lowest precedence.

| Precedence | Associativity | Operators |
| ---------- | ------------- | - |
| 0          | Right         | `=`, `+=`, `-=`, `*=`, `/=`, `%=`, `%/%=` |
| 1          | Right         | `||` |
| 2          | Right         | `&&` |
| 3          | None          | `==`, `!=`, `>`, `>=`, `<`, `<=` |
| 4          | Left          | `|`, `^` |
| 5          | Left          | `&` |
| 6          | Left          | `<<`, `>>` |
| 7          | Left          | `+`, `-` |
| 8          | Left          | `*`, `/`, `%`, `%/%` |
| 9          |               | unary `+`, unary `-` |
| 10\*       | Right\*       | `**` |
| 11         |               | call `a()`, subscript `a[i]`, dot `a.b` |
| 12         |               | parentheses `(...)` |

\* Power operator's associativity and precedence is special since it has lower precedence than unary operators on the right, but higher precedence than them on the left. Put simply, `3 ** -2` is possible and `-3 ** 2` means `-(3 ** 2)` rather than `(-3) ** 2`.


## Next

[Types](types.md)