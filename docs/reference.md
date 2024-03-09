# Baba-lang Reference

## Body
```
body: stmt*

?stmt: cmd
     | label
     | goto_stmt
     | function_stmt
     | if_stmt
     | if_else_stmt
     | while_stmt
     | do_while_stmt
     | for_stmt
     | break_stmt
     | continue_stmt
     | return_stmt
     | expr_stmt
```
Bodies are composed of multiple statements. Statements usually end with `;` (Block statements do not end with `;`).

## Commands
Commands (rule `cmd` in the grammar above) are statements that start with `\`. They end with `;`. They are hardcoded and are a way to implement primitive actions.

As of 0.2.6, commands include: `\print`, `\about`, `\set`, `\py_call`, `\py_exec`, `\goto`, `\call`, `\callsave`, `\sleep`, `\exit`, `\input`, `\nonlocal_set`, `\include`

## \print
```
\print <value>
```
Prints `value`. Accepts all data types.

## \about
```
\about
```
Prints the about message.

## \set
```
\set <name>, <value>
```
Set variable `name` to `value`. Superseded by assignment expressions.

## \py_call
```
\py_call <var>, <function>, [<args 0>, <args 1>, ...]
```
Calls Python function `function` (`function` must be a quoted string) with arguments `args` and save the result to `var`.

Usage example:
```
\py_call i, 'int', '1'; # int(1)

\py_call l, 'lambda *x: x', 1, 2, 3, 4; # (lambda *x: x)(1, 2, 3, 4) => (1, 2, 3, 4)

\py_call l_it, 'tuple.__getitem__', l, i; # tuple.__getitem__(l, i) => l[i]
```

## \py_exec
```
\py_exec <code>
```
Executes `code` as a Python statement.

## \goto
```
\goto <label>
\goto <label> if ( <condition> )
```
First form is unconditional `goto`: jump to `label` unconditionally.
Second form is conditional `goto`: jump to `label` only if `condition` is true.
Superseded by `goto` and `if` statements.

WIP
