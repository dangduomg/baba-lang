"""AST interpreter"""


from dataclasses import dataclass
from typing import Optional

from lark.tree import Meta

from bl_ast import nodes
from bl_ast.base import ASTVisitor

from . import values
from .base import Result, ExpressionResult, BLError, \
                  error_not_implemented, error_var_nonexistent
from .values import Value


#pylint: disable=too-many-return-statements


@dataclass
class Var:
    """Interpreter mutable binding"""

    value: Value


class Env:
    """Interpreter environment"""

    vars: dict[str, Var]
    parent: Optional['Env']

    def __init__(self, parent: Optional['Env'] = None):
        self.vars = {}
        self.parent = parent

    def new_var(self, name: str, value: Value) -> None:
        """Set a new/existing variable"""
        self.vars[name] = Var(value)

    def get_var(self, name: str, meta: Meta) -> ExpressionResult:
        """Retrieve the value of a variable"""
        resolve_result = self.resolve_var(name, meta)
        match resolve_result:
            case Var(value=value):
                return value
            case BLError():
                return resolve_result

    def set_var(self, name: str, value: Value, meta: Meta) -> Optional[BLError]:
        """Assign to an existing variable name"""
        resolve_result = self.resolve_var(name, meta)
        match resolve_result:
            case Var():
                resolve_result.value = value
            case BLError():
                return resolve_result

    def resolve_var(self, name: str, meta: Meta) -> Var | BLError:
        """Resolve a variable name"""
        if name in self.vars:
            return self.vars[name]
        if self.parent is not None:
            return self.parent.resolve_var(name, meta)
        return error_var_nonexistent.fill_args(name).set_meta(meta)


class ASTInterpreter(ASTVisitor):
    """AST interpreter"""

    globals: Env

    def __init__(self):
        self.globals = Env()

    def visit(self, node: nodes._AstNode) -> Result:
        #pylint: disable=protected-access
        match node:
            # case ast_classes._Stmt():
            #     return self.visit_stmt(node)
            case nodes._Expr():
                return self.visit_expr(node)
        return error_not_implemented

    # def visit_stmt(self, node: ast_classes._Stmt) -> Result:
    #     #pylint: disable=protected-access
    #     match node:
    #         case ast_classes.Body(statements=statements):
    #             for stmt in statements:
    #                 self.visit(stmt)
    #             return Success()
    #     return error_not_implemented

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
                    if not isinstance(e_visited, values.Value):
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
