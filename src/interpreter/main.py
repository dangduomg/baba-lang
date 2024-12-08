"""AST interpreter"""


import ast_classes
from ast_base import ASTVisitor

from . import values
from .base import Result, ExpressionResult, error_not_implemented


#pylint: disable=too-many-return-statements


class ASTInterpreter(ASTVisitor):
    """AST interpreter"""

    def visit(self, node: ast_classes._AstNode) -> Result:
        #pylint: disable=protected-access
        match node:
            # case ast_classes._Stmt():
            #     return self.visit_stmt(node)
            case ast_classes._Expr():
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

    def visit_expr(self, node: ast_classes._Expr) -> ExpressionResult:
        """Visit an expression node"""
        match node:
            case ast_classes.BinaryOp(meta=meta, left=left, op=op, right=right):
                return self.visit_expr(left).binary_op(op, self.visit_expr(right), meta)
            case ast_classes.Subscript(meta=meta, subscriptee=subscriptee, index=index):
                return self.visit_expr(subscriptee).get_item(self.visit_expr(index), meta)
            case ast_classes.Prefix(meta=meta, op=op, operand=operand):
                return self.visit_expr(operand).unary_op(op, meta)
            case ast_classes.String(value=value):
                return values.String(value)
            case ast_classes.Int(value=value):
                return values.Int(value)
            case ast_classes.Float(value=value):
                return values.Float(value)
            case ast_classes.TrueLiteral():
                return values.BOOLS[True]
            case ast_classes.FalseLiteral():
                return values.BOOLS[False]
            case ast_classes.NullLiteral():
                return values.NULL
            case ast_classes.List(elems=elems_in_ast):
                elems = []
                for e in elems_in_ast:
                    e_visited = self.visit_expr(e)
                    if not isinstance(e_visited, values.Value):
                        return e_visited
                    elems.append(e_visited)
                return values.List(elems)
            case ast_classes.Dict(pairs=pairs):
                content = {}
                for pair in pairs:
                    k_visited = self.visit(pair.key)
                    v_visited = self.visit(pair.value)
                    content[k_visited] = v_visited
                return values.Dict(content)
        return error_not_implemented
