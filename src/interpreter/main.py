"""AST interpreter"""


from typing import Optional

from lark.tree import Meta

from bl_ast import nodes
from bl_ast.base import ASTVisitor

from . import values, exits
from .base import Result, ExpressionResult, Success, BLError, \
                  error_not_implemented
from .values import Value, PythonFunction
from .env import Env


class ASTInterpreter(ASTVisitor):
    """AST interpreter"""

    #pylint: disable=too-many-return-statements

    globals: Env
    locals: Optional[Env] = None

    def __init__(self):
        self.globals = Env()
        # Populate some builtins
        self.globals.new_var('print', PythonFunction(self._print))
        self.globals.new_var('print_dump', PythonFunction(self._print_dump))
        self.globals.new_var('input', PythonFunction(self._input))

    def visit(self, node: nodes._AstNode) -> Result:
        #pylint: disable=protected-access
        match node:
            case nodes._Expr():
                return self.visit_expr(node)
            case nodes._Stmt():
                return self.visit_stmt(node)
        return error_not_implemented

    def visit_stmt(self, node: nodes._Stmt) -> Result:
        """Visit a statement node"""
        match node:
            case nodes.Body(statements=statements):
                for stmt in statements:
                    match res := self.visit(stmt):
                        case exits.Exit():
                            return res
                return Success()
            case nodes.IfStmt(meta=meta, condition=condition, body=body):
                match cond := self.visit_expr(condition).to_bool(meta):
                    case BLError():
                        return cond
                    case values.Bool(True):
                        return self.visit_stmt(body)
                    case values.Bool(False):
                        return Success()
            case nodes.IfElseStmt(meta=meta, condition=condition,
                                  then_body=then_body, else_body=else_body):
                match cond := self.visit_expr(condition).to_bool(meta):
                    case BLError():
                        return cond
                    case values.Bool(True):
                        return self.visit_stmt(then_body)
                    case values.Bool(False):
                        return self.visit_stmt(else_body)
            case nodes.WhileStmt(meta=meta, condition=condition, body=body,
                                 eval_condition_after=eval_condition_after):
                while True:
                    if not eval_condition_after:
                        match cond := self.visit_expr(condition).to_bool(meta):
                            case BLError():
                                return cond
                            case values.Bool(False):
                                return Success()
                    match res := self.visit_stmt(body):
                        case exits.Continue():
                            pass
                        case exits.Exit():
                            return res
                    if eval_condition_after:
                        match cond := self.visit_expr(condition).to_bool(meta):
                            case BLError():
                                return cond
                            case values.Bool(False):
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
            case nodes.FunctionStmt(name=name, form_args=form_args, body=body):
                env = None if self.locals is None else self.locals.copy()
                self.globals.new_var(name, values.BLFunction(str(name), form_args, body, env))
                return Success()
        return error_not_implemented

    def visit_expr(self, node: nodes._Expr) -> ExpressionResult:
        """Visit an expression node"""
        #pylint: disable=too-many-locals
        match node:
            case nodes.Exprs(expressions=expressions):
                final_res = values.NULL
                for expr in expressions:
                    match res := self.visit_expr(expr):
                        case BLError():
                            return res
                        case Value():
                            final_res = res
                return final_res
            case nodes.Assign():
                return self.visit_assign(node)
            case nodes.Inplace():
                return self.visit_inplace(node)
            case nodes.BinaryOp(meta=meta, left=left, op=op, right=right):
                return self.visit_expr(left).binary_op(op, self.visit_expr(right), meta)
            case nodes.Subscript(meta=meta, subscriptee=subscriptee, index=index):
                return self.visit_expr(subscriptee).get_item(self.visit_expr(index), meta)
            case nodes.Call(meta=meta, callee=callee, args=args_in_ast):
                args = []
                for arg in args_in_ast.args:
                    arg_visited = self.visit_expr(arg)
                    if not isinstance(arg_visited, Value):
                        return arg_visited
                    args.append(arg_visited)
                return self.visit_expr(callee).call(args, self, meta)
            case nodes.Prefix(meta=meta, op=op, operand=operand):
                return self.visit_expr(operand).unary_op(op, meta)
            case nodes.Var(meta=meta, name=name):
                if self.locals is not None:
                    if isinstance(res := self.locals.get_var(name, meta), Value):
                        return res
                return self.globals.get_var(name, meta)
            case nodes.String(value=value):
                return values.String(value)
            case nodes.Int(value=value):
                return values.Int(value)
            case nodes.Float(value=value):
                return values.Float(value)
            case nodes.TrueLiteral():
                return values.BOOLS[True]
            case nodes.FalseLiteral():
                return values.BOOLS[False]
            case nodes.NullLiteral():
                return values.NULL
            case nodes.List(elems=elems_in_ast):
                elems = []
                for e in elems_in_ast:
                    e_visited = self.visit_expr(e)
                    if not isinstance(e_visited, Value):
                        return e_visited
                    elems.append(e_visited)
                return values.BLList(elems)
            case nodes.Dict(pairs=pairs):
                content = {}
                for pair in pairs:
                    k_visited = self.visit(pair.key)
                    v_visited = self.visit(pair.value)
                    content[k_visited] = v_visited
                return values.BLDict(content)
            case nodes.FunctionLiteral(form_args=form_args, body=body):
                env = None if self.locals is None else self.locals.copy()
                return values.BLFunction('<anonymous>', form_args, body, env)
        return error_not_implemented

    def visit_assign(self, node: nodes.Assign) -> ExpressionResult:
        """Visit an assignment node"""
        rhs_result = self.visit_expr(node.right)
        if isinstance(rhs_result, BLError):
            return rhs_result
        if isinstance(rhs_result, Value):
            value = rhs_result
            match node.pattern:
                case nodes.VarPattern(name=name):
                    self.globals.new_var(name, value)
                    return value
                case nodes.SubscriptPattern(subscriptee=subscriptee_, index=index_):
                    subscriptee = self.visit_expr(subscriptee_)
                    index = self.visit_expr(index_)
                    return subscriptee.set_item(index, value, node.meta)
        return error_not_implemented.set_meta(node.meta)

    def visit_inplace(self, node: nodes.Inplace) -> ExpressionResult:
        """Visit an in-place assignment node"""
        rhs_result = self.visit_expr(node.right)
        if isinstance(rhs_result, BLError):
            return rhs_result
        if isinstance(rhs_result, Value):
            by = rhs_result
            match node.pattern:
                case nodes.VarPattern(name=name):
                    old_value_get_result = self.globals.get_var(name, node.meta)
                    new_result = old_value_get_result.binary_op(node.op[:-1], by, node.meta)
                    match old_value_get_result, new_result:
                        case Value(), BLError():
                            return new_result
                        case BLError(), _:
                            return old_value_get_result
                        case _, Value():
                            value = new_result
                            self.globals.set_var(name, value, node.meta)
                            return value
                case nodes.SubscriptPattern(subscriptee=subscriptee, index=index):
                    subscriptee = self.visit_expr(subscriptee)
                    index = self.visit_expr(index)
                    old_value_get_result = subscriptee.get_item(index, node.meta)
                    new_result = old_value_get_result.binary_op(node.op[:-1], by, node.meta)
                    match old_value_get_result, new_result:
                        case Value(), BLError():
                            return new_result
                        case BLError(), _:
                            return old_value_get_result
                        case _, Value():
                            value = new_result
                            subscriptee.set_item(index, value, node.meta)
                            return value
        return error_not_implemented.set_meta(node.meta)

    # Builtins

    def _print(self, meta: Optional[Meta], interpreter: 'ASTInterpreter', /, *args: Value
               ) -> values.Null:
        #pylint: disable=unused-argument
        print(*(arg.to_string(meta).value for arg in args))
        return values.NULL

    def _print_dump(self, meta: Optional[Meta], interpreter: 'ASTInterpreter', /, *args: Value
                    ) -> values.Null:
        #pylint: disable=unused-argument
        print(*(arg.dump(meta) for arg in args))
        return values.NULL

    def _input(self, meta: Optional[Meta], interpreter: 'ASTInterpreter', /, *args: Value
              ) -> values.String:
        #pylint: disable=unused-argument
        return values.String(input(args[0] if args else ''))
