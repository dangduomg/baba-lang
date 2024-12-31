"""AST interpreter"""


from pathlib import Path
from typing import Optional

from lark.tree import Meta
from lark.exceptions import UnexpectedInput

from bl_ast import nodes, parse_to_ast
from bl_ast.base import ASTVisitor

from . import built_ins, bl_types
from .bl_types import exits, function, pywrapper, Value, NULL, Item
from .bl_types.base import Result, ExpressionResult, Success, BLError
from .bl_types.errors import (
    error_not_implemented, error_include_syntax, error_inside_include,
    error_invalid_include,
)
from .bl_types.function import PythonFunction
from .env import Env


class ASTInterpreter(ASTVisitor):
    """AST interpreter"""

    # pylint: disable=too-many-return-statements
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches

    path: str

    globals: Env
    locals: Optional[Env] = None

    calls: list[function.Call]

    def __init__(self, path=''):
        self.path = path
        self.calls = []

        self.globals = Env()
        # Populate some builtins
        self.globals.new_var("print", PythonFunction(built_ins.print_))
        self.globals.new_var(
            "print_dump", PythonFunction(built_ins.print_dump)
        )
        self.globals.new_var("input", PythonFunction(built_ins.input_))
        self.globals.new_var("int", PythonFunction(built_ins.int_))
        self.globals.new_var("float", PythonFunction(built_ins.float_))
        self.globals.new_var("bool", PythonFunction(built_ins.bool_))
        self.globals.new_var("str", PythonFunction(built_ins.str_))
        self.globals.new_var(
            "py_function", PythonFunction(pywrapper.py_function)
        )
        self.globals.new_var(
            "py_method", PythonFunction(pywrapper.py_method)
        )
        self.globals.new_var(
            "py_constant", PythonFunction(pywrapper.py_constant)
        )
        self.globals.new_var("Object", bl_types.ObjectClass)

    def visit(self, node: nodes._AstNode) -> Result:
        # pylint: disable=protected-access
        match node:
            case nodes._Expr():
                return self.visit_expr(node)
            case nodes._Stmt():
                return self.visit_stmt(node)
        return error_not_implemented.copy()

    def visit_stmt(self, node: nodes._Stmt) -> Result:
        """Visit a statement node"""
        match node:
            case nodes.NopStmt():
                return Success()
            case nodes.Body(statements=statements):
                for stmt in statements:
                    if isinstance(res := self.visit(stmt), exits.Exit):
                        return res
                return Success()
            case nodes.IfStmt(meta=meta, condition=condition, body=body):
                match cond := self.visit_expr(condition).to_bool(self, meta):
                    case BLError():
                        return cond
                    case bl_types.Bool(True):
                        return self.visit_stmt(body)
                    case bl_types.Bool(False):
                        return Success()
            case nodes.IfElseStmt(
                meta=meta, condition=condition,
                then_body=then_body, else_body=else_body
            ):
                cond = self.visit_expr(condition).to_bool(self, meta)
                match cond:
                    case BLError():
                        return cond
                    case bl_types.Bool(True):
                        return self.visit_stmt(then_body)
                    case bl_types.Bool(False):
                        return self.visit_stmt(else_body)
            case nodes.WhileStmt(
                meta=meta, condition=condition, body=body,
                eval_condition_after=eval_condition_after,
            ):
                eval_condition = not eval_condition_after
                while True:
                    if eval_condition:
                        cond = self.visit_expr(condition).to_bool(self, meta)
                        match cond:
                            case BLError():
                                return cond
                            case bl_types.Bool(False):
                                return Success()
                    res = self.visit_stmt(body)
                    if isinstance(res, exits.Continue):
                        pass
                    elif isinstance(res, exits.Exit):
                        return res
                    if eval_condition_after:
                        eval_condition = True
            case nodes.ForEachStmt(
                meta=meta, pattern=pattern, iterable=iterable, body=body
            ):
                match iterator := (
                    self.visit_expr(iterable).iterate(self, meta)
                ):
                    case BLError():
                        return iterator
                while (next_ := iterator.next(self, meta)) is not NULL:
                    match next_:
                        case BLError():
                            return next_
                        case Item(value):
                            self.assign(meta, pattern, value)
                        case _:
                            return error_not_implemented.copy().set_meta(meta)
                    res = self.visit_stmt(body)
                    if isinstance(res, exits.Continue):
                        pass
                    elif isinstance(res, exits.Exit):
                        return res
                return Success()
            case nodes.BreakStmt():
                return exits.Break()
            case nodes.ContinueStmt():
                return exits.Continue()
            case nodes.ReturnStmt(value=value):
                res = None if value is None else self.visit_expr(value)
                if isinstance(res, BLError):
                    return res
                if isinstance(res, Value):
                    return exits.Return(res)
            case nodes.ThrowStmt(meta=meta, value=value):
                match res := self.visit_expr(value):
                    case BLError():
                        return res
                    case bl_types.String(value=value):
                        return BLError(value, meta)
            case nodes.FunctionStmt(name=name, form_args=form_args, body=body):
                env = None if self.locals is None else self.locals.copy()
                self.globals.new_var(
                    name, bl_types.BLFunction(str(name), form_args, body, env)
                )
                return Success()
            case nodes.ModuleStmt(name=name, body=body):
                # Create new environment
                self.globals = Env(parent=self.globals)
                # Evaluate the body
                match res := self.visit_stmt(body):
                    case BLError():
                        return res
                vars_ = {str(name): var.value
                         for name, var in self.globals.vars.items()}
                # Clean up
                if self.globals.parent is not None:
                    self.globals = self.globals.parent
                self.globals.new_var(name, bl_types.Module(name, vars_))
                return Success()
            case nodes.ClassStmt(
                meta=meta, name=name, super=super_, body=body
            ):
                # Create new environment
                self.globals = Env(parent=self.globals)
                # Evaluate the body
                match res := self.visit_stmt(body):
                    case BLError():
                        return res
                vars_ = {
                    str(name): var.value
                    for name, var in self.globals.vars.items()
                }
                # Clean up
                if self.globals.parent is not None:
                    self.globals = self.globals.parent
                # Create the class
                if super_ is None:
                    superclass = bl_types.ObjectClass
                else:
                    superclass = self._get_var(super_, meta)
                    match superclass:
                        case bl_types.Class():
                            pass
                        case BLError():
                            return res
                        case _:
                            return error_not_implemented.copy().set_meta(meta)
                self.globals.new_var(
                    name, bl_types.Class(name, vars_, superclass)
                )
                return Success()
            case nodes.IncludeStmt():
                return self.visit_include(node)
        return error_not_implemented.copy().set_meta(node.meta)

    def visit_include(self, node: nodes.IncludeStmt) -> Result:
        """Visit an include statement node"""
        path = node.path
        meta = node.meta
        try:
            # Find from current working directory
            f = open(Path.cwd() / path, encoding='utf-8')
        except FileNotFoundError:
            return error_invalid_include.copy().fill_args(path).set_meta(meta)
        with f:
            src = f.read()
            # Execute Python source code
            if path.endswith('.py'):
                exec(src, globals())  # pylint: disable=exec-used
                return Success()
            # Invalid include target
            if not path.endswith('.bl'):
                return (
                    error_invalid_include.copy().fill_args(path).set_meta(meta)
                )
            try:
                include_ast = parse_to_ast(src)
            except UnexpectedInput as e:
                return (
                    error_include_syntax.copy()
                    .fill_args(f"{e.get_context(src)}\n{e}")
                    .set_meta(meta)
                )
            match self.visit(include_ast):
                case BLError(value=msg, meta=meta):
                    if meta is None:
                        return (
                            error_inside_include.copy()
                            .fill_args("n/a", "n/a", msg)
                            .set_meta(meta)
                        )
                    return (
                        error_inside_include.copy()
                        .fill_args(meta.line, meta.column, msg)
                        .set_meta(meta)
                    )
                case Success():
                    return Success()
        return error_not_implemented.copy().set_meta(meta)

    def visit_expr(self, node: nodes._Expr) -> ExpressionResult:
        """Visit an expression node"""
        match node:
            case nodes.Exprs(expressions=expressions):
                final_res = bl_types.NULL
                for expr in expressions:
                    res = self.visit_expr(expr)
                    if isinstance(res, BLError):
                        return res
                    if isinstance(res, Value):
                        final_res = res
                return final_res
            case nodes.Assign(meta=meta, pattern=pattern, right=right):
                rhs_result = self.visit_expr(right)
                if isinstance(rhs_result, BLError):
                    return rhs_result
                if isinstance(rhs_result, Value):
                    return self.assign(meta, pattern, rhs_result)
            case nodes.Inplace():
                return self.visit_inplace(node)
            case nodes.And(left=left, op=op, right=right):
                left_res = self.visit_expr(left).to_bool(self, left.meta)
                match left_res:
                    case BLError():
                        return left_res
                    case bl_types.Bool(True):
                        return left_res
                    case bl_types.Bool(False):
                        return self.visit_expr(right)
            case nodes.Or(left=left, op=op, right=right):
                left_res = self.visit_expr(left).to_bool(self, left.meta)
                match left_res:
                    case BLError():
                        return left_res
                    case bl_types.Bool(False):
                        return left_res
                    case bl_types.Bool(True):
                        return self.visit_expr(right)
            case nodes.BinaryOp(meta=meta, left=left, op=op, right=right):
                return (
                    self.visit_expr(left)
                    .binary_op(op, self.visit_expr(right), self, meta)
                )
            case nodes.Subscript(meta=meta, subscriptee=subscriptee,
                                 index=index):
                return self.visit_expr(subscriptee).get_item(
                    self.visit_expr(index), self, meta
                )
            case nodes.Call(meta=meta, callee=callee, args=args_in_ast):
                # Visit all args, stop if one is an error
                args = []
                for arg in args_in_ast.args:
                    arg_visited = self.visit_expr(arg)
                    if not isinstance(arg_visited, Value):
                        return arg_visited
                    args.append(arg_visited)
                callee = self.visit_expr(callee)
                return callee.call(args, self, meta)
            case nodes.New(meta=meta, class_name=name, args=args_):
                # Visit all args, stop if one is an error
                args = []
                if args_ is not None:
                    for arg in args_.args:
                        arg_visited = self.visit_expr(arg)
                        if not isinstance(arg_visited, Value):
                            return arg_visited
                        args.append(arg_visited)
                match class_ := self._get_var(name, meta):
                    case bl_types.Class():
                        return class_.new(args, self, meta)
                    case BLError():
                        return class_
            case nodes.Prefix(meta=meta, op=op, operand=operand):
                return self.visit_expr(operand).unary_op(op, self, meta)
            case nodes.Dot(meta=meta, accessee=accessee, attr_name=attr):
                return self.visit_expr(accessee).get_attr(attr, meta)
            case nodes.Var(meta=meta, name=name):
                return self._get_var(name, meta)
            case nodes.String(value=value):
                return bl_types.String(value)
            case nodes.Int(value=value):
                return bl_types.Int(value)
            case nodes.Float(value=value):
                return bl_types.Float(value)
            case nodes.TrueLiteral():
                return bl_types.BOOLS[True]
            case nodes.FalseLiteral():
                return bl_types.BOOLS[False]
            case nodes.NullLiteral():
                return bl_types.NULL
            case nodes.List(elems=elems_in_ast):
                elems = []
                for e in elems_in_ast:
                    e_visited = self.visit_expr(e)
                    if not isinstance(e_visited, Value):
                        return e_visited
                    elems.append(e_visited)
                return bl_types.BLList(elems)
            case nodes.Dict(pairs=pairs):
                content = {}
                for pair in pairs:
                    k_visited = self.visit(pair.key)
                    v_visited = self.visit(pair.value)
                    content[k_visited] = v_visited
                return bl_types.BLDict(content)
            case nodes.FunctionLiteral(form_args=form_args, body=body):
                env = None if self.locals is None else self.locals.copy()
                return bl_types.BLFunction("<anonymous>", form_args, body, env)
        return error_not_implemented.copy().set_meta(node.meta)

    def assign(
        self, meta: Meta, pattern: nodes._Pattern, value: Value
    ) -> ExpressionResult:
        """Visit an assignment node"""
        match pattern:
            case nodes.VarPattern(name=name):
                self._new_var(name, value)
                return value
            case nodes.SubscriptPattern(
                subscriptee=subscriptee_,
                index=index_,
            ):
                subscriptee = self.visit_expr(subscriptee_)
                index = self.visit_expr(index_)
                return subscriptee.set_item(index, value, self, meta)
            case nodes.DotPattern(
                accessee=accessee_,
                attr_name=attr,
            ):
                accessee = self.visit_expr(accessee_)
                return accessee.set_attr(attr, value, meta)
        return error_not_implemented.copy().set_meta(meta)

    def visit_inplace(self, node: nodes.Inplace) -> ExpressionResult:
        """Visit an in-place assignment node"""
        meta = node.meta
        rhs_result = self.visit_expr(node.right)
        if isinstance(rhs_result, BLError):
            return rhs_result
        if not isinstance(rhs_result, Value):
            return error_not_implemented.copy().set_meta(meta)
        by = rhs_result
        pattern = node.pattern
        if isinstance(pattern, nodes.VarPattern):
            name = pattern.name
            old_value_get_result = self._get_var(name, meta)
            new_result = old_value_get_result.binary_op(
                node.op[:-1], by, self, meta
            )
            match old_value_get_result, new_result:
                case Value(), BLError():
                    return new_result
                case BLError(), _:
                    return old_value_get_result
                case _, Value():
                    value = new_result
                    self.globals.set_var(name, value, node.meta)
                    return value
        if isinstance(pattern, nodes.SubscriptPattern):
            subscriptee = self.visit_expr(pattern.subscriptee)
            index = self.visit_expr(pattern.index)
            old_value_get_result = subscriptee.get_item(index, self, meta)
            new_result = old_value_get_result.binary_op(
                node.op[:-1], by, self, meta
            )
            match old_value_get_result, new_result:
                case Value(), BLError():
                    return new_result
                case BLError(), _:
                    return old_value_get_result
                case _, Value():
                    value = new_result
                    subscriptee.set_item(index, value, self, meta)
                    return value
        if isinstance(pattern, nodes.DotPattern):
            subscriptee = self.visit_expr(pattern.accessee)
            old_value_get_result = (
                subscriptee.get_attr(pattern.attr_name, meta)
            )
            new_result = old_value_get_result.binary_op(
                node.op[:-1], by, self, meta
            )
            match old_value_get_result, new_result:
                case Value(), BLError():
                    return new_result
                case BLError(), _:
                    return old_value_get_result
                case _, Value():
                    value = new_result
                    subscriptee.set_attr(pattern.attr_name, value, meta)
                    return value
        return error_not_implemented.copy().set_meta(meta)

    def _get_var(self, name: str, meta: Meta) -> ExpressionResult:
        """Get a variable either from locals or globals"""
        if self.locals is not None:
            res = self.locals.get_var(name, meta)
            if isinstance(res, Value):
                return res
        return self.globals.get_var(name, meta)

    def _set_var(self, name: str, value: Value, meta: Meta) -> BLError | None:
        """Set a variable either in locals or globals"""
        if self.locals is not None:
            res = self.locals.set_var(name, value, meta)
            if res is not None:  # if its an error
                return res
        return self.globals.set_var(name, value, meta)

    def _new_var(self, name: str, value: Value) -> None:
        """Assign a new variable either in locals or globals"""
        if self.locals is not None:
            self.locals.new_var(name, value)
            return
        self.globals.new_var(name, value)
