---
layout: default
---


[Back](index.md)


# Types

All values in baba-lang has a type associated with it. There are currently 12 types in baba-lang: string, integer, float, boolean, null, list, dict, module, baba-lang function, native (Python) function, class and instance


## Integer type

The integer type is one of the most basic and important types in most programming languages. Integers in baba-lang are just simple wrappers around Python integers, therefore it largely inherits behavior from Python. This means that it is arbitrary-precision.

### Syntax

Right now, baba-lang only supports decimal syntax, and leading zeros are simply ignored, rather than treated specially.
```
0
1
-1
010  # == 10 (not 8)
001  # == 1
0xff  # illegal
1234567891011121314151617181920  # possible thanks to arbitrary precision
```

### Supported operators:

1. All binary operators:
    1. Arithmetic operators: `+`, `-`, `*`, `/`, `%/%`, `%`, `**`
    2. Bitwise operators: `&`, `|`, `^`, `<<`, `>>`
    3. Comparison operators: `==`, `!=`, `>`, `>=`, `<`, `<=`

2. All unary operators: `+`, `-`, `~`


## Float type

Float in baba-lang are just simple wrappers around Python integers, therefore it largely inherits behavior from Python. This means that it is a double-precision floating-point number that follows the IEEE 754 standard.

### Syntax

Floats in baba-lang consists of three parts: Integer part, fractional part and exponent. All parts are optional, but at least one is required.

The special numbers `Infinity`, `-Infinity` and `NaN` are available from the `std/math.bl` library as `Math.INF`, `-Math.INF` and `Math.NAN` respectively
```
1.1
-0.2
.2
2.
2  # not a float, but an integer
2e100
1.2e-10
.00000000012   # equivalent to the above
```

### Supported operators:

1. Binary operators:
    1. Arithmetic operators: `+`, `-`, `*`, `/`, `%/%`, `%`, `**`
    2. Comparison operators: `==`, `!=`, `>`, `>=`, `<`, `<=`

2. Unary operators: `+`, `-`


## String type

Strings in baba-lang are largely similar to Python's. Strings can be double-quoted or single-quoted
