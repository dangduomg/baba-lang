import sys
from time import sleep

import operator
from lark import Lark
from lark.visitors import Interpreter
from ast import literal_eval


VERSION = '0.2.2'
ABOUT = f'''\
this is babalang, (C) 2024
version {VERSION}
'''


pl_parser = Lark(r'''
?start: body

body: stmt*

?stmt: print_stmt
     | about_stmt
     | var_stmt
     | python_call_stmt
     | label
     | goto_stmt
     | goto_if_stmt
     | python_exec_stmt
     | function_stmt
     | call_stmt
     | call_and_save_stmt
     | return_stmt
     | sleep_stmt
     | exit_stmt
     | input_stmt
     | nonlocal_var_stmt

print_stmt: "\\print" value ";"

about_stmt: "\\about" ";"

var_stmt: "\\set" CNAME "," value ";"

python_call_stmt: "\\py_call" CNAME "," string ("," value)* ";"

label: CNAME ":"

goto_stmt: "\\goto" CNAME ";"

goto_if_stmt: "\\goto" CNAME "if" "(" value ")" ";"

python_exec_stmt: "\\py_exec" string ";"

function_stmt: "function" CNAME "(" args ")" "{" body "}"
args: (CNAME ("," CNAME)*)?

call_stmt: "\\call" value ("," value)* ";"

call_and_save_stmt: "\\callsave" CNAME "," value ("," value)* ";"

return_stmt: "return" value ";"

sleep_stmt: "\\sleep" value ";"

exit_stmt: "\\exit" ";"

input_stmt: "\\input" CNAME "," value ";"

nonlocal_var_stmt: "\\nonlocal_set" CNAME "," value ";"

?value: rhs_expr

?rhs_expr: cmp

?cmp: sum "==" sum -> eq
    | sum "!=" sum -> ne
    | sum "<" sum -> lt
    | sum "<=" sum -> le
    | sum ">" sum -> gt
    | sum ">=" sum -> ge
    | sum

?sum: sum "+" prod -> add
    | sum "-" prod -> sub
    | prod

?prod: prod "*" atom -> mul
     | prod "/" atom -> div
     | prod "%/%" atom -> floordiv
     | prod "%" atom -> mod
     | atom

?atom: literal
     | CNAME -> var
     | "(" rhs_expr ")"

?literal: string
        | SIGNED_INT -> int
        | SIGNED_FLOAT -> float

string: ESCAPED_STRING

%import common.CNAME
%import common.ESCAPED_STRING
%import common.SIGNED_INT
%import common.SIGNED_FLOAT
%import common.SH_COMMENT
%import common.C_COMMENT
%import common.CPP_COMMENT
%import common.WS

%ignore SH_COMMENT
%ignore C_COMMENT
%ignore CPP_COMMENT
%ignore WS
''')


class PLCtrlException(Exception):
    pass

class PLReturn(PLCtrlException):
    pass

class PLJump(PLCtrlException):
    pass


class PLFrame:
    def __init__(self, vars, env):
        self.vars = vars
        self.env = env

    def var_search(self, name):
        if name in self.vars:
                return self.vars[name]
        for scope in self.env:
            if name in scope.vars:
                return scope.vars[name]
        else:
            raise RuntimeError(f'Can\'t find variable {name}!')

    def var_set(self, name, value):
        self.vars[name] = value
        return self.vars[name]

    def var_search_set(self, name, value):
        if name in self.vars:
                return self.var_set(name, value)
        for scope in self.env:
            if name in scope.vars:
                return scope.var_set(name, value)
        else:
            raise RuntimeError(f'Can\'t find variable {name}!')


class PLFunction:
    def __init__(self, name, form_args, body, env):
        self.name = name
        self.form_args = form_args
        self.body = body
        self.env = env

    def __repr__(self):
        return f'babalang function {self.name}({", ".join(form_args)})'


def binary_operator(f):
    def operator(self, tree):
        a, b = tree.children
        return f(self.visit(a), self.visit(b))
    operator.__name__ = f.__name__
    operator.__doc__ = f.__doc__
    return operator


