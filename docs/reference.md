# Baba-lang Reference

## Body
Bodies are composed of multiple statements. There are four types of statements:
- Commands
- Block statements
- Labels
- Other statements

Statements usually end with `;` (Block statements and labels do not end with `;`).

## Commands
Commands are statements that start with `\`. They end with `;`. They are hardcoded and are a way to implement primitive actions.

As of 0.2.6, commands include: `\print`, `\about`, `\set`, `\py_call`, `\py_exec`, `\goto`, `\call`, `\callsave`, `\sleep`, `\exit`, `\input`, `\nonlocal_set`, `\include`

### \print
```
\print <value>;
```
Prints `value`. Accepts all data types.

### \about
```
\about;
```
Prints the about message.

### \set
```
\set <name>, <value>;
```
Set variable `name` to `value`. Superseded by assignment expressions.

### \py_call
```
\py_call <var>, <function> [, <args 0>, <args 1>, ...];
```
Calls Python function `function` (`function` must be a quoted string) with arguments `args` and saves the result to `var`.

Usage example:
```
\py_call i, 'int', '1'; # int(1)

\py_call l, 'lambda *x: x', 1, 2, 3, 4; # (lambda *x: x)(1, 2, 3, 4) => (1, 2, 3, 4)

\py_call l_it, 'tuple.__getitem__', l, i; # tuple.__getitem__(l, i) => l[i]
```

### \py_exec
```
\py_exec <code>;
```
Executes `code` as a Python statement.

### \goto
```
\goto <label>;
\goto <label> if ( <condition> );
```
First form is unconditional `goto`: jump to `label` unconditionally.
Second form is conditional `goto`: jump to `label` only if `condition` is true.
Superseded by `goto` and `if` statements.

### \call
```
\call <function> [, <args 0>, <args 1>, ...];
```
Calls function `function` (can be any expression) with arguments `args` without saving its result to a variable.
Superseded by call expressions.

### \callsave
```
\callsave <var>, <function> [, <args 0>, <args 1>, ...];
```
Calls function `function` (can be any expression) with arguments `args`, saving its result to `var`.
Superseded by call expressions.

### \sleep
```
\sleep <time>;
```
Sleeps for `time` seconds (can be any expression).

### \exit
```
\exit [<code>];
```
Exits the interpreter with exit code `code`.

### \input
```
\input <var> [, <prompt>];
```
Asks the user for input with prompt `prompt` then saves it to `var`.

### \nonlocal_set
```
\nonlocal_set <name>, <value>;
```
Searches for a variable (even ones outside the scope) then set it.

### \include
```
\include <file>;
```
Evaluate the file `file` (must be a string) as if it were literally included into the current source file.

## Block statements
Block statements are statements having code blocks `{ ... }`. They don't end in `;`.

Block statements include:

### if
```
if (<condition>) { <code> }
if (<condition>) { <then_code> } else { <else_code> }
```
In the first variant, if `condition` is true, `code` is executed.
In the second variant, also called `if..else`, if `condition` is true, `then_code` is executed. Otherwise, `else_code` is executed.
`if..else` statements can be chained together as in (excerpt from tests/fizzbuzz.txt)
```
if (i % 15 == 0) {
  print(str(i) + ": fizzbuzz");
} else if (i % 5 == 0) {
  print(str(i) + ": buzz");
} else if (i % 3 == 0) {
  print(str(i) + ": fizz");
} else {
  print(str(i) + ":");
}
```
