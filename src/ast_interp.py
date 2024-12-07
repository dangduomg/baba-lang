"""AST interpreter"""


from dataclasses import dataclass

from lark import Token

import ast_classes
from ast_base import ASTVisitor


class Result:
    def binary_op(self, op: Token, other: 'Result') -> 'Result':
        match op:
            case '+':
                return self.add(other)
            case _:
                return Error_('Operation not implemented')

    def add(self, other: 'Result') -> 'Result':
        return Error_('Operation not implemented')


@dataclass
class Error_(Result):
    value: object


@dataclass(frozen=True)
class Value(Result):
    pass


@dataclass(frozen=True)
class Int(Value):
    value: int


class ASTInterpreter(ASTVisitor):
    """AST interpreter"""

    def visit(self, node: ast_classes._AstNode) -> Result:
        #pylint: disable=protected-access
        match node:
            case ast_classes._Expr():
                return self.visit_expr(node)
        return error_not_implemented

    def visit_expr(self, node: ast_classes._Expr) -> ExpressionResult:
        """Visit an expression node"""
        match node:
            case ast_classes.BinaryOp(meta=meta, left=left, op=op, right=right):
                return self.visit_expr(left).binary_op(op, self.visit_expr(right), meta)
            case ast_classes.Prefix(meta=meta, op=op, operand=operand):
                return self.visit_expr(operand).unary_op(op, meta)
            case ast_classes.Int(value=value):
                return Int(value)
        return error_not_implemented