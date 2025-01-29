---
layout: default
---


[Back](index.md)


# Basic types

All values in baba-lang has a type associated with it. There are currently 12 types in baba-lang: string, integer, float, boolean, null, list, dict, module, baba-lang function, native (Python) function, class and instance


## Integer type

The integer type is one of the most basic and important types in most programming languages. Integers in baba-lang are just simple wrappers around Python integers, therefore it largely inherits behavior from Python. This means that it is arbitrary-precision.

### Syntax

Right now, baba-lang only supports decimal syntax, and leading zeros are simply ignored, rather than treated specially.

Note that, for simplicity, the baba-lang grammar does not treat negative numbers as a single literal, but a production consisting of an unary operator (`+` or `-`) and the number itself.
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

Strings in baba-lang are largely similar to Python's. Strings can be double-quoted or single-quoted. Unlike Perl, single-quoted and double-quoted strings are nearly identical in behavior, therefore which delimiter to use is largely a matter of style and preference.

### Syntax

As baba-lang uses `str` to parse a string, the syntax for strings is identical to Python. See [](https://docs.python.org/3/reference/lexical_analysis.html#strings) for details.

```
'hello'
"world"
"eBaum's World"
'eBaum\'s World'  # having 2 different quotes avoid this

'There is a website\nnamed "eBaum\'s World"'
# this is:
# There is a website
# named "eBaum's World"

print('I hate\b\b\b\blove you\a')  # prints 'I love you' and plays a sound (if the console supports it)

'a
b'  # illegal

'a"  # also illegal
```

### Supported operators

1. Binary operators:
    1. Concatenation: `+`
    2. Repetition: `*`
    3. Comparison in lexicographical order: `==`, `!=`, `>`, `>=`, `<`, `<=`


## Boolean type

Booleans are either `true` or `false`. Unlike Python, booleans are not subtypes of integers, therefore most operations on booleans do not work on integers.

### Syntax

There are 2 Boolean literals: `true` and `false`. They are reserved keywords (cannot be used as identifiers)

### Supported operators

None. The logical operators works based on the truth value of its operands, but it works on any value and therefore are not considered here.


## Null type

The null type only has a single instance: `null`. `null` is used as the default return value for functions without an explicit `return`.

### Syntax

The only instance `null` is a reserved keyword.

### Supported operators

None.


## The rest

The rest of the types will have their separate pages to detail them:

- Lists and dicts
- Functions (Python functions and baba-lang functions)
- Modules
- OOP (classes and instances)


## Next

- [Functions](function.md)
- [Scoping](scoping.md)
