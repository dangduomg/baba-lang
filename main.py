import sys
from time import sleep
import operator
import logging

from lark import Lark
from lark.visitors import Interpreter
from ast import literal_eval


VERSION = '0.2.6'
ABOUT = f'''\
this is babalang, (C) 2024
version {VERSION}
'''


pl_parser = Lark(r'''
?start: body

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

?cmd: "\\print" expr ";"                           -> print_stmt
    | "\\about" ";"                                -> about_stmt
    | "\\set" IDENT "," expr ";"                   -> var_stmt
    | "\\py_call" IDENT "," string ("," expr)* ";" -> python_call_stmt
    | "\\py_exec" string ";"                       -> python_exec_stmt
    | "\\goto" IDENT ";"                           -> goto_stmt
    | "\\goto" IDENT _IF "(" expr ")" ";"          -> goto_if_stmt
    | "\\call" expr ("," expr)* ";"                -> call_stmt
    | "\\callsave" IDENT "," expr ("," expr)* ";"  -> call_and_save_stmt
    | "\\sleep" expr ";"                           -> sleep_stmt
    | "\\exit" expr? ";"                           -> exit_stmt
    | "\\input" IDENT ("," expr)? ";"              -> input_stmt
    | "\\nonlocal_set" IDENT "," expr ";"          -> nonlocal_var_stmt
    | "\\include" string ";"                       -> include_stmt

label: IDENT ":"

goto_stmt: _GOTO IDENT ";"

function_stmt: _FUNCTION IDENT "(" args ")" "{" body "}"

return_stmt: _RETURN expr ";"

if_stmt: _IF "(" expr ")" "{" body "}"

if_else_stmt: _IF "(" expr ")" "{" body "}" _ELSE (if_else_stmt | if_stmt | "{" body "}")

while_stmt: _WHILE "(" expr ")" "{" body "}"

do_while_stmt: _DO "{" body "}" _WHILE "(" expr ")"

for_stmt: _FOR "(" expr ";" expr ";" expr ")" "{" body "}"

break_stmt: _BREAK ";"
continue_stmt: _CONTINUE ";"

expr_stmt: expr ";"

?expr: assign

?assign: assign_expr "=" assign
       | assign_expr "+=" assign -> iadd
       | assign_expr "-=" assign -> isub
       | assign_expr "*=" assign -> imul
       | assign_expr "/=" assign -> idiv
       | assign_expr "%=" assign -> imod
       | assign_expr "%/%=" assign -> ifloordiv
       | cmp

?assign_expr: IDENT -> var

?cmp: sum "==" sum -> eq
    | sum "!=" sum -> ne
    | sum "<" sum  -> lt
    | sum "<=" sum -> le
    | sum ">" sum  -> gt
    | sum ">=" sum -> ge
    | sum

?sum: sum "+" prod -> add
    | sum "-" prod -> sub
    | prod

?prod: prod "*" prefix   -> mul
     | prod "/" prefix   -> div
     | prod "%/%" prefix -> floordiv
     | prod "%" prefix   -> mod
     | prefix

?prefix: "+" prefix -> pos
       | "-" prefix -> neg
       | power

?power: postfix "**" prefix -> pow
      | postfix

?postfix: postfix "(" (expr ("," expr)*)? ")" -> call
        | atom

?atom: literal
     | IDENT -> var
     | "(" expr ")"

?literal: string
        | function
        | INT -> int
        | FLOAT -> float
        | _TRUE -> true
        | _FALSE -> false
        | _NULL -> null

string: STRING_DQUOTE
      | STRING_SQUOTE
STRING_DQUOTE: "\"" _STRING_ESC_INNER "\""
STRING_SQUOTE: "'" _STRING_ESC_INNER "'"
_STRING_INNER: /.*?/
_STRING_ESC_INNER: _STRING_INNER /(?<!\\)(\\\\)*?/

function: _FUNCTION "(" args ")" "{" body "}"
args: (IDENT ("," IDENT)*)?

IDENT: /(?!/ RESERVED  /)/ CNAME

RESERVED: _TRUE | _FALSE | _NULL | _FUNCTION | _RETURN | _IF | _ELSE | _WHILE | _GOTO | _DO | _FOR | _BREAK | _CONTINUE
_TRUE: "True"
_FALSE: "False"
_NULL: "None"
_FUNCTION: "function"
_RETURN: "return"
_IF: "if"
_ELSE: "else"
_WHILE: "while"
_GOTO: "goto"
_DO: "do"
_FOR: "for"
_BREAK: "break"
_CONTINUE: "continue"

%import common.CNAME
%import common.ESCAPED_STRING
%import common.INT
%import common.FLOAT
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

class PLBreak(PLCtrlException):
    pass

class PLContinue(PLCtrlException):
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
        return f'<baba-lang function {self.name}({", ".join(self.form_args)})>'


def unary_operator(f):
    def operator(self, tree):
        a, = tree.children
        return f(self.visit(a))
    operator.__name__ = f.__name__
    return operator

def binary_operator(f):
    def operator(self, tree):
        a, b = tree.children
        return f(self.visit(a), self.visit(b))
    operator.__name__ = f.__name__
    return operator

def inplace_operator(f):
    def operator(self, tree):
        a, b = tree.children
        new_a = f(self.visit(a), self.visit(b))
        self._nonlocal_assign(a, new_a)
        return new_a
    operator.__name__ = f.__name__
    return operator


class PLInterpreter(Interpreter):
    def __init__(self):
        self.call_stack = [PLFrame({}, [])]

    # ----- helpers -----

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
        label, = tree.children
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
        self._call(func, args)

    def call_and_save_stmt(self, tree):
        '''Calls a function and save its result to a variable'''
        varname, func, *args = tree.children
        func = self.visit(func)
        args = [self.visit(a) for a in args]
        self.var_set(varname.value, self._call(func, args))

    def return_stmt(self, tree):
        '''Raises an exception to return control'''
        value, = tree.children
        raise PLReturn(self.visit(value))

    def sleep_stmt(self, tree):
        '''Sleeps for a certain amount of time'''
        time, = tree.children
        sleep(self.visit(time))

    def exit_stmt(self, tree):
        '''Exits the interpreter'''
        if len(tree.children) == 0:
            exitcode = 0
        elif len(tree.children) == 1:
            exitcode, = tree.children
            exitcode = self.visit(exitcode)
        sys.exit(exitcode)

    def input_stmt(self, tree):
        '''Get input from the user'''
        if len(tree.children) == 1:
            varname, = tree.children
            prompt = ''
        elif len(tree.children) == 2:
            varname, prompt = tree.children
            prompt = self.visit(prompt)
        self.var_set(varname.value, input(prompt))
        
    def include_stmt(self, tree):
        '''Execute a script'''
        filename, = tree.children
        filename = self.visit(filename)
        with open(filename, encoding='utf-8') as f:
            interpret(f.read())

    def if_stmt(self, tree):
        '''Executes the body if the condition is true'''
        cond, body = tree.children
        if self.visit(cond):
            self.visit(body)

    def if_else_stmt(self, tree):
        '''Executes body 1 if the condition is true, otherwise body 2'''
        cond, body1, body2 = tree.children
        if self.visit(cond):
            self.visit(body1)
        else:
            self.visit(body2)

    def while_stmt(self, tree):
        '''Executes the body *while* the condition is true'''
        cond, body = tree.children
        self._loop(cond, body)

    def do_while_stmt(self, tree):
        '''Same as while_stmt, but executes the body first before evaluating the condition'''
        cond, body = tree.children
        self.visit(body)
        self._loop(cond, body)

    def for_stmt(self, tree):
        '''C for loop'''
        start, cond, step, body = tree.children
        self.visit(start)
        self._loop(cond, body, step)

    def break_stmt(self, tree):
        '''Breaks out of a loop'''
        raise PLBreak

    def continue_stmt(self, tree):
        '''Skip the rest of the loop body'''
        raise PLContinue

    def _loop(self, cond, body, step=None):
        while self.visit(cond):
            try:
                self.visit(body)
            except PLBreak:
                break
            except PLContinue:
                continue
            except Exception as e:
                raise e
            finally:
                if step:
                    self.visit(step)

    def expr_stmt(self, tree):
        '''Expression statement'''
        expr, = tree.children
        return self.visit(expr)

    def assign(self, tree):
        assign_expr, value = tree.children
        value = self.visit(value)
        if assign_expr.data == 'var':
            name, = assign_expr.children
            self.var_set(name.value, value)
        return value

    def _nonlocal_assign(self, assign_expr, value):
        if assign_expr.data == 'var':
            name, = assign_expr.children
            self.var_search_set(name.value, value)

    iadd = inplace_operator(operator.add)
    isub = inplace_operator(operator.sub)
    imul = inplace_operator(operator.mul)
    idiv = inplace_operator(operator.truediv)
    imod = inplace_operator(operator.mod)
    ifloordiv = inplace_operator(operator.floordiv)
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
    pos = unary_operator(operator.pos)
    neg = unary_operator(operator.neg)
    pow = binary_operator(operator.pow)

    def call(self, tree):
        func, *spec_args = tree.children
        func = self.visit(func)
        spec_args = [self.visit(a) for a in spec_args]
        return self._call(func, spec_args)

    def _call(self, func, spec_args):
        if len(spec_args) < len(func.form_args):
            raise RuntimeError('Too little arguments!')
        elif len(spec_args) > len(func.form_args):
            raise RuntimeError('Too many arguments!')
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

    def var(self, tree):
        '''Variable reference'''
        name, = tree.children
        return self.var_search(name)

    def string(self, tree):
        '''String type'''
        s, = tree.children
        return literal_eval(s)

    def function(self, tree):
        '''Anonymous function type'''
        form_args, body = tree.children
        form_args = [a.value for a in form_args.children]
        return PLFunction('<anonymous>', form_args, body, self.call_stack[:])

    def int(self, tree):
        '''Integer type'''
        i, = tree.children
        return literal_eval(i)

    def float(self, tree):
        '''Float type'''
        f, = tree.children
        return literal_eval(f)

    def true(self, tree):
        '''Boolean "True"'''
        return True

    def false(self, tree):
        '''Boolean "False"'''
        return False

    def null(self, tree):
        '''Null value'''
        return None

pl_interpreter = PLInterpreter()


def interpret(src):
    parse_tree = pl_parser.parse(src)
    pl_interpreter.visit(parse_tree)


def main(args):
    if len(args) > 1:
        file = args[1]
        with open(file, encoding='utf-8') as f:
            interpret(f.read())
    else:
        logging.basicConfig(format='%(levelname)s: %(message)s')
        while True:
            inpt = input('> ')
            try:
                interpret(inpt)
            except Exception as e:
                logging.error(e)

if __name__ == '__main__':
    main(sys.argv)
