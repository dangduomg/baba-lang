"""AST interpreter"""


from bl_ast import nodes
from bl_ast.base import ASTVisitor

from . import values
from .base import Result, ExpressionResult, error_not_implemented


#pylint: disable=too-many-return-statements


class ASTInterpreter(ASTVisitor):
    """AST interpreter"""

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
        match node:
            case nodes.BinaryOp(meta=meta, left=left, op=op, right=right):
                return self.visit_expr(left).binary_op(op, self.visit_expr(right), meta)
            case nodes.Subscript(meta=meta, subscriptee=subscriptee, index=index):
                return self.visit_expr(subscriptee).get_item(self.visit_expr(index), meta)
            case nodes.Prefix(meta=meta, op=op, operand=operand):
                return self.visit_expr(operand).unary_op(op, meta)
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
