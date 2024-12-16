"""AST interpreter"""


from lark.tree import Meta

from bl_ast import nodes
from bl_ast.base import ASTVisitor

from . import values
from .base import Result, ExpressionResult, Success, BLError, \
                  error_not_implemented
from .values import Value, PythonFunction
from .env import Env


#pylint: disable=too-many-return-statements


class ASTInterpreter(ASTVisitor):
    """AST interpreter"""

    globals: Env

    def __init__(self):
        self.globals = Env()
        # Populate some builtins
        self.globals.new_var('print', PythonFunction(self._print))
        self.globals.new_var('print_dump', PythonFunction(self._print_dump))


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
        #pylint: disable=protected-access
        match node:
            case nodes.Body(statements=statements):
                for stmt in statements:
                    self.visit(stmt)
                return Success()
        return error_not_implemented

    def visit_expr(self, node: nodes._Expr) -> ExpressionResult:
        """Visit an expression node"""
        #pylint: disable=too-many-locals
        match node:
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
                return self.visit_expr(callee).call(args, meta)
            case nodes.Prefix(meta=meta, op=op, operand=operand):
                return self.visit_expr(operand).unary_op(op, meta)
            case nodes.Var(meta=meta, name=name):
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
        return error_not_implemented

    def visit_assign(self, node: nodes.Assign) -> ExpressionResult:
        """Visit an assignment node"""
        value_eval_result = self.visit_expr(node.value)
        if isinstance(value_eval_result, BLError):
            return value_eval_result
        if isinstance(value_eval_result, Value):
            value = value_eval_result
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
        by_eval_result = self.visit_expr(node.by)
        if isinstance(by_eval_result, BLError):
            return by_eval_result
        if isinstance(by_eval_result, Value):
            by = by_eval_result
            match node.pattern:
                case nodes.VarPattern(name=name):
                    old_value_get_result = self.globals.get_var(name, node.meta)
                    value_eval_result = old_value_get_result.binary_op(node.op, by, node.meta)
                    match old_value_get_result, value_eval_result:
                        case Value(), BLError():
                            return value_eval_result
                        case BLError(), _:
                            return old_value_get_result
                        case _, Value():
                            value = value_eval_result
                            self.globals.set_var(name, value, node.meta)
                            return value
                case nodes.SubscriptPattern(subscriptee=subscriptee_, index=index_):
                    subscriptee = self.visit_expr(subscriptee_)
                    index = self.visit_expr(index_)
                    old_value_get_result = subscriptee.get_item(index, node.meta)
                    value_eval_result = old_value_get_result.binary_op(node.op, by, node.meta)
                    match old_value_get_result, value_eval_result:
                        case Value(), BLError():
                            return value_eval_result
                        case BLError(), _:
                            return old_value_get_result
                        case _, Value():
                            value = value_eval_result
                            subscriptee.set_item(index, value, node.meta)
                            return value
        return error_not_implemented.set_meta(node.meta)

    # Builtins

    def _print(self, meta: Meta, /, *args: Value) -> values.Null:
        print(*(arg.to_string(meta).value for arg in args))
        return values.NULL

    def _print_dump(self, meta: Meta, /, *args: Value) -> values.Null:
        print(*(arg.dump(meta) for arg in args))
        return values.NULL
