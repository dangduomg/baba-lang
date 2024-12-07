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

    def visit(self, node: ast_classes._AstNode) -> Result:
        match node:
            case ast_classes.BinaryOp(left=left, op=op, right=right):
                return self.visit(left).binary_op(op, self.visit(right))
            case ast_classes.Int(value=value):
                return Int(value)