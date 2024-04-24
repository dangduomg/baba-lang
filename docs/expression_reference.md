# Expression Reference

## Operators
All operators in baba-lang are:
| Symbol | Name | Notes |
| - | - | - |
| `=` | Assignment | |
| `+=` `-=` `*=` `/=` `%=` `%/%=` | In-place assignment | |
| `==` | Equality | |
| `!=` | Inequality | |
| `>` | Greater than | |
| `>=` | Greater than or equal to | |
| `<` | Less than | |
| `<=` | Less than or equal to | |
| `+` | Addition | Adds numbers, concatenates strings and lists |
| `-` | Subtraction | |
| `*` | Multiplication | Multiplies numbers, repeats strings |
| `/` | Division | Always return floats |
| `%/%` | Floor division | |
| `%` | Modulo | Satisfies `a % b == a - b * (a %/% b)` |
| `**` | Power | |
| `+` | Unary plus | |
| `-` | Negation | |
| | Function call | Syntax: `f(a, b, ...)` |
| | Subscript | Syntax: `a[i]` |

This is their precedence table:
| Operators | Precedence | Associativity |
| - | - | - |
| `=`, `+=`, `-=`, `*=`, `/=`, `%=`, `%/%=` | 0 | Right |
| `==`, `!=`, `>`, `>=`, `<`, `<=` | 1 | None |
| `+`, `-` | 2 | Left |
| `*`, `/`, `%`, `%/%` | 3 | Left |
| unary `+`, unary `-` | 4 | |
| ** | 5* | Right* |
| call, subscript | 6 | |

Power operator's associativity and precedence since it has lower precedence than unary operators on the right, but higher precedence than them on the left.
