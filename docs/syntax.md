---
layout: default
---


[Back](index.md)


# Syntax

This is the explanation of all syntactic rules and their uses in baba-lang, based on `grammar.lark`.


## Body
```
?start: body

body: stmt*

// Statement grammar

?stmt: if_stmt
     | if_else_stmt
     | while_stmt
     | do_while_stmt
     | for_stmt
     | break_stmt
     | continue_stmt
     | try_stmt
     | return_stmt
     | throw_stmt
     | include_stmt
     | function_stmt
     | module_stmt
     | class_stmt
     | exprs ";"
     | ";" -> nop_stmt
```
baba-lang's top-level consists of a single body. A body is a list of statements. All statements, except for block statements, requires a semicolon to terminate. The second-to-last rule is a special type of statement, known as an expression statement. And the last rule is a no-op empty statement that is discarded by the post-processor.


## Statement syntax


### `if` statement
```
if_stmt: _IF expr "{" body "}"

if_else_stmt: _IF expr "{" body "}" _ELSE (if_else_stmt | if_stmt | "{" body "}")
```
`if` statements follow C-style syntax, except that the parentheses around the condition is not required, but the braces are required.
SOme possible variations:
```
if condition {
    ...
}

if condition {
    ...
} else {
    ...
}

if condition {
    ...
} else if condition2 {
    ...
}

if condition {
    ...
} else if condition2 {
    ...
} else {

}
```

### `while` statement
```
while_stmt: _WHILE expr "{" body "}"

do_while_stmt: _DO "{" body "}" _WHILE expr ";"
```
`while` and `do..while` statements, again, largely follow C-style syntax, except for the parentheses.

### `for` statements
```
for_stmt: _FOR "(" [exprs] ";" [expr] ";" [exprs] ")" "{" body "}"
        | _FOR IDENT _IN expr "{" body "}" -> for_each_stmt
```
There are 2 types of `for` statements.

### C-style `for` statement
```
for_stmt: _FOR "(" [exprs] ";" [expr] ";" [exprs] ")" "{" body "}"
```
The syntax of C-style `for` is almost identical to that of C. It is syntactic sugar, being desugared to a `while` statement at parse time.

### Iterator `for` statement
```
_FOR IDENT _IN expr "{" body "}" -> for_each_stmt
```
This syntax resembles `for` syntax from Python, Swift, and Rust.
```
for x in some_iterable {
    ...
}
```
Iterator `for` converts the expression after `in` from an iterable to an iterator (using the `.iter` method), then consumes it (using `.next` method) and assigns the consumed value to the identifier. The `.next` method must either return an `Item`, which contains the consumed value, or `null`, signaling the end of iteration.

### `break` and `continue` statement
```
break_stmt: _BREAK ";"
continue_stmt: _CONTINUE ";"
```
`break` and `continue` statements are early exit statements for loops. Right now, they only consists of a single keyword and mandatory semicolon, as nested `break` and `continue` haven't been added yet.

### `try..catch` statement
```
try_stmt: _TRY "{" body "}" catch_clause
catch_clause: _CATCH IDENT "{" body "}"
```
`try..catch` is baba-lang's exception handling facility. Any exceptions raised in `try` blocks (including from functions called inside it) are handled in the corresponding `catch` block. `try` follows the same syntax as in JavaScript, but without parentheses around the `catch` capture variable. There are no `finally` yet.

### `return` statement
```
return_stmt: _RETURN [expr] ";"
```
`return` statements are straightforward and follow C syntax.

### `throw` statement
