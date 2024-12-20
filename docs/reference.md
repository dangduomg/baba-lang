# Baba-lang Reference

## Body
Bodies are composed of multiple statements. Statements usually end with `;`. Most block statements however, do not end with `;`.

## Block statements
Block statements are statements having code blocks `{ ... }`. They usually don't end in `;`.

Block statements include:

### if
```
if <condition> { <code> }
if <condition> { <then_code> } else { <else_code> }
```
In the first variant, if `condition` is true, `code` is executed.
In the second variant, also called `if..else`, if `condition` is true, `then_code` is executed. Otherwise, `else_code` is executed.
`if..else` statements can be chained together as in
```
if i % 15 == 0 {
  print(str(i) + ": fizzbuzz");
} else if i % 5 == 0 {
  print(str(i) + ": buzz");
} else if i % 3 == 0 {
  print(str(i) + ": fizz");
} else {
  print(str(i) + ":");
}
```

### while, do..while
```
while <condition> { <code> }
do { <code> } while <condition>;
```
In the first variant, while `condition` is true, `code` is executed (i.e. it repeats until `condition` is false or terminated early by `break` or `return`).
In the second variant, also called `do..while`, `code` is executed before `condition` is checked.

### for
```
for ([<init>]; [<condition>]; [<update>]) { <code> }
```
Is basically equivalent to:
```
<init>;
while <condition> {
  <code>;
  <update>;
}
```
`init` and `update` are expressions.

When `condition` is omitted, it defaults to `true`, meaning the loop will run forever (unless terminated early by `break` or `return`).

## Other statements

### break
```
break;
```
Breaks from a loop.

### continue
```
continue;
```
Skips the rest of the loop body in a loop. In `for` loops, update expressions are still executed after `continue`.

### return
```
return <value>;
```
Returns a `value` from a function.

### include
```
include <file>;
```
Evaluate the file `file` (must be a string) as if it were literally included into the current source file.

## Expressions

All operators in baba-lang are: `==`, `!=`, `<`, `<=`, `>`, `>=`, `+`, `-`, `*`, `/`, `%/%`, `%`, `**`, unary `+`, unary `-`, function call, subscripting.

All types in baba-lang are: integers, floats, strings, booleans, lists, dictionaries.

For expression reference, see [Expression Reference](expression_reference.md)
