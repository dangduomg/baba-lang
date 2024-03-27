import sys
import types
import time
import operator
import logging

from lark import Lark
from lark.visitors import Interpreter
from ast import literal_eval


VERSION = '0.2.10'
ABOUT = f'''\
this is babalang, (C) 2024
version {VERSION}
'''


pl_parser = Lark.open('grammar.lark')


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

class PLError(Exception):
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
            raise PLError(f'Can\'t find variable {name}!')

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
            raise PLError(f'Can\'t find variable {name}!')


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

    def top_body(self, tree):
        '''Top-level body in a script. Used for handling leaked control exceptions.'''
        body, = tree.children
        try:
            self.visit(body)
        except PLBreak:
            raise PLError("'break' not in a loop")
        except PLContinue:
            raise PLError("'continue' not in a loop")
        except PLReturn:
            raise PLError("'return' not in a function")
        except Exception as e:
            raise e

    def fn_body(self, tree):
        '''Top-level body in a function. Used for handling leaked control exceptions.'''
        body, = tree.children
        try:
            self.visit(body)
        except PLBreak:
            raise PLError("'break' not in a loop")
        except PLContinue:
            raise PLError("'continue' not in a loop")
        except Exception as e:
            raise e

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
                    raise PLError(f'label "{label}" does not exist')
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
        raise PLReturn(self.visit(value) if value else None)

    def sleep_stmt(self, tree):
        '''Sleeps for a certain amount of time'''
        t, = tree.children
        time.sleep(self.visit(t))

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
        if start:
            self.visit(start)
        self._loop(cond, body, step)

    def break_stmt(self, tree):
        '''Breaks out of a loop'''
        raise PLBreak

    def continue_stmt(self, tree):
        '''Skip the rest of the loop body'''
        raise PLContinue

    def _loop(self, cond, body, step=None):
        while self.visit(cond) if cond else True:
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

    def exprs(self, tree):
        '''Multiple expressions by use of sequence operator'''
        for expr in tree.children:
            res = self.visit(expr)
        return res

    def assign(self, tree):
        assign_expr, value = tree.children
        value = self.visit(value)
        if assign_expr.data == 'var':
            name, = assign_expr.children
            self.var_set(name.value, value)
        elif assign_expr.data == 'subscript':
            expr, index = assign_expr.children
            self.visit(expr)[self.visit(index)] = value
        return value

    def _nonlocal_assign(self, assign_expr, value):
        if assign_expr.data == 'var':
            name, = assign_expr.children
            self.var_search_set(name.value, value)
        elif assign_expr.data == 'subscript':
            expr, index = assign_expr.children
            self.visit(expr)[self.visit(index)] = value

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
    pow = binary_operator(operator.pow)
    subscript = binary_operator(operator.getitem)

    pos = unary_operator(operator.pos)
    neg = unary_operator(operator.neg)

    def call(self, tree):
        func, *spec_args = tree.children
        func = self.visit(func)
        spec_args = [self.visit(a) for a in spec_args]
        return self._call(func, spec_args)

    def _call(self, func, spec_args):
        if not isinstance(func, PLFunction):
            return func(*spec_args)
        decoded_args = self._decode_args(func.form_args, spec_args)
        self.push_frame({}, func.env)
        for k, v in decoded_args.items():
            self.var_set(k, v)
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

    def _decode_args(self, form_args, spec_args):
        if len(spec_args) < len(form_args):
            raise PLError('Too little arguments!')
        if len(spec_args) > len(form_args):
            raise PLError('Too many arguments!')
        return dict(zip(form_args, spec_args))

    def var(self, tree):
        '''Variable reference'''
        name, = tree.children
        return self.var_search(name)

    def string(self, tree):
        '''String type'''
        s, = tree.children
        return literal_eval(s)

    def list(self, tree):
        '''List type'''
        return [self.visit(e) for e in tree.children]
    
    def dict(self, tree):
        '''Dictionary type'''
        pairs = [p.children for p in tree.children]
        return {self.visit(k): self.visit(v) for k, v in pairs}

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