class PLInterpreter(Interpreter):
    def __init__(self):
        self.call_stack = [PLFrame({}, None)]

    def push_frame(self, *args, **kwargs):
        self.call_stack.append(PLFrame(*args, **kwargs))

    def pop_frame(self):
        self.call_stack.pop()

    def var_search(self, *args, **kwargs):
        return self.call_stack[-1].var_search(*args, **kwargs)

    def var_set(self, *args, **kwargs):
        return self.call_stack[-1].var_set(*args, **kwargs)

    def var_search_set(self, *args, **kwargs):
        return self.call_stack[-1].var_search_set(*args, **kwargs)

    # ---- interpreter callbacks -----

    def body(self, tree):
        '''Collect labels and run statements sequentially'''
        stmts = tree.children
        labels = {}
        for i, stmt in enumerate(stmts):
            if stmt.data == 'label':
                label, = stmt.children
                labels[label] = i
        pc = 0
        while pc < len(stmts):
            stmt = stmts[pc]
            try:
                self.visit(stmt)
            except PLJump as jmp:
                label, = jmp.args
                if label in labels:
                    pc = labels[label]
                else:
                    raise RuntimeError(f'label "{label}" does not exist')
            except Exception as e:
                raise e
            else:
                pc += 1

    def print_stmt(self, tree):
        '''Prints something'''
        value, = tree.children
        print(self.visit(value))

    def about_stmt(self, tree):
        '''Prints the about string'''
        print(ABOUT)

    def var_stmt(self, tree):
        '''Set a variable'''
        varname, value = tree.children
        self.var_set(varname.value, self.visit(value))

    def nonlocal_var_stmt(self, tree):
        '''Set a nonlocal variable'''
        varname, value = tree.children
        self.var_search_set(varname.value, self.visit(value))

    def python_call_stmt(self, tree):
        '''Calls a Python function with the arguments given by baba-lang'''
        varname, func, *args = tree.children
        func = self.visit(func)
        args = [self.visit(a) for a in args]
        self.var_set(varname.value, eval(func)(*args))

    def goto_stmt(self, tree):
        '''Raises an exception to jump to a label'''
        label, = tree.children;
        raise PLJump(label)

    def goto_if_stmt(self, tree):
        '''Same as goto_stmt, but only if a condition is true'''
        label, value = tree.children
        if self.visit(value):
            raise PLJump(label)

    def python_exec_stmt(self, tree):
        '''Executes Python statements'''
        code, = tree.children
        code = self.visit(code)
        exec(code)

    def function_stmt(self, tree):
        '''Creates a function'''
        name, form_args, body = tree.children
        form_args = [a.value for a in form_args.children]
        self.var_set(name.value, PLFunction(name.value, form_args, body, self.call_stack[:]))

    def call_stmt(self, tree):
        '''Calls a function'''
        func, *args = tree.children
        func = self.visit(func)
        args = [self.visit(a) for a in args]
        self._call_stmt(func, args)

    def call_and_save_stmt(self, tree):
        '''Calls a function and save its result to a variable'''
        varname, func, *args = tree.children
        func = self.visit(func)
        args = [self.visit(a) for a in args]
        self.var_set(varname.value, self._call_stmt(func, args))

    def _call_stmt(self, func, spec_args):
        if len(spec_args) < len(func.form_args):
            raise RuntimeError('too little arguments!')
        elif len(spec_args) > len(func.form_args):
            raise RuntimeError('too many arguments!')
        self.push_frame({}, func.env)
        for f, s in zip(func.form_args, spec_args):
            self.var_set(f, s)
        retval = None
        try:
            self.visit(func.body)
        except PLReturn as ret:
            retval, = ret.args
        except Exception as e:
            raise e
        finally:
            self.pop_frame()
        return retval

    def return_stmt(self, tree):
        '''Returns a value'''
        value, = tree.children
        raise PLReturn(self.visit(value))

    def sleep_stmt(self, tree):
        '''Sleeps for a certain amount of time'''
        time, = tree.children
        sleep(self.visit(time))

    def exit_stmt(self, tree):
        '''Exits the interpreter'''
        sys.exit(0)

    def input_stmt(self, tree):
        '''Get input from the user'''
        varname, prompt = tree.children
        self.var_set(varname.value, input(self.visit(prompt)))

    eq = binary_operator(operator.eq)
    ne = binary_operator(operator.ne)
    lt = binary_operator(operator.lt)
    le = binary_operator(operator.le)
    gt = binary_operator(operator.gt)
    ge = binary_operator(operator.ge)
    add = binary_operator(operator.add)
    sub = binary_operator(operator.sub)
    mul = binary_operator(operator.mul)
    div = binary_operator(operator.truediv)
    floordiv = binary_operator(operator.floordiv)
    mod = binary_operator(operator.mod)

    def var(self, tree):
        '''Variable reference'''
        name, = tree.children
        return self.var_search(name)

    def string(self, tree):
        '''String type'''
        s, = tree.children
        return literal_eval(s)

    def int(self, tree):
        '''Integer type'''
        i, = tree.children
        return literal_eval(i)

    def float(self, tree):
        '''Float type'''
        f, = tree.children
        return literal_eval(f)

pl_interpreter = PLInterpreter()


def interpret(pl_string):
    parse_tree = pl_parser.parse(pl_string)
    pl_interpreter.visit(parse_tree)


def main(args):
    if len(args) > 1:
        file = args[1]
        with open(file) as f:
            interpret(f.read())
    else:
        while True:
            inpt = input('> ')
            interpret(inpt)

if __name__ == '__main__':
    main(sys.argv)
